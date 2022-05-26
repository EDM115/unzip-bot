# Copyright (c) 2022 EDM115

import os
import logging
import time
import signal

from pyrogram import idle
from . import unzipperbot
from .helpers.unzip_help import check_logs, TimeFormatter
from config import Config
from .modules.bot_data import Messages

running = True

def handler_stop_signals(signum, frame):
    global running
    running = False

signal.signal(signal.SIGINT, handler_stop_signals)
signal.signal(signal.SIGTERM, handler_stop_signals)

logging.basicConfig(
    level=logging.WARN,
    format="%(asctime)s - %(levelname)s - %(name)s - %(threadName)s - %(message)s"
)
LOGGER = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARN)
logging.getLogger("motor").setLevel(logging.INFO)
logging.getLogger("aiohttp").setLevel(logging.INFO)

while running:
    if __name__ == "__main__" :
        if not os.path.isdir(Config.DOWNLOAD_LOCATION):
            os.makedirs(Config.DOWNLOAD_LOCATION)
        unzipperbot.start()
        starttime = time.strftime("%Y/%m/%d - %H:%M:%S")
        unzipperbot.send_message(chat_id=Config.LOGS_CHANNEL, text=Messages.START_TXT.format(starttime))
        LOGGER.info("Checking Log channel…")
        check_logs()
        LOGGER.info("Starting bot…")
        LOGGER.info("Bot is running now ! Join @EDM115bots")
        idle()

stoptime = time.strftime("%Y/%m/%d - %H:%M:%S")
unzipperbot.send_message(chat_id=Config.LOGS_CHANNEL, text=Messages.STOP_TXT.format(stoptime))
LOGGER.info("Bot stopped 😪")
