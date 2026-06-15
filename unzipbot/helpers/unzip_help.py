import math
import time
from asyncio import sleep

import psutil
from pyrogram import enums
from pyrogram.errors import FloodPremiumWait, FloodWait

from unzipbot.config.config import Config
from unzipbot.helpers.database import del_cancel_task, get_cancel_task, get_lang
from unzipbot.i18n.buttons import Buttons
from unzipbot.i18n.messages import Messages

messages = Messages(lang_fetcher=get_lang)


# TODO
async def progress_for_pyrogram(current, total, ud_type, message, start, unzip_bot):
    if not message:
        return

    uid = message.chat.id

    if message.chat.type == enums.ChatType.PRIVATE and await get_cancel_task(uid):
        await del_cancel_task(uid)
        await message.edit(text=messages.get(file="unzip_help", key="DL_STOPPED", user_id=uid))
        unzip_bot.stop_transmission()
    else:
        now = time.time()
        diff = now - start

        if total == 0:
            tmp = messages.get(file="unzip_help", key="UNKNOWN_SIZE", user_id=uid)

            try:
                await message.edit(
                    text=messages.get(
                        file="unzip_help",
                        key="PROGRESS_MSG",
                        user_id=uid,
                        extra_args=[ud_type, tmp],
                    ),
                    reply_markup=Buttons.I_PREFER_STOP,
                )
            except (FloodWait, FloodPremiumWait) as f:
                await sleep(f.value)
                await message.edit(
                    text=messages.get(
                        file="unzip_help",
                        key="PROGRESS_MSG",
                        user_id=uid,
                        extra_args=[ud_type, tmp],
                    ),
                    reply_markup=Buttons.I_PREFER_STOP,
                )
            except:
                pass
        elif round(number=diff % 10.00) == 0 or current == total:
            percentage = current * 100 / total
            speed = current / diff
            estimated_total_time = round(number=(total - current) / speed) * 1000
            estimated_total_time = TimeFormatter(milliseconds=estimated_total_time)
            filled = "".join(["⬢" for _ in range(math.floor(percentage / 5))])
            empty = "".join(["⬡" for _ in range(20 - math.floor(percentage / 5))])
            progress = f"[{filled}{empty}] \n"
            progress += (
                f"{messages.get(file='unzip_help', key='PROCESSING', user_id=uid)} : "
                f"`{round(number=percentage, ndigits=2)}%`\n"
            )
            eta = (
                estimated_total_time if estimated_total_time != "" or percentage != "100" else "0 s"
            )
            tmp = (
                progress
                + f"`{humanbytes(current)} of {humanbytes(total)}`\n"
                + f"{messages.get(file='unzip_help', key='SPEED', user_id=uid)} "
                + f"`{humanbytes(speed)}/s`\n"
                + f"{messages.get(file='unzip_help', key='ETA', user_id=uid)} "
                + f"`{eta}`\n"
            )

            try:
                await message.edit(
                    text=messages.get(
                        file="unzip_help",
                        key="PROGRESS_MSG",
                        user_id=uid,
                        extra_args=[ud_type, tmp],
                    ),
                    reply_markup=Buttons.I_PREFER_STOP,
                )
            except (FloodWait, FloodPremiumWait) as f:
                await sleep(f.value)
                await message.edit(
                    text=messages.get(
                        file="unzip_help",
                        key="PROGRESS_MSG",
                        user_id=uid,
                        extra_args=[ud_type, tmp],
                    ),
                    reply_markup=Buttons.I_PREFER_STOP,
                )
            except:
                pass


