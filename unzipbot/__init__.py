import asyncio
import logging
import sys
import time

from pyrogram import Client

from .config.config import Config

# https://stackoverflow.com/questions/69890200/how-to-configure-os-specific-dependencies-in-a-pyproject-toml-file-maturin/75711133#75711133
if sys.platform.startswith("win32") or sys.platform.startswith("linux-cross"):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
else:
    import uvloop  # pyright: ignore[reportMissingImports]

    uvloop.install()
    loop = uvloop.new_event_loop()
    asyncio.set_event_loop(loop)

boottime = time.time()
plugins = dict(
    root="plugins",
    include=["commands.global", "commands.user", "commands.admin", "callbacks.global"],
)

unzipbot_client = Client(
    name="unzip-bot",
    bot_token=Config.BOT_TOKEN,
    api_id=Config.APP_ID,
    api_hash=Config.API_HASH,
    plugins=plugins,
    sleep_threshold=7200,
    max_concurrent_transmissions=3,
)

logging.basicConfig(
    level=logging.INFO,
    handlers=[logging.FileHandler(filename="unzip-bot.log"), logging.StreamHandler()],
    format="%(asctime)s - %(levelname)s - %(name)s - %(threadName)s - %(message)s",
)

LOGGER = logging.getLogger(__name__)

logging.getLogger("aiohttp").setLevel(logging.WARNING)
logging.getLogger("aiofiles").setLevel(logging.WARNING)
logging.getLogger("GitPython").setLevel(logging.WARNING)
logging.getLogger("motor").setLevel(logging.WARNING)
logging.getLogger("Pillow").setLevel(logging.WARNING)
logging.getLogger("psutil").setLevel(logging.WARNING)
logging.getLogger("pyrogram").setLevel(logging.WARNING)
