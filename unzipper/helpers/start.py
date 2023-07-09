# Copyright (c) 2023 EDM115
import asyncio
import shutil
import sys

from pyrogram import enums
from pyrogram.errors import FloodWait
from time import time

from config import Config
from unzipper import LOGGER, boottime, unzipperbot as client
from unzipper.modules.bot_data import Messages
from unzipper.modules.callbacks import download

from .database import clear_cancel_tasks, clear_merge_tasks, del_ongoing_task, get_thumb_users, set_boot, get_boot, set_old_boot, get_old_boot, is_boot_different, count_ongoing_tasks, get_ongoing_tasks, clear_ongoing_tasks


def check_logs():
    try:
        if Config.LOGS_CHANNEL:
            c_info = client.get_chat(chat_id=Config.LOGS_CHANNEL)
            if c_info.type in (enums.ChatType.PRIVATE, enums.ChatType.BOT):
                LOGGER.warning(Messages.PRIVATE_CHAT)
                return False
            return True
        LOGGER.warning(Messages.NO_LOG_ID)
        return sys.exit()
    except:
        LOGGER.warning(Messages.ERROR_LOG_CHECK)
        return False


def dl_thumbs():
    loop = asyncio.get_event_loop()
    coroutine = get_thumb_users()
    thumbs = loop.run_until_complete(coroutine)
    i = 0
    maxthumbs = len(thumbs)
    LOGGER.info(Messages.DL_THUMBS.format(maxthumbs))
    for thumb in thumbs:
        i += 1
        loop2 = asyncio.get_event_loop()
        coroutine2 = download(
            thumb["url"], (Config.THUMB_LOCATION + "/" + str(thumb["_id"]) + ".jpg")
        )
        loop2.run_until_complete(coroutine2)
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
            await client.send_message(Config.BOT_OWNER, Messages.BOT_RESTARTED.format(old_boot, boot))
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
                await client.send_message(task["user_id"], Messages.RESEND_TASK)
            except FloodWait as f:
                await asyncio.sleep(f.value)
                await client.send_message(task["user_id"], Messages.RESEND_TASK)
            except:
                pass  # user deleted chat
        await clear_ongoing_tasks()


def removal():
    loop = asyncio.get_event_loop()
    loop.create_task(remove_expired_tasks())
    loop.run_until_complete(asyncio.sleep(0))


async def remove_expired_tasks():
    while True:
        ongoing_tasks = await get_ongoing_tasks()
        current_time = time()

        for task in ongoing_tasks:
            start_time = task["start_time"]
            type = task["type"]
            time_gap = current_time - start_time

            if type == "extract":
                if time_gap > Config.MAX_TASK_DURATION_EXTRACT:
                    user_id = task["user_id"]
                    await del_ongoing_task(user_id)
                    try:
                        shutil.rmtree(f"{Config.DOWNLOAD_LOCATION}/{user_id}")
                    except:
                        pass
                    await client.send_message(user_id, Messages.TASK_EXPIRED.format(Config.MAX_TASK_DURATION_EXTRACT // 60))
            elif type == "merge":
                if time_gap > Config.MAX_TASK_DURATION_MERGE:
                    user_id = task["user_id"]
                    await del_ongoing_task(user_id)
                    try:
                        shutil.rmtree(f"{Config.DOWNLOAD_LOCATION}/{user_id}")
                    except:
                        pass
                    await client.send_message(user_id, Messages.TASK_EXPIRED.format(Config.MAX_TASK_DURATION_MERGE // 60))

        await asyncio.sleep(5 * 60)  # Sleep for 5 minutes
