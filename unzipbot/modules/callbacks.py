import asyncio
import concurrent.futures
import os
import re
import shutil
import tarfile
import unicodedata
from email.parser import Parser
from email.policy import default
from fnmatch import fnmatch
from time import time
from urllib.parse import unquote, urlsplit
from uuid import uuid4

import unzip_http
from aiofiles import open as openfile
from aiohttp import ClientSession, InvalidURL
from pyrogram import Client
from pyrogram.errors import ReplyMarkupTooLong
from pyrogram.types import CallbackQuery

from config import Config
from unzipbot import LOGGER, unzipbot_client
from unzipbot.helpers.database import (
    add_cancel_task,
    add_ongoing_task,
    count_ongoing_tasks,
    del_cancel_task,
    del_merge_task,
    del_ongoing_task,
    del_thumb_db,
    get_cancel_task,
    get_lang,
    get_maintenance,
    get_merge_task_message_id,
    get_ongoing_task_log_message_id,
    get_ongoing_tasks,
    set_ongoing_task_log_message_id,
    set_upload_mode,
    update_thumb,
    update_uploaded,
)
from unzipbot.helpers.unzip_help import (
    ERROR_MSGS,
    TimeFormatter,
    extentions_list,
    humanbytes,
    progress_for_pyrogram,
)
from unzipbot.i18n.buttons import Buttons
from unzipbot.i18n.messages import Messages

from .commands import get_stats, https_url_regex, sufficient_disk_space
from .ext_script.custom_thumbnail import silent_del
from .ext_script.ext_helper import (
    extr_files,
    get_files,
    make_keyboard,
    make_keyboard_empty,
    merge_files,
    split_files,
    test_with_7z_helper,
    test_with_pea_helper,
    test_with_unarc_helper,
    test_with_unrar_helper,
)
from .ext_script.up_helper import answer_query, get_size, send_file, send_url_logs

split_file_pattern = r"\.z[0-9]+$"
rar_file_pattern = r"\.(?:r[0-9]+|part[0-9]+\.rar)$"
volume_file_pattern = r"\.[0-9]+$"
telegram_url_pattern = r"(?:http[s]?:\/\/)?(?:www\.)?t\.me\/([a-zA-Z0-9_]+)\/(\d+)"
messages = Messages(lang_fetcher=get_lang)


def resolve_extraction_paths(parts, action, user_id, chat_id, download_location):
    minimum_fields = {"ext_f": 5, "ext_a": 4}
    if (
        action not in minimum_fields
        or len(parts) < minimum_fields[action]
        or parts[0] != action
        or parts[1] != str(user_id)
        or parts[2] != str(chat_id)
    ):
        return None

    download_root = os.path.realpath(download_location)
    user_root = os.path.join(download_root, str(user_id))
    extracted_root = os.path.join(user_root, "extracted")

    # Reject symlinks that could redirect a user's workspace into another directory
    if (
        os.path.realpath(user_root) != user_root
        or os.path.realpath(extracted_root) != extracted_root
    ):
        return None

    return user_root, extracted_root


def extracted_files_are_safe(paths, extracted_root):
    extracted_root = os.path.realpath(extracted_root)
    for path in paths:
        resolved = os.path.realpath(path)
        if (
            resolved == extracted_root
            or os.path.commonpath((extracted_root, resolved)) != extracted_root
        ):
            return False
    return True


def split_archive_part(path):
    name = unicodedata.normalize("NFC", os.path.basename(path))
    name = "".join(char for char in name if unicodedata.category(char) != "Cf")
    patterns = (
        ("rar_new", r"^(.+)\.part([0-9]+)\.rar$"),
        ("rar_old", r"^(.+)\.r([0-9]+)$"),
        ("zip", r"^(.+)\.z([0-9]+)$"),
        ("pea", r"^(.+)\.([0-9]{6})\.pea$"),
        ("volume", r"^(.+)\.([0-9]{3,})$"),
    )
    for kind, pattern in patterns:
        match = re.fullmatch(pattern, name, flags=re.IGNORECASE)
        if match:
            number = int(match.group(2))
            if kind == "rar_old":
                number += 1
            return kind, match.group(1).casefold(), number, len(match.group(2))
    if name.lower().endswith(".rar"):
        return "rar_old", name[:-4].casefold(), 0, 2
    if name.lower().endswith(".zip"):
        return "zip", name[:-4].casefold(), 0, 2
    return None


def prepare_split_archive(files):
    groups = {}
    for path in files:
        part = split_archive_part(path)
        if part:
            kind, base, number, width = part
            groups.setdefault((kind, base), []).append((path, number, width))

    candidates = []
    for (kind, base), parts in groups.items():
        numbers = [number for _, number, _ in parts]
        first = 0 if kind in ("rar_old", "zip") else 1
        if first not in numbers or (first == 0 and len(parts) < 2):
            continue
        if len(set(numbers)) != len(numbers) or sorted(numbers) != list(range(first, max(numbers) + 1)):
            raise IndexError("Missing or duplicate archive volume")
        candidates.append((kind, base, parts, first))

    if len(candidates) != 1:
        raise IndexError("Expected one complete archive volume set")

    kind, base, parts, first = candidates[0]
    width = max(width for _, _, width in parts)
    prefix = f"unzipbot-{uuid4().hex}"
    if kind == "volume":
        suffix = os.path.splitext(base)[1]
        if suffix in (".7z", ".zip", ".rar", ".arc", ".tar", ".gz", ".zst"):
            prefix += suffix

    starter = None
    original_name = None
    for path, number, _ in parts:
        if kind == "rar_new":
            part_suffix = f".part{number:0{width}d}.rar"
        elif kind == "rar_old":
            part_suffix = ".rar" if number == 0 else f".r{number - 1:0{width}d}"
        elif kind == "zip":
            part_suffix = ".zip" if number == 0 else f".z{number:0{width}d}"
        elif kind == "pea":
            part_suffix = f".{number:0{width}d}.pea"
        else:
            part_suffix = f".{number:0{width}d}"
        target = os.path.join(os.path.dirname(path), prefix + part_suffix)
        os.rename(path, target)
        if number == first:
            starter = target
            original_name = os.path.basename(path)

    extractor = "rar" if kind.startswith("rar") else "zip" if kind == "zip" else "pea" if kind == "pea" else "arc" if prefix.endswith(".arc") else "volume"
    return starter, extractor, original_name


def safe_download_name(name):
    if not name:
        return ""
    name = unquote(name).replace("\\", "/").rsplit("/", 1)[-1]
    name = "".join(char for char in name if unicodedata.category(char) != "Cc")
    return name if name not in ("", ".", "..") else ""


async def download(url, path):
    try:
        async with (
            ClientSession() as session,
            session.get(url=url, timeout=None, allow_redirects=True) as resp,
            openfile(file=path, mode="wb") as file,
        ):
            async for chunk in resp.content.iter_chunked(Config.CHUNK_SIZE):
                await file.write(chunk)
    except InvalidURL:
        # LOGGER.error(msg=messages.get(file="callbacks", key="INVALID_URL"))
        pass
    except Exception:
        # LOGGER.error(msg=messages.get(file="callbacks", key="ERR_DL", extra_args=url))
        pass


