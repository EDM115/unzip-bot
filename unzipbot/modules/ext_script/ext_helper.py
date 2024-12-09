import os
import shutil
from asyncio import create_subprocess_shell, subprocess
from shlex import quote

from pykeyboard import InlineKeyboard
from pyrogram.types import InlineKeyboardButton

from config import Config
from unzipbot import LOGGER
from unzipbot.helpers.database import get_lang
from unzipbot.helpers.unzip_help import calculate_memory_limit, tarball_extensions
from unzipbot.i18n.messages import Messages


messages = Messages(lang_fetcher=get_lang)


# Get files in directory as a list
async def get_files(path):
    path_list = [
        val
        for sublist in [[os.path.join(i[0], j) for j in i[2]] for i in os.walk(path)]
        for val in sublist
    ]  # skipcq: FLK-E501

    return sorted(path_list)


async def cleanup_macos_artifacts(extraction_path):
    for root, dirs, files in os.walk(extraction_path):
        for name in files:
            if name == ".DS_Store":
                os.remove(os.path.join(root, name))
        for name in dirs:
            if name == "__MACOSX":
                shutil.rmtree(os.path.join(root, name))


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
        ulimit_command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        executable="/bin/bash",
    )
    stdout, stderr = await process.communicate()

    e = stderr.decode("utf-8", errors="replace")
    o = stdout.decode("utf-8", errors="replace")
    LOGGER.info(f"command : {command}")
    LOGGER.info(f"stdout : {o}")
    LOGGER.info(f"stderr : {e}")

    return o + "\n" + e


# Extract with 7z
async def __extract_with_7z_helper(path, archive_path, password=None):
    LOGGER.info("7z : " + archive_path + " : " + path)

    if password:
        cmd = [
            "7z",
            "x",
            f"-o{quote(path)}",
            f"-p{quote(password)}",
            quote(archive_path),
            "-y",
        ]
    else:
        cmd = ["7z", "x", f"-o{quote(path)}", quote(archive_path), "-y"]

    result = await run_shell_cmds(" ".join(cmd))

    return result


async def test_with_7z_helper(archive_path):
    password = "dont care + didnt ask + cry about it + stay mad + get real + L"  # skipcq: PTC-W1006, SCT-A000
    cmd = ["7z", "t", f"-p{quote(password)}", quote(archive_path), "-y"]
    result = await run_shell_cmds(" ".join(cmd))

    return "Everything is Ok" in result


async def __extract_with_unrar_helper(path, archive_path, password=None):
    LOGGER.info("unrar : " + archive_path + " : " + path)

    if password:
        cmd = [
            "unrar",
            "x",
            quote(archive_path),
            quote(path),
            f"-p{quote(password)}",
            "-y",
        ]
    else:
        cmd = ["unrar", "x", quote(archive_path), quote(path), "-y"]

    result = await run_shell_cmds(" ".join(cmd))

    return result


async def test_with_unrar_helper(archive_path):
    password = "dont care + didnt ask + cry about it + stay mad + get real + L"  # skipcq: PTC-W1006, SCT-A000
    cmd = ["unrar", "t", quote(archive_path), f"-p{quote(password)}", "-y"]
    result = await run_shell_cmds(" ".join(cmd))

    return "All OK" in result


# Extract with zstd (for .tar.zst files)
async def __extract_with_zstd(path, archive_path):
    cmd = ["zstd", "-f", "--output-dir-flat", quote(path), "-d", quote(archive_path)]
    result = await run_shell_cmds(" ".join(cmd))

    return result


