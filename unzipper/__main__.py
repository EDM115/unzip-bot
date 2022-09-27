# Copyright (c) 2022 EDM115
import logging
import os
import signal
import time

from pyrogram import idle
from . import unzipperbot
from .helpers.unzip_help import check_logs, dl_thumbs
from .modules.bot_data import Messages
from config import Config

running = True
# https://stackoverflow.com/questions/18499497/how-to-process-sigterm-signal-gracefully


def handler_stop_signals(signum, frame):
    global running
    running = False


signal.signal(signal.SIGINT, handler_stop_signals)
signal.signal(signal.SIGTERM, handler_stop_signals)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(threadName)s - %(message)s",
)
LOGGER = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARN)
logging.getLogger("motor").setLevel(logging.INFO)
logging.getLogger("aiohttp").setLevel(logging.INFO)

while running:
    if __name__ == "__main__":
        if not os.path.isdir(Config.DOWNLOAD_LOCATION):
            os.makedirs(Config.DOWNLOAD_LOCATION)
        if not os.path.isdir(Config.THUMB_LOCATION):
            os.makedirs(Config.THUMB_LOCATION)
        unzipperbot.start()
        starttime = time.strftime("%Y/%m/%d - %H:%M:%S")
        unzipperbot.send_message(
            chat_id=Config.LOGS_CHANNEL, text=Messages.START_TXT.format(starttime)
        )
        dl_thumbs()
        LOGGER.info("Checking Log channel…")
        if check_logs():
            LOGGER.info("Log channel alright")
            LOGGER.info("Starting bot…")
            LOGGER.info("Bot is running now ! Join @EDM115bots")
            idle()
        else:
            try:
                unzipperbot.send_message(
                    chat_id=Config.BOT_OWNER,
                    text=f"Error : the provided **LOGS_CHANNEL** (`{Config.LOGS_CHANNEL}`) is incorrect. Bot crashed 😪",
                )
            except:
                unzipperbot.stop()

LOGGER.info("Received SIGTERM")
stoptime = time.strftime("%Y/%m/%d - %H:%M:%S")
unzipperbot.send_message(
    chat_id=Config.LOGS_CHANNEL, text=Messages.STOP_TXT.format(stoptime)
)
LOGGER.info("Bot stopped 😪")
