# Copyright (c) 2023 EDM115
import logging
import os
import signal
import time

from pyrogram import idle
from pyrogram.errors import AuthKeyDuplicated

from config import Config

from . import unzipperbot, premiumuser
from .helpers.start import check_logs, dl_thumbs, set_boot_time, removal
from .modules.bot_data import Messages

running = True


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
        LOGGER.info(Messages.STARTING_BOT)
        unzipperbot.start()
        starttime = time.strftime("%Y/%m/%d - %H:%M:%S")
        unzipperbot.send_message(
            chat_id=Config.LOGS_CHANNEL, text=Messages.START_TXT.format(starttime)
        )
        set_boot_time()
        dl_thumbs()
        if Config.SESSION_STRING:
            try:
                premiumuser.start()
            except AuthKeyDuplicated:
                pass
        LOGGER.info(Messages.CHECK_LOG)
        if check_logs():
            LOGGER.info(Messages.LOG_CHECKED)
            LOGGER.info(Messages.BOT_RUNNING)
            removal(True)
            idle()
        else:
            try:
                unzipperbot.send_message(
                    chat_id=Config.BOT_OWNER,
                    text=Messages.WRONG_LOG.format(Config.LOGS_CHANNEL),
                )
            except:
                pass
            unzipperbot.stop()

LOGGER.info("Received SIGTERM")
stoptime = time.strftime("%Y/%m/%d - %H:%M:%S")
unzipperbot.send_message(
    chat_id=Config.LOGS_CHANNEL, text=Messages.STOP_TXT.format(stoptime)
)
unzipperbot.stop()
LOGGER.info("Bot stopped 😪")
