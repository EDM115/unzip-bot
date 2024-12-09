import math
import psutil
import time
from asyncio import sleep

from pyrogram import enums
from pyrogram.errors import FloodWait

from config import Config
from unzipbot.helpers.database import del_cancel_task, get_cancel_task, get_lang
from unzipbot.i18n.buttons import Buttons
from unzipbot.i18n.messages import Messages


messages = Messages(lang_fetcher=get_lang)


async def progress_for_pyrogram(current, total, ud_type, message, start, unzip_bot):
    if not message:
        return

    uid = message.chat.id

    if message.chat.type == enums.ChatType.PRIVATE and await get_cancel_task(uid):
        await del_cancel_task(uid)
        await message.edit(text=messages.get("unzip_help", "DL_STOPPED", uid))
        unzip_bot.stop_transmission()
    else:
        now = time.time()
        diff = now - start

        if total == 0:
            tmp = messages.get("unzip_help", "UNKNOWN_SIZE", uid)

            try:
                await message.edit(
                    text=messages.get("unzip_help", "PROGRESS_MSG", uid, ud_type, tmp),
                    reply_markup=Buttons.I_PREFER_STOP,
                )
            except FloodWait as f:
                await sleep(f.value)
                await message.edit(
                    text=messages.get("unzip_help", "PROGRESS_MSG", uid, ud_type, tmp),
                    reply_markup=Buttons.I_PREFER_STOP,
                )
            except:
                pass
        elif round(diff % 10.00) == 0 or current == total:
            percentage = current * 100 / total
            speed = current / diff
            time_to_completion = round((total - current) / speed) * 1000
            estimated_total_time = time_to_completion
            estimated_total_time = TimeFormatter(milliseconds=estimated_total_time)
            progress = f'[{"".join(["⬢" for i in range(math.floor(percentage / 5))])}{"".join(["⬡" for i in range(20 - math.floor(percentage / 5))])}] \n{messages.get("unzip_help", "PROCESSING", uid)} : `{round(percentage, 2)}%`\n'
            tmp = (
                progress
                + f'`{humanbytes(current)} of {humanbytes(total)}`\n{messages.get("unzip_help", "SPEED", uid)} `{humanbytes(speed)}/s`\n{messages.get("unzip_help", "ETA", uid)} `{estimated_total_time if estimated_total_time != "" or percentage != "100" else "0 s"}`\n'
            )

            try:
                await message.edit(
                    text=messages.get("unzip_help", "PROGRESS_MSG", uid, ud_type, tmp),
                    reply_markup=Buttons.I_PREFER_STOP,
                )
            except FloodWait as f:
                await sleep(f.value)
                await message.edit(
                    text=messages.get("unzip_help", "PROGRESS_MSG", uid, ud_type, tmp),
                    reply_markup=Buttons.I_PREFER_STOP,
                )
            except:
                pass


async def progress_urls(current, total, ud_type, message, start):
    now = time.time()
    diff = now - start
    uid = message.chat.id

    if round(diff % 10.00) == 0 or current == total:
        percentage = current * 100 / total
        speed = current / diff
        time_to_completion = round((total - current) / speed) * 1000
        estimated_total_time = time_to_completion
        estimated_total_time = TimeFormatter(milliseconds=estimated_total_time)
        progress = f'[{"".join(["⬢" for i in range(math.floor(percentage / 5))])}{"".join(["⬡" for i in range(20 - math.floor(percentage / 5))])}] \n{messages.get("unzip_help", "PROCESSING", uid)} : `{round(percentage, 2)}%`\n'
        tmp = (
            progress
            + f'{messages.get("unzip_help", "ETA", uid)} `{estimated_total_time if estimated_total_time != "" or percentage != "100" else "0 s"}`\n'
        )

        try:
            await message.edit(
                messages.get("unzip_help", "PROGRESS_MSG", uid, ud_type, tmp)
            )
        except FloodWait as f:
            await sleep(f.value)
            await message.edit(
                messages.get("unzip_help", "PROGRESS_MSG", uid, ud_type, tmp)
            )
        except:
            pass


def humanbytes(size):
    if not size:
        return ""

    power = 2**10
    n = 0
    Dic_powerN = {0: " ", 1: "Ki", 2: "Mi", 3: "Gi", 4: "Ti"}

    while size > power:
        size /= power
        n += 1

    return str(round(size, 2)) + " " + Dic_powerN.get(n) + "B"


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