# TODO
async def progress_urls(current, total, ud_type, message, start):
    now = time.time()
    diff = now - start
    uid = message.chat.id

    if round(number=diff % 10.00) == 0 or current == total:
        percentage = current * 100 / total
        speed = current / diff
        estimated_total_time = round(number=(total - current) / speed) * 1000
        estimated_total_time = TimeFormatter(milliseconds=estimated_total_time)
        filled = "".join(["⬢" for _ in range(math.floor(percentage / 5))])
        empty = "".join(["⬡" for _ in range(20 - math.floor(percentage / 5))])
        progress = f"[{filled}{empty}] \n"
        progress += (
            f"{messages.get(file='unzip_help', key='PROCESSING', user_id=uid)} : "
            f"`{round(number=percentage, ndigits=2)}%`\n"
        )
        eta = estimated_total_time if estimated_total_time != "" or percentage != "100" else "0 s"
        tmp = (
            progress
            + f"`{humanbytes(current)} of {humanbytes(total)}`\n"
            + f"{messages.get(file='unzip_help', key='SPEED', user_id=uid)} "
            + f"`{humanbytes(speed)}/s`\n"
            + f"{messages.get(file='unzip_help', key='ETA', user_id=uid)} "
            + f"`{eta}`\n"
        )

        try:
            await message.edit(
                messages.get(
                    file="unzip_help", key="PROGRESS_MSG", user_id=uid, extra_args=[ud_type, tmp]
                )
            )
        except (FloodWait, FloodPremiumWait) as f:
            await sleep(f.value)
            await message.edit(
                messages.get(
                    file="unzip_help", key="PROGRESS_MSG", user_id=uid, extra_args=[ud_type, tmp]
                )
            )
        except:
            pass


# TODO
def humanbytes(size):
    if not size:
        return ""

    power = 2**10
    n = 0
    Dic_powerN = {0: " ", 1: "Ki", 2: "Mi", 3: "Gi", 4: "Ti"}

    while size > power:
        size /= power
        n += 1

    return str(round(number=size, ndigits=2)) + " " + Dic_powerN.get(n) + "B"


# TODO
def TimeFormatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = (
        ((str(days) + "d, ") if days else "")
        + ((str(hours) + "h, ") if hours else "")
        + ((str(minutes) + "m, ") if minutes else "")
        + ((str(seconds) + "s, ") if seconds else "")
        + ((str(milliseconds) + "ms, ") if milliseconds else "")
    )

    return tmp[:-2]


# TODO
def timeformat_sec(seconds: int) -> str:
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = (
        ((str(days) + "d, ") if days else "")
        + ((str(hours) + "h, ") if hours else "")
        + ((str(minutes) + "m, ") if minutes else "")
        + ((str(seconds) + "s, ") if seconds else "")
    )

    return tmp[:-2]


def calculate_memory_limit():
    if Config.MAX_RAM_AMOUNT_KB != -1:
        return int(Config.MAX_RAM_AMOUNT_KB * Config.MAX_RAM_USAGE / 100)

    # we may need to use virtual_memory().available instead of total
    total_memory = psutil.virtual_memory().total
    memory_limit_kb = int(total_memory * Config.MAX_RAM_USAGE / 100 / 1024)

    return memory_limit_kb


# List of error messages from 7zip
ERROR_MSGS = ["Error", "Can't open as archive"]

# List of common extentions
extentions_list = {
    "archive": [
        "7z",
        "apk",
        "apkm",
        "apks",
        "appx",
        "arc",
        "bcm",
        "bin",
        "br",
        "bz2",
        "dmg",
        "exe",
        "gz",
        "img",
        "ipsw",
        "iso",
        "jar",
        "lz4",
        "msi",
        "paf",
        "pak",
        "pea",
        "pkg",
        "rar",
        "tar",
        "tgz",
        "wim",
        "x7",
        "xapk",
        "xz",
        "z",
        "zip",
        "zipx",
        "zpaq",
        "zst",
        "zstd",
    ],
    "audio": ["aac", "aif", "aiff", "alac", "flac", "m4a", "mp3", "ogg", "wav", "wma"],
    "photo": ["gif", "jpg", "jpeg", "png", "tiff", "webp"],
    "split": ["0*", "001", "002", "003", "004", "005", "006", "007", "008", "009"],
    "video": ["3gp", "avi", "flv", "mp4", "mkv", "mov", "mpeg", "mpg", "webm"],
}

tarball_extensions = (
    ".tar.gz",
    ".gz",
    ".tgz",
    ".taz",
    ".tar.bz2",
    ".bz2",
    ".tb2",
    ".tbz",
    ".tbz2",
    ".tz2",
    ".tar.lz",
    ".lz",
    ".tar.lzma",
    ".lzma",
    ".tlz",
    ".tar.lzo",
    ".lzo",
    ".tar.xz",
    ".xz",
    ".txz",
    ".tar.z",
    ".z",
    ".tz",
    ".taz",
)
