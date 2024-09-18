# Copyright (c) 2022 - 2024 EDM115
import aiocron
import asyncio
import shutil

from datetime import datetime
from pyrogram import enums
from pyrogram.errors import FloodWait
from time import time

from .database import (
    clear_cancel_tasks,
    clear_merge_tasks,
    get_thumb_users,
    set_boot,
    get_boot,
    set_old_boot,
    get_old_boot,
    is_boot_different,
    count_ongoing_tasks,
    get_ongoing_tasks,
    clear_ongoing_tasks,
    del_ongoing_task,
)
from config import Config
from unzipper import boottime, LOGGER, unzipperbot
from unzipper.modules.bot_data import Messages
from unzipper.modules.callbacks import download


def check_logs():
    try:
        if Config.LOGS_CHANNEL:
            c_info = unzipperbot.get_chat(chat_id=Config.LOGS_CHANNEL)
            if c_info.type in (enums.ChatType.PRIVATE, enums.ChatType.BOT):
                LOGGER.error(Messages.PRIVATE_CHAT)
                return False
            return True
        LOGGER.error(Messages.NO_LOG_ID)
        return False
    except:
        LOGGER.error(Messages.ERROR_LOG_CHECK)
        return False


def dl_thumbs():
    loop = asyncio.get_event_loop()
    coroutine = get_thumb_users()
    thumbs = loop.run_until_complete(coroutine)
    i = 0
    maxthumbs = len(thumbs)
    LOGGER.info(Messages.DL_THUMBS.format(maxthumbs))
    for thumb in thumbs:
        if thumb.get("url") is None and thumb.get("file_id") is not None:
            unzipperbot.download_media(
                message=thumb.get("file_id"),
                file_name=(
                    Config.THUMB_LOCATION + "/" + str(thumb.get("_id")) + ".jpg"
                ),
            )
        elif thumb.get("url") is not None and thumb.get("file_id") is None:
            loop2 = asyncio.get_event_loop()
            coroutine2 = download(
                thumb.get("url"),
                (Config.THUMB_LOCATION + "/" + str(thumb.get("_id")) + ".jpg"),
            )
            loop2.run_until_complete(coroutine2)
        i += 1
        if i % 10 == 0 or i == maxthumbs:
            LOGGER.info(Messages.DOWNLOADED_THUMBS.format(i, maxthumbs))


def set_boot_time():
    loop = asyncio.get_event_loop()
    coroutine = check_boot()
    loop.run_until_complete(coroutine)


async def check_boot():
    boot = await get_boot()
    await set_old_boot(boot)
    await set_boot(boottime)
    boot = await get_boot()
    old_boot = await get_old_boot()
    different = await is_boot_different()
    if different:
        try:
            await unzipperbot.send_message(
                Config.BOT_OWNER,
                Messages.BOT_RESTARTED.format(
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
                await unzipperbot.send_message(
                    task.get("user_id"), Messages.RESEND_TASK
                )
            except FloodWait as f:
                await asyncio.sleep(f.value)
                await unzipperbot.send_message(
                    task.get("user_id"), Messages.RESEND_TASK
                )
            except:
                pass  # user deleted chat
        await clear_ongoing_tasks()


def removal(firststart=False):
    loop = asyncio.get_event_loop()
    loop.create_task(remove_expired_tasks(firststart))
    loop.run_until_complete(asyncio.sleep(0))


async def remove_expired_tasks(firststart=False):
    ongoing_tasks = await get_ongoing_tasks()
    if firststart:
        await clear_ongoing_tasks()
        try:
            shutil.rmtree(Config.DOWNLOAD_LOCATION)
        except:
            pass
    else:
        for task in ongoing_tasks:
            user_id = task.get("user_id")
            if not user_id == Config.BOT_OWNER:
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
                        await unzipperbot.send_message(
                            user_id,
                            Messages.TASK_EXPIRED.format(
                                Config.MAX_TASK_DURATION_EXTRACT // 60
                            ),
                        )
                elif task_type == "merge":
                    if time_gap > Config.MAX_TASK_DURATION_MERGE:
                        try:
                            await del_ongoing_task(user_id)
                            shutil.rmtree(f"{Config.DOWNLOAD_LOCATION}/{user_id}")
                        except:
                            pass
                        await unzipperbot.send_message(
                            user_id,
                            Messages.TASK_EXPIRED.format(
                                Config.MAX_TASK_DURATION_MERGE // 60
                            ),
                        )


@aiocron.crontab("*/5 * * * *")
async def scheduled_remove_expired_tasks():
    await remove_expired_tasks()


def start_cron_jobs():
    scheduled_remove_expired_tasks.start()
    asyncio.get_event_loop().run_forever()
