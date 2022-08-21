# Copyright (c) 2022 EDM115

import os
import re
import shutil
import subprocess
import pathlib
from asyncio import sleep
from time import time

from pyrogram.errors import FloodWait
from unzipper import unzipperbot
from unzipper.helpers.database import get_upload_mode, get_cloud
from unzipper.helpers.unzip_help import extentions_list, progress_for_pyrogram
from unzipper.modules.bot_data import Messages
from unzipper.modules.ext_script.custom_thumbnail import thumb_exists
from unzipper.modules.ext_script.cloud_upload import bayfiles
from config import Config
from unzipper import LOGGER

# To get video duration and thumbnail
async def run_shell_cmds(command):
    run = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
    )
    shell_output = run.stdout.read()[:-1].decode("utf-8")
    return shell_output


# Send file to a user
async def send_file(unzip_bot, c_id, doc_f, query, full_path, log_msg):
    try:
        ul_mode = await get_upload_mode(c_id)
        # Checks if url file size is bigger than 2 Gb (Telegram limit)
        u_file_size = os.stat(doc_f).st_size
        fname = os.path.basename(doc_f)
        fext = (pathlib.Path(os.path.abspath(doc_f)).suffix).casefold()
        if int(u_file_size) > Config.TG_MAX_SIZE:
            LOGGER.info("File too large")
            uptocloud = await unzip_bot.send_message(
                chat_id=c_id,
                text=f"`{fname}` is too huge to be sent to Telegram directly (`{u_file_size}`).\nUploading to Bayfiles, please wait some minutes…"
            )
            upurl = await get_cloud(c_id)
            bfup = await bayfiles(os.path.abspath(doc_f), upurl)
            if "Error happened on BayFiles upload" in bfup:
                await uptocloud.edit(bfup)
            elif bfup["status"] == "True":
                fsize = bfup["data"]["file"]["metadata"]["size"]["readable"]
                furl = bfup["data"]["file"]["url"]["full"]
                await uptocloud.edit(Messages.URL_UPLOAD.format(fname, fsize, furl))
            elif bfup["status"] == "False":
                etype = bfup["error"]["message"]
                emess = bfup["error"]["type"]
                ecode = bfup["error"]["code"]
                await uptocloud.edit(
                    Messages.URL_ERROR.format(fname, ecode, etypr, emess)
                )
                await log_msg.reply(
                    Messages.URL_ERROR.format(fname, ecode, etypr, emess)
                )
            else:
                await uptocloud.edit(bfup)
                await log_msg.reply(bfup)
            return os.remove(doc_f)
            """
            # Workaround : https://ccm.net/computing/linux/4327-split-a-file-into-several-parts-in-linux/
            # run_shell_cmds(f"split -b 2GB -d {doc_f} SPLIT-{doc_f}")
            return await unzip_bot.send_message(
                chat_id=c_id,
                text="File size is too large to send in telegram 😥 \n\n**Sorry, but I can't do anything about this as it's Telegram limitation 😔**"
            )
            """
        thumbornot = await thumb_exists(c_id)
        upmsg = await unzip_bot.send_message(c_id, "`Processing… ⏳`")
        if ul_mode == "media" and fext in extentions_list["audio"]:
            if thumbornot:
                thumb_image = Config.THUMB_LOCATION + "/" + str(c_id) + ".jpg"
                await unzip_bot.send_audio(
                    chat_id=c_id,
                    audio=doc_f,
                    caption=Messages.EXT_CAPTION.format(fname),
                    thumb=thumb_image,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        f"**Trying to upload {fname}… Please wait** \n",
                        upmsg,
                        time()
                    )
                )
            else:
                await unzip_bot.send_audio(
                    chat_id=c_id,
                    audio=doc_f,
                    caption=Messages.EXT_CAPTION.format(fname),
                    progress=progress_for_pyrogram,
                    progress_args=(
                        f"**Trying to upload {fname}… Please wait** \n",
                        upmsg,
                        time()
                    )
                )
        elif ul_mode == "media" and fext in extentions_list["photo"]:
            # impossible to use a thumb here :(
            await unzip_bot.send_photo(
                chat_id=c_id,
                photo=doc_f,
                caption=Messages.EXT_CAPTION.format(fname),
                progress=progress_for_pyrogram,
                progress_args=(
                    f"**Trying to upload {fname}… Please wait** \n",
                    upmsg,
                    time()
                )
            )
        elif ul_mode == "media" and fext in extentions_list["video"]:
            vid_duration = await run_shell_cmds(
                f"ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {doc_f}"
            )
            if thumbornot:
                thumb_image = Config.THUMB_LOCATION + "/" + str(c_id) + ".jpg"
                await unzip_bot.send_video(
                    chat_id=c_id,
                    video=doc_f,
                    caption=Messages.EXT_CAPTION.format(fname),
                    duration=int(vid_duration) if vid_duration.isnumeric() else 0,
                    thumb=thumb_image,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        f"**Trying to upload {fname}… Please wait** \n",
                        upmsg,
                        time()
                    )
                )
            else:
                thmb_pth = (
                    f"{Config.THUMB_LOCATION}/thumbnail_{os.path.basename(doc_f)}.jpg"
                )
                if os.path.exists(thmb_pth):
                    os.remove(thmb_pth)
                thumb = await run_shell_cmds(
                    f"ffmpeg -ss 00:00:01.00 -i {doc_f} -vf 'scale=320:320:force_original_aspect_ratio=decrease' -vframes 1 {thmb_pth}"
                )
                await unzip_bot.send_video(
                    chat_id=c_id,
                    video=doc_f,
                    caption=Messages.EXT_CAPTION.format(fname),
                    duration=int(vid_duration) if vid_duration.isnumeric() else 0,
                    thumb=str(thumb),
                    progress=progress_for_pyrogram,
                    progress_args=(
                        f"**Trying to upload {fname}… Please wait** \n",
                        upmsg,
                        time()
                    )
                )
                os.remove(thmb_pth)
        else:
            if thumbornot:
                thumb_image = Config.THUMB_LOCATION + "/" + str(c_id) + ".jpg"
                await unzip_bot.send_document(
                    chat_id=c_id,
                    document=doc_f,
                    thumb=thumb_image,
                    caption=Messages.EXT_CAPTION.format(fname),
                    progress=progress_for_pyrogram,
                    progress_args=(
                        f"**Trying to upload {fname}… Please wait** \n",
                        upmsg,
                        time()
                    )
                )
            else:
                await unzip_bot.send_document(
                    chat_id=c_id,
                    document=doc_f,
                    caption=Messages.EXT_CAPTION.format(fname),
                    progress=progress_for_pyrogram,
                    progress_args=(
                        f"**Trying to upload {fname}… Please wait** \n",
                        upmsg,
                        time()
                    )
                )
        await upmsg.delete()
        os.remove(doc_f)
    except FloodWait as f:
        sleep(f.x)
        return await send_file(c_id, doc_f)
    except FileNotFoundError:
        return await query.answer("Sorry ! I can't find that file 💀", show_alert=True)
    except BaseException as e:
        LOGGER.warning(e)
        shutil.rmtree(full_path)


