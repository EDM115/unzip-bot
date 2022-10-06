# Copyright (c) 2022 EDM115
import math
import time
from typing import List, Union

from pyrogram import Client


# Credits: SpEcHiDe's AnyDL-Bot for Progress bar + Time formatter
async def progress_for_pyrogram(current, total, ud_type, message, start,
                                client, status):
    if not status:
        now = time.time()
        diff = now - start
        if round(diff % 10.00) == 0 or current == total:
            timenow = round(time.time() - start) * 1000
            percentage = current * 100 / total
            speed = current / diff
            elapsed_time = round(diff) * 1000
            time_to_completion = round((total - current) / speed) * 1000
            estimated_total_time = elapsed_time + time_to_completion
            elapsed_time = TimeFormatter(milliseconds=elapsed_time)
            """
            if ((int(estimated_total_time) > int(elapsed_time)) and (int(timenow) > int(elapsed_time))) or ((int(estimated_total_time) > int(elapsed_time)) and (int(percentage) > 50)):
                estimated_total_time -= elapsed_time / 10
            """
            estimated_total_time = TimeFormatter(
                milliseconds=estimated_total_time)
            progress = "[{0}{1}] \n**Processing…** : `{2}%`\n".format(
                "".join(["⬢" for i in range(math.floor(percentage / 5))]),
                "".join(["⬡" for i in range(20 - math.floor(percentage / 5))]),
                round(percentage, 2),
            )

            tmp = (
                progress +
                "`{0} of {1}`\n**Speed :** `{2}/s`\n**ETA :** `{3}`\n".format(
                    humanbytes(current),
                    humanbytes(total),
                    humanbytes(speed),
                    estimated_total_time if estimated_total_time != ""
                    or percentage != "100" else "0 s",
                ))
            try:
                await message.edit(
                    text="{}\n {} \n\n**Powered by @EDM115bots**".format(
                        ud_type, tmp))
            except:
                pass
        else:
            return await client.stop_transmission()


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
    tmp = (((str(days) + "d, ") if days else "") +
           ((str(hours) + "h, ") if hours else "") +
           ((str(minutes) + "m, ") if minutes else "") +
           ((str(seconds) + "s, ") if seconds else "") +
           ((str(milliseconds) + "ms, ") if milliseconds else ""))
    return tmp[:-2]


def timeformat_sec(seconds: int) -> str:
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = (((str(days) + "d, ") if days else "") +
           ((str(hours) + "h, ") if hours else "") +
           ((str(minutes) + "m, ") if minutes else "") +
           ((str(seconds) + "s, ") if seconds else ""))
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
        "iso",
        "jar",
        "lz4",
        "msi",
        "paf",
        "pak",
        "pea",
        "rar",
        "tar",
        "wim",
        "xapk",
        "xz",
        "z",
        "zip",
        "zpaq",
        "zstd",
    ],
    "audio": ["aif", "aiff", "aac", "flac", "mp3", "ogg", "wav", "wma"],
    "photo": ["gif", "ico", "jpg", "jpeg", "png", "tiff", "webp"],
    "split": ["0*", "001", "002", "003", "004", "005"],
    "video": ["3gp", "avi", "flv", "mp4", "mkv", "mov", "mpeg", "mpg", "webm"],
}
