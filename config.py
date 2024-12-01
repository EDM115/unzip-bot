import os


class Config:
    APP_ID = int(os.environ.get("APP_ID"))
    API_HASH = os.environ.get("API_HASH")
    BASE_LANGUAGE = os.environ.get("BASE_LANGUAGE", "en")
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    BOT_THUMB = f"{os.path.dirname(__file__)}/bot_thumb.jpg"
    BOT_OWNER = int(os.environ.get("BOT_OWNER"))
    # Default chunk size (0.005 MB → 1024*6) Increase if you need faster downloads
    CHUNK_SIZE = 1024 * 1024 * 10  # 10 MB
    DOWNLOAD_LOCATION = f"{os.path.dirname(__file__)}/Downloaded"
    IS_HEROKU = os.environ.get("DYNO", "").startswith("worker.")
    LOGS_CHANNEL = (
        int(os.environ.get("LOGS_CHANNEL"))
        if os.environ.get("LOGS_CHANNEL").strip("-").isdigit()
        else os.environ.get("LOGS_CHANNEL")
    )
    MAX_CONCURRENT_TASKS = 75
    MAX_MESSAGE_LENGTH = 4096
    # 512 MB by default for Heroku, unlimited otherwise
    MAX_RAM_AMOUNT_KB = 1024 * 512 if IS_HEROKU else -1
    MAX_RAM_USAGE = 100 if IS_HEROKU else 80
    MAX_TASK_DURATION_EXTRACT = 120 * 60  # 2 hours (in seconds)
    MAX_TASK_DURATION_MERGE = 240 * 60  # 4 hours (in seconds)
    MONGODB_URL = os.environ.get("MONGODB_URL")
    MONGODB_DBNAME = os.environ.get("MONGODB_DBNAME", "Unzipper_Bot")
    TG_MAX_SIZE = 2097152000
    THUMB_LOCATION = f"{os.path.dirname(__file__)}/Thumbnails"
    VERSION = os.environ.get("UNZIPBOT_VERSION", "7.0.2a")
