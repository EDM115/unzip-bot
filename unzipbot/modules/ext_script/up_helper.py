import asyncio
import os
import pathlib
import re
import shutil
from datetime import timedelta
from shlex import quote
from time import time

from pyrogram.errors import FloodPremiumWait, FloodWait, PhotoExtInvalid, PhotoSaveFileInvalid

from unzipbot import LOGGER, unzipbot_client
from unzipbot.config.config import Config
from unzipbot.helpers.database import get_lang, get_upload_mode
from unzipbot.helpers.unzip_help import extentions_list, progress_for_pyrogram, progress_urls
from unzipbot.i18n.messages import Messages
from unzipbot.modules.ext_script.custom_thumbnail import thumb_exists
from unzipbot.modules.ext_script.ext_helper import run_shell_cmds

messages = Messages(lang_fetcher=get_lang)


# Get file size
async def get_size(doc_f):
    try:
        fsize = os.stat(path=doc_f).st_size

        return fsize
    except:
        return -1


# TODO
# Send file to a user
async def send_file(unzip_bot, c_id, doc_f, query, full_path, log_msg, split):
    fsize = await get_size(doc_f)

    if fsize in (-1, 0):  # File not found or empty
        try:
            await unzipbot_client.send_message(
                chat_id=c_id,
                text=messages.get(
                    file="up_helper",
                    key="EMPTY_FILE",
                    user_id=c_id,
                    extra_args=os.path.basename(doc_f),
                ),
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
                chat_id=c_id,
                text=messages.get(file="up_helper", key="PROCESSING2", user_id=c_id),
                disable_notification=True,
            )
        else:
            upmsg = None

        if ul_mode == "media" and fext in extentions_list["audio"]:
            if thumbornot:
                thumb_image = Config.THUMB_LOCATION + "/" + str(c_id) + ".jpg"
                await unzip_bot.send_audio(
                    chat_id=c_id,
                    audio=doc_f,
                    caption=messages.get(
                        file="up_helper", key="EXT_CAPTION", user_id=c_id, extra_args=fname
                    ),
                    thumb=thumb_image,
                    disable_notification=True,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        messages.get(
                            file="up_helper", key="TRY_UP", user_id=c_id, extra_args=fname
                        ),
                        upmsg,
                        time(),
                        unzip_bot,
                    ),
                )
            else:
                await unzip_bot.send_audio(
                    chat_id=c_id,
                    audio=doc_f,
                    caption=messages.get(
                        file="up_helper", key="EXT_CAPTION", user_id=c_id, extra_args=fname
                    ),
                    disable_notification=True,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        messages.get(
                            file="up_helper", key="TRY_UP", user_id=c_id, extra_args=fname
                        ),
                        upmsg,
                        time(),
                        unzip_bot,
                    ),
                )

        elif ul_mode == "media" and fext in extentions_list["photo"]:
            try:
                await unzip_bot.send_photo(
                    chat_id=c_id,
                    photo=doc_f,
                    caption=messages.get(
                        file="up_helper", key="EXT_CAPTION", user_id=c_id, extra_args=fname
                    ),
                    disable_notification=True,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        messages.get(
                            file="up_helper", key="TRY_UP", user_id=c_id, extra_args=fname
                        ),
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
                        caption=messages.get(
                            file="up_helper", key="EXT_CAPTION", user_id=c_id, extra_args=fname
                        ),
                        force_document=True,
                        disable_notification=True,
                        progress=progress_for_pyrogram,
                        progress_args=(
                            messages.get(
                                file="up_helper", key="TRY_UP", user_id=c_id, extra_args=fname
                            ),
                            upmsg,
                            time(),
                            unzip_bot,
                        ),
                    )
                else:
                    await unzip_bot.send_document(
                        chat_id=c_id,
                        document=doc_f,
                        caption=messages.get(
                            file="up_helper", key="EXT_CAPTION", user_id=c_id, extra_args=fname
                        ),
                        force_document=True,
                        disable_notification=True,
                        progress=progress_for_pyrogram,
                        progress_args=(
                            messages.get(
                                file="up_helper", key="TRY_UP", user_id=c_id, extra_args=fname
                            ),
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
                    caption=messages.get(
                        file="up_helper", key="EXT_CAPTION", user_id=c_id, extra_args=fname
                    ),
                    duration=vid_duration,
                    thumb=thumb_image,
                    disable_notification=True,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        messages.get(
                            file="up_helper", key="TRY_UP", user_id=c_id, extra_args=fname
                        ),
                        upmsg,
                        time(),
                        unzip_bot,
                    ),
                )
            else:
                thmb_pth = f"{Config.THUMB_LOCATION}/thumbnail_{os.path.basename(doc_f)}.jpg"

                if os.path.exists(thmb_pth):
                    os.remove(path=thmb_pth)

                midpoint_seconds = int(vid_duration / 2)
                midpoint_timedelta = timedelta(seconds=midpoint_seconds)
                midpoint_str = str(midpoint_timedelta)

                if "." not in midpoint_str:
                    midpoint_str += ".00"
                else:
                    midpoint_str = (
                        midpoint_str.split(sep=".")[0] + "." + midpoint_str.split(sep=".")[1][:2]
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
                    shutil.copy(src=Config.BOT_THUMB, dst=thmb_pth)

                await unzip_bot.send_video(
                    chat_id=c_id,
                    video=doc_f,
                    caption=messages.get(
                        file="up_helper", key="EXT_CAPTION", user_id=c_id, extra_args=fname
                    ),
                    duration=vid_duration,
                    thumb=thmb_pth,
                    disable_notification=True,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        messages.get(
                            file="up_helper", key="TRY_UP", user_id=c_id, extra_args=fname
                        ),
                        upmsg,
                        time(),
                        unzip_bot,
                    ),
                )

                try:
                    os.remove(path=thmb_pth)
                except:
                    pass

        else:
            if thumbornot:
                thumb_image = Config.THUMB_LOCATION + "/" + str(c_id) + ".jpg"
                await unzip_bot.send_document(
                    chat_id=c_id,
                    document=doc_f,
                    thumb=thumb_image,
                    caption=messages.get(
                        file="up_helper", key="EXT_CAPTION", user_id=c_id, extra_args=fname
                    ),
                    force_document=True,
                    disable_notification=True,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        messages.get(
                            file="up_helper", key="TRY_UP", user_id=c_id, extra_args=fname
                        ),
                        upmsg,
                        time(),
                        unzip_bot,
                    ),
                )
            else:
                await unzip_bot.send_document(
                    chat_id=c_id,
                    document=doc_f,
                    caption=messages.get(
                        file="up_helper", key="EXT_CAPTION", user_id=c_id, extra_args=fname
                    ),
                    force_document=True,
                    disable_notification=True,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        messages.get(
                            file="up_helper", key="TRY_UP", user_id=c_id, extra_args=fname
                        ),
                        upmsg,
                        time(),
                        unzip_bot,
                    ),
                )

        if upmsg:
            await upmsg.delete()

        os.remove(path=doc_f)
    except (FloodWait, FloodPremiumWait) as f:
        await asyncio.sleep(f.value)
        await send_file(
            unzip_bot=unzip_bot,
            c_id=c_id,
            doc_f=doc_f,
            query=query,
            full_path=full_path,
            log_msg=log_msg,
            split=split,
        )
    except FileNotFoundError:
        try:
            await unzipbot_client.send_message(
                chat_id=c_id,
                text=messages.get(
                    file="up_helper",
                    key="CANT_FIND",
                    user_id=c_id,
                    extra_args=os.path.basename(doc_f),
                ),
            )
        except:
            pass

        return
    except BaseException as e:
        LOGGER.error(msg=e)
        shutil.rmtree(full_path)


