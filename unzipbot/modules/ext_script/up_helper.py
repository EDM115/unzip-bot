import asyncio
import os
import pathlib
import re
import shutil
from datetime import timedelta
from time import time
from shlex import quote

from pyrogram.errors import FloodWait, PhotoExtInvalid, PhotoSaveFileInvalid

from config import Config
from unzipbot import LOGGER, unzipbot_client
from unzipbot.helpers.database import get_lang, get_upload_mode
from unzipbot.helpers.unzip_help import (
    extentions_list,
    progress_for_pyrogram,
    progress_urls,
)
from unzipbot.i18n.messages import Messages
from unzipbot.modules.ext_script.custom_thumbnail import thumb_exists
from unzipbot.modules.ext_script.ext_helper import run_shell_cmds
from unzipbot.modules.ext_script.metadata_helper import get_audio_metadata


messages = Messages(lang_fetcher=get_lang)


# Get file size
async def get_size(doc_f):
    try:
        fsize = os.stat(doc_f).st_size

        return fsize
    except:
        return -1


# Send file to a user
async def send_file(unzip_bot, c_id, doc_f, query, full_path, log_msg, split):
    fsize = await get_size(doc_f)

    if fsize in (-1, 0):  # File not found or empty
        try:
            await unzipbot_client.send_message(
                c_id,
                messages.get("up_helper", "EMPTY_FILE", c_id, os.path.basename(doc_f)),
            )
        except:
            pass

        return

    try:
        ul_mode = await get_upload_mode(c_id)
        fname = os.sep.join(os.path.abspath(doc_f).split(os.sep)[5:])
        fext = (pathlib.Path(os.path.abspath(doc_f)).suffix).casefold().replace(".", "")
        thumbornot = await thumb_exists(c_id)

        if fsize > Config.MIN_SIZE_PROGRESS:
            upmsg = await unzipbot_client.send_message(
                c_id,
                messages.get("up_helper", "PROCESSING2", c_id),
                disable_notification=True,
            )
        else:
            upmsg = None

        if ul_mode == "media" and fext in extentions_list["audio"]:
            metadata = await get_audio_metadata(doc_f)

            if thumbornot:
                thumb_image = Config.THUMB_LOCATION + "/" + str(c_id) + ".jpg"
                await unzip_bot.send_audio(
                    chat_id=c_id,
                    audio=doc_f,
                    caption=messages.get("up_helper", "EXT_CAPTION", c_id, fname),
                    duration=metadata["duration"],
                    performer=metadata["performer"],
                    title=metadata["title"],
                    thumb=thumb_image,
                    disable_notification=True,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        messages.get("up_helper", "TRY_UP", c_id, fname),
                        upmsg,
                        time(),
                        unzip_bot,
                    ),
                )
            else:
                await unzip_bot.send_audio(
                    chat_id=c_id,
                    audio=doc_f,
                    caption=messages.get("up_helper", "EXT_CAPTION", c_id, fname),
                    duration=metadata["duration"],
                    performer=metadata["performer"],
                    title=metadata["title"],
                    disable_notification=True,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        messages.get("up_helper", "TRY_UP", c_id, fname),
                        upmsg,
                        time(),
                        unzip_bot,
                    ),
                )

        elif ul_mode == "media" and fext in extentions_list["photo"]:
            # impossible to use a thumb here :(
            try:
                await unzip_bot.send_photo(
                    chat_id=c_id,
                    photo=doc_f,
                    caption=messages.get("up_helper", "EXT_CAPTION", c_id, fname),
                    disable_notification=True,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        messages.get("up_helper", "TRY_UP", c_id, fname),
                        upmsg,
                        time(),
                        unzip_bot,
                    ),
                )
            except (PhotoExtInvalid, PhotoSaveFileInvalid):
                if thumbornot:
                    thumb_image = Config.THUMB_LOCATION + "/" + str(c_id) + ".jpg"
                    await unzip_bot.send_document(
                        chat_id=c_id,
                        document=doc_f,
                        thumb=thumb_image,
                        caption=messages.get("up_helper", "EXT_CAPTION", c_id, fname),
                        force_document=True,
                        disable_notification=True,
                        progress=progress_for_pyrogram,
                        progress_args=(
                            messages.get("up_helper", "TRY_UP", c_id, fname),
                            upmsg,
                            time(),
                            unzip_bot,
                        ),
                    )
                else:
                    await unzip_bot.send_document(
                        chat_id=c_id,
                        document=doc_f,
                        caption=messages.get("up_helper", "EXT_CAPTION", c_id, fname),
                        force_document=True,
                        disable_notification=True,
                        progress=progress_for_pyrogram,
                        progress_args=(
                            messages.get("up_helper", "TRY_UP", c_id, fname),
                            upmsg,
                            time(),
                            unzip_bot,
                        ),
                    )

        elif ul_mode == "media" and fext in extentions_list["video"]:
            cmd = [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                quote(doc_f),
            ]
            result = await run_shell_cmds(" ".join(cmd))
            vid_duration = int(float(result.strip()))

            if thumbornot:
                thumb_image = Config.THUMB_LOCATION + "/" + str(c_id) + ".jpg"
                await unzip_bot.send_video(
                    chat_id=c_id,
                    video=doc_f,
                    caption=messages.get("up_helper", "EXT_CAPTION", c_id, fname),
                    duration=vid_duration,
                    thumb=thumb_image,
                    disable_notification=True,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        messages.get("up_helper", "TRY_UP", c_id, fname),
                        upmsg,
                        time(),
                        unzip_bot,
                    ),
                )
            else:
                thmb_pth = (
                    f"{Config.THUMB_LOCATION}/thumbnail_{os.path.basename(doc_f)}.jpg"
                )

                if os.path.exists(thmb_pth):
                    os.remove(thmb_pth)

                midpoint_seconds = int(vid_duration / 2)
                midpoint_timedelta = timedelta(seconds=midpoint_seconds)
                midpoint_str = str(midpoint_timedelta)

                if "." not in midpoint_str:
                    midpoint_str += ".00"
                else:
                    midpoint_str = (
                        midpoint_str.split(".")[0]
                        + "."
                        + midpoint_str.split(".")[1][:2]
                    )

                cmd = [
                    "ffmpeg",
                    "-ss",
                    midpoint_str,
                    "-i",
                    quote(doc_f),
                    "-vf",
                    "scale=320:320:force_original_aspect_ratio=decrease",
                    "-vframes",
                    "1",
                    quote(thmb_pth),
                ]
                await run_shell_cmds(" ".join(cmd))

                if not os.path.exists(thmb_pth):
                    shutil.copy(Config.BOT_THUMB, thmb_pth)

                await unzip_bot.send_video(
                    chat_id=c_id,
                    video=doc_f,
                    caption=messages.get("up_helper", "EXT_CAPTION", c_id, fname),
                    duration=vid_duration,
                    thumb=thmb_pth,
                    disable_notification=True,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        messages.get("up_helper", "TRY_UP", c_id, fname),
                        upmsg,
                        time(),
                        unzip_bot,
                    ),
                )

                try:
                    os.remove(thmb_pth)
                except:
                    pass

        else:
            if thumbornot:
                thumb_image = Config.THUMB_LOCATION + "/" + str(c_id) + ".jpg"
                await unzip_bot.send_document(
                    chat_id=c_id,
                    document=doc_f,
                    thumb=thumb_image,
                    caption=messages.get("up_helper", "EXT_CAPTION", c_id, fname),
                    force_document=True,
                    disable_notification=True,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        messages.get("up_helper", "TRY_UP", c_id, fname),
                        upmsg,
                        time(),
                        unzip_bot,
                    ),
                )
            else:
                await unzip_bot.send_document(
                    chat_id=c_id,
                    document=doc_f,
                    caption=messages.get("up_helper", "EXT_CAPTION", c_id, fname),
                    force_document=True,
                    disable_notification=True,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        messages.get("up_helper", "TRY_UP", c_id, fname),
                        upmsg,
                        time(),
                        unzip_bot,
                    ),
                )

        if upmsg:
            await upmsg.delete()

        os.remove(doc_f)
    except FloodWait as f:
        await asyncio.sleep(f.value)
        await send_file(unzip_bot, c_id, doc_f, query, full_path, log_msg, split)
    except FileNotFoundError:
        try:
            await unzipbot_client.send_message(
                c_id,
                messages.get("up_helper", "CANT_FIND", c_id, os.path.basename(doc_f)),
            )
        except:
            pass

        return
    except BaseException as e:
        LOGGER.error(e)
        shutil.rmtree(full_path)