async def download_with_progress(url, path, message, unzip_bot):
    uid = message.from_user.id

    try:
        async with (
            ClientSession() as session,
            session.get(url=url, timeout=None, allow_redirects=True) as resp,
        ):
            total_size = int(resp.headers.get("Content-Length", default=0))
            current_size = 0
            start_time = time()

            async with openfile(file=path, mode="wb") as file:
                async for chunk in resp.content.iter_chunked(Config.CHUNK_SIZE):
                    if message.from_user is not None and await get_cancel_task(uid):
                        await message.edit(
                            text=messages.get(
                                file="callbacks", key="DL_STOPPED", user_id=uid
                            )
                        )
                        await del_cancel_task(uid)

                        return False

                    await file.write(chunk)
                    current_size += len(chunk)
                    await progress_for_pyrogram(
                        current=current_size,
                        total=total_size,
                        ud_type=messages.get(
                            file="callbacks", key="DL_URL", user_id=uid, extra_args=url
                        ),
                        message=message,
                        start=start_time,
                        unzip_bot=unzip_bot,
                    )
    except Exception:
        # LOGGER.error(msg=messages.get(file="callbacks", key="ERR_DL", extra_args=url))
        pass


def get_zip_http(url):
    rzf = unzip_http.RemoteZipFile(url)
    paths = rzf.namelist()
    return rzf, paths


async def async_generator(iterable):
    for item in iterable:
        yield item


async def get_task_log_message(unzip_bot, user_id):
    message_id = await get_ongoing_task_log_message_id(user_id)
    if message_id is None:
        return None
    try:
        return await unzip_bot.get_messages(chat_id=Config.LOGS_CHANNEL, message_ids=message_id)
    except Exception:
        return None


