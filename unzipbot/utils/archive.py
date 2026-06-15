import os
import shutil
from asyncio import create_subprocess_shell, subprocess
from shlex import quote

from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from unzipbot import LOGGER
from unzipbot.config.config import Config
from unzipbot.db.functions import get_lang
from unzipbot.helpers.unzip_help import calculate_memory_limit, tarball_extensions
from unzipbot.i18n.messages import Messages

messages = Messages(lang_fetcher=get_lang)


# Get files in directory as a list
async def get_files(path):
    path_list = [
        val
        for sublist in [[os.path.join(i[0], j) for j in i[2]] for i in os.walk(top=path)]
        for val in sublist
    ]

    return sorted(path_list)


async def cleanup_macos_artifacts(extraction_path):
    for root, dirs, files in os.walk(top=extraction_path):
        for name in files:
            if name == ".DS_Store":
                os.remove(path=os.path.join(root, name))
        for name in dirs:
            if name == "__MACOSX":
                shutil.rmtree(os.path.join(root, name))


# TODO
async def run_shell_cmds(command):
    memlimit = calculate_memory_limit()
    cpulimit = Config.MAX_CPU_CORES_COUNT * Config.MAX_CPU_USAGE
    ulimit_cmd = [
        "ulimit",
        "-v",
        str(memlimit),
        "&&",
        "cpulimit",
        "-l",
        str(cpulimit),
        "--",
        command,
    ]
    ulimit_command = " ".join(ulimit_cmd)
    process = await create_subprocess_shell(
        cmd=ulimit_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, executable="/bin/bash"
    )
    stdout, stderr = await process.communicate()

    e = stderr.decode(encoding="utf-8", errors="replace")
    o = stdout.decode(encoding="utf-8", errors="replace")
    LOGGER.info(msg=f"command : {command}")
    LOGGER.info(msg=f"stdout : {o}")
    LOGGER.info(msg=f"stderr : {e}")

    return o + "\n" + e


# TODO
# Extract with 7z
async def __extract_with_7z_helper(path, archive_path, password=None):
    LOGGER.info(msg="7z : " + archive_path + " : " + path)

    if password:
        cmd = ["7z", "x", f"-o{quote(path)}", f"-p{quote(password)}", quote(archive_path), "-y"]
    else:
        cmd = ["7z", "x", f"-o{quote(path)}", quote(archive_path), "-y"]

    result = await run_shell_cmds(" ".join(cmd))

    return result


# TODO
async def test_with_7z_helper(archive_path):
    # skipcq: PTC-W1006, SCT-A000
    password = "dont care + didnt ask + cry about it + stay mad + get real + L"
    cmd = ["7z", "t", f"-p{quote(password)}", quote(archive_path), "-y"]
    result = await run_shell_cmds(" ".join(cmd))

    return "Everything is Ok" in result


# TODO
async def __extract_with_unrar_helper(path, archive_path, password=None):
    LOGGER.info(msg="unrar : " + archive_path + " : " + path)

    if password:
        cmd = ["unrar", "x", quote(archive_path), quote(path), f"-p{quote(password)}", "-y"]
    else:
        cmd = ["unrar", "x", quote(archive_path), quote(path), "-y"]

    result = await run_shell_cmds(" ".join(cmd))

    return result


# TODO
async def test_with_unrar_helper(archive_path):
    # skipcq: PTC-W1006, SCT-A000
    password = "dont care + didnt ask + cry about it + stay mad + get real + L"
    cmd = ["unrar", "t", quote(archive_path), f"-p{quote(password)}", "-y"]
    result = await run_shell_cmds(" ".join(cmd))

    return "All OK" in result


# TODO
# Extract with zstd (for .tar.zst files)
async def __extract_with_zstd(path, archive_path):
    cmd = ["zstd", "-f", "--output-dir-flat", quote(path), "-d", quote(archive_path)]
    result = await run_shell_cmds(" ".join(cmd))

    return result


