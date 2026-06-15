import asyncio
import os
import signal
import time

from pyrogram import idle

from . import LOGGER, unzipbot_client
from .config.config import Config
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
    LOGGER.info(msg=messages.get(file="main", key="STOP_TXT", extra_args=stoptime))

    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    [task.cancel() for task in tasks]
    await asyncio.gather(*tasks, return_exceptions=True)

    try:
        await unzipbot_client.send_message(
            chat_id=Config.LOGS_CHANNEL,
            text=messages.get(file="main", key="STOP_TXT", extra_args=stoptime),
        )

        with open(file="unzip-bot.log", mode="rb") as doc_f:
            try:
                await unzipbot_client.send_document(
                    chat_id=Config.LOGS_CHANNEL, document=doc_f, file_name=doc_f.name
                )
            except:
                pass
    except Exception as e:
        LOGGER.error(msg=messages.get(file="main", key="ERROR_SHUTDOWN_MSG", extra_args=e))
    finally:
        await unzipbot_client.stop()
        LOGGER.info(msg=messages.get(file="main", key="BOT_STOPPED"))


def handle_stop_signals(signum, frame):
    LOGGER.info(
        msg=messages.get(
            file="main",
            key="RECEIVED_STOP_SIGNAL",
            extra_args=[signal.Signals(signum).name, signum, frame],
        )
    )
    loop = asyncio.get_event_loop()
    loop.create_task(coro=async_shutdown_bot())


def setup_signal_handlers():
    loop = asyncio.get_event_loop()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(
            sig=sig, callback=lambda s=sig: handle_stop_signals(signum=s, frame=None)
        )


async def main():
    try:
        os.makedirs(name=Config.DOWNLOAD_LOCATION, exist_ok=True)
        os.makedirs(name=Config.THUMB_LOCATION, exist_ok=True)

        if os.path.exists(Config.LOCKFILE):
            os.remove(path=Config.LOCKFILE)

        with open(file=Config.LOCKFILE, mode="w") as lock_f:
            lock_f.close()

        LOGGER.info(msg=messages.get(file="main", key="STARTING_BOT"))
        await unzipbot_client.start()
        starttime = time.strftime("%Y/%m/%d - %H:%M:%S")
        await unzipbot_client.send_message(
            chat_id=Config.LOGS_CHANNEL,
            text=messages.get(file="main", key="START_TXT", extra_args=starttime),
        )
        await set_boot_time()
        LOGGER.info(msg=messages.get(file="main", key="CHECK_LOG"))

        if await check_logs():
            LOGGER.info(msg=messages.get(file="main", key="LOG_CHECKED"))
            setup_signal_handlers()
            await remove_expired_tasks(True)
            await dl_thumbs()
            await start_cron_jobs()
            os.remove(path=Config.LOCKFILE)
            LOGGER.info(msg=messages.get(file="main", key="BOT_RUNNING"))
            await idle()
        else:
            try:
                await unzipbot_client.send_message(
                    chat_id=Config.BOT_OWNER,
                    text=messages.get(file="main", key="WRONG_LOG", extra_args=Config.LOGS_CHANNEL),
                )
            except:
                pass

            os.remove(path=Config.LOCKFILE)
            await async_shutdown_bot()
    except Exception as e:
        LOGGER.error(msg=messages.get(file="main", key="ERROR_MAIN_LOOP", extra_args=e))
    finally:
        if os.path.exists(Config.LOCKFILE):
            os.remove(path=Config.LOCKFILE)
        await async_shutdown_bot()


if __name__ == "__main__":
    unzipbot_client.run(main())