# TODO
async def forward_file(message, cid):
    try:
        await unzipbot_client.copy_message(
            chat_id=cid,
            from_chat_id=message.chat.id,
            message_id=message.id,
            disable_notification=True,
        )
    except (FloodWait, FloodPremiumWait) as f:
        await asyncio.sleep(f.value)
        await forward_file(message=message, cid=cid)


# TODO
async def send_url_logs(unzip_bot, c_id, doc_f, source, message):
    try:
        u_file_size = os.stat(path=doc_f).st_size

        if Config.TG_MAX_SIZE < int(u_file_size):
            await unzip_bot.send_message(
                chat_id=c_id, text=messages.get(file="up_helper", key="TOO_LARGE", user_id=c_id)
            )

            return

        fname = os.path.basename(doc_f)
        await unzip_bot.send_document(
            chat_id=c_id,
            document=doc_f,
            caption=messages.get(
                file="up_helper", key="LOG_CAPTION", user_id=c_id, extra_args=[fname, source]
            ),
            disable_notification=True,
            progress=progress_urls,
            progress_args=(
                messages.get(file="up_helper", key="CHECK_MSG", user_id=c_id),
                message,
                time(),
            ),
        )
    except (FloodWait, FloodPremiumWait) as f:
        await asyncio.sleep(f.value)

        return send_url_logs(
            unzip_bot=unzip_bot, c_id=c_id, doc_f=doc_f, source=source, message=message
        )
    except FileNotFoundError:
        await unzip_bot.send_message(
            chat_id=Config.LOGS_CHANNEL,
            text=messages.get(file="up_helper", key="ARCHIVE_GONE", user_id=c_id),
        )
    except BaseException:
        pass


# TODO
async def merge_split_archives(user_id, path):
    cmd = f'cd "{path}" && cat * > MERGED_{user_id}.zip'
    await run_shell_cmds(cmd)


# Function to remove basic markdown characters from a string
async def rm_mark_chars(text: str):
    return re.sub(pattern="[*`_]", repl="", string=text)


# TODO
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
                    chat_id=query.message.chat.id, text=message_text, reply_markup=buttons
                )
            else:
                await unzipbot_client.send_message(
                    chat_id=query.message.chat.id, text=message_text, reply_markup=buttons
                )
        except:
            pass