# Callbacks
@unzipbot_client.on_callback_query()
async def unzip_cb(unzip_bot: Client, query: CallbackQuery):
    uid = query.from_user.id

    if uid != Config.BOT_OWNER:  # skipcq: PTC-W0048
        if await count_ongoing_tasks() >= Config.MAX_CONCURRENT_TASKS:
            ogtasks = await get_ongoing_tasks()

            if not any(ogtask.get("user_id") == uid for ogtask in ogtasks):
                await unzip_bot.send_message(
                    chat_id=uid,
                    text=messages.get(
                        file="callbacks",
                        key="MAX_TASKS",
                        user_id=uid,
                        extra_args=Config.MAX_CONCURRENT_TASKS,
                    ),
                )

                return

    if (
        uid != Config.BOT_OWNER
        and await get_maintenance()
        and query.data
        not in [
            "megoinhome",
            "helpcallback",
            "aboutcallback",
            "donatecallback",
            "statscallback",
            "canceldownload",
            "check_thumb",
            "check_before_del",
            "save_thumb",
            "del_thumb",
            "nope_thumb",
            "set_mode",
            "cancel_dis",
            "nobully",
        ]
    ):
        await answer_query(
            query=query,
            message_text=messages.get(
                file="callbacks", key="MAINTENANCE_ON", user_id=uid
            ),
        )

        return

    sent_files = 0
    if query.data == "megoinhome":
        await query.edit_message_text(
            text=messages.get(
                file="callbacks",
                key="START_TEXT",
                user_id=uid,
                extra_args=query.from_user.mention,
            ),
            reply_markup=Buttons.START_BUTTON,
        )

    elif query.data == "helpcallback":
        await query.edit_message_text(
            text=messages.get(file="callbacks", key="HELP_TXT", user_id=uid),
            reply_markup=Buttons.ME_GOIN_HOME,
        )

    elif query.data == "aboutcallback":
        await query.edit_message_text(
            text=messages.get(
                file="callbacks",
                key="ABOUT_TXT",
                user_id=uid,
                extra_args=Config.VERSION,
            ),
            reply_markup=Buttons.ME_GOIN_HOME,
            disable_web_page_preview=True,
        )

    elif query.data == "donatecallback":
        await query.edit_message_text(
            text=messages.get(file="callbacks", key="DONATE_TEXT", user_id=uid),
            reply_markup=Buttons.ME_GOIN_HOME,
            disable_web_page_preview=True,
        )

    elif query.data.startswith("statscallback"):
        if query.data.endswith("refresh"):
            await query.edit_message_text(
                text=messages.get(file="callbacks", key="REFRESH_STATS", user_id=uid)
            )
        text_stats = await get_stats(query.from_user.id)
        await query.edit_message_text(
            text=text_stats, reply_markup=Buttons.REFRESH_BUTTON
        )

    elif query.data == "canceldownload":
        await add_cancel_task(query.from_user.id)

    elif query.data == "check_thumb":
        user_id = query.from_user.id
        thumb_location = Config.THUMB_LOCATION + "/" + str(user_id) + ".jpg"
        await unzip_bot.send_photo(
            chat_id=user_id,
            photo=thumb_location,
            caption=messages.get(file="callbacks", key="ACTUAL_THUMB", user_id=uid),
        )
        await unzip_bot.delete_messages(chat_id=user_id, message_ids=query.message.id)
        await unzip_bot.send_message(
            chat_id=user_id,
            text=messages.get(file="callbacks", key="EXISTING_THUMB", user_id=uid),
            reply_markup=Buttons.THUMB_FINAL,
        )

    elif query.data == "check_before_del":
        user_id = query.from_user.id
        thumb_location = Config.THUMB_LOCATION + "/" + str(user_id) + ".jpg"
        await unzip_bot.send_photo(
            chat_id=user_id,
            photo=thumb_location,
            caption=messages.get(file="callbacks", key="ACTUAL_THUMB", user_id=uid),
        )
        await unzip_bot.delete_messages(chat_id=user_id, message_ids=query.message.id)
        await unzip_bot.send_message(
            chat_id=user_id,
            text=messages.get(file="callbacks", key="DEL_CONFIRM_THUMB_2", user_id=uid),
            reply_markup=Buttons.THUMB_DEL_2,
        )

    elif query.data.startswith("save_thumb"):
        user_id = query.from_user.id
        replace = query.data.split("|")[1]

        if replace == "replace":
            await silent_del(user_id)

        thumb_location = Config.THUMB_LOCATION + "/" + str(user_id) + ".jpg"
        final_thumb = Config.THUMB_LOCATION + "/waiting_" + str(user_id) + ".jpg"

        try:
            shutil.move(final_thumb, thumb_location)
        except Exception as e:
            #LOGGER.warning(msg=messages.get(file="callbacks", key="ERROR_THUMB_RENAME"))
            #LOGGER.error(msg=e)
            pass

        try:
            await update_thumb(query.from_user.id)
        except:
            # LOGGER.error(msg=messages.get(file="callbacks", key="ERROR_THUMB_UPDATE"))
            pass

        await answer_query(
            query=query,
            message_text=messages.get(
                file="callbacks", key="SAVED_THUMBNAIL", user_id=uid
            ),
        )

    elif query.data == "del_thumb":
        user_id = query.from_user.id
        thumb_location = Config.THUMB_LOCATION + "/" + str(user_id) + ".jpg"

        try:
            await del_thumb_db(user_id)
        except Exception as e:
            """
            LOGGER.error(
                msg=messages.get(file="callbacks", key="ERROR_THUMB_DEL", extra_args=e)
            )
            """
            pass

        try:
            os.remove(path=thumb_location)
        except:
            pass

        await query.edit_message_text(
            text=messages.get(file="callbacks", key="DELETED_THUMB", user_id=uid)
        )

    elif query.data == "nope_thumb":
        user_id = query.from_user.id
        del_1 = Config.THUMB_LOCATION + "/not_resized_" + str(user_id) + ".jpg"
        del_2 = Config.THUMB_LOCATION + "/waiting_" + str(user_id) + ".jpg"

        try:
            os.remove(path=del_1)
        except:
            pass

        try:
            os.remove(path=del_2)
        except:
            pass

        await query.edit_message_text(
            text=messages.get(
                file="callbacks",
                key="CANCELLED_TXT",
                user_id=uid,
                extra_args=messages.get(
                    file="callbacks", key="PROCESS_CANCELLED", user_id=uid
                ),
            )
        )

    elif query.data.startswith("set_mode"):
        user_id = query.from_user.id
        mode = query.data.split("|")[1]
        await set_upload_mode(user_id=user_id, mode=mode)
        await answer_query(
            query=query,
            message_text=messages.get(
                file="callbacks",
                key="CHANGED_UPLOAD_MODE_TXT",
                user_id=uid,
                extra_args=mode,
            ),
        )

    elif query.data == "merge_this":
        user_id = query.from_user.id
        m_id = query.message.id
        start_time = time()
        await add_ongoing_task(
            user_id=user_id, start_time=start_time, task_type="merge"
        )
        s_id = await get_merge_task_message_id(user_id)
        merge_msg = await query.message.edit(
            text=messages.get(file="callbacks", key="PROCESSING_TASK", user_id=uid)
        )
        download_path = f"{Config.DOWNLOAD_LOCATION}/{user_id}/merge"

        if s_id and (m_id - s_id) > 1:
            files_array = list(range(s_id, m_id))

            try:
                messages_array = await unzip_bot.get_messages(
                    chat_id=user_id, message_ids=files_array
                )
            except Exception as e:
                """
                LOGGER.error(
                    msg=messages.get(
                        file="callbacks", key="ERROR_GET_MSG", extra_args=e
                    )
                )
                """
                await answer_query(
                    query=query,
                    message_text=messages.get(
                        file="callbacks", key="ERROR_TXT", user_id=uid, extra_args=e
                    ),
                )
                await del_ongoing_task(user_id)
                await del_merge_task(user_id)

                try:
                    shutil.rmtree(f"{Config.DOWNLOAD_LOCATION}/{user_id}")
                except:
                    pass

                return

            length = len(messages_array)
            os.makedirs(name=download_path, exist_ok=True)
            rs_time = time()
            newarray = []
            await merge_msg.edit(
                text=messages.get(
                    file="callbacks", key="PROCESS_MSGS", user_id=uid, extra_args=length
                )
            )

            for message in messages_array:
                if message.document is None:
                    pass
                else:
                    if message.from_user.id == user_id:
                        newarray.append(message)

            length = len(newarray)

            if length == 0:
                await answer_query(
                    query=query,
                    message_text=messages.get(
                        file="callbacks", key="NO_MERGE_TASK", user_id=uid
                    ),
                )
                await del_ongoing_task(user_id)
                await del_merge_task(user_id)

                try:
                    shutil.rmtree(f"{Config.DOWNLOAD_LOCATION}/{user_id}")
                except:
                    pass

                return

            i = 0
            async_newarray = async_generator(newarray)

            async for message in async_newarray:
                i += 1
                fname = safe_download_name(message.document.file_name) or f"document_{message.id}"
                await message.forward(chat_id=Config.LOGS_CHANNEL)
                location = os.path.join(download_path, fname)
                s_time = time()
                await message.download(
                    file_name=location,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        messages.get(
                            file="callbacks",
                            key="DL_FILES",
                            user_id=uid,
                            extra_args=[i, length],
                        ),
                        merge_msg,
                        s_time,
                        unzip_bot,
                    ),
                )

            e_time = time()
            dltime = TimeFormatter(round(number=e_time - rs_time) * 1000)

            if dltime == "":
                dltime = "1 s"

            await merge_msg.edit(
                text=messages.get(
                    file="callbacks",
                    key="AFTER_OK_MERGE_DL_TXT",
                    user_id=uid,
                    extra_args=[i, dltime],
                )
            )
            await merge_msg.edit(
                text=messages.get(
                    file="callbacks", key="CHOOSE_EXT_MODE_MERGE", user_id=uid
                ),
                reply_markup=Buttons.CHOOSE_E_F_M__BTNS,
            )
            await del_merge_task(user_id)
        else:
            await answer_query(
                query=query,
                message_text=messages.get(
                    file="callbacks", key="NO_MERGE_TASK", user_id=uid
                ),
            )
            await del_ongoing_task(user_id)
            await del_merge_task(user_id)

            try:
                shutil.rmtree(f"{Config.DOWNLOAD_LOCATION}/{user_id}")
            except:
                pass

    elif query.data.startswith("merged"):
        user_id = query.from_user.id
        download_path = f"{Config.DOWNLOAD_LOCATION}/{user_id}/merge"
        ext_files_dir = f"{Config.DOWNLOAD_LOCATION}/{user_id}/extracted"
        os.makedirs(name=ext_files_dir, exist_ok=True)

        try:
            files = await get_files(download_path)
            file, file_type, original_name = prepare_split_archive(files)
        except IndexError:
            await answer_query(
                query=query,
                message_text=messages.get(
                    file="callbacks", key="NO_MERGE_TASK", user_id=uid
                ),
            )
            await del_ongoing_task(user_id)
            await del_merge_task(user_id)

            try:
                shutil.rmtree(f"{Config.DOWNLOAD_LOCATION}/{user_id}")
            except:
                pass

            return

        split_data = query.data.split("|")
        log_msg = await unzip_bot.send_message(
            chat_id=Config.LOGS_CHANNEL,
            text=messages.get(
                file="callbacks",
                key="PROCESS_MERGE",
                extra_args=[user_id, os.path.splitext(original_name)[0]],
            ),
        )
        await set_ongoing_task_log_message_id(user_id, log_msg.id)

        try:
            await query.message.edit(
                text=messages.get(file="callbacks", key="PROCESSING_TASK", user_id=uid)
            )
        except:
            pass

        if split_data[1] == "with_pass":
            password = await unzip_bot.ask(
                chat_id=query.message.chat.id,
                text=messages.get(
                    file="callbacks", key="PLS_SEND_PASSWORD", user_id=uid
                ),
            )
            ext_s_time = time()
            extractor = await merge_files(
                iinput=file,
                ooutput=ext_files_dir,
                file_type=file_type,
                password=password.text,
            )
            ext_e_time = time()
        else:
            # Can't test the archive apparently
            ext_s_time = time()
            extractor = await merge_files(
                iinput=file, ooutput=ext_files_dir, file_type=file_type
            )
            ext_e_time = time()

        # Checks if there is an error happened while extracting the archive
        if any(err in extractor for err in ERROR_MSGS):
            try:
                await query.message.edit(
                    text=messages.get(
                        file="callbacks", key="EXT_FAILED_TXT", user_id=uid
                    )
                )
                shutil.rmtree(ext_files_dir)
                shutil.rmtree(download_path)
                await del_ongoing_task(user_id)
            except:
                try:
                    await query.message.delete()
                except:
                    pass

                await unzip_bot.send_message(
                    chat_id=query.message.chat.id,
                    text=messages.get(
                        file="callbacks", key="EXT_FAILED_TXT", user_id=uid
                    ),
                )
                shutil.rmtree(ext_files_dir)
                await del_ongoing_task(user_id)

            return

        # Check if user was dumb 😐
        paths = await get_files(path=ext_files_dir)

        if not paths:
            await unzip_bot.send_message(
                chat_id=query.message.chat.id,
                text=messages.get(
                    file="callbacks", key="PASSWORD_PROTECTED", user_id=uid
                ),
            )
            await answer_query(
                query=query,
                message_text=messages.get(
                    file="callbacks", key="EXT_FAILED_TXT", user_id=uid
                ),
                unzip_client=unzip_bot,
            )
            shutil.rmtree(ext_files_dir)
            shutil.rmtree(download_path)
            await del_ongoing_task(user_id)

            return

        try:
            shutil.rmtree(download_path)
        except:
            pass

        # Upload extracted files
        extrtime = TimeFormatter(round(number=ext_e_time - ext_s_time) * 1000)

        if extrtime == "":
            extrtime = "1s"
        await answer_query(
            query=query,
            message_text=messages.get(
                file="callbacks", key="EXT_OK_TXT", user_id=uid, extra_args=[extrtime]
            ),
            unzip_client=unzip_bot,
        )

        try:
            i_e_buttons = await make_keyboard(
                paths=paths,
                user_id=user_id,
                chat_id=query.message.chat.id,
                unziphttp=False,
            )

            try:
                await query.message.edit(
                    text=messages.get(
                        file="callbacks", key="SELECT_FILES", user_id=uid
                    ),
                    reply_markup=i_e_buttons,
                )
            except ReplyMarkupTooLong:
                empty_buttons = await make_keyboard_empty(
                    user_id=user_id, chat_id=query.message.chat.id, unziphttp=False
                )
                await query.message.edit(
                    text=messages.get(
                        file="callbacks", key="UNABLE_GATHER_FILES", user_id=uid
                    ),
                    reply_markup=empty_buttons,
                )
        except:
            try:
                await query.message.delete()
                i_e_buttons = await make_keyboard(
                    paths=paths,
                    user_id=user_id,
                    chat_id=query.message.chat.id,
                    unziphttp=False,
                )
                await unzip_bot.send_message(
                    chat_id=query.message.chat.id,
                    text=messages.get(
                        file="callbacks", key="SELECT_FILES", user_id=uid
                    ),
                    reply_markup=i_e_buttons,
                )
            except:
                try:
                    await query.message.delete()
                    empty_buttons = await make_keyboard_empty(
                        user_id=user_id, chat_id=query.message.chat.id, unziphttp=False
                    )
                    await unzip_bot.send_message(
                        chat_id=query.message.chat.id,
                        text=messages.get(
                            file="callbacks", key="UNABLE_GATHER_FILES", user_id=uid
                        ),
                        reply_markup=empty_buttons,
                    )
                except:
                    await answer_query(
                        query=query,
                        message_text=messages.get(
                            file="callbacks", key="EXT_FAILED_TXT", user_id=uid
                        ),
                        unzip_client=unzip_bot,
                    )
                    shutil.rmtree(ext_files_dir)
                    # LOGGER.error(msg=messages.get(file="callbacks", key="FATAL_ERROR"))
                    await del_ongoing_task(user_id)

                    return

    elif query.data.startswith("extract_file"):
        user_id = query.from_user.id
        start_time = time()
        await add_ongoing_task(
            user_id=user_id, start_time=start_time, task_type="extract"
        )
        download_path = f"{Config.DOWNLOAD_LOCATION}/{user_id}"
        ext_files_dir = f"{download_path}/extracted"
        r_message = query.message.reply_to_message
        split_data = query.data.split("|")

        try:
            await query.message.edit(
                text=messages.get(file="callbacks", key="PROCESSING_TASK", user_id=uid)
            )
        except:
            pass

        log_msg = await unzip_bot.send_message(
            chat_id=Config.LOGS_CHANNEL,
            text=messages.get(file="callbacks", key="USER_QUERY", extra_args=user_id),
        )
        await set_ongoing_task_log_message_id(user_id, log_msg.id)
        archive_msg = log_msg

        try:
            if split_data[1] == "url":
                url = r_message.text

                # Double check
                if not re.match(pattern=https_url_regex, string=url):
                    await del_ongoing_task(user_id)
                    await query.message.edit(
                        text=messages.get(
                            file="callbacks", key="INVALID_URL", user_id=uid
                        )
                    )

                    return

                if re.match(pattern=telegram_url_pattern, string=url):
                    r_message = await unzip_bot.get_messages(
                        chat_id=url.split(sep="/")[-2],
                        message_ids=int(url.split(sep="/")[-1]),
                    )
                    split_data[1] = "tg_file"

                if split_data[1] == "url":
                    s = ClientSession()

                    async with s as session:
                        # Get the file size
                        unzip_head = await session.head(url=url, allow_redirects=True)
                        f_size = unzip_head.headers.get("content-length")
                        u_file_size = f_size if f_size else "undefined"

                        if u_file_size != "undefined" and not sufficient_disk_space(
                            int(u_file_size)
                        ):
                            await del_ongoing_task(user_id)
                            await query.message.edit(
                                text=messages.get(
                                    file="callbacks", key="NO_SPACE", user_id=uid
                                )
                            )

                            return

                        await log_msg.edit(
                            text=messages.get(
                                file="callbacks",
                                key="LOG_TXT",
                                extra_args=[user_id, url, u_file_size],
                            )
                        )
                        archive_msg = log_msg
                        unzip_resp = await session.get(
                            url=url, timeout=None, allow_redirects=True
                        )

                        if "application/" not in unzip_resp.headers.get("content-type"):
                            await del_ongoing_task(user_id)
                            await query.message.edit(
                                text=messages.get(
                                    file="callbacks", key="NOT_AN_ARCHIVE", user_id=uid
                                )
                            )

                            return

                        content_disposition = unzip_head.headers.get(
                            "content-disposition"
                        )
                        real_filename = ""
                        if content_disposition:
                            headers = Parser(policy=default).parsestr(
                                text=f"Content-Disposition: {content_disposition}"
                            )
                            real_filename = headers.get_filename()
                        rfnamebro = safe_download_name(real_filename) or safe_download_name(urlsplit(url).path)

                        if unzip_resp.status == 200:
                            os.makedirs(name=download_path, exist_ok=True)
                            s_time = time()

                            archive = os.path.join(download_path, rfnamebro or "download")
                            fext = rfnamebro.rsplit(sep=".", maxsplit=1)[-1].casefold() if "." in rfnamebro else ""

                            if (
                                split_data[2] not in ["thumb", "thumbrename"]
                                and fext not in extentions_list["archive"]
                            ):
                                await del_ongoing_task(user_id)
                                await query.message.edit(
                                    text=messages.get(
                                        file="callbacks",
                                        key="DEF_NOT_AN_ARCHIVE",
                                        user_id=uid,
                                    )
                                )

                                try:
                                    shutil.rmtree(
                                        f"{Config.DOWNLOAD_LOCATION}/{user_id}"
                                    )
                                except:
                                    pass

                                return

                            await answer_query(
                                query=query,
                                message_text=messages.get(
                                    file="callbacks", key="PROCESSING2", user_id=uid
                                ),
                                unzip_client=unzip_bot,
                            )

                            if (
                                fext == "zip"
                                and "accept-ranges" in unzip_resp.headers
                                and "content-length" in unzip_resp.headers
                            ):
                                try:
                                    loop = asyncio.get_event_loop()

                                    with (
                                        concurrent.futures.ThreadPoolExecutor() as pool
                                    ):
                                        rzf, paths = await loop.run_in_executor(
                                            pool, get_zip_http, url
                                        )

                                    try:
                                        i_e_buttons = await make_keyboard(
                                            paths=paths,
                                            user_id=user_id,
                                            chat_id=query.message.chat.id,
                                            unziphttp=True,
                                            rzfile=rzf,
                                        )

                                        try:
                                            await query.message.edit(
                                                text=messages.get(
                                                    file="callbacks",
                                                    key="SELECT_FILES",
                                                    user_id=uid,
                                                ),
                                                reply_markup=i_e_buttons,
                                            )
                                        except ReplyMarkupTooLong:
                                            empty_buttons = await make_keyboard_empty(
                                                user_id=user_id,
                                                chat_id=query.message.chat.id,
                                                unziphttp=True,
                                                rzfile=rzf,
                                            )
                                            await query.message.edit(
                                                text=messages.get(
                                                    file="callbacks",
                                                    key="UNABLE_GATHER_FILES",
                                                    user_id=uid,
                                                ),
                                                reply_markup=empty_buttons,
                                            )
                                    except:
                                        try:
                                            await query.message.delete()
                                            i_e_buttons = await make_keyboard(
                                                paths=paths,
                                                user_id=user_id,
                                                chat_id=query.message.chat.id,
                                                unziphttp=True,
                                                rzfile=rzf,
                                            )
                                            await unzip_bot.send_message(
                                                chat_id=query.message.chat.id,
                                                text=messages.get(
                                                    file="callbacks",
                                                    key="SELECT_FILES",
                                                    user_id=uid,
                                                ),
                                                reply_markup=i_e_buttons,
                                            )
                                        except:
                                            try:
                                                await query.message.delete()
                                                empty_buttons = (
                                                    await make_keyboard_empty(
                                                        user_id=user_id,
                                                        chat_id=query.message.chat.id,
                                                        unziphttp=True,
                                                        rzfile=rzf,
                                                    )
                                                )
                                                await unzip_bot.send_message(
                                                    chat_id=query.message.chat.id,
                                                    text=messages.get(
                                                        file="callbacks",
                                                        key="UNABLE_GATHER_FILES",
                                                        user_id=uid,
                                                    ),
                                                    reply_markup=empty_buttons,
                                                )
                                            except:
                                                pass
                                except Exception as e:
                                    """
                                    LOGGER.error(
                                        msg=messages.get(
                                            file="callbacks",
                                            key="UNZIP_HTTP",
                                            extra_args=[url, e],
                                        )
                                    )
                                    """
                                    pass

                            try:
                                dled = await download_with_progress(
                                    url=url,
                                    path=archive,
                                    message=query.message,
                                    unzip_bot=unzip_bot,
                                )
                            except Exception as e:
                                dled = False
                                """
                                LOGGER.error(
                                    msg=messages.get(
                                        file="callbacks", key="ERR_DL", extra_args=e
                                    )
                                )
                                """

                            if isinstance(dled, bool) and not dled:
                                return

                            e_time = time()
                            await send_url_logs(
                                unzip_bot=unzip_bot,
                                c_id=Config.LOGS_CHANNEL,
                                doc_f=archive,
                                source=url,
                                message=query.message,
                            )
                        else:
                            await del_ongoing_task(user_id)
                            await query.message.edit(
                                text=messages.get(
                                    file="callbacks", key="CANT_DL_URL", user_id=uid
                                )
                            )

                            try:
                                shutil.rmtree(f"{Config.DOWNLOAD_LOCATION}/{user_id}")
                            except:
                                pass

                            return

            elif split_data[1] == "tg_file":
                if r_message.document is None:
                    await del_ongoing_task(user_id)
                    await query.message.edit(
                        text=messages.get(
                            file="callbacks", key="GIVE_ARCHIVE", user_id=uid
                        )
                    )

                    return

                fname = safe_download_name(r_message.document.file_name) or "download"
                rfnamebro = fname
                archive_msg = await r_message.forward(chat_id=Config.LOGS_CHANNEL)
                await log_msg.edit(
                    text=messages.get(
                        file="callbacks",
                        key="LOG_TXT",
                        extra_args=[
                            user_id,
                            fname,
                            humanbytes(r_message.document.file_size),
                        ],
                    )
                )

                if split_data[2] not in ["thumb", "thumbrename"]:
                    fext = fname.split(sep=".")[-1].casefold()

                    if (
                        fnmatch(name=fext, pat=extentions_list["split"][0])
                        or fext in extentions_list["split"]
                        or bool(re.search(pattern=rar_file_pattern, string=fname))
                    ):
                        await query.message.edit(
                            text=messages.get(
                                file="callbacks", key="ITS_SPLITTED", user_id=uid
                            )
                        )

                        return

                    if bool(re.search(pattern=split_file_pattern, string=fname)):
                        await del_ongoing_task(user_id)
                        await query.message.edit(
                            text=messages.get(
                                file="callbacks", key="SPL_RZ", user_id=uid
                            )
                        )

                        return

                    if fext not in extentions_list["archive"]:
                        await del_ongoing_task(user_id)
                        await query.message.edit(
                            text=messages.get(
                                file="callbacks", key="DEF_NOT_AN_ARCHIVE", user_id=uid
                            )
                        )

                        return

                os.makedirs(name=download_path, exist_ok=True)
                s_time = time()
                location = os.path.join(download_path, fname)
                # LOGGER.info("location: %s", location)
                archive = await r_message.download(
                    file_name=location,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        messages.get(file="callbacks", key="TRY_DL", user_id=uid),
                        query.message,
                        s_time,
                        unzip_bot,
                    ),
                )
                e_time = time()
            else:
                await del_ongoing_task(user_id)
                await answer_query(
                    query=query,
                    message_text=messages.get(
                        file="callbacks", key="QUERY_PARSE_ERR", user_id=uid
                    ),
                    answer_only=True,
                    unzip_client=unzip_bot,
                )

                return

            if split_data[2].startswith("thumb"):
                await query.message.edit(
                    text=messages.get(file="callbacks", key="PROCESSING2", user_id=uid)
                )
                archive_name = location.split("/")[-1]

                if "rename" in split_data[2]:
                    newname = await unzip_bot.ask(
                        chat_id=user_id,
                        text=messages.get(
                            file="callbacks",
                            key="GIVE_NEW_NAME",
                            user_id=uid,
                            extra_args=rfnamebro,
                        ),
                    )
                    renamed = location.replace(archive_name, newname.text)
                else:
                    renamed = location.replace(archive_name, rfnamebro)

                try:
                    shutil.move(src=location, dst=renamed)
                except OSError as e:
                    await del_ongoing_task(user_id)
                    # LOGGER.error(msg=e)

                    return

                newfname = renamed.split(sep="/")[-1]
                fsize = await get_size(renamed)

                if fsize <= Config.TG_MAX_SIZE:
                    await send_file(
                        unzip_bot=unzip_bot,
                        c_id=user_id,
                        doc_f=renamed,
                        query=query,
                        full_path=renamed,
                        split=False,
                    )
                    await query.message.delete()
                    await del_ongoing_task(user_id)

                    return shutil.rmtree(f"{Config.DOWNLOAD_LOCATION}/{user_id}")

                await query.message.edit(
                    text=messages.get(
                        file="callbacks",
                        key="SPLITTING",
                        user_id=uid,
                        extra_args=newfname,
                    )
                )
                splitdir = f"{Config.DOWNLOAD_LOCATION}/split/{user_id}"
                os.makedirs(name=splitdir, exist_ok=True)
                ooutput = f"{splitdir}/{newfname}"
                splitfiles = await split_files(
                    iinput=renamed, ooutput=ooutput, size=Config.TG_MAX_SIZE
                )

                if not splitfiles:
                    try:
                        shutil.rmtree(splitdir)
                    except:
                        pass

                    await del_ongoing_task(user_id)
                    await query.message.edit(
                        text=messages.get(
                            file="callbacks", key="ERR_SPLIT", user_id=uid
                        )
                    )

                    return

                await query.message.edit(
                    text=messages.get(
                        file="callbacks",
                        key="SEND_ALL_PARTS",
                        user_id=uid,
                        extra_args=newfname,
                    )
                )
                async_splitfiles = async_generator(splitfiles)

                async for file in async_splitfiles:
                    sent_files += 1
                    await send_file(
                        unzip_bot=unzip_bot,
                        c_id=user_id,
                        doc_f=file,
                        query=query,
                        full_path=splitdir,
                        split=True,
                    )

                try:
                    shutil.rmtree(splitdir)
                    shutil.rmtree(renamed.replace(newfname, ""))
                except:
                    pass

                await del_ongoing_task(user_id)

                try:
                    await unzip_bot.send_message(
                        chat_id=user_id,
                        text=messages.get(
                            file="callbacks", key="UPLOADED", user_id=uid
                        ),
                        reply_markup=Buttons.RATE_ME,
                    )
                    await query.message.edit(
                        text=messages.get(
                            file="callbacks", key="UPLOADED", user_id=uid
                        ),
                        reply_markup=Buttons.RATE_ME,
                    )
                except:
                    pass

                return

            dltime = TimeFormatter(round(number=e_time - s_time) * 1000)

            if dltime == "":
                dltime = "1s"

            await answer_query(
                query=query,
                message_text=messages.get(
                    file="callbacks",
                    key="AFTER_OK_DL_TXT",
                    user_id=uid,
                    extra_args=dltime,
                ),
                unzip_client=unzip_bot,
            )

            # Attempt to fetch password protected archives
            if split_data[2] == "with_pass":
                password = await unzip_bot.ask(
                    chat_id=query.message.chat.id,
                    text=messages.get(
                        file="callbacks", key="PLS_SEND_PASSWORD", user_id=uid
                    ),
                )
                ext_s_time = time()
                extractor = await extr_files(
                    path=ext_files_dir, archive_path=archive, password=password.text
                )
                ext_e_time = time()
                await archive_msg.reply(
                    messages.get(
                        file="callbacks", key="PASS_TXT", extra_args=password.text
                    )
                )
            else:
                ext_s_time = time()

                if fext in ("rar", "cbr"):
                    tested = await test_with_unrar_helper(archive)
                elif fext in ("arc", "wrc"):
                    tested = await test_with_unarc_helper(archive)
                elif fext == "pea":
                    tested = await test_with_pea_helper(archive)
                elif fext == "md5":
                    tested = tarfile.is_tarfile(archive) and await test_with_7z_helper(archive)
                else:
                    tested = await test_with_7z_helper(archive)

                ext_t_time = time()
                testtime = TimeFormatter(round(number=ext_t_time - ext_s_time) * 1000)

                if testtime == "":
                    testtime = "1s"

                await answer_query(
                    query=query,
                    message_text=messages.get(
                        file="callbacks",
                        key="AFTER_OK_TEST_TXT",
                        user_id=uid,
                        extra_args=testtime,
                    ),
                    unzip_client=unzip_bot,
                )

                if tested:
                    extractor = await extr_files(
                        path=ext_files_dir, archive_path=archive
                    )
                    ext_e_time = time()
                else:
                    # LOGGER.info(msg="Error on test")
                    extractor = "Error"
                    ext_e_time = time()

            # Checks if there is an error happened while extracting the archive
            if any(err in extractor for err in ERROR_MSGS):
                try:
                    await query.message.edit(
                        text=messages.get(
                            file="callbacks", key="EXT_FAILED_TXT", user_id=uid
                        )
                    )
                    shutil.rmtree(ext_files_dir)
                    await del_ongoing_task(user_id)
                    await log_msg.reply(
                        text=messages.get(file="callbacks", key="EXT_FAILED_TXT")
                    )

                    return
                except:
                    try:
                        await query.message.delete()
                    except:
                        pass

                    await unzip_bot.send_message(
                        chat_id=query.message.chat.id,
                        text=messages.get(
                            file="callbacks", key="EXT_FAILED_TXT", user_id=uid
                        ),
                    )
                    shutil.rmtree(ext_files_dir)
                    await del_ongoing_task(user_id)
                    await archive_msg.reply(
                        messages.get(file="callbacks", key="EXT_FAILED_TXT")
                    )

                    return

            # Check if user was dumb 😐
            paths = await get_files(path=ext_files_dir)

            if not paths:
                await archive_msg.reply(
                    messages.get(file="callbacks", key="PASSWORD_PROTECTED")
                )
                await unzip_bot.send_message(
                    chat_id=query.message.chat.id,
                    text=messages.get(
                        file="callbacks", key="PASSWORD_PROTECTED", user_id=uid
                    ),
                )
                await answer_query(
                    query=query,
                    message_text=messages.get(
                        file="callbacks", key="EXT_FAILED_TXT", user_id=uid
                    ),
                    unzip_client=unzip_bot,
                )
                shutil.rmtree(ext_files_dir)
                await del_ongoing_task(user_id)

                return

            # Upload extracted files
            extrtime = TimeFormatter(round(number=ext_e_time - ext_s_time) * 1000)

            if extrtime == "":
                extrtime = "1s"

            await answer_query(
                query=query,
                message_text=messages.get(
                    file="callbacks", key="EXT_OK_TXT", user_id=uid, extra_args=extrtime
                ),
                unzip_client=unzip_bot,
            )

            try:
                i_e_buttons = await make_keyboard(
                    paths=paths,
                    user_id=user_id,
                    chat_id=query.message.chat.id,
                    unziphttp=False,
                )

                try:
                    await query.message.edit(
                        text=messages.get(
                            file="callbacks", key="SELECT_FILES", user_id=uid
                        ),
                        reply_markup=i_e_buttons,
                    )
                except ReplyMarkupTooLong:
                    empty_buttons = await make_keyboard_empty(
                        user_id=user_id, chat_id=query.message.chat.id, unziphttp=False
                    )
                    await query.message.edit(
                        text=messages.get(
                            file="callbacks", key="UNABLE_GATHER_FILES", user_id=uid
                        ),
                        reply_markup=empty_buttons,
                    )
            except:
                try:
                    await query.message.delete()
                    i_e_buttons = await make_keyboard(
                        paths=paths,
                        user_id=user_id,
                        chat_id=query.message.chat.id,
                        unziphttp=False,
                    )
                    await unzip_bot.send_message(
                        chat_id=query.message.chat.id,
                        text=messages.get(
                            file="callbacks", key="SELECT_FILES", user_id=uid
                        ),
                        reply_markup=i_e_buttons,
                    )
                except:
                    try:
                        await query.message.delete()
                        empty_buttons = await make_keyboard_empty(
                            user_id=user_id,
                            chat_id=query.message.chat.id,
                            unziphttp=False,
                        )
                        await unzip_bot.send_message(
                            chat_id=query.message.chat.id,
                            text=messages.get(
                                file="callbacks", key="UNABLE_GATHER_FILES", user_id=uid
                            ),
                            reply_markup=empty_buttons,
                        )
                    except:
                        await answer_query(
                            query=query,
                            message_text=messages.get(
                                file="callbacks", key="EXT_FAILED_TXT", user_id=uid
                            ),
                            unzip_client=unzip_bot,
                        )
                        await archive_msg.reply(
                            messages.get(
                                file="callbacks", key="EXT_FAILED_TXT", user_id=uid
                            )
                        )
                        shutil.rmtree(ext_files_dir)
                        """
                        LOGGER.error(
                            msg=messages.get(file="callbacks", key="FATAL_ERROR")
                        )
                        """
                        await del_ongoing_task(user_id)

                        return

        except Exception as e:
            await del_ongoing_task(user_id)

            try:
                try:
                    await query.message.edit(
                        text=messages.get(
                            file="callbacks", key="ERROR_TXT", user_id=uid, extra_args=e
                        )
                    )
                except:
                    await unzip_bot.send_message(
                        chat_id=query.message.chat.id,
                        text=messages.get(
                            file="callbacks", key="ERROR_TXT", user_id=uid, extra_args=e
                        ),
                    )

                await archive_msg.reply(
                    messages.get(file="callbacks", key="ERROR_TXT", extra_args=e)
                )
                shutil.rmtree(ext_files_dir)

                try:
                    await ClientSession().close()
                except:
                    pass

                # LOGGER.error(msg=e)
            except Exception as err:
                # LOGGER.error(msg=err)
                await archive_msg.reply(err)

    elif query.data.startswith("ext_f"):
        # LOGGER.info(msg=query.data)
        user_id = query.from_user.id
        spl_data = query.data.split("|")
        paths_for_user = resolve_extraction_paths(
            spl_data, "ext_f", user_id, query.message.chat.id, Config.DOWNLOAD_LOCATION
        )
        if paths_for_user is None:
            await answer_query(
                query=query, message_text="Invalid request.", answer_only=True
            )
            return
        user_root, file_path = paths_for_user

        try:
            urled = spl_data[4] if isinstance(spl_data[4], bool) else False
        except:
            urled = False

        if urled:
            paths = spl_data[5].namelist()
        else:
            paths = await get_files(path=file_path)

        if not urled and not extracted_files_are_safe(paths, file_path):
            await answer_query(
                query=query, message_text="Invalid request.", answer_only=True
            )
            return

        if not paths and not urled:
            if os.path.isdir(user_root):
                shutil.rmtree(user_root)

            await del_ongoing_task(user_id)
            await query.message.edit(
                text=messages.get(file="callbacks", key="NO_FILE_LEFT", user_id=uid),
                reply_markup=Buttons.RATE_ME,
            )

            return

        # LOGGER.info(msg="ext_f paths : " + str(paths))

        try:
            await query.message.edit(
                text=messages.get(
                    file="callbacks", key="UPLOADING_THIS_FILE", user_id=uid
                )
            )
        except:
            pass

        sent_files += 1

        if urled:
            file = spl_data[5].open(paths[int(spl_data[3])])
        else:
            file = paths[int(spl_data[3])]

        fsize = await get_size(file)
        split = False

        if fsize <= Config.TG_MAX_SIZE:
            await send_file(
                unzip_bot=unzip_bot,
                c_id=spl_data[2],
                doc_f=file,
                query=query,
                full_path=user_root,
                split=False,
            )
        else:
            split = True

        if split:
            fname = file.split("/")[-1]
            smessage = await unzip_bot.send_message(
                chat_id=user_id,
                text=messages.get(
                    file="callbacks", key="SPLITTING", user_id=uid, extra_args=fname
                ),
            )
            splitdir = f"{Config.DOWNLOAD_LOCATION}/split/{user_id}"
            os.makedirs(name=splitdir, exist_ok=True)
            ooutput = f"{splitdir}/{fname}"
            splitfiles = await split_files(
                iinput=file, ooutput=ooutput, size=Config.TG_MAX_SIZE
            )
            # LOGGER.info(msg=splitfiles)

            if not splitfiles:
                try:
                    shutil.rmtree(splitdir)
                except:
                    pass

                await del_ongoing_task(user_id)
                await smessage.edit(
                    text=messages.get(file="callbacks", key="ERR_SPLIT", user_id=uid)
                )

                return

            await smessage.edit(
                text=messages.get(
                    file="callbacks",
                    key="SEND_ALL_PARTS",
                    user_id=uid,
                    extra_args=fname,
                )
            )
            async_splitfiles = async_generator(splitfiles)

            original_file = file
            async for s_file in async_splitfiles:
                sent_files += 1
                await send_file(
                    unzip_bot=unzip_bot,
                    c_id=user_id,
                    doc_f=s_file,
                    query=query,
                    full_path=splitdir,
                    split=True,
                )

            try:
                shutil.rmtree(splitdir)
                os.remove(path=original_file + "_temp")
            except:
                pass

            try:
                await smessage.delete()
            except:
                pass

        await query.message.edit(
            text=messages.get(file="callbacks", key="REFRESHING", user_id=uid)
        )

        if urled:
            rpaths = paths.remove(paths[int(spl_data[3])])
        else:
            rpaths = await get_files(path=file_path)

        if not rpaths:
            try:
                shutil.rmtree(user_root)
            except:
                pass

            await del_ongoing_task(user_id)
            await query.message.edit(
                text=messages.get(file="callbacks", key="NO_FILE_LEFT", user_id=uid),
                reply_markup=Buttons.RATE_ME,
            )

            return

        if urled:
            try:
                i_e_buttons = await make_keyboard(
                    paths=rpaths,
                    user_id=query.from_user.id,
                    chat_id=query.message.chat.id,
                    unziphttp=True,
                    rzfile=spl_data[5],
                )
                await query.message.edit(
                    text=messages.get(
                        file="callbacks", key="SELECT_FILES", user_id=uid
                    ),
                    reply_markup=i_e_buttons,
                )
            except ReplyMarkupTooLong:
                empty_buttons = await make_keyboard_empty(
                    user_id=user_id,
                    chat_id=query.message.chat.id,
                    unziphttp=True,
                    rzfile=spl_data[5],
                )
                await query.message.edit(
                    text=messages.get(
                        file="callbacks", key="UNABLE_GATHER_FILES", user_id=uid
                    ),
                    reply_markup=empty_buttons,
                )
        else:
            try:
                i_e_buttons = await make_keyboard(
                    paths=rpaths,
                    user_id=query.from_user.id,
                    chat_id=query.message.chat.id,
                    unziphttp=False,
                )
                await query.message.edit(
                    text=messages.get(
                        file="callbacks", key="SELECT_FILES", user_id=uid
                    ),
                    reply_markup=i_e_buttons,
                )
            except ReplyMarkupTooLong:
                empty_buttons = await make_keyboard_empty(
                    user_id=user_id, chat_id=query.message.chat.id, unziphttp=False
                )
                await query.message.edit(
                    text=messages.get(
                        file="callbacks", key="UNABLE_GATHER_FILES", user_id=uid
                    ),
                    reply_markup=empty_buttons,
                )

        await update_uploaded(user_id=user_id, upload_count=sent_files)

    elif query.data.startswith("ext_a"):
        # LOGGER.info(msg=query.data)
        user_id = query.from_user.id
        spl_data = query.data.split("|")
        paths_for_user = resolve_extraction_paths(
            spl_data, "ext_a", user_id, query.message.chat.id, Config.DOWNLOAD_LOCATION
        )
        if paths_for_user is None:
            await answer_query(
                query=query, message_text="Invalid request.", answer_only=True
            )
            return
        user_root, file_path = paths_for_user
        log_msg = await get_task_log_message(unzip_bot, user_id)

        try:
            urled = spl_data[4] if isinstance(spl_data[3], bool) else False
        except:
            urled = False

        if urled:
            paths = spl_data[4].namelist()
        else:
            paths = await get_files(path=file_path)

        if not urled and not extracted_files_are_safe(paths, file_path):
            await answer_query(
                query=query, message_text="Invalid request.", answer_only=True
            )
            return

        # LOGGER.info("ext_a paths : " + str(paths))

        if not paths and not urled:
            try:
                shutil.rmtree(user_root)
            except:
                pass

            await del_ongoing_task(user_id)
            await query.message.edit(
                text=messages.get(file="callbacks", key="NO_FILE_LEFT", user_id=uid),
                reply_markup=Buttons.RATE_ME,
            )

            return

        await query.message.edit(
            text=messages.get(file="callbacks", key="SENDING_ALL_FILES", user_id=uid)
        )
        async_paths = async_generator(paths)

        async for file in async_paths:
            sent_files += 1

            if urled:
                file = spl_data[4].open(file)
                # security as we can't always retrieve the file size from URL
                fsize = Config.TG_MAX_SIZE + 1
            else:
                fsize = await get_size(file)

            split = False

            if fsize <= Config.TG_MAX_SIZE:
                await send_file(
                    unzip_bot=unzip_bot,
                    c_id=spl_data[2],
                    doc_f=file,
                    query=query,
                    full_path=user_root,
                    split=False,
                )
            else:
                split = True

            if split:
                fname = file.split("/")[-1]
                smessage = await unzip_bot.send_message(
                    chat_id=user_id,
                    text=messages.get(
                        file="callbacks", key="SPLITTING", user_id=uid, extra_args=fname
                    ),
                )
                splitdir = f"{Config.DOWNLOAD_LOCATION}/split/{user_id}"
                os.makedirs(name=splitdir, exist_ok=True)
                ooutput = f"{splitdir}/{fname}"
                splitfiles = await split_files(
                    iinput=file, ooutput=ooutput, size=Config.TG_MAX_SIZE
                )
                # LOGGER.info(msg=splitfiles)

                if not splitfiles:
                    try:
                        shutil.rmtree(splitdir)
                    except:
                        pass

                    await del_ongoing_task(user_id)
                    await smessage.edit(
                        text=messages.get(
                            file="callbacks", key="ERR_SPLIT", user_id=uid
                        )
                    )

                    return

                await smessage.edit(
                    text=messages.get(
                        file="callbacks",
                        key="SEND_ALL_PARTS",
                        user_id=uid,
                        extra_args=fname,
                    )
                )
                async_splitfiles = async_generator(splitfiles)

                async for s_file in async_splitfiles:
                    sent_files += 1
                    await send_file(
                        unzip_bot=unzip_bot,
                        c_id=user_id,
                        doc_f=s_file,
                        query=query,
                        full_path=splitdir,
                        split=True,
                    )

                try:
                    shutil.rmtree(splitdir)
                    os.remove(path=file + "_temp")
                except:
                    pass

                try:
                    await smessage.delete()
                except:
                    pass

        try:
            await unzip_bot.send_message(
                chat_id=user_id,
                text=messages.get(file="callbacks", key="UPLOADED", user_id=uid),
                reply_markup=Buttons.RATE_ME,
            )
            await query.message.edit(
                text=messages.get(file="callbacks", key="UPLOADED", user_id=uid),
                reply_markup=Buttons.RATE_ME,
            )
        except:
            pass

        if log_msg:
            await log_msg.reply(
                messages.get(
                    file="callbacks", key="HOW_MANY_UPLOADED", extra_args=sent_files
                )
            )
        await update_uploaded(user_id=user_id, upload_count=sent_files)
        await del_ongoing_task(user_id)

        try:
            shutil.rmtree(user_root)
        except Exception as e:
            await query.message.edit(
                text=messages.get(
                    file="callbacks", key="ERROR_TXT", user_id=uid, extra_args=e
                )
            )
            if log_msg:
                await log_msg.reply(
                    messages.get(file="callbacks", key="ERROR_TXT", extra_args=e)
                )

    elif query.data == "cancel_dis":
        uid = query.from_user.id
        log_msg = await get_task_log_message(unzip_bot, uid)
        await del_ongoing_task(uid)
        await del_merge_task(uid)

        try:
            await query.message.edit(
                text=messages.get(
                    file="callbacks",
                    key="CANCELLED_TXT",
                    user_id=uid,
                    extra_args=messages.get(
                        file="callbacks", key="PROCESS_CANCELLED", user_id=uid
                    ),
                )
            )
            shutil.rmtree(f"{Config.DOWNLOAD_LOCATION}/{uid}")
            await update_uploaded(user_id=uid, upload_count=sent_files)

            if log_msg:
                try:
                    await log_msg.reply(
                        messages.get(
                            file="callbacks", key="HOW_MANY_UPLOADED", extra_args=sent_files
                        )
                    )
                except:
                    return
        except:
            await unzip_bot.send_message(
                chat_id=uid,
                text=messages.get(
                    file="callbacks",
                    key="CANCELLED_TXT",
                    user_id=uid,
                    extra_args=messages.get(
                        file="callbacks", key="PROCESS_CANCELLED", user_id=uid
                    ),
                ),
            )

            return

    elif query.data == "nobully":
        await query.message.edit(
            text=messages.get(file="callbacks", key="CANCELLED", user_id=uid)
        )