async def forward_file(message, cid):
    try:
        await unzipbot_client.copy_message(
            chat_id=cid,
            from_chat_id=message.chat.id,
            message_id=message.id,
            disable_notification=True,
        )
    except FloodWait as f:
        await asyncio.sleep(f.value)
        await forward_file(message, cid)


async def send_url_logs(unzip_bot, c_id, doc_f, source, message):
    try:
        u_file_size = os.stat(doc_f).st_size

        if Config.TG_MAX_SIZE < int(u_file_size):
            await unzip_bot.send_message(
                chat_id=c_id, text=messages.get("up_helper", "TOO_LARGE", c_id)
            )

            return

        fname = os.path.basename(doc_f)
        await unzip_bot.send_document(
            chat_id=c_id,
            document=doc_f,
            caption=messages.get("up_helper", "LOG_CAPTION", c_id, fname, source),
            disable_notification=True,
            progress=progress_urls,
            progress_args=(
                messages.get("up_helper", "CHECK_MSG", c_id),
                message,
                time(),
            ),
        )
    except FloodWait as f:
        await asyncio.sleep(f.value)

        return send_url_logs(unzip_bot, c_id, doc_f, source, message)
    except FileNotFoundError:
        await unzip_bot.send_message(
            chat_id=Config.LOGS_CHANNEL,
            text=messages.get("up_helper", "ARCHIVE_GONE", c_id),
        )
    except BaseException:
        pass


async def merge_splitted_archives(user_id, path):
    cmd = f'cd "{path}" && cat * > MERGED_{user_id}.zip'
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
        try:
            if unzip_client:
                await unzip_client.send_message(
                    chat_id=query.message.chat.id,
                    text=message_text,
                    reply_markup=buttons,
                )
            else:
                await unzipbot_client.send_message(
                    chat_id=query.message.chat.id,
                    text=message_text,
                    reply_markup=buttons,
                )
        except:
            pass
