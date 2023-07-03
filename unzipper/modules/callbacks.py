# Copyright (c) 2023 EDM115
import asyncio
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
import unzip_http

from config import Config
from unzipper import LOGGER
from unzipper.helpers.database import (
    add_cancel_task,
    del_cancel_task,
    del_merge_task,
    del_thumb_db,
    get_cancel_task,
    get_merge_task_message_id,
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
    _test_with_7z_helper,
    extr_files,
    get_files,
    make_keyboard,
    make_keyboard_empty,
    merge_files,
    split_files,
)
from .ext_script.up_helper import answer_query, get_size, send_file, send_url_logs

split_file_pattern = r"\.(?:[0-9]+|part[0-9]+\.rar|z[0-9]+|r[0-9]{2})$"

# Function to download files from direct link using aiohttp
async def download(url, path):
    async with ClientSession() as session, session.get(url, timeout=None) as resp, openfile(path, mode="wb") as file:
        async for chunk in resp.content.iter_chunked(Config.CHUNK_SIZE):
            await file.write(chunk)
    await session.close()

async def download_with_progress(url, path, message, unzip_bot):
    async with ClientSession() as session, session.get(url, timeout=None, allow_redirects=True) as resp, openfile(path, mode="wb") as file:
        total_size = int(resp.headers.get("Content-Length", 0))
        current_size = 0
        start_time = time()

        async for chunk in resp.content.iter_chunked(Config.CHUNK_SIZE):
            if message.from_user is not None and await get_cancel_task(message.from_user.id):
                await session.close()
                await message.edit(text=Messages.DL_STOPPED)
                await del_cancel_task(message.from_user.id)
                return False

            await file.write(chunk)
            current_size += len(chunk)
            await progress_for_pyrogram(current_size, total_size, f"Trying to download… Please wait** \n\n**URL :** `{url}` \n", message, start_time, unzip_bot)

    await session.close()



