import asyncio
import os
import shutil
import signal
import time

from pyrogram import idle

from config import Config

from . import LOGGER, unzipbot_client
from .helpers.database import get_lang
from .helpers.start import (
    check_logs,
    dl_thumbs,
    removal,
    set_boot_time,
    start_cron_jobs,
)
from .i18n.messages import Messages


messages = Messages(lang_fetcher=get_lang)


def recurse_delete(dir):
    for items in os.listdir(dir):
        if os.path.isdir(os.path.join(dir, items)):
            shutil.rmtree(os.path.join(dir, items), ignore_errors=True)
        else:
            os.remove(os.path.join(dir, items))


def handler_stop_signals(signum, frame):
    LOGGER.info(
        messages.get(
            "main",
            "RECEIVED_STOP_SIGNAL",
            None,
            signal.Signals(signum).name,
            signum,
            frame,
        )
    )
    shutdown_bot()


signal.signal(signal.SIGINT, handler_stop_signals)
signal.signal(signal.SIGTERM, handler_stop_signals)


async def async_shutdown_bot():
    stoptime = time.strftime("%Y/%m/%d - %H:%M:%S")
    LOGGER.info(messages.get("main", "STOP_TXT", None, stoptime))

    try:
        await unzipbot_client.send_message(
            chat_id=Config.LOGS_CHANNEL,
            text=messages.get("main", "STOP_TXT", None, stoptime),
        )

        with open("unzip-bot.log", "rb") as doc_f:
            try:
                await unzipbot_client.send_document(
                    chat_id=Config.LOGS_CHANNEL,
                    document=doc_f,
                    file_name=doc_f.name,
                )
            except:
                pass
    except Exception as e:
        LOGGER.error(messages.get("main", "ERROR_SHUTDOWN_MSG", None, e))
    finally:
        LOGGER.info(messages.get("main", "BOT_STOPPED"))
        await unzipbot_client.stop(block=False)


def shutdown_bot():
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(async_shutdown_bot())
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(async_shutdown_bot())


if __name__ == "__main__":
    try:
        os.makedirs(Config.DOWNLOAD_LOCATION, exist_ok=True)
        os.makedirs(Config.THUMB_LOCATION, exist_ok=True)

        if os.path.exists(Config.LOCKFILE):
            os.remove(Config.LOCKFILE)

        with open(Config.LOCKFILE, "w") as lock_f:
            lock_f.close()

        LOGGER.info(messages.get("main", "STARTING_BOT"))
        unzipbot_client.start()
        starttime = time.strftime("%Y/%m/%d - %H:%M:%S")
        unzipbot_client.send_message(
            chat_id=Config.LOGS_CHANNEL,
            text=messages.get("main", "START_TXT", None, starttime),
        )
        set_boot_time()
        LOGGER.info(messages.get("main", "CHECK_LOG"))

        if check_logs():
            LOGGER.info(messages.get("main", "LOG_CHECKED"))
            removal(True)
            dl_thumbs()
            # clean previous downloads on volumes
            recurse_delete(Config.DOWNLOAD_LOCATION)
            os.makedirs(Config.DOWNLOAD_LOCATION, exist_ok=True)
            os.remove(Config.LOCKFILE)
            LOGGER.info(messages.get("main", "BOT_RUNNING"))
            start_cron_jobs()
            idle()
        else:
            try:
                unzipbot_client.send_message(
                    chat_id=Config.BOT_OWNER,
                    text=messages.get("main", "WRONG_LOG", None, Config.LOGS_CHANNEL),
                )
            except:
                pass

            os.remove(Config.LOCKFILE)
            shutdown_bot()
    except Exception as e:
        LOGGER.error(messages.get("main", "ERROR_MAIN_LOOP", None, e))
    finally:
        if os.path.exists(Config.LOCKFILE):
            os.remove(Config.LOCKFILE)
        shutdown_bot()
