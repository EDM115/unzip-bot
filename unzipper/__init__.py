# Copyright (c) 2022 EDM115

from pyrogram import Client
from pyromod import listen
import logging

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
    level=logging.INFO,
    handlers=[logging.FileHandler('log.txt'), logging.StreamHandler()],
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
LOGGER = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)
