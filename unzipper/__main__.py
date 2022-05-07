# Copyright (c) 2022 EDM115

import os
import logging
from time import time

from pyrogram import idle
from . import unzipperbot
from .helpers.unzip_help import check_logs, TimeFormatter
from config import Config

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
LOGGER = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

if __name__ == "__main__" :
    if not os.path.isdir(Config.DOWNLOAD_LOCATION):
        os.makedirs(Config.DOWNLOAD_LOCATION)
    unzipperbot.start()
    starttime = TimeFormatter(time())
    await unzipperbot.send_message(chat_id=Config.LOGS_CHANNEL, text=Messages.START_TXT.format(starttime))
    print("Checking Log channel…")
    check_logs()
    LOGGER.info("Starting bot…")
    print("Bot is running now ! Join @EDM115bots")
    idle()
    stoptime = TimeFormatter(time())
    await unzipperbot.send_message(chat_id=Config.LOGS_CHANNEL, text=Messages.STOP_TXT.format(stoptime))
    LOGGER.info("Bot stopped 😪")
