# Copyright (c) 2022 EDM115

from pyrogram import Client
from pyromod import listen
import logging
import time

from config import Config

plugins = dict(root="unzipper/modules")
unzipperbot = Client(
        "UnzipperBot",
        bot_token=Config.BOT_TOKEN,
        api_id=Config.APP_ID,
        api_hash=Config.API_HASH,
        plugins=plugins,
        sleep_threshold=10
    )

logging.basicConfig(
    level=logging.DEBUG,
    actualtime=time.strftime(%d-%m-%Y)
    logfilename=actualtime+"unzip-log.txt"
    handlers=[logging.FileHandler(logfilename), logging.StreamHandler()],
    format="%(asctime)s - %(levelname)s - %(name)s - %(threadName)s - %(message)s"
)
LOGGER = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.DEBUG)
logging.getLogger("motor").setLevel(logging.DEBUG)
logging.getLogger("aiohttp").setLevel(logging.DEBUG)
