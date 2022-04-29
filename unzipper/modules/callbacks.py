# Copyright (c) 2022 EDM115

import os
import re
import shutil

from time import time
from aiohttp import ClientSession
from aiofiles import open as openfile
from pyrogram import Client
from pyrogram.types import CallbackQuery

from .bot_data import Buttons, Messages, ERROR_MSGS
from .ext_script.ext_helper import extr_files, get_files, make_keyboard
from .ext_script.up_helper import send_file, answer_query, send_url_logs
from .commands import https_url_regex
from unzipper.helpers.unzip_help import progress_for_pyrogram, TimeFormatter, humanbytes
from unzipper.helpers.database import set_upload_mode
from config import Config

# Function to download files from direct link using aiohttp
async def download(url, path):
    async with ClientSession() as session:
        async with session.get(url, timeout=None) as resp:
            async with openfile(path, mode="wb") as file:
                async for chunk in resp.content.iter_chunked(Config.CHUNK_SIZE):
                    await file.write(chunk)

# Callbacks
@Client.on_callback_query()
async def unzipper_cb(unzip_bot: Client, query: CallbackQuery):
    if query.data == "megoinhome":
        await query.edit_message_text(text=Messages.START_TEXT.format(query.from_user.mention), reply_markup=Buttons.START_BUTTON)
    
    elif query.data == "helpcallback":
        await query.edit_message_text(text=Messages.HELP_TXT, reply_markup=Buttons.ME_GOIN_HOME)
    
    elif query.data == "aboutcallback":
        await query.edit_message_text(text=Messages.ABOUT_TXT, reply_markup=Buttons.ME_GOIN_HOME, disable_web_page_preview=True)
    
    elif query.data.startswith("set_mode"):
        user_id = query.from_user.id
        mode = query.data.split("|")[1]
        await set_upload_mode(user_id, mode)
        await answer_query(query, Messages.CHANGED_UPLOAD_MODE_TXT.format(mode))

    elif query.data.startswith("extract_file"):
        user_id = query.from_user.id
        download_path = f"{Config.DOWNLOAD_LOCATION}/{user_id}"
        ext_files_dir = f"{download_path}/extracted"
        r_message = query.message.reply_to_message
        splitted_data = query.data.split("|")

        try:
            if splitted_data[1] == "url":
                url = r_message.text
                # Double check
                if not re.match(https_url_regex, url):
                    return await query.message.edit("That's not a valid url 💀")
                s = ClientSession()
                async with s as ses:
                    # Get the file size
                    unzip_head = await ses.head(url)
                    f_size = unzip_head.headers.get('content-length')
                    u_file_size = f_size if f_size else "undefined"
                    # Checks if file is an archive using content-type header
                    unzip_resp = await ses.get(url, timeout=None)
                    if "application/" not in unzip_resp.headers.get('content-type'):
                        return await query.message.edit("That's not an archive 💀")
                    if unzip_resp.status == 200:
                        # Makes download dir
                        os.makedirs(download_path)
                        # Send logs
                        await unzip_bot.send_message(chat_id=Config.LOGS_CHANNEL, text=Messages.LOG_TXT.format(user_id, url, u_file_size))
                        s_time = time()
                        archive = f"{download_path}/archive_from_{user_id}{os.path.splitext(url)[1]}"
                        await answer_query(query, f"**Trying to download… Please wait** \n\n**URL :** `{url}` \n\nThis may take a while, go grab a coffee ☕️", unzip_client=unzip_bot)
                        await download(url, archive)
                        e_time = time()
                        paths = await get_files(path=archive)
                        await send_url_logs(unzip_bot=unzip_bot,
                            c_id=Config.LOGS_CHANNEL,
                            doc_f=paths[int(spl_data[3])]
                            #full_path=archive
                        )
                    else:
                        return await query.message.edit("**Sorry, I can't download that URL 😭 Try to @transload it**")
            
            elif splitted_data[1] == "tg_file":
                if r_message.document is None:
                    return await query.message.edit("Give me an archive to extract 😐")
                # Makes download dir
                os.makedirs(download_path)
                # Send Logs
                log_msg = await r_message.forward(chat_id=Config.LOGS_CHANNEL)
                await log_msg.reply(Messages.LOG_TXT.format(user_id, r_message.document.file_name, humanbytes(r_message.document.file_size)))
                s_time = time()
                archive = await r_message.download(
                    file_name=f"{download_path}/archive_from_{user_id}{os.path.splitext(r_message.document.file_name)[1]}",
                    progress=progress_for_pyrogram, progress_args=("**Trying to download… Please wait** \n", query.message, s_time)
                    )
                e_time = time()
            else:
                await answer_query(query, "Can't find details 💀 Please contact @EDM115 if it's an error", answer_only=True, unzip_client=unzip_bot)
            
            await answer_query(query, Messages.AFTER_OK_DL_TXT.format(TimeFormatter(round(e_time-s_time) * 1000)), unzip_client=unzip_bot)
            
            # Attempt to fetch password protected archives
            global protected
            protected = False
            if splitted_data[2] == "with_pass":
                password = await unzip_bot.ask(chat_id=query.message.chat.id ,text="**Please send me the password 🔑**")
                ext_s_time = time()
                extractor = await extr_files(protected, path=ext_files_dir, archive_path=archive, password=password.text)
                ext_e_time = time()
                await unzip_bot.send_message(chat_id=Config.LOGS_CHANNEL, text=Messages.PASS_TXT.format(password.text))
            else:
                ext_s_time = time()
                extractor = await extr_files(protected, path=ext_files_dir, archive_path=archive)
                ext_e_time = time()
            # Checks if there is an error happened while extracting the archive
            if any(err in extractor for err in ERROR_MSGS):
                try:
                    return await query.message.edit(Messages.EXT_FAILED_TXT)
                except:
                    try:
                        await query.message.delete()
                    except:
                        pass
                    return await unzip_bot.send_message(chat_id=query.message.chat.id, text=Messages.EXT_FAILED_TXT)
            
            await answer_query(query, Messages.EXT_OK_TXT.format(TimeFormatter(round(ext_e_time-ext_s_time) * 1000)), unzip_client=unzip_bot)
            
            # Upload extracted files
            paths = await get_files(path=ext_files_dir)
            if not paths:
                await unzip_bot.send_message(chat_id=Config.LOGS_CHANNEL, text="That archive is password protected 😡")
                await unzip_bot.send_message(chat_id=query.message.chat.id, text="That archive is password protected 😡 **Don't fool me !**")
                global fooled
                fooled = True
            else:
                i_e_buttons = await make_keyboard(paths=paths, user_id=user_id, chat_id=query.message.chat.id)
                try:
                    await query.message.edit("Select files to upload 👇", reply_markup=i_e_buttons)
                except:
                    await unzip_bot.send_message(chat_id=query.message.chat.id, text="Select files to upload 👇", reply_markup=i_e_buttons)
                    await query.message.delete()
            
        except Exception as e:
            try:
                await query.message.edit(Messages.ERROR_TXT.format(e))
                shutil.rmtree(download_path)
                await s.close()
            except Exception as er:
                print(er)

    elif query.data.startswith("ext_f"):
        spl_data = query.data.split("|")
        file_path = f"{Config.DOWNLOAD_LOCATION}/{spl_data[1]}/extracted"
        paths = await get_files(path=file_path)
        # Next level logic lmao
        if not paths:
            if os.path.isdir(f"{Config.DOWNLOAD_LOCATION}/{spl_data[1]}"):
                shutil.rmtree(f"{Config.DOWNLOAD_LOCATION}/{spl_data[1]}")
            return await query.message.edit("I've already sent you those files 🙂")
        
        await query.answer("Sending that file to you… Please wait")
        await send_file(unzip_bot=unzip_bot,
                        c_id=spl_data[2],
                        doc_f=paths[int(spl_data[3])],
                        query=query,
                        full_path=f"{Config.DOWNLOAD_LOCATION}/{spl_data[1]}"
                    )

        # Refreshing Inline keyboard
        await query.message.edit("Refreshing… ⏳")
        rpaths = await get_files(path=file_path)
        # There are no files let's die
        if not rpaths:
            try:
                shutil.rmtree(f"{Config.DOWNLOAD_LOCATION}/{spl_data[1]}")
            except:
                pass
            return await query.message.edit("I've already sent you those files 🙂")
        i_e_buttons = await make_keyboard(paths=rpaths, user_id=query.from_user.id, chat_id=query.message.chat.id)
        await query.message.edit("Select files to upload 👇", reply_markup=i_e_buttons)
    
    elif query.data.startswith("ext_a"):
        spl_data = query.data.split("|")
        file_path = f"{Config.DOWNLOAD_LOCATION}/{spl_data[1]}/extracted"
        paths = await get_files(path=file_path)
        if not paths:
            try:
                shutil.rmtree(f"{Config.DOWNLOAD_LOCATION}/{spl_data[1]}")
            except:
                pass
            return await query.message.edit("I've already sent you those files 🙂")
        await query.answer("Trying to send all files to you… Please wait")
        for file in paths:
            await send_file(unzip_bot=unzip_bot,
                            c_id=spl_data[2],
                            doc_f=file,
                            query=query,
                            full_path=f"{Config.DOWNLOAD_LOCATION}/{spl_data[1]}"
                        )
        await query.message.edit("**Successfully uploaded ✅** \n\n **Join @EDM115bots ❤️**")
        try:
            shutil.rmtree(f"{Config.DOWNLOAD_LOCATION}/{spl_data[1]}")
        except Exception as e:
            await query.message.edit(Messages.ERROR_TXT.format(e))
    
    elif query.data == "cancel_dis":
        try:
            shutil.rmtree(f"{Config.DOWNLOAD_LOCATION}/{query.from_user.id}")
            await query.message.edit(Messages.CANCELLED_TXT.format("Process cancelled ❌"))
        except:
            return await query.answer("There is nothing to remove 💀", show_alert=True)
    
    elif query.data == "nobully":
        await query.message.edit("**Ok, I won't delete those files 😇**")
