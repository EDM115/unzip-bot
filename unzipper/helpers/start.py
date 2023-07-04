# Copyright (c) 2023 EDM115
import asyncio
import sys

from pyrogram import enums

from config import Config
from unzipper import LOGGER, boottime, unzipperbot as client
from unzipper.modules.bot_data import Messages
from unzipper.modules.callbacks import download

from .database import clear_cancel_tasks, clear_merge_tasks, get_thumb_users, set_boot, get_boot, set_old_boot, get_old_boot, is_boot_different, count_ongoing_tasks, get_ongoing_tasks, clear_ongoing_tasks


def check_logs():
    try:
        if Config.LOGS_CHANNEL:
            c_info = client.get_chat(chat_id=Config.LOGS_CHANNEL)
            if c_info.type in (enums.ChatType.PRIVATE, enums.ChatType.BOT):
                LOGGER.warning(Messages.PRIVATE_CHAT)
                return False
            return True
        LOGGER.warning(Messages.NO_LOG_ID)
        sys.exit()
    except:
        LOGGER.warning(Messages.ERROR_LOG_CHECK)


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
            except:
                pass  # user deleted chat
        await clear_ongoing_tasks()