async def send_url_logs(unzip_bot, c_id, doc_f, source):
    try:
        u_file_size = os.stat(doc_f).st_size
        if Config.TG_MAX_SIZE < int(u_file_size):
            return await unzip_bot.send_message(
                chat_id=c_id, text="URL file is too large to send in telegram 😥"
            )
        fname = os.path.basename(doc_f)
        await unzip_bot.send_document(
            chat_id=c_id,
            document=doc_f,
            caption=Messages.LOG_CAPTION.format(fname, source)
        )
    except FloodWait as f:
        asyncio.sleep(f.x)
        return send_url_logs(c_id, doc_f, source)
    except FileNotFoundError:
        await unzip_bot.send_message(
            chat_id=Config.LOGS_CHANNEL,
            text="Archive has gone from servers before uploading 😥"
        )
    except BaseException:
        pass


async def merge_splitted_archives(user_id, path):
    cmd = f"cd {path} && cat * > MERGED_{user_id}.zip"
    await run_shell_cmds(cmd)


# Function to remove basic markdown characters from a string
async def rm_mark_chars(text: str):
    return re.sub("[*`_]", "", text)


# Function to answer queries
async def answer_query(
    query, message_text: str, answer_only: bool = False, unzip_client=None, buttons=None
):
    try:
        if answer_only:
            await query.answer(await rm_mark_chars(message_text), show_alert=True)
        else:
            await query.message.edit(message_text, reply_markup=buttons)
    except:
        if unzip_client:
            await unzip_client.send_message(
                chat_id=query.message.chat.id, text=message_text, reply_markup=buttons
            )
        else:
            await unzipperbot.send_message(
                chat_id=query.message.chat.id, text=message_text, reply_markup=buttons
            )