# TODO
# Main function to extract files
async def extr_files(path, archive_path, password=None):
    os.makedirs(name=path, exist_ok=True)

    if archive_path.endswith(tarball_extensions):
        LOGGER.info(msg="tar")
        temp_path = path.rsplit("/", 1)[0] + "/tar_temp"
        os.makedirs(name=temp_path, exist_ok=True)
        result = await __extract_with_7z_helper(path=temp_path, archive_path=archive_path)
        filename = await get_files(temp_path)
        filename = filename[0]
        cmd = ["tar", "-xvf", quote(filename), "-C", quote(path)]
        result2 = await run_shell_cmds(" ".join(cmd))
        result += result2
        shutil.rmtree(temp_path)
    elif archive_path.endswith((".tar.zst", ".zst", ".tzst")):
        LOGGER.info(msg="zstd")
        os.mkdir(path=path)
        result = await __extract_with_zstd(path=path, archive_path=archive_path)
    elif archive_path.endswith(".rar"):
        LOGGER.info(msg="rar")

        if password:
            result = await __extract_with_unrar_helper(
                path=path, archive_path=archive_path, password=password
            )
        else:
            result = await __extract_with_unrar_helper(path=path, archive_path=archive_path)
    else:
        LOGGER.info(msg="normal archive")
        result = await __extract_with_7z_helper(
            path=path, archive_path=archive_path, password=password
        )

    LOGGER.info(msg=await get_files(path))
    await cleanup_macos_artifacts(path)

    return result


# TODO
# Split files
async def split_files(iinput, ooutput, size):
    temp_location = iinput + "_temp"
    shutil.move(src=iinput, dst=temp_location)
    cmd = ["7z", "a", "-tzip", "-mx=0", quote(ooutput), quote(temp_location), f"-v{size}b"]
    await run_shell_cmds(" ".join(cmd))
    spdir = ooutput.replace("/" + ooutput.split("/")[-1], "")
    files = await get_files(spdir)

    return files


# TODO
# Merge files
async def merge_files(iinput, ooutput, file_type, password=None):
    if file_type == "volume":
        result = await __extract_with_7z_helper(
            path=ooutput, archive_path=iinput, password=password
        )
    elif file_type == "rar":
        result = await __extract_with_unrar_helper(
            path=ooutput, archive_path=iinput, password=password
        )

    return result


def chunk_buttons(buttons, row_width: int):
    return [buttons[i : i + row_width] for i in range(0, len(buttons), row_width)]


# TODO
# Make keyboard
async def make_keyboard(paths, user_id, chat_id, unziphttp, rzfile=None):
    buttons = []
    cb = f"ext_a|{user_id}|{chat_id}|{unziphttp}"

    if unziphttp and rzfile:
        cb += f"|{rzfile}"

    buttons.append(
        InlineKeyboardButton(
            text=messages.get(file="ext_helper", key="UP_ALL", user_id=user_id), callback_data=cb
        )
    )

    buttons.append(
        InlineKeyboardButton(
            text=messages.get(file="ext_helper", key="CANCEL_IT", user_id=user_id),
            callback_data="cancel_dis",
        )
    )

    for num, path in enumerate(paths):
        if num > 96:
            break

        cb = f"ext_f|{user_id}|{chat_id}|{num}|{unziphttp}"

        if unziphttp and rzfile:
            cb += f"|{rzfile}"

        buttons.append(
            InlineKeyboardButton(
                text=f"{num} - {os.path.basename(path)}".encode(
                    encoding="utf-8", errors="surrogateescape"
                ).decode(encoding="utf-8", errors="surrogateescape"),
                callback_data=cb,
            )
        )

    keyboard = chunk_buttons(buttons, 1)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# TODO
async def make_keyboard_empty(user_id, chat_id, unziphttp, rzfile=None):
    buttons = []
    cb = f"ext_a|{user_id}|{chat_id}|{unziphttp}"

    if unziphttp and rzfile:
        cb += f"|{rzfile}"

    buttons.append(
        InlineKeyboardButton(
            text=messages.get(file="ext_helper", key="UP_ALL", user_id=user_id), callback_data=cb
        )
    )

    buttons.append(
        InlineKeyboardButton(
            text=messages.get(file="ext_helper", key="CANCEL_IT", user_id=user_id),
            callback_data="cancel_dis",
        )
    )

    keyboard = chunk_buttons(buttons, 2)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
