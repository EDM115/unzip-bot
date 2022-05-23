# Copyright (c) 2022 EDM115

import os
import re
import shutil
import asyncio
import subprocess

from pyrogram.errors import FloodWait
from unzipper.helpers.database import get_upload_mode
from unzipper.modules.bot_data import Messages
from config import Config
from unzipper import LOGGER

# To get video duration and thumbnail
async def run_shell_cmds(command):
    run = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    shell_ouput = run.stdout.read()[:-1].decode("utf-8")
    return shell_ouput

# Send file to a user
async def send_file(unzip_bot, c_id, doc_f, query, full_path):
    try:
        ul_mode = await get_upload_mode(c_id)
        # Checks if url file size is bigger than 2 Gb (Telegram limit)
        u_file_size = os.stat(doc_f).st_size
        if Config.TG_MAX_SIZE < int(u_file_size):
            LOGGER.info("File too large")
            return await unzip_bot.send_message(
                chat_id=c_id,
                text="File size is too large to send in telegram 😥 \n\n**Sorry, but I can't do anything about this as it's Telegram limitation 😔**"
            )
        if ul_mode == "video":
            vid_duration = await run_shell_cmds(f"ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {doc_f}")
            thmb_pth = f"Dump/thumbnail_{os.path.basename(doc_f)}.jpg"
            if os.path.exists(thmb_pth):
                os.remove(thmb_pth)
            thumb = await run_shell_cmds(f"ffmpeg -i {doc_f} -ss 00:00:01.000 -vframes 1 {thmb_pth}")
            fname = os.path.basename(doc_f)
            await unzip_bot.send_video(chat_id=c_id, video=doc_f, caption=Messages.EXT_CAPTION.format(fname), duration=int(vid_duration) if vid_duration.isnumeric() else 0, thumb=str(thumb))
        else:
            fname = os.path.basename(doc_f)
            await unzip_bot.send_document(chat_id=c_id, document=doc_f, caption=Messages.EXT_CAPTION.format(fname))
        os.remove(doc_f)
    except FloodWait as f:
        asyncio.sleep(f.x)
        return send_file(c_id, doc_f)
    except FileNotFoundError:
        await query.answer("Sorry ! I can't find that file 💀", show_alert=True)
    except BaseException:
        shutil.rmtree(full_path)

async def send_url_logs(unzip_bot, c_id, doc_f, source):
    try:
        u_file_size = os.stat(doc_f).st_size
        if Config.TG_MAX_SIZE < int(u_file_size):
            return await unzip_bot.send_message(
                chat_id=c_id,
                text="URL file is too large to send in telegram 😥"
            )
        fname = os.path.basename(doc_f)
        await unzip_bot.send_document(chat_id=c_id, document=doc_f, caption=Messages.LOG_CAPTION.format(fname, source))
    except FloodWait as f:
        asyncio.sleep(f.x)
        return send_url_logs(c_id, doc_f, source)
    except FileNotFoundError:
        await unzip_bot.send_message(chat_id=Config.LOGS_CHANNEL, text="Archive has gone from servers before uploading 😥")
    except BaseException:
        #shutil.rmtree(full_path)
        pass

# Function to remove basic markdown characters from a string
async def rm_mark_chars(text: str):
    return re.sub("[*`_]", "", text)

# Function to answer queries
async def answer_query(query, message_text: str, answer_only: bool = False, unzip_client = None):
    try:
        if answer_only:
            await query.answer(await rm_mark_chars(message_text), show_alert=True)
        else:
            await query.message.edit(message_text)
    except:
        if unzip_client:
            await unzip_client.send_message(chat_id=query.message.chat.id, text=message_text)
