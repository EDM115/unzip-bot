import os
import shutil
import tarfile
from asyncio import create_subprocess_shell, subprocess
from shlex import join, quote
from tempfile import TemporaryDirectory

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
        for sublist in [
            [os.path.join(i[0], j) for j in i[2]] for i in os.walk(top=path)
        ]
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


async def run_shell_cmds(command, with_status=False, limit_virtual_memory=True):
    cpulimit = Config.MAX_CPU_CORES_COUNT * Config.MAX_CPU_USAGE
    ulimit_cmd = ["cpulimit", "-l", str(cpulimit), "--", command]
    if limit_virtual_memory:
        ulimit_cmd[:0] = ["ulimit", "-v", str(calculate_memory_limit()), "&&"]
    ulimit_command = " ".join(ulimit_cmd)
    process = await create_subprocess_shell(
        cmd=ulimit_command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        executable="/bin/bash",
    )
    stdout, stderr = await process.communicate()

    e = stderr.decode(encoding="utf-8", errors="replace")
    o = stdout.decode(encoding="utf-8", errors="replace")
    # LOGGER.info(msg=f"command : {command}")
    # LOGGER.info(msg=f"stdout : {o}")
    # LOGGER.info(msg=f"stderr : {e}")

    output = o + "\n" + e
    return (output, process.returncode) if with_status else output


# Extract with 7z
async def __extract_with_7z_helper(path, archive_path, password=None):
    # LOGGER.info(msg="7z : " + archive_path + " : " + path)

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

    result, status = await run_shell_cmds(" ".join(cmd), with_status=True)
    return result if status == 0 else result + "\nError"


async def test_with_7z_helper(archive_path):
    # skipcq: PTC-W1006, SCT-A000
    password = "dont care + didnt ask + cry about it + stay mad + get real + L"
    cmd = ["7z", "t", f"-p{quote(password)}", quote(archive_path), "-y"]
    _, status = await run_shell_cmds(" ".join(cmd), with_status=True)
    return status == 0


async def __extract_with_unrar_helper(path, archive_path, password=None):
    # LOGGER.info(msg="unrar : " + archive_path + " : " + path)

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

    result, status = await run_shell_cmds(" ".join(cmd), with_status=True)
    return result if status == 0 else result + "\nError"


async def test_with_unrar_helper(archive_path):
    # skipcq: PTC-W1006, SCT-A000
    password = "dont care + didnt ask + cry about it + stay mad + get real + L"
    cmd = ["unrar", "t", quote(archive_path), f"-p{quote(password)}", "-y"]
    _, status = await run_shell_cmds(" ".join(cmd), with_status=True)
    return status == 0


async def __extract_with_unarc_helper(path, archive_path):
    command = join(["unarc", "x", f"-dp{path}", "-o+", archive_path])
    # The 32-bit FreeArc binary needs its full virtual address space under emulation
    result, status = await run_shell_cmds(command, with_status=True, limit_virtual_memory=False)
    return result if status == 0 else result + "\nError"


async def test_with_unarc_helper(archive_path):
    _, status = await run_shell_cmds(join(["unarc", "t", archive_path]), with_status=True, limit_virtual_memory=False)
    return status == 0


def pea_archive_has_header(archive_path):
    try:
        with open(archive_path, "rb") as archive:
            return archive.read(1) == b"\xea"
    except OSError:
        return False


async def __extract_with_pea_helper(path, archive_path, password=None):
    if not pea_archive_has_header(archive_path):
        return "Error: not a PEA archive"
    if os.path.isdir(path):
        if os.listdir(path):
            return "Error: output directory is not empty"
        os.rmdir(path)
    command = ["timeout", "-k", "5", str(Config.MAX_TASK_DURATION_EXTRACT), "xvfb-run", "-a", "pea", "UNPEA", archive_path, path, "RESETDATE", "RESETATTR", "EXTRACT2DIR", "HIDDEN"]
    if password:
        command.extend([password, "NOKEYFILE"])
    result, status = await run_shell_cmds(join(command), with_status=True)
    return result if status == 0 and os.path.isdir(path) else result + "\nError"


async def test_with_pea_helper(archive_path):
    if not pea_archive_has_header(archive_path):
        return False
    with TemporaryDirectory(prefix="pea-test-", dir=os.path.dirname(archive_path)) as temp_dir:
        output = os.path.join(temp_dir, "extracted")
        command = ["timeout", "-k", "5", str(Config.MAX_TASK_DURATION_EXTRACT), "xvfb-run", "-a", "pea", "UNPEA", archive_path, output, "RESETDATE", "RESETATTR", "EXTRACT2TESTB", "HIDDEN"]
        _, status = await run_shell_cmds(join(command), with_status=True)
        return status == 0


