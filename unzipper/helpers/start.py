# Copyright (c) 2023 EDM115
import asyncio
import sys

from pyrogram import enums

from config import Config
from unzipper import LOGGER, boottime
from unzipper import unzipperbot as client
from unzipper.modules.callbacks import download

from .database import get_thumb_users, set_boot, get_boot, set_old_boot, get_old_boot, is_boot_different


def check_logs():
    try:
        if Config.LOGS_CHANNEL:
            c_info = client.get_chat(chat_id=Config.LOGS_CHANNEL)
            if c_info.type in (enums.ChatType.PRIVATE, enums.ChatType.BOT):
                LOGGER.warn("A private chat can't be used 😐")
                return False
            return True
        LOGGER.warn("No Log channel ID is given !")
        sys.exit()
    except:
        print(
            "Error happened while checking Log channel 💀 Make sure you're not dumb enough to provide a wrong Log channel ID 🧐"
        )


def dl_thumbs():
    loop = asyncio.get_event_loop()
    coroutine = get_thumb_users()
    thumbs = loop.run_until_complete(coroutine)
    for thumb in thumbs:
        loop2 = asyncio.get_event_loop()
        coroutine2 = download(
            thumb["url"], (Config.THUMB_LOCATION + "/" + str(thumb["_id"]) + ".jpg")
        )
        loop2.run_until_complete(coroutine2)

def set_boot_time():
    loop = asyncio.get_event_loop()
    coroutine = check_boot()
    loop.run_until_complete(coroutine)

async def check_boot():
    # Put the previous boot time in old_boot
    boot = await get_boot()
    await set_old_boot(boot)

    # Set the current boot time in boot
    await set_boot(boottime)

    # Get the newest values
    boot = await get_boot()
    old_boot = await get_old_boot()

    if await is_boot_different():
        await client.send_message(Config.BOT_OWNER, f"Bot restarted !\n\n**Old boot time** : `{old_boot}`\n**New boot time** : `{boot}`")
    