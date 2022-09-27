# Copyright (c) 2022 EDM115
import sys
import asyncio

from pyrogram import enums

from config import Config
from unzipper import unzipperbot as client, LOGGER
from unzipper.modules.callbacks import download
from .database import get_thumb_users

# Checking log channel
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
    LOGGER.info(thumbs)
    for thumb in thumbs:
        loop2 = asyncio.get_event_loop()
        coroutine2 = download(thumb["url"], (Config.THUMB_LOCATION + "/" + str(thumb["_id"]) + ".jpg"))
        loop2.run_until_complete(coroutine2)