# Main function to extract files
async def extr_files(path, archive_path, password=None):
    os.makedirs(name=path, exist_ok=True)
    lower_name = archive_path.casefold()

    if lower_name.endswith(tarball_extensions):
        # LOGGER.info(msg="tar")
        with TemporaryDirectory(prefix="tar-", dir=os.path.dirname(path)) as temp_path:
            result = await __extract_with_7z_helper(path=temp_path, archive_path=archive_path)
            extracted = await get_files(temp_path)
            if "Error" in result or len(extracted) != 1:
                result += "\nError"
            elif tarfile.is_tarfile(extracted[0]):
                command = join(["tar", "-xvf", extracted[0], "-C", path, "--no-same-owner", "--no-same-permissions"])
                output, status = await run_shell_cmds(command, with_status=True)
                result += output
                if status != 0:
                    result += "\nError"
            else:
                shutil.move(extracted[0], os.path.join(path, os.path.basename(extracted[0])))
    elif lower_name.endswith((".rar", ".cbr")):
        # LOGGER.info(msg="rar")

        if password:
            result = await __extract_with_unrar_helper(
                path=path, archive_path=archive_path, password=password
            )
        else:
            result = await __extract_with_unrar_helper(
                path=path, archive_path=archive_path
            )
    elif lower_name.endswith((".arc", ".wrc")):
        result = await __extract_with_unarc_helper(path=path, archive_path=archive_path)
    elif lower_name.endswith(".pea"):
        result = await __extract_with_pea_helper(path=path, archive_path=archive_path, password=password)
    else:
        # LOGGER.info(msg="normal archive")
        result = await __extract_with_7z_helper(
            path=path, archive_path=archive_path, password=password
        )

    # LOGGER.info(msg=await get_files(path))
    await cleanup_macos_artifacts(path)

    return result


# Split files
async def split_files(iinput, ooutput, size):
    temp_location = iinput + "_temp"
    shutil.move(src=iinput, dst=temp_location)
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
    if file_type in ("volume", "zip"):
        result = await __extract_with_7z_helper(
            path=ooutput, archive_path=iinput, password=password
        )
    elif file_type == "rar":
        result = await __extract_with_unrar_helper(
            path=ooutput, archive_path=iinput, password=password
        )
    elif file_type == "arc":
        result = await __extract_with_unarc_helper(path=ooutput, archive_path=iinput)
    elif file_type == "pea":
        result = await __extract_with_pea_helper(path=ooutput, archive_path=iinput, password=password)

    return result


# Make keyboard
async def make_keyboard(paths, user_id, chat_id, unziphttp, rzfile=None):
    num = 0
    i_kbd = InlineKeyboard(row_width=1)
    data = []

    if unziphttp:
        data.append(
            InlineKeyboardButton(
                text=messages.get(file="ext_helper", key="UP_ALL", user_id=user_id),
                callback_data=f"ext_a|{user_id}|{chat_id}|{unziphttp}|{rzfile}",
            )
        )
    else:
        data.append(
            InlineKeyboardButton(
                text=messages.get(file="ext_helper", key="UP_ALL", user_id=user_id),
                callback_data=f"ext_a|{user_id}|{chat_id}|{unziphttp}",
            )
        )

    data.append(
        InlineKeyboardButton(
            text=messages.get(file="ext_helper", key="CANCEL_IT", user_id=user_id),
            callback_data="cancel_dis",
        )
    )

    for file in paths:
        if num > 96:
            break

        if unziphttp:
            data.append(
                InlineKeyboardButton(
                    text=f"{num} - {os.path.basename(file)}".encode(
                        encoding="utf-8", errors="surrogateescape"
                    ).decode(encoding="utf-8", errors="surrogateescape"),
                    callback_data=f"ext_f|{user_id}|{chat_id}|{num}|{unziphttp}|{rzfile}",
                )
            )
        else:
            data.append(
                InlineKeyboardButton(
                    text=f"{num} - {os.path.basename(file)}".encode(
                        encoding="utf-8", errors="surrogateescape"
                    ).decode(encoding="utf-8", errors="surrogateescape"),
                    callback_data=f"ext_f|{user_id}|{chat_id}|{num}|{unziphttp}",
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
                text=messages.get(file="ext_helper", key="UP_ALL", user_id=user_id),
                callback_data=f"ext_a|{user_id}|{chat_id}|{unziphttp}|{rzfile}",
            )
        )
    else:
        data.append(
            InlineKeyboardButton(
                text=messages.get(file="ext_helper", key="UP_ALL", user_id=user_id),
                callback_data=f"ext_a|{user_id}|{chat_id}|{unziphttp}",
            )
        )

    data.append(
        InlineKeyboardButton(
            text=messages.get(file="ext_helper", key="CANCEL_IT", user_id=user_id),
            callback_data="cancel_dis",
        )
    )

    i_kbd.add(*data)

    return i_kbd
