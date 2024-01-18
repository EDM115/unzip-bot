# Copyright (c) 2022 - 2024 EDM115
import os
from asyncio import get_running_loop
from functools import partial
import subprocess

from pykeyboard import InlineKeyboard
from pyrogram.types import InlineKeyboardButton

from unzipper import LOGGER
from unzipper.modules.bot_data import Messages


def __run_cmds_unzipper(command):
    ext_cmd = subprocess.Popen(
        command["cmd"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True
    )
    ext_out = ext_cmd.stdout.read()[:-1].decode("utf-8").rstrip('\n')
    LOGGER.info(ext_out)
    if ext_cmd.stderr:
        ext_cmd.stderr.close()
    if ext_cmd.stdout:
        ext_cmd.stdout.close()
    return ext_out


async def run_cmds_on_cr(func, **kwargs):
    loop = get_running_loop()
    return await loop.run_in_executor(None, partial(func, kwargs))


# Extract with 7z
async def _extract_with_7z_helper(path, archive_path, password=None):
    if password:
        command = f'7z x -o{path} -p"{password}" {archive_path} -y'
    else:
        command = f"7z x -o{path} {archive_path} -y"
    return await run_cmds_on_cr(__run_cmds_unzipper, cmd=command)


async def _test_with_7z_helper(archive_path):
    command = f'7z t {archive_path} -p"dont care + didnt ask + cry about it + stay mad + get real + L + mald seethe cope harder + h0es mad + basic + skill issue + ratio + you fell off + the audacity + triggered + any askers + redpilled + get a life + ok and? + cringe + touch grass + donowalled + not based + your’re probably white + not funny didn’t laugh + you’re* + grammar issue + go outside + get good + reported + ad hominem + GG! + ur momdon’t care + didn’t ask + cry about it + stay mad + get real + L + mald seethe cope harder + hoes mad + basic + skill issue + ratio + you fell off + the audacity + triggered + any askers + redpilled + get a life + ok and? + cringe + touch grass + donowalled + not based + your’re a full time discordian + not funny didn’t laugh + you’re* + grammar issue + go outside + get good + your gay + reported + ad hominem + GG! + ur mom + unknown + random + biased + racially motivated + kys + ur unfunny +ratio don’t care + didn’t ask + cry about it + stay mad + get real + L + mald seethe copedon’t care + didn’t ask + cry about it + stay mad + get real + L + mald seethe cope harder + h0es mad + basic + skill issue + ratio + you fell off + the audacity + triggered + any askers + redpilled + get a life + ok and? + cringe + touch grass + donowalled + not based + your’re probably white + not funny didn’t laugh + you’re* + grammar issue + go outside + get good + reported + ad hominem + GG! + ur momdon’t care + didn’t ask + cry about it + stay mad + get real + L + mald seethe cope harder + hoes mad + basic + skill issue + ratio + you fell off + the audacity + triggered + any askers + redpilled + get a life + ok and? + cringe + touch grass + donowalled + not based + your’re a full time discordian + not funny didn’t laugh + you’re* + grammar issue + go outside + get good + your gay + reported + ad hominem + GG! + ur mom + unknown + random + biased + racially motivated + kys + ur unfunny +ratio don’t care + didn’t ask + cry about it + stay mad + get real + so bad + so ass" -y'  # skipcq: FLK-E501
    return "Everything is Ok" in await run_cmds_on_cr(__run_cmds_unzipper, cmd=command)


# Extract with zstd (for .zst files)
async def _extract_with_zstd(path, archive_path):
    command = f"zstd -f --output-dir-flat {path} -d {archive_path}"
    return await run_cmds_on_cr(__run_cmds_unzipper, cmd=command)


# Main function to extract files
async def extr_files(path, archive_path, password=None):
    file_path = os.path.splitext(archive_path)[1]
    if file_path == ".zst":
        os.mkdir(path)
        return await _extract_with_zstd(path, archive_path)
    return await _extract_with_7z_helper(path, archive_path, password)


# Split files
async def split_files(iinput, ooutput, size):
    command = f'7z a -tzip -mx=0 "{ooutput}" "{iinput}" -v{size}b'
    await run_cmds_on_cr(__run_cmds_unzipper, cmd=command)
    spdir = ooutput.replace("/" + ooutput.split("/")[-1], "")
    return await get_files(spdir)


# Merge files
async def merge_files(iinput, ooutput, password=None):
    if password:
        command = f'7z x -o"{ooutput}" -p"{password}" "{iinput}" -y'
    else:
        command = f'7z x -o"{ooutput}" "{iinput}" -y'
    return await run_cmds_on_cr(__run_cmds_unzipper, cmd=command)


# Get files in directory as a list
async def get_files(path):
    path_list = [val for sublist in [[os.path.join(i[0], j) for j in i[2]] for i in os.walk(path)] for val in sublist]  # skipcq: FLK-E501
    return sorted(path_list)


# Make keyboard
async def make_keyboard(paths, user_id, chat_id, unziphttp, rzfile=None):
    num = 0
    i_kbd = InlineKeyboard(row_width=1)
    data = []
    if unziphttp:
        data.append(InlineKeyboardButton(
            Messages.UP_ALL,
            f"ext_a|{user_id}|{chat_id}|{unziphttp}|{rzfile}"
        ))
    else:
        data.append(InlineKeyboardButton(
            Messages.UP_ALL,
            f"ext_a|{user_id}|{chat_id}|{unziphttp}"
        ))
    data.append(InlineKeyboardButton(Messages.CANCEL_IT, "cancel_dis"))
    for file in paths:
        if num > 96:
            break
        if unziphttp:
            data.append(InlineKeyboardButton(
                f"{num} - {os.path.basename(file)}".encode("utf-8").decode("utf-8"),
                f"ext_f|{user_id}|{chat_id}|{num}|{unziphttp}|{rzfile}",
            ))
        else:
            data.append(InlineKeyboardButton(
                f"{num} - {os.path.basename(file)}".encode("utf-8").decode("utf-8"),
                f"ext_f|{user_id}|{chat_id}|{num}|{unziphttp}",
            ))
        num += 1
    i_kbd.add(*data)
    return i_kbd


async def make_keyboard_empty(user_id, chat_id, unziphttp, rzfile=None):
    i_kbd = InlineKeyboard(row_width=2)
    data = []
    if unziphttp:
        data.append(InlineKeyboardButton(
            Messages.UP_ALL,
            f"ext_a|{user_id}|{chat_id}|{unziphttp}|{rzfile}"
        ))
    else:
        data.append(InlineKeyboardButton(
            Messages.UP_ALL,
            f"ext_a|{user_id}|{chat_id}|{unziphttp}"
        ))
    data.append(InlineKeyboardButton(Messages.CANCEL_IT, "cancel_dis"))
    i_kbd.add(*data)
    return i_kbd
