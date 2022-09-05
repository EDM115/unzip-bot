# Copyright (c) 2022 EDM115

import math
import time
from typing import List, Union

from pyrogram import enums
from unzipper import unzipperbot as client, LOGGER
from config import Config

# Credits: SpEcHiDe's AnyDL-Bot for Progress bar + Time formatter


async def progress_for_pyrogram(current, total, ud_type, message, start):
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
        # if ((int(estimated_total_time) > int(elapsed_time)) and (int(timenow) > int(elapsed_time))) or ((int(estimated_total_time) > int(elapsed_time)) and (int(percentage) > 50)):
        #    estimated_total_time -= elapsed_time / 10
        estimated_total_time = TimeFormatter(milliseconds=estimated_total_time)
        progress = "[{0}{1}] \n**Processing…** : `{2}%`\n".format(
            "".join(["⬢" for i in range(math.floor(percentage / 5))]),
            "".join(["⬡" for i in range(20 - math.floor(percentage / 5))]),
            round(percentage, 2),
        )

        tmp = progress + "`{0} of {1}`\n**Speed :** `{2}/s`\n**ETA :** `{3}`\n".format(
            humanbytes(current),
            humanbytes(total),
            humanbytes(speed),
            estimated_total_time
            if estimated_total_time != "" or percentage != "100"
            else "0 s",
        )
        try:
            await message.edit(
                text="{}\n {} \n\n**Powered by @EDM115bots**".format(ud_type, tmp)
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


class HumanBytes:
    METRIC_LABELS: List[str] = ["B", "kB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]
    BINARY_LABELS: List[str] = [
        "B",
        "KiB",
        "MiB",
        "GiB",
        "TiB",
        "PiB",
        "EiB",
        "ZiB",
        "YiB",
    ]
    # PREDEFINED FOR SPEED.
    PRECISION_OFFSETS: List[float] = [0.5, 0.05, 0.005, 0.0005]
    PRECISION_FORMATS: List[str] = [
        "{}{:.0f} {}",
        "{}{:.1f} {}",
        "{}{:.2f} {}",
        "{}{:.3f} {}",
    ]  # PREDEFINED FOR SPEED.

    @staticmethod
    def format(num: Union[int, float], metric: bool = False, precision: int = 1) -> str:
        # Human-readable formatting of bytes, using binary (powers of 1024)
        # or metric (powers of 1000) representation.
        assert isinstance(num, (int, float)), "num must be an int or float"
        assert isinstance(metric, bool), "metric must be a bool"
        assert (
            isinstance(precision, int) and precision >= 0 and precision <= 3
        ), "precision must be an int (range 0-3)"
        unit_labels = HumanBytes.METRIC_LABELS if metric else HumanBytes.BINARY_LABELS
        last_label = unit_labels[-1]
        unit_step = 1000 if metric else 1024
        unit_step_thresh = unit_step - HumanBytes.PRECISION_OFFSETS[precision]
        is_negative = num < 0
        if is_negative:  # Faster than ternary assignment or always running abs().
            num = abs(num)
        for unit in unit_labels:
            if num < unit_step_thresh:
                # VERY IMPORTANT:
                # Only accepts the CURRENT unit if we're BELOW the threshold where
                # float rounding behavior would place us into the NEXT unit: F.ex.
                # when rounding a float to 1 decimal, any number ">= 1023.95" will
                # be rounded to "1024.0". Obviously we don't want ugly output such
                # as "1024.0 KiB", since the proper term for that is "1.0 MiB".
                break
            if unit != last_label:
                # We only shrink the number if we HAVEN'T reached the last unit.
                # NOTE: These looped divisions accumulate floating point rounding
                # errors, but each new division pushes the rounding errors further
                # and further down in the decimals, so it doesn't matter at all.
                num /= unit_step
        return HumanBytes.PRECISION_FORMATS[precision].format(
            "-" if is_negative else "", num, unit
        )


# Usage : HumanBytes.format({value}))


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


# Checking log channel
def check_logs():
    try:
        if Config.LOGS_CHANNEL:
            c_info = client.get_chat(chat_id=Config.LOGS_CHANNEL)
            if (
                c_info.type == enums.ChatType.PRIVATE
                or c_info.type == enums.ChatType.BOT
            ):
                LOGGER.warn("A private chat can't be used 😐")
                return False
            else:
                return True
        else:
            LOGGER.warn("No Log channel ID is given !")
            exit()
    except:
        print(
            "Error happened while checking Log channel 💀 Make sure you're not dumb enough to provide a wrong Log channel ID 🧐"
        )


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
