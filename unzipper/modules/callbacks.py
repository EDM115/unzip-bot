# Copyright (c) 2023 EDM115
import os
import re
import shutil
from fnmatch import fnmatch
from time import time
from urllib.parse import unquote

from aiofiles import open as openfile
from aiohttp import ClientSession
from pyrogram import Client
from pyrogram.errors import ReplyMarkupTooLong
from pyrogram.types import CallbackQuery

from config import Config
from unzipper import LOGGER
from unzipper.helpers.database import (
    add_cancel_task,
    del_thumb_db,
    set_upload_mode,
    update_thumb,
    update_uploaded,
    upload_thumb,
    add_ongoing_task,
    del_ongoing_task,
)
from unzipper.helpers.unzip_help import (
    TimeFormatter,
    extentions_list,
    humanbytes,
    progress_for_pyrogram,
)

from .bot_data import ERROR_MSGS, Buttons, Messages
from .commands import https_url_regex, get_stats
from .ext_script.custom_thumbnail import silent_del
from .ext_script.ext_helper import (
    extr_files,
    get_files,
    make_keyboard,
    make_keyboard_empty,
    split_files,
)
from .ext_script.up_helper import answer_query, get_size, send_file, send_url_logs

# We avoid having a 700 lines long file that way
# from .callbacks_func.cancel import cancel
# from .callbacks_func.ext_a import ext_a
# from .callbacks_func.ext_f import ext_f
# from .callbacks_func.file import file
# from .callbacks_func.keyboard import keyboard
# from .callbacks_func.password import password
# from .callbacks_func.rename import rename
# from .callbacks_func.thumb import thumb
# from .callbacks_func.url import url

split_file_pattern = r"\.(?:[0-9]+|part[0-9]+\.rar|z[0-9]+)$"

# Function to download files from direct link using aiohttp
async def download(url, path):
    async with ClientSession() as session, session.get(url, timeout=None) as resp, openfile(path, mode="wb") as file:
        async for chunk in resp.content.iter_chunked(Config.CHUNK_SIZE):
            await file.write(chunk)
    await session.close()


