import asyncio
import os
import signal
import time

from pyrogram import idle

from config import Config

from . import LOGGER, unzipbot_client
from .helpers.database import get_lang
from .helpers.start import (
    check_logs,
    dl_thumbs,
    remove_expired_tasks,
    set_boot_time,
    start_cron_jobs,
)
from .i18n.messages import Messages


messages = Messages(lang_fetcher=get_lang)


async def async_shutdown_bot():
    stoptime = time.strftime("%Y/%m/%d - %H:%M:%S")
    LOGGER.info(messages.get("main", "STOP_TXT", None, stoptime))

    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    [task.cancel() for task in tasks]
    await asyncio.gather(*tasks, return_exceptions=True)

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
        await unzipbot_client.stop()
        LOGGER.info(messages.get("main", "BOT_STOPPED"))


def handle_stop_signals(signum, frame):
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
    loop = asyncio.get_event_loop()
    loop.create_task(async_shutdown_bot())


def setup_signal_handlers():
    loop = asyncio.get_event_loop()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda s=sig: handle_stop_signals(s, None))


async def main():
    try:
        os.makedirs(Config.DOWNLOAD_LOCATION, exist_ok=True)
        os.makedirs(Config.THUMB_LOCATION, exist_ok=True)

        if os.path.exists(Config.LOCKFILE):
            os.remove(Config.LOCKFILE)

        with open(Config.LOCKFILE, "w") as lock_f:
            lock_f.close()

        LOGGER.info(messages.get("main", "STARTING_BOT"))
        await unzipbot_client.start()
        starttime = time.strftime("%Y/%m/%d - %H:%M:%S")
        await unzipbot_client.send_message(
            chat_id=Config.LOGS_CHANNEL,
            text=messages.get("main", "START_TXT", None, starttime),
        )
        await set_boot_time()
        LOGGER.info(messages.get("main", "CHECK_LOG"))

        if await check_logs():
            LOGGER.info(messages.get("main", "LOG_CHECKED"))
            setup_signal_handlers()
            await remove_expired_tasks(True)
            await dl_thumbs()
            await start_cron_jobs()
            os.remove(Config.LOCKFILE)
            LOGGER.info(messages.get("main", "BOT_RUNNING"))
            await idle()
        else:
            try:
                await unzipbot_client.send_message(
                    chat_id=Config.BOT_OWNER,
                    text=messages.get("main", "WRONG_LOG", None, Config.LOGS_CHANNEL),
                )
            except:
                pass

            os.remove(Config.LOCKFILE)
            await async_shutdown_bot()
    except Exception as e:
        LOGGER.error(messages.get("main", "ERROR_MAIN_LOOP", None, e))
    finally:
        if os.path.exists(Config.LOCKFILE):
            os.remove(Config.LOCKFILE)
        await async_shutdown_bot()


if __name__ == "__main__":
    unzipbot_client.run(main())
