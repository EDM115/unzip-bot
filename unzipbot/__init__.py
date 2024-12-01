import logging
import time

import pyrogram
from pyromod import listen  # skipcq: PY-W2000

from config import Config


boottime = time.time()
plugins = dict(root="modules")

unzipbot_client = pyrogram.Client(
    "unzip-bot",
    bot_token=Config.BOT_TOKEN,
    api_id=Config.APP_ID,
    api_hash=Config.API_HASH,
    plugins=plugins,
    sleep_threshold=10,
    max_concurrent_transmissions=3,
)

pyrogram.utils.MIN_CHAT_ID = -999999999999
pyrogram.utils.MIN_CHANNEL_ID = -100999999999999

logging.basicConfig(
    level=logging.INFO,
    handlers=[logging.FileHandler("unzip-bot.log"), logging.StreamHandler()],
    format="%(asctime)s - %(levelname)s - %(name)s - %(threadName)s - %(message)s",
)

LOGGER = logging.getLogger(__name__)

logging.getLogger("asyncio").setLevel(logging.WARNING)
logging.getLogger("aiohttp").setLevel(logging.WARNING)
logging.getLogger("aiofiles").setLevel(logging.WARNING)
logging.getLogger("dnspython").setLevel(logging.WARNING)
logging.getLogger("GitPython").setLevel(logging.WARNING)
logging.getLogger("motor").setLevel(logging.WARNING)
logging.getLogger("Pillow").setLevel(logging.WARNING)
logging.getLogger("psutil").setLevel(logging.WARNING)
logging.getLogger("pyrogram").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)
