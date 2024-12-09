import asyncio
import os
import shutil
from datetime import datetime
from time import time

import aiocron
from pyrogram import enums
from pyrogram.errors import FloodWait

from config import Config
from unzipbot import LOGGER, boottime, unzipbot_client
from unzipbot.i18n.messages import Messages
from unzipbot.modules.callbacks import download

from .database import (
    clear_cancel_tasks,
    clear_merge_tasks,
    clear_ongoing_tasks,
    count_ongoing_tasks,
    del_ongoing_task,
    get_boot,
    get_lang,
    get_old_boot,
    get_ongoing_tasks,
    get_thumb_users,
    is_boot_different,
    set_boot,
    set_old_boot,
)


def get_size(doc_f):
    try:
        fsize = os.stat(doc_f).st_size
        return fsize
    except:
        return -1


messages = Messages(lang_fetcher=get_lang)


async def check_logs():
    try:
        if Config.LOGS_CHANNEL:
            c_info = await unzipbot_client.get_chat(chat_id=Config.LOGS_CHANNEL)

            if c_info.type in (enums.ChatType.PRIVATE, enums.ChatType.BOT):
                LOGGER.error(messages.get("start", "PRIVATE_CHAT"))

                return False

            return True

        LOGGER.error(messages.get("start", "NO_LOG_ID"))

        return False
    except:
        LOGGER.error(messages.get("start", "ERROR_LOG_CHECK"))

        return False


async def dl_thumbs():
    thumbs = await get_thumb_users()
    i = 0
    maxthumbs = len(thumbs)
    LOGGER.info(messages.get("start", "DL_THUMBS", None, maxthumbs))

    for thumb in thumbs:
        file_path = Config.THUMB_LOCATION + "/" + str(thumb.get("_id")) + ".jpg"

        if not os.path.exists(file_path):
            if thumb.get("url") is None and thumb.get("file_id") is not None:
                try:
                    await unzipbot_client.download_media(
                        message=thumb.get("file_id"),
                        file_name=file_path,
                    )
                except:
                    # Here we could encounter 400 FILE_REFERENCE_EXPIRED
                    # A possible fix is to retrieve the message again with chat ID + message ID to get a refreshed file reference
                    await unzipbot_client.send_message(
                        thumb.get("_id"),
                        messages.get("start", "MISSING_THUMB", thumb.get("_id")),
                    )
            elif thumb.get("url") is not None and thumb.get("file_id") is None:
                await download(thumb.get("url"), file_path)

        if get_size(file_path) in (0, -1):
            os.remove(file_path)

        i += 1

        if i % 10 == 0 or i == maxthumbs:
            LOGGER.info(messages.get("start", "DOWNLOADED_THUMBS", None, i, maxthumbs))


async def set_boot_time():
    boot = await get_boot()
    await set_old_boot(boot)
    await set_boot(boottime)
    boot = await get_boot()
    old_boot = await get_old_boot()
    different = await is_boot_different()

    if different:
        try:
            await unzipbot_client.send_message(
                Config.BOT_OWNER,
                messages.get(
                    "start",
                    "BOT_RESTARTED",
                    Config.BOT_OWNER,
                    datetime.fromtimestamp(old_boot).strftime(r"%d/%m/%Y - %H:%M:%S"),
                    datetime.fromtimestamp(boot).strftime(r"%d/%m/%Y - %H:%M:%S"),
                ),
            )
        except:
            pass  # first start obviously

        await warn_users()


async def warn_users():
    await clear_cancel_tasks()
    await clear_merge_tasks()

    if await count_ongoing_tasks() > 0:
        tasks = await get_ongoing_tasks()

        for task in tasks:
            try:
                await unzipbot_client.send_message(
                    task.get("user_id"),
                    messages.get("start", "RESEND_TASK", task.get("user_id")),
                )
            except FloodWait as f:
                await asyncio.sleep(f.value)
                await unzipbot_client.send_message(
                    task.get("user_id"),
                    messages.get("start", "RESEND_TASK", task.get("user_id")),
                )
            except:
                pass  # user deleted chat

        await clear_ongoing_tasks()


async def remove_expired_tasks(firststart=False):
    ongoing_tasks = await get_ongoing_tasks()
    await clear_cancel_tasks()

    if firststart:
        await clear_ongoing_tasks()

        try:
            shutil.rmtree(Config.DOWNLOAD_LOCATION)
        except:
            pass

        os.makedirs(Config.DOWNLOAD_LOCATION, exist_ok=True)
    else:
        for task in ongoing_tasks:
            user_id = task.get("user_id")

            if user_id != Config.BOT_OWNER:
                current_time = time()
                start_time = task.get("start_time")
                task_type = task.get("type")
                time_gap = current_time - start_time

                if task_type == "extract":
                    if time_gap > Config.MAX_TASK_DURATION_EXTRACT:
                        try:
                            await del_ongoing_task(user_id)
                            shutil.rmtree(f"{Config.DOWNLOAD_LOCATION}/{user_id}")
                        except:
                            pass
                        await unzipbot_client.send_message(
                            user_id,
                            messages.get(
                                "start",
                                "TASK_EXPIRED",
                                user_id,
                                Config.MAX_TASK_DURATION_EXTRACT // 60,
                            ),
                        )
                elif task_type == "merge":
                    if time_gap > Config.MAX_TASK_DURATION_MERGE:
                        try:
                            await del_ongoing_task(user_id)
                            shutil.rmtree(f"{Config.DOWNLOAD_LOCATION}/{user_id}")
                        except:
                            pass
                        await unzipbot_client.send_message(
                            user_id,
                            messages.get(
                                "start",
                                "TASK_EXPIRED",
                                user_id,
                                Config.MAX_TASK_DURATION_MERGE // 60,
                            ),
                        )


@aiocron.crontab("*/5 * * * *")
async def scheduled_remove_expired_tasks():
    await remove_expired_tasks()


async def start_cron_jobs():
    scheduled_remove_expired_tasks.start()
