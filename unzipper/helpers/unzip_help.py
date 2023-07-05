# Copyright (c) 2023 EDM115
import math
import time

from asyncio import sleep
from pyrogram.errors import FloodWait
from unzipper.helpers.database import del_cancel_task, get_cancel_task
from unzipper.modules.bot_data import Buttons, Messages


async def progress_for_pyrogram(current, total, ud_type, message, start, unzip_bot):
    if message.from_user is not None and await get_cancel_task(message.from_user.id):
        unzip_bot.stop_transmission()
        await message.edit(text=Messages.DL_STOPPED)
        await del_cancel_task(message.from_user.id)
    else:
        now = time.time()
        diff = now - start
        if total == 0:
            tmp = Messages.UNKNOWN_SIZE
            try:
                await message.edit(
                    text=Messages.PROGRESS_MSG.format(ud_type, tmp),
                    reply_markup=Buttons.I_PREFER_STOP,
                )
            except FloodWait as f:
                await sleep(f.value)
                await message.edit(
                    text=Messages.PROGRESS_MSG.format(ud_type, tmp),
                    reply_markup=Buttons.I_PREFER_STOP,
                )
            except:
                pass
        elif round(diff % 10.00) == 0 or current == total:
            percentage = current * 100 / total
            speed = current / diff
            elapsed_time = round(diff) * 1000
            time_to_completion = round((total - current) / speed) * 1000
            estimated_total_time = time_to_completion
            elapsed_time = TimeFormatter(milliseconds=elapsed_time)
            estimated_total_time = TimeFormatter(milliseconds=estimated_total_time)
            progress = f'[{"".join(["⬢" for i in range(math.floor(percentage / 5))])}{"".join(["⬡" for i in range(20 - math.floor(percentage / 5))])}] \n{Messages.PROCESSING} : `{round(percentage, 2)}%`\n'
            tmp = progress + f'`{humanbytes(current)} of {humanbytes(total)}`\n{Messages.SPEED} `{humanbytes(speed)}/s`\n{Messages.ETA} `{estimated_total_time if estimated_total_time != "" or percentage != "100" else "0 s"}`\n'
            try:
                await message.edit(
                    text=Messages.PROGRESS_MSG.format(ud_type, tmp),
                    reply_markup=Buttons.I_PREFER_STOP,
                )
            except FloodWait as f:
                await sleep(f.value)
                await message.edit(
                    text=Messages.PROGRESS_MSG.format(ud_type, tmp),
                    reply_markup=Buttons.I_PREFER_STOP,
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
    return str(round(size, 2)) + " " + Dic_powerN[n] + "B"


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
    "audio": ["aif", "aiff", "aac", "flac", "mp3", "ogg", "wav", "wma"],
    "photo": ["gif", "ico", "jpg", "jpeg", "png", "tiff", "webp"],
    "split": ["0*", "001", "002", "003", "004", "005", "006", "007", "008", "009"],
    "video": ["3gp", "avi", "flv", "mp4", "mkv", "mov", "mpeg", "mpg", "webm"],
}