# Callbacks
@Client.on_callback_query()
async def unzipper_cb(unzip_bot: Client, query: CallbackQuery):
    sent_files = 0
    
    if query.data == "megoinhome":
        await query.edit_message_text(
            text=Messages.START_TEXT.format(query.from_user.mention),
            reply_markup=Buttons.START_BUTTON,
        )

    elif query.data == "helpcallback":
        await query.edit_message_text(text=Messages.HELP_TXT,
                                      reply_markup=Buttons.ME_GOIN_HOME)

    elif query.data == "aboutcallback":
        await query.edit_message_text(
            text=Messages.ABOUT_TXT,
            reply_markup=Buttons.ME_GOIN_HOME,
            disable_web_page_preview=True,
        )

    elif query.data == "donatecallback":
        await query.edit_message_text(
            text=Messages.DONATE_TEXT,
            reply_markup=Buttons.ME_GOIN_HOME,
            disable_web_page_preview=True,
        )
    
    elif query.data.startswith("statscallback"):
        if query.data.endswith("refresh"):
            await query.edit_message_text(text="Refreshing stats... ♻️")
        text_stats = await get_stats(query.from_user.id)
        await query.edit_message_text(
            text=text_stats,
            reply_markup=Buttons.REFRESH_BUTTON,
        )

    elif query.data == "canceldownload":
        await add_cancel_task(query.from_user.id)

    elif query.data == "check_thumb":
        user_id = query.from_user.id
        thumb_location = Config.THUMB_LOCATION + "/" + str(user_id) + ".jpg"
        await unzip_bot.send_photo(chat_id=user_id,
                                   photo=thumb_location,
                                   caption="Your actual thumbnail")
        await unzip_bot.delete_messages(chat_id=user_id,
                                        message_ids=query.message.id)
        await unzip_bot.send_message(
            chat_id=user_id,
            text=Messages.EXISTING_THUMB,
            reply_markup=Buttons.THUMB_FINAL,
        )

    elif query.data == "check_before_del":
        user_id = query.from_user.id
        thumb_location = Config.THUMB_LOCATION + "/" + str(user_id) + ".jpg"
        await unzip_bot.send_photo(chat_id=user_id,
                                   photo=thumb_location,
                                   caption="Your actual thumbnail")
        await unzip_bot.delete_messages(chat_id=user_id,
                                        message_ids=query.message.id)
        await unzip_bot.send_message(
            chat_id=user_id,
            text=Messages.DEL_CONFIRM_THUMB_2,
            reply_markup=Buttons.THUMB_DEL_2,
        )

    elif query.data.startswith("save_thumb"):
        user_id = query.from_user.id
        replace = query.data.split("|")[1]
        if replace == "replace":
            await silent_del(user_id)
        thumb_location = Config.THUMB_LOCATION + "/" + str(user_id) + ".jpg"
        final_thumb = Config.THUMB_LOCATION + "/waiting_" + str(
            user_id) + ".jpg"
        os.rename(final_thumb, thumb_location)
        try:
            thumb_url = await upload_thumb(thumb_location)
            try:
                await update_thumb(query.from_user.id, thumb_url, force=True)
            except:
                LOGGER.warning("Error while updating thumb URL on DB")
        except:
            LOGGER.warning("Error on Telegra.ph upload")
        await answer_query(query, Messages.SAVED_THUMBNAIL)

    elif query.data == "del_thumb":
        user_id = query.from_user.id
        thumb_location = Config.THUMB_LOCATION + "/" + str(user_id) + ".jpg"
        try:
            await del_thumb_db(user_id)
        except Exception as e:
            LOGGER.error(f"Error on thumb deletion in DB : {e}")
        try:
            os.remove(thumb_location)
        except:
            pass
        await query.edit_message_text(text=Messages.DELETED_THUMB)

    elif query.data == "nope_thumb":
        user_id = query.from_user.id
        del_1 = Config.THUMB_LOCATION + "/not_resized_" + str(user_id) + ".jpg"
        del_2 = Config.THUMB_LOCATION + "/waiting_" + str(user_id) + ".jpg"
        try:
            os.remove(del_1)
        except:
            pass
        try:
            os.remove(del_2)
        except:
            pass
        await query.edit_message_text(
            text=Messages.CANCELLED_TXT.format("❌ Task sucessfully canceled"))

    elif query.data.startswith("set_mode"):
        user_id = query.from_user.id
        mode = query.data.split("|")[1]
        await set_upload_mode(user_id, mode)
        await answer_query(query,
                           Messages.CHANGED_UPLOAD_MODE_TXT.format(mode))

    elif query.data.startswith("extract_file"):
        user_id = query.from_user.id
        await add_ongoing_task(user_id)
        download_path = f"{Config.DOWNLOAD_LOCATION}/{user_id}"
        ext_files_dir = f"{download_path}/extracted"
        r_message = query.message.reply_to_message
        splitted_data = query.data.split("|")
        await query.message.edit("**✅ Processing your task… Please wait**")
        global log_msg 
        log_msg = await unzip_bot.send_message(
            chat_id=Config.LOGS_CHANNEL,
            text=f"Processing an user query…\n\nUser ID : {user_id}",
        )
        global archive_msg

        try:
            if splitted_data[1] == "url":
                url = r_message.text
                # Double check
                if not re.match(https_url_regex, url):
                    await del_ongoing_task(user_id)
                    return await query.message.edit("That's not a valid url 💀")
                s = ClientSession()
                async with s as session:
                    # Get the file size
                    unzip_head = await session.head(url, allow_redirects=True)
                    f_size = unzip_head.headers.get("content-length")
                    u_file_size = f_size if f_size else "undefined"
                    await log_msg.edit(
                        Messages.LOG_TXT.format(user_id, url, u_file_size))
                    archive_msg = log_msg
                    # Checks if file is an archive using content-type header
                    unzip_resp = await session.get(url, timeout=None)
                    if "application/" not in unzip_resp.headers.get("content-type"):
                        await del_ongoing_task(user_id)
                        return await query.message.edit(
                            "That's not an archive 💀\n\n**Try to @transload it**"
                        )
                    rfnamebro = unquote(url.split("/")[-1])
                    if unzip_resp.status == 200:
                        # Makes download dir
                        os.makedirs(download_path)
                        s_time = time()
                        fname = unquote(os.path.splitext(url)[1])
                        if splitted_data[2] != "thumb":
                            fext = fname.split(".")[-1].casefold()
                            if fext not in extentions_list["archive"]:
                                await del_ongoing_task(user_id)
                                return await query.message.edit(
                                    "This file is NOT an archive 😐\nIf you believe it's an error, send the file to **@EDM115**"
                                )
                        archive = f"{download_path}/archive_from_{user_id}{fname}"
                        location = archive
                        await answer_query(query,
                                           "`Processing… ⏳`",
                                           unzip_client=unzip_bot)
                        await query.edit_message_text(
                            text=
                            f"**Trying to download… Please wait** \n\n**URL :** `{url}` \n\nThis may take a while, go grab a coffee ☕️",
                            reply_markup=Buttons.I_PREFER_STOP,
                        )
                        await download(url, archive)
                        e_time = time()
                        # Send copy in logs in case url has gone
                        # paths = await get_files(path=archive)
                        await send_url_logs(
                            unzip_bot=unzip_bot,
                            c_id=Config.LOGS_CHANNEL,
                            doc_f=archive,
                            source=url,
                        )
                    else:
                        await del_ongoing_task(user_id)
                        return await query.message.edit(
                            "**Sorry, I can't download that URL 😭 Try to @transload it**"
                        )

            elif splitted_data[1] == "tg_file":
                if r_message.document is None:
                    await del_ongoing_task(user_id)
                    return await query.message.edit(
                        "Give me an archive to extract 😐")
                fname = r_message.document.file_name
                rfnamebro = fname
                archive_msg = await r_message.forward(
                    chat_id=Config.LOGS_CHANNEL)
                await log_msg.edit(
                    Messages.LOG_TXT.format(
                        user_id, fname,
                        humanbytes(r_message.document.file_size)))
                # Checks if it's actually an archive
                # fext = (pathlib.Path(fname).suffix).casefold()
                if splitted_data[2] != "thumb":
                    fext = fname.split(".")[-1].casefold()
                    if (fnmatch(fext, extentions_list["split"][0])
                            or fext in extentions_list["split"] or bool(re.search(split_file_pattern, fname))):
                        await del_ongoing_task(user_id)
                        return await query.message.edit(
                            "Splitted archives can't be processed yet")
                    if fext not in extentions_list["archive"]:
                        await del_ongoing_task(user_id)
                        return await query.message.edit(
                            "This file is NOT an archive 😐\nIf you believe it's an error, send the file to **@EDM115**"
                        )
                # Makes download dir
                os.makedirs(download_path)
                s_time = time()
                location = f"{download_path}/archive_from_{user_id}{os.path.splitext(fname)[1]}"
                archive = await r_message.download(
                    file_name=location,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        "**Trying to download… Please wait** \n",
                        query.message,
                        s_time,
                        unzip_bot,
                    ),
                )
                e_time = time()
            else:
                await del_ongoing_task(user_id)
                return await answer_query(
                    query,
                    "Fatal query parsing error 💀 Please contact @EDM115 with details and screenshots",
                    answer_only=True,
                    unzip_client=unzip_bot,
                )

            if splitted_data[2].startswith("thumb"):
                await query.message.edit("`Processing… ⏳`")
                archive_name = location.split("/")[-1]
                LOGGER.info(archive_name)
                LOGGER.info(rfnamebro)
                if "rename" in splitted_data[2]:
                    newname = await unzip_bot.ask(
                        chat_id=user_id,
                        text=
                        f"Current file name : `{rfnamebro}`\nPlease send the new file name (**--INCLUDE THE FILE EXTENTION !--**)",
                    )
                    renamed = location.replace(archive_name, newname.text)
                else:
                    renamed = location.replace(archive_name, rfnamebro)
                LOGGER.info(renamed)
                try:
                    os.rename(location, renamed)
                except OSError as e:
                    await del_ongoing_task(user_id)
                    return LOGGER.error(e)
                newfname = renamed.split("/")[-1]
                LOGGER.info(newfname)
                fsize = await get_size(renamed)
                LOGGER.info(fsize)
                if fsize <= (Config.TG_MAX_SIZE / 2):
                    await send_file(
                        unzip_bot=unzip_bot,
                        c_id=user_id,
                        doc_f=renamed,
                        query=query,
                        full_path=renamed,
                        log_msg=log_msg,
                        split=False,
                    )
                    await query.message.delete()
                    await del_ongoing_task(user_id)
                    return shutil.rmtree(
                        f"{Config.DOWNLOAD_LOCATION}/{user_id}")
                LOGGER.info("File too large")
                await query.message.edit("**Splitting your file… Please wait**"
                                         )
                splitteddir = f"{Config.DOWNLOAD_LOCATION}/splitted/{user_id}"
                os.makedirs(splitteddir)
                LOGGER.info(splitteddir)
                ooutput = f"{splitteddir}/{newfname}."
                LOGGER.info(ooutput)
                LOGGER.info(renamed)
                """
                try:
                    os.rename(renamed, ooutput)
                except OSError as e:
                    return LOGGER.error(e)
                """
                ex1 = os.path.exists(splitteddir)
                ex2 = os.path.exists(renamed)
                ex4 = str(ex1) + " " + str(ex2)
                LOGGER.info(ex4)
                splittedfiles = await split_files(renamed, ooutput)
                if not splittedfiles:
                    try:
                        shutil.rmtree(splitteddir)
                    except:
                        pass
                    LOGGER.info("no splittedfiles")
                    await del_ongoing_task(user_id)
                    return await query.message.edit(
                        "An error occured while splitting a file above 2 Gb 😥")
                LOGGER.info(splittedfiles)
                await query.answer(
                    "Trying to send all parts of the file to you… Please wait")
                for file in splittedfiles:
                    sent_files += 1
                    await send_file(
                        unzip_bot=unzip_bot,
                        c_id=user_id,
                        doc_f=file,
                        query=query,
                        full_path=splitteddir,
                        log_msg=log_msg,
                        split=True,
                    )
                shutil.rmtree(splitteddir)
                await del_ongoing_task(user_id)
                return shutil.rmtree(renamed.replace(newfname, ""))

            dltime = TimeFormatter(round(e_time - s_time) * 1000)
            if dltime == "":
                dltime = "1s"
            await answer_query(query,
                               Messages.AFTER_OK_DL_TXT.format(dltime),
                               unzip_client=unzip_bot)

            # Attempt to fetch password protected archives
            if splitted_data[2] == "with_pass":
                password = await unzip_bot.ask(
                    chat_id=query.message.chat.id,
                    text="**Please send me the password 🔑**",
                )
                ext_s_time = time()
                extractor = await extr_files(
                    path=ext_files_dir,
                    archive_path=archive,
                    password=password.text,
                )
                ext_e_time = time()
                await archive_msg.reply(Messages.PASS_TXT.format(password.text)
                                        )
            else:
                ext_s_time = time()
                extractor = await extr_files(path=ext_files_dir,
                                             archive_path=archive)
                ext_e_time = time()
            # Checks if there is an error happened while extracting the archive
            if any(err in extractor for err in ERROR_MSGS):
                try:
                    await query.message.edit(Messages.EXT_FAILED_TXT)
                    shutil.rmtree(ext_files_dir)
                    await del_ongoing_task(user_id)
                    return await log_msg.reply(Messages.EXT_FAILED_TXT)
                except:
                    try:
                        await query.message.delete()
                    except:
                        pass
                    await unzip_bot.send_message(chat_id=query.message.chat.id,
                                                 text=Messages.EXT_FAILED_TXT)
                    shutil.rmtree(ext_files_dir)
                    await del_ongoing_task(user_id)
                    return await archive_msg.reply(Messages.EXT_FAILED_TXT)
            # Check if user was dumb 😐
            paths = await get_files(path=ext_files_dir)
            if not paths:
                await archive_msg.reply("That archive is password protected 😡")
                await unzip_bot.send_message(
                    chat_id=query.message.chat.id,
                    text=
                    "That archive is password protected 😡 **Don't fool me !**",
                )
                await answer_query(query,
                                   Messages.EXT_FAILED_TXT,
                                   unzip_client=unzip_bot)
                shutil.rmtree(ext_files_dir)
                await del_ongoing_task(user_id)
                return

            # Upload extracted files
            extrtime = TimeFormatter(round(ext_e_time - ext_s_time) * 1000)
            if extrtime == "":
                extrtime = "1s"
            await answer_query(query,
                               Messages.EXT_OK_TXT.format(extrtime),
                               unzip_client=unzip_bot)

            try:
                i_e_buttons = await make_keyboard(
                    paths=paths,
                    user_id=user_id,
                    chat_id=query.message.chat.id)
                try:
                    await query.message.edit("Select files to upload 👇",
                                             reply_markup=i_e_buttons)
                except ReplyMarkupTooLong:
                    empty_buttons = await make_keyboard_empty(
                        user_id=user_id, chat_id=query.message.chat.id)
                    await query.message.edit(
                        "Unable to gather the files to upload 😥\nChoose either to upload everything, or cancel the process",
                        reply_markup=empty_buttons,
                    )
            except:
                try:
                    await query.message.delete()
                    i_e_buttons = await make_keyboard(
                        paths=paths,
                        user_id=user_id,
                        chat_id=query.message.chat.id)
                    await unzip_bot.send_message(
                        chat_id=query.message.chat.id,
                        text="Select files to upload 👇",
                        reply_markup=i_e_buttons,
                    )
                except:
                    try:
                        await query.message.delete()
                        empty_buttons = await make_keyboard_empty(
                            user_id=user_id, chat_id=query.message.chat.id)
                        await unzip_bot.send_message(
                            chat_id=query.message.chat.id,
                            text=
                            "Unable to gather the files to upload 😥\nChoose either to upload everything, or cancel the process",
                            reply_markup=empty_buttons,
                        )
                    except:
                        await answer_query(query,
                                           Messages.EXT_FAILED_TXT,
                                           unzip_client=unzip_bot)
                        await archive_msg.reply(Messages.EXT_FAILED_TXT)
                        shutil.rmtree(ext_files_dir)
                        LOGGER.error("Fatal error : uncorrect archive format")
                        await del_ongoing_task(user_id)
                        return

        except Exception as e:
            await del_ongoing_task(user_id)
            try:
                try:
                    await query.message.edit(Messages.ERROR_TXT.format(e))
                except:
                    await unzip_bot.send_message(
                        chat_id=query.message.chat.id,
                        text=Messages.ERROR_TXT.format(e))
                await archive_msg.reply(Messages.ERROR_TXT.format(e))
                shutil.rmtree(ext_files_dir)
                try:
                    await ClientSession().close()
                except:
                    pass
                LOGGER.error(e)
            except Exception as err:
                LOGGER.error(err)
                await archive_msg.reply(err)

    elif query.data.startswith("ext_f"):
        user_id = query.from_user.id
        spl_data = query.data.split("|")
        LOGGER.warning("ext_f spl_data : " + str(spl_data))
        file_path = f"{Config.DOWNLOAD_LOCATION}/{spl_data[1]}/extracted"
        paths = await get_files(path=file_path)
        LOGGER.warning("ext_f paths : " + str(paths))
        if not paths:
            if os.path.isdir(f"{Config.DOWNLOAD_LOCATION}/{spl_data[1]}"):
                shutil.rmtree(f"{Config.DOWNLOAD_LOCATION}/{spl_data[1]}")
            await del_ongoing_task(user_id)
            return await query.message.edit(
                text="There's no file left to upload",
                reply_markup=Buttons.RATE_ME
            )
        await query.answer("Sending that file to you… Please wait")
        sent_files += 1
        await send_file(
            unzip_bot=unzip_bot,
            c_id=spl_data[2],
            doc_f=paths[int(spl_data[3])],
            query=query,
            full_path=f"{Config.DOWNLOAD_LOCATION}/{spl_data[1]}",
            log_msg=log_msg,
            split=False,
        )

        await query.message.edit("Refreshing… ⏳")
        rpaths = await get_files(path=file_path)
        LOGGER.warning("ext_f rpaths : " + str(rpaths))
        # There are no files let's die
        if not rpaths:
            try:
                shutil.rmtree(f"{Config.DOWNLOAD_LOCATION}/{spl_data[1]}")
            except:
                pass
            await del_ongoing_task(user_id)
            return await query.message.edit(
                text="There's no file left to upload",
                reply_markup=Buttons.RATE_ME
            )
        try:
            i_e_buttons = await make_keyboard(paths=rpaths,
                                              user_id=query.from_user.id,
                                              chat_id=query.message.chat.id)
            await query.message.edit("Select files to upload 👇",
                                     reply_markup=i_e_buttons)
        except ReplyMarkupTooLong:
            empty_buttons = await make_keyboard_empty(
                user_id=user_id, chat_id=query.message.chat.id)
            await query.message.edit(
                "Unable to gather the files to upload 😥\nChoose either to upload everything, or cancel the process",
                reply_markup=empty_buttons,
            )

        # Now theorically it refreshes normally
        await update_uploaded(user_id, upload_count=sent_files)
        single_up = True

    elif query.data.startswith("ext_a"):
        user_id = query.from_user.id
        spl_data = query.data.split("|")
        LOGGER.warning("ext_a spl_data : " + str(spl_data))
        file_path = f"{Config.DOWNLOAD_LOCATION}/{spl_data[1]}/extracted"
        paths = await get_files(path=file_path)
        LOGGER.warning("ext_a paths : " + str(paths))
        if not paths:
            try:
                shutil.rmtree(f"{Config.DOWNLOAD_LOCATION}/{spl_data[1]}")
            except:
                pass
            await del_ongoing_task(user_id)
            return await query.message.edit(
                text="There's no file left to upload",
                reply_markup=Buttons.RATE_ME
            )
        await query.answer("Trying to send all files to you… Please wait")
        for file in paths:
            LOGGER.info("ext_a file in paths: " + file)
            sent_files += 1
            await send_file(
                unzip_bot=unzip_bot,
                c_id=spl_data[2],
                doc_f=file,
                query=query,
                full_path=f"{Config.DOWNLOAD_LOCATION}/{spl_data[1]}",
                log_msg=log_msg,
                split=False,
            )

        await query.message.edit(
            text="**Successfully uploaded ✅**\n\n**Join @EDM115bots ❤️**",
            reply_markup=Buttons.RATE_ME
        )
        await log_msg.reply(Messages.HOW_MANY_UPLOADED.format(sent_files))
        await update_uploaded(user_id, upload_count=sent_files)
        await del_ongoing_task(user_id)
        try:
            shutil.rmtree(f"{Config.DOWNLOAD_LOCATION}/{spl_data[1]}")
        except Exception as e:
            await query.message.edit(Messages.ERROR_TXT.format(e))
            await archive_msg.reply(Messages.ERROR_TXT.format(e))

    elif query.data == "cancel_dis":
        uid = query.from_user.id
        await del_ongoing_task(uid)
        try:
            await query.message.edit(Messages.CANCELLED_TXT.format("❌ Process cancelled"))
            shutil.rmtree(f"{Config.DOWNLOAD_LOCATION}/{uid}")
            if single_up:
                await update_uploaded(user_id=uid,
                                      upload_count=sent_files)
                try:
                    await log_msg.reply(Messages.HOW_MANY_UPLOADED.format(sent_files))
                except:
                    return
        except:
            await unzip_bot.send_message(
                chat_id=uid,
                text=Messages.CANCELLED_TXT.format("❌ Process cancelled")
            )
            return

    elif query.data == "nobully":
        await query.message.edit("**Cancelled successfully ✅**")