# Main function to extract files
async def extr_files(path, archive_path, password=None):
    os.makedirs(path, exist_ok=True)

    if archive_path.endswith(tarball_extensions):
        LOGGER.info("tar")
        temp_path = path.rsplit("/", 1)[0] + "/tar_temp"
        os.makedirs(temp_path, exist_ok=True)
        result = await __extract_with_7z_helper(temp_path, archive_path)
        filename = await get_files(temp_path)
        filename = filename[0]
        cmd = ["tar", "-xvf", quote(filename), "-C", quote(path)]
        result2 = await run_shell_cmds(" ".join(cmd))
        result += result2
        shutil.rmtree(temp_path)
    elif archive_path.endswith((".tar.zst", ".zst", ".tzst")):
        LOGGER.info("zstd")
        os.mkdir(path)
        result = await __extract_with_zstd(path, archive_path)
    elif archive_path.endswith(".rar"):
        LOGGER.info("rar")

        if password:
            result = await __extract_with_unrar_helper(path, archive_path, password)
        else:
            result = await __extract_with_unrar_helper(path, archive_path)
    else:
        LOGGER.info("normal archive")
        result = await __extract_with_7z_helper(path, archive_path, password)

    LOGGER.info(await get_files(path))
    await cleanup_macos_artifacts(path)

    return result


# Split files
async def split_files(iinput, ooutput, size):
    temp_location = iinput + "_temp"
    shutil.move(iinput, temp_location)
    cmd = [
        "7z",
        "a",
        "-tzip",
        "-mx=0",
        quote(ooutput),
        quote(temp_location),
        f"-v{size}b",
    ]
    await run_shell_cmds(" ".join(cmd))
    spdir = ooutput.replace("/" + ooutput.split("/")[-1], "")
    files = await get_files(spdir)

    return files


# Merge files
async def merge_files(iinput, ooutput, file_type, password=None):
    if file_type == "volume":
        result = await __extract_with_7z_helper(ooutput, iinput, password)
    elif file_type == "rar":
        result = await __extract_with_unrar_helper(ooutput, iinput, password)

    return result


# Make keyboard
async def make_keyboard(paths, user_id, chat_id, unziphttp, rzfile=None):
    num = 0
    i_kbd = InlineKeyboard(row_width=1)
    data = []

    if unziphttp:
        data.append(
            InlineKeyboardButton(
                messages.get("ext_helper", "UP_ALL", user_id),
                f"ext_a|{user_id}|{chat_id}|{unziphttp}|{rzfile}",
            )
        )
    else:
        data.append(
            InlineKeyboardButton(
                messages.get("ext_helper", "UP_ALL", user_id),
                f"ext_a|{user_id}|{chat_id}|{unziphttp}",
            )
        )

    data.append(
        InlineKeyboardButton(
            messages.get("ext_helper", "CANCEL_IT", user_id), "cancel_dis"
        )
    )

    for file in paths:
        if num > 96:
            break

        if unziphttp:
            data.append(
                InlineKeyboardButton(
                    f"{num} - {os.path.basename(file)}".encode(
                        "utf-8", errors="surrogateescape"
                    ).decode("utf-8", errors="surrogateescape"),
                    f"ext_f|{user_id}|{chat_id}|{num}|{unziphttp}|{rzfile}",
                )
            )
        else:
            data.append(
                InlineKeyboardButton(
                    f"{num} - {os.path.basename(file)}".encode(
                        "utf-8", errors="surrogateescape"
                    ).decode("utf-8", errors="surrogateescape"),
                    f"ext_f|{user_id}|{chat_id}|{num}|{unziphttp}",
                )
            )

        num += 1

    i_kbd.add(*data)

    return i_kbd


async def make_keyboard_empty(user_id, chat_id, unziphttp, rzfile=None):
    i_kbd = InlineKeyboard(row_width=2)
    data = []

    if unziphttp:
        data.append(
            InlineKeyboardButton(
                messages.get("ext_helper", "UP_ALL", user_id),
                f"ext_a|{user_id}|{chat_id}|{unziphttp}|{rzfile}",
            )
        )
    else:
        data.append(
            InlineKeyboardButton(
                messages.get("ext_helper", "UP_ALL", user_id),
                f"ext_a|{user_id}|{chat_id}|{unziphttp}",
            )
        )

    data.append(
        InlineKeyboardButton(
            messages.get("ext_helper", "CANCEL_IT", user_id), "cancel_dis"
        )
    )

    i_kbd.add(*data)

    return i_kbd