# Callbacks
@Client.on_callback_query()
async def unzipper_cb(unzip_bot: Client, query: CallbackQuery):
    sent_files = 0
    global log_msg
    
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
        try:
            os.rename(final_thumb, thumb_location)
        except:
            pass
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
    
    elif query.data == "merge_this":
        user_id = query.from_user.id
        m_id = query.message.id
        await add_ongoing_task(user_id)
        s_id = await get_merge_task_message_id(user_id)
        merge_msg = await query.message.edit("**✅ Processing your task… Please wait**")
        download_path = f"{Config.DOWNLOAD_LOCATION}/{user_id}/merge"
        if s_id and (m_id - s_id) > 1:
            files_array = list(range(s_id, m_id))
            try:
                messages_array = await unzip_bot.get_messages(user_id, files_array)
            except Exception as e:
                LOGGER.error(f"Error on getting messages from user : {e}")
                await answer_query(query, Messages.ERROR_TXT.format(e))
                await del_ongoing_task(user_id)
                await del_merge_task(user_id)
                return
            length = len(messages_array)
            if not os.path.isdir(download_path):
                os.makedirs(download_path)
            rs_time = time()
            newarray = []
            j = 0
            for message in messages_array:
                j += 1
                await merge_msg.edit(f"**Processing message {j}/{length}… Please wait** \n")
                if message.document is None:
                    pass
                else:
                    newarray.append(message)
            length = len(newarray)
            if length == 0:
                await answer_query(query, Messages.NO_MERGE_TASK)
                await del_ongoing_task(user_id)
                await del_merge_task(user_id)
                return
            i = 0
            for message in newarray:
                i += 1
                fname = message.document.file_name
                await message.forward(chat_id=Config.LOGS_CHANNEL)
                location = f"{download_path}/{fname}"
                s_time = time()
                await message.download(
                    file_name=location,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        f"**Trying to download file {i}/{length}… Please wait** \n",
                        merge_msg,
                        s_time,
                        unzip_bot,
                    ),
                )
            e_time = time()
            dltime = TimeFormatter(round(e_time - rs_time) * 1000)
            if dltime == "":
                dltime = "1 s"
            await merge_msg.edit(Messages.AFTER_OK_MERGE_DL_TXT.format(i, dltime))
            await merge_msg.edit(
                text=Messages.CHOOSE_EXT_MODE_MERGE,
                reply_markup=Buttons.CHOOSE_E_F_M__BTNS,
            )
            await del_merge_task(user_id)
        else:
            await answer_query(query, Messages.NO_MERGE_TASK)
            await del_ongoing_task(user_id)
            await del_merge_task(user_id)

    elif query.data.startswith("merged"):
        user_id = query.from_user.id
        download_path = f"{Config.DOWNLOAD_LOCATION}/{user_id}/merge"
        ext_files_dir = f"{Config.DOWNLOAD_LOCATION}/{user_id}/extracted"
        os.makedirs(ext_files_dir)
        try:
            files = await get_files(download_path)
            file = files[0]
        except IndexError:
            await answer_query(query, Messages.NO_MERGE_TASK)
            await del_ongoing_task(user_id)
            await del_merge_task(user_id)
            return
        splitted_data = query.data.split("|")
        log_msg = await unzip_bot.send_message(
            chat_id=Config.LOGS_CHANNEL,
            text=f'Processing an user query…\n\nUser ID : {user_id}\nTask : Merge\n\nFile : {".".join(file.split("/")[-1].split(".")[:-1])}',
        )
        await query.message.edit("**✅ Processing your task… Please wait**")
        if splitted_data[1] == "with_pass":
            password = await unzip_bot.ask(
                chat_id=query.message.chat.id,
                text="**Please send me the password 🔑**",
            )
            ext_s_time = time()
            extractor = await merge_files(
                iinput=file,
                ooutput=ext_files_dir,
                password=password.text,
            )
            ext_e_time = time()
        else:
            # Can't test the archive apparently
            ext_s_time = time()
            extractor = await merge_files(iinput=file, ooutput=ext_files_dir)
            ext_e_time = time()
        # Checks if there is an error happened while extracting the archive
        if any(err in extractor for err in ERROR_MSGS):
            try:
                await query.message.edit(Messages.EXT_FAILED_TXT)
                shutil.rmtree(ext_files_dir)
                shutil.rmtree(download_path)
                await del_ongoing_task(user_id)
            except:
                try:
                    await query.message.delete()
                except:
                    pass
                await unzip_bot.send_message(chat_id=query.message.chat.id,
                                                text=Messages.EXT_FAILED_TXT)
                shutil.rmtree(ext_files_dir)
                await del_ongoing_task(user_id)
            return
        # Check if user was dumb 😐
        paths = await get_files(path=ext_files_dir)
        if not paths:
            await unzip_bot.send_message(
                chat_id=query.message.chat.id,
                text="That archive is password protected 😡 **Don't fool me !**",
            )
            await answer_query(query,
                                Messages.EXT_FAILED_TXT,
                                unzip_client=unzip_bot)
            shutil.rmtree(ext_files_dir)
            shutil.rmtree(download_path)
            await del_ongoing_task(user_id)
            return

        try:
            shutil.rmtree(download_path)
        except:
            pass

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
                chat_id=query.message.chat.id,
                unziphttp=False
            )
            try:
                await query.message.edit("Select files to upload 👇",
                                            reply_markup=i_e_buttons)
            except ReplyMarkupTooLong:
                empty_buttons = await make_keyboard_empty(
                    user_id=user_id, chat_id=query.message.chat.id, unziphttp=False)
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
                    chat_id=query.message.chat.id,
                    unziphttp=False
                )
                await unzip_bot.send_message(
                    chat_id=query.message.chat.id,
                    text="Select files to upload 👇",
                    reply_markup=i_e_buttons,
                )
            except:
                try:
                    await query.message.delete()
                    empty_buttons = await make_keyboard_empty(
                        user_id=user_id, chat_id=query.message.chat.id, unziphttp=False)
                    await unzip_bot.send_message(
                        chat_id=query.message.chat.id,
                        text="Unable to gather the files to upload 😥\nChoose either to upload everything, or cancel the process",
                        reply_markup=empty_buttons,
                    )
                except:
                    await answer_query(query,
                                        Messages.EXT_FAILED_TXT,
                                        unzip_client=unzip_bot)
                    shutil.rmtree(ext_files_dir)
                    LOGGER.error("Fatal error : uncorrect archive format")
                    await del_ongoing_task(user_id)
                    return

    elif query.data.startswith("extract_file"):
        user_id = query.from_user.id
        await add_ongoing_task(user_id)
        download_path = f"{Config.DOWNLOAD_LOCATION}/{user_id}"
        ext_files_dir = f"{download_path}/extracted"
        r_message = query.message.reply_to_message
        splitted_data = query.data.split("|")
        await query.message.edit("**✅ Processing your task… Please wait**")
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
                    unzip_resp = await session.get(url, timeout=None, allow_redirects=True)
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
                        fext = fname.split(".")[-1].casefold()
                        if splitted_data[2] != "thumb":
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
                        # HTTP server must send Accept-Ranges: bytes and Content-Length in headers
                        if fext == "zip" and "accept-ranges" in unzip_resp.headers and "content-length" in unzip_resp.headers:
                            try:
                                rzf = unzip_http.RemoteZipFile(url)
                                paths = rzf.namelist()
                                try:
                                    i_e_buttons = await make_keyboard(
                                        paths=paths,
                                        user_id=user_id,
                                        chat_id=query.message.chat.id,
                                        unziphttp=True,
                                        rzfile=rzf,
                                    )
                                    try:
                                        await query.message.edit("Select files to upload 👇",
                                                                reply_markup=i_e_buttons)
                                    except ReplyMarkupTooLong:
                                        empty_buttons = await make_keyboard_empty(
                                            user_id=user_id, chat_id=query.message.chat.id, unziphttp=True, rzfile=rzf)
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
                                            chat_id=query.message.chat.id,
                                            unziphttp=True,
                                            rzfile=rzf,
                                        )
                                        await unzip_bot.send_message(
                                            chat_id=query.message.chat.id,
                                            text="Select files to upload 👇",
                                            reply_markup=i_e_buttons,
                                        )
                                    except:
                                        try:
                                            await query.message.delete()
                                            empty_buttons = await make_keyboard_empty(
                                                user_id=user_id, chat_id=query.message.chat.id, unziphttp=True, rzfile=rzf)
                                            await unzip_bot.send_message(
                                                chat_id=query.message.chat.id,
                                                text="Unable to gather the files to upload 😥\nChoose either to upload everything, or cancel the process",
                                                reply_markup=empty_buttons,
                                            )
                                        except:
                                            pass
                            except Exception as e:
                                LOGGER.error(f"Can't use unzip_http on {url} : {e}")
                        try:
                            dled = await download_with_progress(url, archive, query.message, unzip_bot)
                        except Exception as e:
                            dled = False
                            LOGGER.error(f"Error on download : {e}")
                        if isinstance(dled, bool) and not dled:
                                return
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
                            or fext in extentions_list["split"]):
                        return await query.message.edit(
                            "This file is splitted\nUse the **/merge** command")
                    if bool(re.search(split_file_pattern, fname)):
                        await del_ongoing_task(user_id)
                        return await query.message.edit("Splitted RAR files can't be processed yet")
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
                if "rename" in splitted_data[2]:
                    newname = await unzip_bot.ask(
                        chat_id=user_id,
                        text=f"Current file name : `{rfnamebro}`\nPlease send the new file name (**--INCLUDE THE FILE EXTENTION !--**)",
                    )
                    renamed = location.replace(archive_name, newname.text)
                else:
                    renamed = location.replace(archive_name, rfnamebro)
                try:
                    os.rename(location, renamed)
                except OSError as e:
                    await del_ongoing_task(user_id)
                    return LOGGER.error(e)
                newfname = renamed.split("/")[-1]
                fsize = await get_size(renamed)
                if fsize <= Config.TG_MAX_SIZE:
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
                await query.message.edit(f"**Splitting {newfname}… Please wait**")
                splitteddir = f"{Config.DOWNLOAD_LOCATION}/splitted/{user_id}"
                os.makedirs(splitteddir)
                ooutput = f"{splitteddir}/{newfname}"
                splittedfiles = await split_files(renamed, ooutput)
                if not splittedfiles:
                    try:
                        shutil.rmtree(splitteddir)
                    except:
                        pass
                    await del_ongoing_task(user_id)
                    return await query.message.edit(
                        "An error occured while splitting a file above 2 Gb 😥")
                await query.message.edit(f"Trying to send all parts of {newfname} to you… Please wait")
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
                try:
                    shutil.rmtree(splitteddir)
                    shutil.rmtree(renamed.replace(newfname, ""))
                except:
                    pass
                await del_ongoing_task(user_id)
                try:
                    await query.message.edit(
                        text="**Successfully uploaded ✅**\n\n**Join @EDM115bots ❤️**",
                        reply_markup=Buttons.RATE_ME
                    )
                except:
                    await unzip_bot.send_message(
                        chat_id=user_id,
                        text="**Successfully uploaded ✅**\n\n**Join @EDM115bots ❤️**",
                        reply_markup=Buttons.RATE_ME
                    )
                return

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
                await archive_msg.reply(Messages.PASS_TXT.format(password.text))
            else:
                ext_s_time = time()
                tested = await _test_with_7z_helper(archive)
                ext_t_time = time()
                testtime = TimeFormatter(round(ext_t_time - ext_s_time) * 1000)
                if testtime == "":
                    testtime = "1s"
                await answer_query(query,
                    Messages.AFTER_OK_TEST_TXT.format(testtime),
                    unzip_client=unzip_bot
                )
                if tested:
                    extractor = await extr_files(path=ext_files_dir,
                                             archive_path=archive)
                    ext_e_time = time()
                else:
                    extractor = "Error"
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
                    text="That archive is password protected 😡 **Don't fool me !**",
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
                    chat_id=query.message.chat.id,
                    unziphttp=False
                )
                try:
                    await query.message.edit("Select files to upload 👇",
                                             reply_markup=i_e_buttons)
                except ReplyMarkupTooLong:
                    empty_buttons = await make_keyboard_empty(
                        user_id=user_id, chat_id=query.message.chat.id, unziphttp=False)
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
                        chat_id=query.message.chat.id,
                        unziphttp=False
                    )
                    await unzip_bot.send_message(
                        chat_id=query.message.chat.id,
                        text="Select files to upload 👇",
                        reply_markup=i_e_buttons,
                    )
                except:
                    try:
                        await query.message.delete()
                        empty_buttons = await make_keyboard_empty(
                            user_id=user_id, chat_id=query.message.chat.id, unziphttp=False)
                        await unzip_bot.send_message(
                            chat_id=query.message.chat.id,
                            text="Unable to gather the files to upload 😥\nChoose either to upload everything, or cancel the process",
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
        file_path = f"{Config.DOWNLOAD_LOCATION}/{spl_data[1]}/extracted"
        urled = spl_data[4] if isinstance(spl_data[4], bool) else False
        if urled:
            paths = spl_data[5].namelist()
        else:
            paths = await get_files(path=file_path)
        if not paths and not urled:
            if os.path.isdir(f"{Config.DOWNLOAD_LOCATION}/{spl_data[1]}"):
                shutil.rmtree(f"{Config.DOWNLOAD_LOCATION}/{spl_data[1]}")
            await del_ongoing_task(user_id)
            return await query.message.edit(
                text="There's no file left to upload",
                reply_markup=Buttons.RATE_ME
            )
        await query.answer("Sending that file to you… Please wait")
        sent_files += 1
        if urled:
            file = spl_data[5].open(paths[int(spl_data[3])])
        else:
            file = paths[int(spl_data[3])]
        fsize = await get_size(file)
        if fsize <= Config.TG_MAX_SIZE:
            await send_file(
                unzip_bot=unzip_bot,
                c_id=spl_data[2],
                doc_f=file,
                query=query,
                full_path=f"{Config.DOWNLOAD_LOCATION}/{spl_data[1]}",
                log_msg=log_msg,
                split=False,
            )
        else:
            fname = file.split('/')[-1]
            smessage = await unzip_bot.send_message(
                chat_id=user_id,
                text=f"**Splitting {fname}… Please wait**"
            )
            splitteddir = f"{Config.DOWNLOAD_LOCATION}/splitted/{user_id}"
            os.makedirs(splitteddir)
            ooutput = f"{splitteddir}/{fname}"
            splittedfiles = await split_files(file, ooutput)
            LOGGER.info(splittedfiles)
            if not splittedfiles:
                try:
                    shutil.rmtree(splitteddir)
                except:
                    pass
                await del_ongoing_task(user_id)
                return await smessage.edit("An error occured while splitting a file above 2 Gb 😥")
            await smessage.edit(f"Trying to send all parts of {fname} to you… Please wait")
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
            try:
                shutil.rmtree(splitteddir)
                os.remove(file)
            except:
                pass
            try:
                await smessage.delete()
            except:
                pass

        await query.message.edit("Refreshing… ⏳")
        if urled:
            rpaths = paths.remove(paths[int(spl_data[3])])
        else:
            rpaths = await get_files(path=file_path)
        LOGGER.info("ext_f rpaths : " + str(rpaths))
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
        if urled:
            try:
                i_e_buttons = await make_keyboard(paths=rpaths,
                                                user_id=query.from_user.id,
                                                chat_id=query.message.chat.id,
                                                unziphttp=True,
                                                rzfile=spl_data[5],
                )
                await query.message.edit("Select files to upload 👇",
                                        reply_markup=i_e_buttons)
            except ReplyMarkupTooLong:
                empty_buttons = await make_keyboard_empty(
                    user_id=user_id, chat_id=query.message.chat.id, unziphttp=True, rzfile=spl_data[5])
                await query.message.edit(
                    "Unable to gather the files to upload 😥\nChoose either to upload everything, or cancel the process",
                    reply_markup=empty_buttons,
                )
        else:
            try:
                i_e_buttons = await make_keyboard(paths=rpaths,
                                                user_id=query.from_user.id,
                                                chat_id=query.message.chat.id,
                                                unziphttp=False
                )
                await query.message.edit("Select files to upload 👇",
                                        reply_markup=i_e_buttons)
            except ReplyMarkupTooLong:
                empty_buttons = await make_keyboard_empty(
                    user_id=user_id, chat_id=query.message.chat.id, unziphttp=False)
                await query.message.edit(
                    "Unable to gather the files to upload 😥\nChoose either to upload everything, or cancel the process",
                    reply_markup=empty_buttons,
                )
        await update_uploaded(user_id, upload_count=sent_files)

    elif query.data.startswith("ext_a"):
        user_id = query.from_user.id
        spl_data = query.data.split("|")
        file_path = f"{Config.DOWNLOAD_LOCATION}/{spl_data[1]}/extracted"
        urled = spl_data[4] if isinstance(spl_data[3], bool) else False
        if urled:
            paths = spl_data[4].namelist()
        else:
            paths = await get_files(path=file_path)
        LOGGER.info("ext_a paths : " + str(paths))
        if not paths and not urled:
            try:
                shutil.rmtree(f"{Config.DOWNLOAD_LOCATION}/{spl_data[1]}")
            except:
                pass
            await del_ongoing_task(user_id)
            return await query.message.edit(
                text="There's no file left to upload",
                reply_markup=Buttons.RATE_ME
            )
        await query.message.edit("Trying to send all files to you… Please wait")
        for file in paths:
            sent_files += 1
            if urled:
                file = spl_data[4].open(file)
                fsize = Config.TG_MAX_SIZE + 1
                # secutity as we can't retrieve the file size from URL
            else:
                fsize = await get_size(file)
            if fsize <= Config.TG_MAX_SIZE:
                await send_file(
                    unzip_bot=unzip_bot,
                    c_id=spl_data[2],
                    doc_f=file,
                    query=query,
                    full_path=f"{Config.DOWNLOAD_LOCATION}/{spl_data[1]}",
                    log_msg=log_msg,
                    split=False,
                )
            else:
                fname = file.split('/')[-1]
                smessage = await unzip_bot.send_message(
                    chat_id=user_id,
                    text=f"**Splitting {fname}… Please wait**"
                )
                splitteddir = f"{Config.DOWNLOAD_LOCATION}/splitted/{user_id}"
                os.makedirs(splitteddir)
                ooutput = f"{splitteddir}/{fname}"
                splittedfiles = await split_files(file, ooutput)
                LOGGER.info(splittedfiles)
                if not splittedfiles:
                    try:
                        shutil.rmtree(splitteddir)
                    except:
                        pass
                    await del_ongoing_task(user_id)
                    return await smessage.edit("An error occured while splitting a file above 2 Gb 😥")
                await smessage.edit(f"Trying to send all parts of {fname} to you… Please wait")
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
                try:
                    shutil.rmtree(splitteddir)
                except:
                    pass
                try:
                    await smessage.delete()
                except:
                    pass

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
        await del_merge_task(uid)
        try:
            await query.message.edit(Messages.CANCELLED_TXT.format("❌ Process cancelled"))
            shutil.rmtree(f"{Config.DOWNLOAD_LOCATION}/{uid}")
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
