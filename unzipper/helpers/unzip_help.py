# Copyright (c) 2022 EDM115

import math
import time
from typing import List, Union

from unzipper import unzipperbot as client
from config import Config

# Credits: SpEcHiDe's AnyDL-Bot for Progress bar + Time formatter
async def progress_for_pyrogram(current, total, ud_type, message, start):
    now = time.time()
    diff = now - start
    if round(diff % 10.00) == 0 or current == total:
        percentage = current * 100 / total
        speed = current / diff
        elapsed_time = round(diff) * 1000
        time_to_completion = round((total - current) / speed) * 1000
        estimated_total_time = elapsed_time + time_to_completion
        elapsed_time = TimeFormatter(milliseconds=elapsed_time)
        estimated_total_time = TimeFormatter(milliseconds=estimated_total_time)
        progress = "[{0}{1}] \n**Processing…** : `{2}%`\n".format(
            ''.join(["⬢" for i in range(math.floor(percentage / 5))]),
            ''.join(["⬡" for i in range(20 - math.floor(percentage / 5))]),
            round(percentage, 2))

        tmp = progress + "`{0} of {1}`\n**Speed :** `{2}/s`\n**ETA :** `{3}`\n".format(
            humanbytes(current),
            humanbytes(total),
            humanbytes(speed),
            estimated_total_time if estimated_total_time != '' else "0 s"
        )
        try:
            await message.edit(text="{}\n {} \n\n**Powered by @EDM115bots**".format(ud_type,tmp))
        except:
            pass

# Workaround :
"""
def exponential_moving_average(data, samples=0, smoothing=0.02):
    '''
    data: an array of all values.
    samples: how many previous data samples are avraged. Set to 0 to average all data points.
    smoothing: a value between 0-1, 1 being a linear average (no falloff).
    '''

    if len(data) == 1:
        return data[0]

    if samples == 0 or samples > len(data):
        samples = len(data)

    average = sum(data[-samples:]) / samples
    last_speed = data[-1]
    return (smoothing * last_speed) + ((1 - smoothing) * average)

input_data = [4.5, 8.21, 8.7, 5.8, 3.8, 2.7, 2.5, 7.1, 9.3, 2.1, 3.1, 9.7, 5.1, 6.1, 9.1, 5.0, 1.6, 6.7, 5.5, 3.2] # this would be a constant stream of download speeds as you go, pre-defined here for illustration

data = []
ema_data = []

for sample in input_data:
    data.append(sample)
    average_value = exponential_moving_average(data)
    ema_data.append(average_value)

# print it out for visualization
for i in range(len(data)):
    print("REAL: ", data[i])
    print("EMA:  ", ema_data[i])
    print("--")
"""

"""
averageSpeed = SMOOTHING_FACTOR * lastSpeed + (1-SMOOTHING_FACTOR) * averageSpeed;

SMOOTHING_FACTOR is a number between 0 and 1. The higher this number, the faster older samples are discarded. As you can see in the formula, when SMOOTHING_FACTOR is 1 you are simply using the value of your last observation. When SMOOTHING_FACTOR is 0 averageSpeed never changes. So, you want something in between, and usually a low value to get decent smoothing. I've found that 0.005 provides a pretty good smoothing value for an average download speed.
lastSpeed is the last measured download speed. You can get this value by running a timer every second or so to calculate how many bytes have downloaded since the last time you ran it.
averageSpeed is, obviously, the number that you want to use to calculate your estimated time remaining. Initialize this to the first lastSpeed measurement you get.
"""

def humanbytes(size):
    if not size:
        return ""
    power = 2**10
    n = 0
    Dic_powerN = {0: ' ', 1: 'Ki', 2: 'Mi', 3: 'Gi', 4: 'Ti'}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN[n] + 'B'

# Workaround
class HumanBytes:
    METRIC_LABELS: List[str] = ["B", "kB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]
    BINARY_LABELS: List[str] = ["B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB"]
    PRECISION_OFFSETS: List[float] = [0.5, 0.05, 0.005, 0.0005] # PREDEFINED FOR SPEED.
    PRECISION_FORMATS: List[str] = ["{}{:.0f} {}", "{}{:.1f} {}", "{}{:.2f} {}", "{}{:.3f} {}"] # PREDEFINED FOR SPEED.
    @staticmethod
    def format(num: Union[int, float], metric: bool=False, precision: int=1) -> str:
        # Human-readable formatting of bytes, using binary (powers of 1024)
        # or metric (powers of 1000) representation.
        assert isinstance(num, (int, float)), "num must be an int or float"
        assert isinstance(metric, bool), "metric must be a bool"
        assert isinstance(precision, int) and precision >= 0 and precision <= 3, "precision must be an int (range 0-3)"
        unit_labels = HumanBytes.METRIC_LABELS if metric else HumanBytes.BINARY_LABELS
        last_label = unit_labels[-1]
        unit_step = 1000 if metric else 1024
        unit_step_thresh = unit_step - HumanBytes.PRECISION_OFFSETS[precision]
        is_negative = num < 0
        if is_negative: # Faster than ternary assignment or always running abs().
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
        return HumanBytes.PRECISION_FORMATS[precision].format("-" if is_negative else "", num, unit)
# Usage : HumanBytes.format({value}))

def TimeFormatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + "d, ") if days else "") + \
        ((str(hours) + "h, ") if hours else "") + \
        ((str(minutes) + "m, ") if minutes else "") + \
        ((str(seconds) + "s, ") if seconds else "") + \
        ((str(milliseconds) + "ms, ") if milliseconds else "")
    return tmp[:-2]

def timeformat_sec(seconds: int) -> str:
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + "d, ") if days else "") + \
        ((str(hours) + "h, ") if hours else "") + \
        ((str(minutes) + "m, ") if minutes else "") + \
        ((str(seconds) + "s, ") if seconds else "")
    return tmp[:-2]

# Checking log channel
def check_logs():
    try:
        if Config.LOGS_CHANNEL:
            c_info = client.get_chat(chat_id=Config.LOGS_CHANNEL)
            if c_info.type != "channel":
                print("A chat is **not** a channel 😐")
                return
            elif c_info.username is not None:
                print("A chat is **not** private 😐")
                return
            else:
                client.send_message(chat_id=Config.LOGS_CHANNEL, text=f"`unzip-bot has successfully started !` \n\n**Powered by @EDM115bots ❤️**")
        else:
            print("No Log channel ID is given !")
            exit()
    except:
        print("Error happened while checking Log channel 💀 Make sure you're not dumb enough to provide a wrong Log channel ID 🧐")
