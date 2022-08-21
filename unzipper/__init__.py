# Copyright (c) 2022 EDM115

from pyrogram import Client
from pyromod import listen
import logging
import time

from config import Config

boottime = time.time()

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
    level=logging.INFO,
    # Can't be done due to https://github.com/EDM115/unzip-bot/blob/3f951a29cd2a19d592bbc3e65bbbbb678fa5cee3/unzipper/modules/commands.py#L242
    # Reference for future implementation : https://stackoverflow.com/questions/5013532/open-file-by-filename-wildcard
    # actualtime=time.strftime(%d-%m-%Y)
    # logfilename=actualtime+"unzip-log.txt"
    # handlers=[logging.FileHandler(logfilename), logging.StreamHandler()],
    handlers=[logging.FileHandler("unzip-log.txt"), logging.StreamHandler()],
    format="%(asctime)s - %(levelname)s - %(name)s - %(threadName)s - %(message)s"
)
LOGGER = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARN)
logging.getLogger("motor").setLevel(logging.INFO)
logging.getLogger("aiohttp").setLevel(logging.INFO)
