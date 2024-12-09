import asyncio
import concurrent.futures
import os
import re
import shutil
from email.parser import Parser
from email.policy import default
from fnmatch import fnmatch
from time import time
from urllib.parse import unquote

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
    get_ongoing_tasks,
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
    test_with_7z_helper,
    test_with_unrar_helper,
    extr_files,
    get_files,
    make_keyboard,
    make_keyboard_empty,
    merge_files,
    split_files,
)
from .ext_script.up_helper import answer_query, get_size, send_file, send_url_logs


split_file_pattern = r"\.z\d+$"
rar_file_pattern = r"\.(?:r\d+|part\d+\.rar)$"
volume_file_pattern = r"\.\d+$"
telegram_url_pattern = r"(?:http[s]?:\/\/)?(?:www\.)?t\.me\/([a-zA-Z0-9_]+)\/(\d+)"
messages = Messages(lang_fetcher=get_lang)


# Function to extract the sequence number from filenames
def get_sequence_number(filename, pattern):
    match = re.search(pattern, filename)

    if match:
        # Extract the numeric part from the matched pattern
        num_match = re.findall(r"\d+", match.group())

        if num_match:
            return int(num_match[-1])

    # Use infinity if no number is found (ensures this file is always last)
    return float("inf")


# Function to find the file with the lowest sequence
def find_lowest_sequence_file(files):
    if not files:
        raise IndexError("No files to match")

    # Match the files against the patterns
    rar_matches = [f for f in files if re.search(rar_file_pattern, f)]
    volume_matches = [f for f in files if re.search(volume_file_pattern, f)]

    # Handle RAR pattern cases
    if rar_matches:
        # Separate .rX and .partX.rar cases
        r_files = [
            f for f in rar_matches if f.endswith(".rar") or re.search(r"\.r\d+$", f)
        ]
        part_files = [f for f in rar_matches if re.search(r"part\d+\.rar$", f)]

        # Priority: .partX.rar -> .rX
        if part_files:
            return min(part_files, key=lambda x: get_sequence_number(x, r"part\d+")), "rar"
        elif r_files:
            return min(r_files, key=lambda x: get_sequence_number(x, r"\.r\d+$")), "rar"

    # Handle other cases
    if volume_matches:
        return min(volume_matches, key=lambda x: get_sequence_number(x, r"\.\d+$")), "volume"

    raise IndexError("No matching files found")


async def download(url, path):
    try:
        async with ClientSession() as session, session.get(
            url, timeout=None, allow_redirects=True
        ) as resp, openfile(path, mode="wb") as file:
            async for chunk in resp.content.iter_chunked(Config.CHUNK_SIZE):
                await file.write(chunk)
    except InvalidURL:
        LOGGER.error(messages.get("callbacks", "INVALID_URL"))
    except Exception:
        LOGGER.error(messages.get("callbacks", "ERR_DL", None, url))


async def download_with_progress(url, path, message, unzip_bot):
    uid = message.from_user.id

    try:
        async with ClientSession() as session, session.get(
            url, timeout=None, allow_redirects=True
        ) as resp:
            total_size = int(resp.headers.get("Content-Length", 0))
            current_size = 0
            start_time = time()

            async with openfile(path, mode="wb") as file:
                async for chunk in resp.content.iter_chunked(Config.CHUNK_SIZE):
                    if message.from_user is not None and await get_cancel_task(uid):
                        await message.edit(
                            text=messages.get("callbacks", "DL_STOPPED", uid)
                        )
                        await del_cancel_task(uid)

                        return False

                    await file.write(chunk)
                    current_size += len(chunk)
                    await progress_for_pyrogram(
                        current_size,
                        total_size,
                        messages.get("callbacks", "DL_URL", uid, url),
                        message,
                        start_time,
                        unzip_bot,
                    )
    except Exception:
        LOGGER.error(messages.get("callbacks", "ERR_DL", None, url))


def get_zip_http(url):
    rzf = unzip_http.RemoteZipFile(url)
    paths = rzf.namelist()
    return rzf, paths


async def async_generator(iterable):
    for item in iterable:
        yield item


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
                        "callbacks", "MAX_TASKS", uid, Config.MAX_CONCURRENT_TASKS
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
        await answer_query(query, messages.get("callbacks", "MAINTENANCE_ON", uid))

        return

    sent_files = 0
    global log_msg

    if query.data == "megoinhome":
        await query.edit_message_text(
            text=messages.get("callbacks", "START_TEXT", uid, query.from_user.mention),
            reply_markup=Buttons.START_BUTTON,
        )

    elif query.data == "helpcallback":
        await query.edit_message_text(
            text=messages.get("callbacks", "HELP_TXT", uid),
            reply_markup=Buttons.ME_GOIN_HOME,
        )

    elif query.data == "aboutcallback":
        await query.edit_message_text(
            text=messages.get("callbacks", "ABOUT_TXT", uid, Config.VERSION),
            reply_markup=Buttons.ME_GOIN_HOME,
            disable_web_page_preview=True,
        )

    elif query.data == "donatecallback":
        await query.edit_message_text(
            text=messages.get("callbacks", "DONATE_TEXT", uid),
            reply_markup=Buttons.ME_GOIN_HOME,
            disable_web_page_preview=True,
        )

    elif query.data.startswith("statscallback"):
        if query.data.endswith("refresh"):
            await query.edit_message_text(
                text=messages.get("callbacks", "REFRESH_STATS", uid)
            )
        text_stats = await get_stats(query.from_user.id)
        await query.edit_message_text(
            text=text_stats,
            reply_markup=Buttons.REFRESH_BUTTON,
        )

    elif query.data == "canceldownload":
        await add_cancel_task(query.from_user.id)

    elif query.data == "check_thumb":
        user_id = query.from_user.id
        thumb_location = Config.THUMB_LOCATION + "/" + str(user_id) + ".jpg"
        await unzip_bot.send_photo(
            chat_id=user_id,
            photo=thumb_location,
            caption=messages.get("callbacks", "ACTUAL_THUMB", uid),
        )
        await unzip_bot.delete_messages(chat_id=user_id, message_ids=query.message.id)
        await unzip_bot.send_message(
            chat_id=user_id,
            text=messages.get("callbacks", "EXISTING_THUMB", uid),
            reply_markup=Buttons.THUMB_FINAL,
        )

    elif query.data == "check_before_del":
        user_id = query.from_user.id
        thumb_location = Config.THUMB_LOCATION + "/" + str(user_id) + ".jpg"
        await unzip_bot.send_photo(
            chat_id=user_id,
            photo=thumb_location,
            caption=messages.get("callbacks", "ACTUAL_THUMB", uid),
        )
        await unzip_bot.delete_messages(chat_id=user_id, message_ids=query.message.id)
        await unzip_bot.send_message(
            chat_id=user_id,
            text=messages.get("callbacks", "DEL_CONFIRM_THUMB_2", uid),
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
            LOGGER.warning(messages.get("callbacks", "ERROR_THUMB_RENAME", None))
            LOGGER.error(e)

        try:
            await update_thumb(query.from_user.id)
        except:
            LOGGER.error(messages.get("callbacks", "ERROR_THUMB_UPDATE", None))

        await answer_query(query, messages.get("callbacks", "SAVED_THUMBNAIL", uid))

    elif query.data == "del_thumb":
        user_id = query.from_user.id
        thumb_location = Config.THUMB_LOCATION + "/" + str(user_id) + ".jpg"

        try:
            await del_thumb_db(user_id)
        except Exception as e:
            LOGGER.error(messages.get("callbacks", "ERROR_THUMB_DEL", None, e))

        try:
            os.remove(thumb_location)
        except:
            pass

        await query.edit_message_text(
            text=messages.get("callbacks", "DELETED_THUMB", uid)
        )

    elif query.data == "nope_thumb":
        user_id = query.from_user.id
        del_1 = Config.THUMB_LOCATION + "/not_resized_" + str(user_id) + ".jpg"
        del_2 = Config.THUMB_LOCATION + "/waiting_" + str(user_id) + ".jpg"

        try:
            os.remove(del_1)
        except:
            pass

        try:
            os.remove(del_2)
        except:
            pass

        await query.edit_message_text(
            text=messages.get(
                "callbacks",
                "CANCELLED_TXT",
                uid,
                messages.get("callbacks", "PROCESS_CANCELLED", uid),
            )
        )

    elif query.data.startswith("set_mode"):
        user_id = query.from_user.id
        mode = query.data.split("|")[1]
        await set_upload_mode(user_id, mode)
        await answer_query(
            query, messages.get("callbacks", "CHANGED_UPLOAD_MODE_TXT", uid, mode)
        )

    elif query.data == "merge_this":
        user_id = query.from_user.id
        m_id = query.message.id
        start_time = time()
        await add_ongoing_task(user_id, start_time, "merge")
        s_id = await get_merge_task_message_id(user_id)
        merge_msg = await query.message.edit(
            messages.get("callbacks", "PROCESSING_TASK", uid)
        )
        download_path = f"{Config.DOWNLOAD_LOCATION}/{user_id}/merge"

        if s_id and (m_id - s_id) > 1:
            files_array = list(range(s_id, m_id))

            try:
                messages_array = await unzip_bot.get_messages(user_id, files_array)
            except Exception as e:
                LOGGER.error(messages.get("callbacks", "ERROR_GET_MSG", None, e))
                await answer_query(
                    query, messages.get("callbacks", "ERROR_TXT", uid, e)
                )
                await del_ongoing_task(user_id)
                await del_merge_task(user_id)

                try:
                    shutil.rmtree(f"{Config.DOWNLOAD_LOCATION}/{user_id}")
                except:
                    pass

                return

            length = len(messages_array)
            os.makedirs(download_path, exist_ok=True)
            rs_time = time()
            newarray = []
            await merge_msg.edit(messages.get("callbacks", "PROCESS_MSGS", uid, length))

            for message in messages_array:
                if message.document is None:
                    pass
                else:
                    if message.from_user.id == user_id:
                        newarray.append(message)

            length = len(newarray)

            if length == 0:
                await answer_query(
                    query, messages.get("callbacks", "NO_MERGE_TASK", uid)
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
                fname = message.document.file_name
                await message.forward(chat_id=Config.LOGS_CHANNEL)
                location = f"{download_path}/{fname}"
                s_time = time()
                await message.download(
                    file_name=location,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        messages.get("callbacks", "DL_FILES", uid, i, length),
                        merge_msg,
                        s_time,
                        unzip_bot,
                    ),
                )

            e_time = time()
            dltime = TimeFormatter(round(e_time - rs_time) * 1000)

            if dltime == "":
                dltime = "1 s"

            await merge_msg.edit(
                messages.get("callbacks", "AFTER_OK_MERGE_DL_TXT", uid, i, dltime)
            )
            await merge_msg.edit(
                text=messages.get("callbacks", "CHOOSE_EXT_MODE_MERGE", uid),
                reply_markup=Buttons.CHOOSE_E_F_M__BTNS,
            )
            await del_merge_task(user_id)
        else:
            await answer_query(query, messages.get("callbacks", "NO_MERGE_TASK", uid))
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
        os.makedirs(ext_files_dir, exist_ok=True)

        try:
            files = await get_files(download_path)
            file, file_type = find_lowest_sequence_file(files)
        except IndexError:
            await answer_query(query, messages.get("callbacks", "NO_MERGE_TASK", uid))
            await del_ongoing_task(user_id)
            await del_merge_task(user_id)

            try:
                shutil.rmtree(f"{Config.DOWNLOAD_LOCATION}/{user_id}")
            except:
                pass

            return

        splitted_data = query.data.split("|")
        log_msg = await unzip_bot.send_message(
            chat_id=Config.LOGS_CHANNEL,
            text=messages.get(
                "callbacks",
                "PROCESS_MERGE",
                None,
                user_id,
                ".".join(file.split("/")[-1].split(".")[:-1]),
            ),
        )

        try:
            await query.message.edit(messages.get("callbacks", "PROCESSING_TASK", uid))
        except:
            pass

        if splitted_data[1] == "with_pass":
            password = await unzip_bot.ask(
                chat_id=query.message.chat.id,
                text=messages.get("callbacks", "PLS_SEND_PASSWORD", uid),
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
            extractor = await merge_files(iinput=file, ooutput=ext_files_dir, file_type=file_type)
            ext_e_time = time()

        # Checks if there is an error happened while extracting the archive
        if any(err in extractor for err in ERROR_MSGS):
            try:
                await query.message.edit(
                    messages.get("callbacks", "EXT_FAILED_TXT", uid)
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
                    text=messages.get("callbacks", "EXT_FAILED_TXT", uid),
                )
                shutil.rmtree(ext_files_dir)
                await del_ongoing_task(user_id)

            return

        # Check if user was dumb 😐
        paths = await get_files(path=ext_files_dir)

        if not paths:
            await unzip_bot.send_message(
                chat_id=query.message.chat.id,
                text=messages.get("callbacks", "PASSWORD_PROTECTED", uid),
            )
            await answer_query(
                query,
                messages.get("callbacks", "EXT_FAILED_TXT", uid),
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
        extrtime = TimeFormatter(round(ext_e_time - ext_s_time) * 1000)

        if extrtime == "":
            extrtime = "1s"
        await answer_query(
            query,
            messages.get("callbacks", "EXT_OK_TXT", uid, extrtime),
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
                    messages.get("callbacks", "SELECT_FILES", uid),
                    reply_markup=i_e_buttons,
                )
            except ReplyMarkupTooLong:
                empty_buttons = await make_keyboard_empty(
                    user_id=user_id, chat_id=query.message.chat.id, unziphttp=False
                )
                await query.message.edit(
                    messages.get("callbacks", "UNABLE_GATHER_FILES", uid),
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
                    text=messages.get("callbacks", "SELECT_FILES", uid),
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
                        text=messages.get("callbacks", "UNABLE_GATHER_FILES", uid),
                        reply_markup=empty_buttons,
                    )
                except:
                    await answer_query(
                        query,
                        messages.get("callbacks", "EXT_FAILED_TXT", uid),
                        unzip_client=unzip_bot,
                    )
                    shutil.rmtree(ext_files_dir)
                    LOGGER.error(messages.get("callbacks", "FATAL_ERROR", None))
                    await del_ongoing_task(user_id)

                    return

    elif query.data.startswith("extract_file"):
        user_id = query.from_user.id
        start_time = time()
        await add_ongoing_task(user_id, start_time, "extract")
        download_path = f"{Config.DOWNLOAD_LOCATION}/{user_id}"
        ext_files_dir = f"{download_path}/extracted"
        r_message = query.message.reply_to_message
        splitted_data = query.data.split("|")

        try:
            await query.message.edit(messages.get("callbacks", "PROCESSING_TASK", uid))
        except:
            pass

        log_msg = await unzip_bot.send_message(
            chat_id=Config.LOGS_CHANNEL,
            text=messages.get("callbacks", "USER_QUERY", None, user_id),
        )

        global archive_msg

        try:
            if splitted_data[1] == "url":
                url = r_message.text

                # Double check
                if not re.match(https_url_regex, url):
                    await del_ongoing_task(user_id)
                    await query.message.edit(
                        messages.get("callbacks", "INVALID_URL", uid)
                    )

                    return

                if re.match(telegram_url_pattern, url):
                    r_message = await unzip_bot.get_messages(
                        chat_id=url.split("/")[-2], message_ids=int(url.split("/")[-1])
                    )
                    splitted_data[1] = "tg_file"

                if splitted_data[1] == "url":
                    s = ClientSession()

                    async with s as session:
                        # Get the file size
                        unzip_head = await session.head(url, allow_redirects=True)
                        f_size = unzip_head.headers.get("content-length")
                        u_file_size = f_size if f_size else "undefined"

                        if u_file_size != "undefined" and not sufficient_disk_space(
                            int(u_file_size)
                        ):
                            await del_ongoing_task(user_id)
                            await query.message.edit(
                                messages.get("callbacks", "NO_SPACE", uid)
                            )

                            return

                        await log_msg.edit(
                            messages.get(
                                "callbacks", "LOG_TXT", None, user_id, url, u_file_size
                            )
                        )
                        archive_msg = log_msg
                        unzip_resp = await session.get(
                            url, timeout=None, allow_redirects=True
                        )

                        if "application/" not in unzip_resp.headers.get("content-type"):
                            await del_ongoing_task(user_id)
                            await query.message.edit(
                                messages.get("callbacks", "NOT_AN_ARCHIVE", uid)
                            )

                            return

                        content_disposition = unzip_head.headers.get(
                            "content-disposition"
                        )
                        rfnamebro = ""
                        real_filename = ""

                        if content_disposition:
                            headers = Parser(policy=default).parsestr(
                                f"Content-Disposition: {content_disposition}"
                            )
                            real_filename = headers.get_filename()

                            if real_filename != "":
                                rfnamebro = unquote(real_filename)

                        if rfnamebro == "":
                            rfnamebro = unquote(url.split("/")[-1])

                        if unzip_resp.status == 200:
                            os.makedirs(download_path, exist_ok=True)
                            s_time = time()

                            if real_filename:
                                archive = os.path.join(download_path, real_filename)
                                fext = real_filename.split(".")[-1].casefold()
                            else:
                                fname = unquote(os.path.splitext(url)[1])
                                fname = fname.split("?")[0]
                                fext = fname.split(".")[-1].casefold()
                                archive = f"{download_path}/{fname}"

                            if (
                                splitted_data[2] not in ["thumb", "thumbrename"]
                                and fext not in extentions_list["archive"]
                            ):
                                await del_ongoing_task(user_id)
                                await query.message.edit(
                                    messages.get("callbacks", "DEF_NOT_AN_ARCHIVE", uid)
                                )

                                try:
                                    shutil.rmtree(
                                        f"{Config.DOWNLOAD_LOCATION}/{user_id}"
                                    )
                                except:
                                    pass

                                return

                            await answer_query(
                                query,
                                messages.get("callbacks", "PROCESSING2", uid),
                                unzip_client=unzip_bot,
                            )

                            if (
                                fext == "zip"
                                and "accept-ranges" in unzip_resp.headers
                                and "content-length" in unzip_resp.headers
                            ):
                                try:
                                    loop = asyncio.get_event_loop()

                                    with concurrent.futures.ThreadPoolExecutor() as pool:
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
                                                messages.get(
                                                    "callbacks", "SELECT_FILES", uid
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
                                                messages.get(
                                                    "callbacks",
                                                    "UNABLE_GATHER_FILES",
                                                    uid,
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
                                                    "callbacks", "SELECT_FILES", uid
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
                                                        "callbacks",
                                                        "UNABLE_GATHER_FILES",
                                                        uid,
                                                    ),
                                                    reply_markup=empty_buttons,
                                                )
                                            except:
                                                pass
                                except Exception as e:
                                    LOGGER.error(
                                        messages.get(
                                            "callbacks", "UNZIP_HTTP", None, url, e
                                        )
                                    )

                            try:
                                dled = await download_with_progress(
                                    url, archive, query.message, unzip_bot
                                )
                            except Exception as e:
                                dled = False
                                LOGGER.error(
                                    messages.get("callbacks", "ERR_DL", None, e)
                                )

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
                                messages.get("callbacks", "CANT_DL_URL", uid)
                            )

                            try:
                                shutil.rmtree(f"{Config.DOWNLOAD_LOCATION}/{user_id}")
                            except:
                                pass

                            return

            elif splitted_data[1] == "tg_file":
                if r_message.document is None:
                    await del_ongoing_task(user_id)
                    await query.message.edit(
                        messages.get("callbacks", "GIVE_ARCHIVE", uid)
                    )

                    return

                fname = r_message.document.file_name
                rfnamebro = fname
                archive_msg = await r_message.forward(chat_id=Config.LOGS_CHANNEL)
                await log_msg.edit(
                    messages.get(
                        "callbacks",
                        "LOG_TXT",
                        None,
                        user_id,
                        fname,
                        humanbytes(r_message.document.file_size),
                    )
                )

                if splitted_data[2] not in ["thumb", "thumbrename"]:
                    fext = fname.split(".")[-1].casefold()

                    if (
                        fnmatch(fext, extentions_list["split"][0])
                        or fext in extentions_list["split"]
                        or bool(re.search(rar_file_pattern, fname))
                    ):
                        await query.message.edit(
                            messages.get("callbacks", "ITS_SPLITTED", uid)
                        )

                        return

                    if bool(re.search(split_file_pattern, fname)):
                        await del_ongoing_task(user_id)
                        await query.message.edit(
                            messages.get("callbacks", "SPL_RZ", uid)
                        )

                        return

                    if fext not in extentions_list["archive"]:
                        await del_ongoing_task(user_id)
                        await query.message.edit(
                            messages.get("callbacks", "DEF_NOT_AN_ARCHIVE", uid)
                        )

                        return

                os.makedirs(download_path, exist_ok=True)
                s_time = time()
                location = f"{download_path}/{fname}"
                LOGGER.info("location: %s", location)
                archive = await r_message.download(
                    file_name=location,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        messages.get("callbacks", "TRY_DL", uid),
                        query.message,
                        s_time,
                        unzip_bot,
                    ),
                )
                e_time = time()
            else:
                await del_ongoing_task(user_id)
                await answer_query(
                    query,
                    messages.get("callbacks", "QUERY_PARSE_ERR", uid),
                    answer_only=True,
                    unzip_client=unzip_bot,
                )

                return

            if splitted_data[2].startswith("thumb"):
                await query.message.edit(messages.get("callbacks", "PROCESSING2", uid))
                archive_name = location.split("/")[-1]

                if "rename" in splitted_data[2]:
                    newname = await unzip_bot.ask(
                        chat_id=user_id,
                        text=messages.get("callbacks", "GIVE_NEW_NAME", uid, rfnamebro),
                    )
                    renamed = location.replace(archive_name, newname.text)
                else:
                    renamed = location.replace(archive_name, rfnamebro)

                try:
                    shutil.move(location, renamed)
                except OSError as e:
                    await del_ongoing_task(user_id)
                    LOGGER.error(e)

                    return

                newfname = renamed.split("/")[-1]
                fsize = await get_size(renamed)

                if fsize <= Config.TG_MAX_SIZE:
                    await send_file(
                        unzip_bot=unzip_bot,
                        c_id=user_id,
                        doc_f=renamed,
                        query=query,
                        full_path=renamed,
                        log_msg=log_msg,
                        split=False,
                    )
                    await query.message.delete()
                    await del_ongoing_task(user_id)

                    return shutil.rmtree(f"{Config.DOWNLOAD_LOCATION}/{user_id}")

                await query.message.edit(
                    messages.get("callbacks", "SPLITTING", uid, newfname)
                )
                splitteddir = f"{Config.DOWNLOAD_LOCATION}/splitted/{user_id}"
                os.makedirs(splitteddir, exist_ok=True)
                ooutput = f"{splitteddir}/{newfname}"
                splittedfiles = await split_files(renamed, ooutput, Config.TG_MAX_SIZE)

                if not splittedfiles:
                    try:
                        shutil.rmtree(splitteddir)
                    except:
                        pass

                    await del_ongoing_task(user_id)
                    await query.message.edit(
                        messages.get("callbacks", "ERR_SPLIT", uid)
                    )

                    return

                await query.message.edit(
                    messages.get("callbacks", "SEND_ALL_PARTS", uid, newfname)
                )
                async_splittedfiles = async_generator(splittedfiles)

                async for file in async_splittedfiles:
                    sent_files += 1
                    await send_file(
                        unzip_bot=unzip_bot,
                        c_id=user_id,
                        doc_f=file,
                        query=query,
                        full_path=splitteddir,
                        log_msg=log_msg,
                        split=True,
                    )

                try:
                    shutil.rmtree(splitteddir)
                    shutil.rmtree(renamed.replace(newfname, ""))
                except:
                    pass

                await del_ongoing_task(user_id)

                try:
                    await unzip_bot.send_message(
                        chat_id=user_id,
                        text=messages.get("callbacks", "UPLOADED", uid),
                        reply_markup=Buttons.RATE_ME,
                    )
                    await query.message.edit(
                        text=messages.get("callbacks", "UPLOADED", uid),
                        reply_markup=Buttons.RATE_ME,
                    )
                except:
                    pass

                return

            dltime = TimeFormatter(round(e_time - s_time) * 1000)

            if dltime == "":
                dltime = "1s"

            await answer_query(
                query,
                messages.get("callbacks", "AFTER_OK_DL_TXT", uid, dltime),
                unzip_client=unzip_bot,
            )

            # Attempt to fetch password protected archives
            if splitted_data[2] == "with_pass":
                password = await unzip_bot.ask(
                    chat_id=query.message.chat.id,
                    text=messages.get("callbacks", "PLS_SEND_PASSWORD", uid),
                )
                ext_s_time = time()
                extractor = await extr_files(
                    path=ext_files_dir,
                    archive_path=archive,
                    password=password.text,
                )
                ext_e_time = time()
                await archive_msg.reply(
                    messages.get("callbacks", "PASS_TXT", None, password.text)
                )
            else:
                ext_s_time = time()

                if fext == "rar":
                    tested = await test_with_unrar_helper(archive)
                else:
                    tested = await test_with_7z_helper(archive)

                ext_t_time = time()
                testtime = TimeFormatter(round(ext_t_time - ext_s_time) * 1000)

                if testtime == "":
                    testtime = "1s"

                await answer_query(
                    query,
                    messages.get("callbacks", "AFTER_OK_TEST_TXT", uid, testtime),
                    unzip_client=unzip_bot,
                )

                if tested:
                    extractor = await extr_files(
                        path=ext_files_dir, archive_path=archive
                    )
                    ext_e_time = time()
                else:
                    LOGGER.info("Error on test")
                    extractor = "Error"
                    ext_e_time = time()

            # Checks if there is an error happened while extracting the archive
            if any(err in extractor for err in ERROR_MSGS):
                try:
                    await query.message.edit(
                        messages.get("callbacks", "EXT_FAILED_TXT", uid)
                    )
                    shutil.rmtree(ext_files_dir)
                    await del_ongoing_task(user_id)
                    await log_msg.reply(
                        messages.get("callbacks", "EXT_FAILED_TXT", None)
                    )

                    return
                except:
                    try:
                        await query.message.delete()
                    except:
                        pass

                    await unzip_bot.send_message(
                        chat_id=query.message.chat.id,
                        text=messages.get("callbacks", "EXT_FAILED_TXT", uid),
                    )
                    shutil.rmtree(ext_files_dir)
                    await del_ongoing_task(user_id)
                    await archive_msg.reply(
                        messages.get("callbacks", "EXT_FAILED_TXT", None)
                    )

                    return

            # Check if user was dumb 😐
            paths = await get_files(path=ext_files_dir)

            if not paths:
                await archive_msg.reply(
                    messages.get("callbacks", "PASSWORD_PROTECTED", None)
                )
                await unzip_bot.send_message(
                    chat_id=query.message.chat.id,
                    text=messages.get("callbacks", "PASSWORD_PROTECTED", uid),
                )
                await answer_query(
                    query,
                    messages.get("callbacks", "EXT_FAILED_TXT", uid),
                    unzip_client=unzip_bot,
                )
                shutil.rmtree(ext_files_dir)
                await del_ongoing_task(user_id)

                return

            # Upload extracted files
            extrtime = TimeFormatter(round(ext_e_time - ext_s_time) * 1000)

            if extrtime == "":
                extrtime = "1s"

            await answer_query(
                query,
                messages.get("callbacks", "EXT_OK_TXT", uid, extrtime),
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
                        messages.get("callbacks", "SELECT_FILES", uid),
                        reply_markup=i_e_buttons,
                    )
                except ReplyMarkupTooLong:
                    empty_buttons = await make_keyboard_empty(
                        user_id=user_id, chat_id=query.message.chat.id, unziphttp=False
                    )
                    await query.message.edit(
                        messages.get("callbacks", "UNABLE_GATHER_FILES", uid),
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
                        text=messages.get("callbacks", "SELECT_FILES", uid),
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
                            text=messages.get("callbacks", "UNABLE_GATHER_FILES", uid),
                            reply_markup=empty_buttons,
                        )
                    except:
                        await answer_query(
                            query,
                            messages.get("callbacks", "EXT_FAILED_TXT", uid),
                            unzip_client=unzip_bot,
                        )
                        await archive_msg.reply(
                            messages.get("callbacks", "EXT_FAILED_TXT", uid)
                        )
                        shutil.rmtree(ext_files_dir)
                        LOGGER.error(messages.get("callbacks", "FATAL_ERROR", None))
                        await del_ongoing_task(user_id)

                        return

        except Exception as e:
            await del_ongoing_task(user_id)

            try:
                try:
                    await query.message.edit(
                        messages.get("callbacks", "ERROR_TXT", uid, e)
                    )
                except:
                    await unzip_bot.send_message(
                        chat_id=query.message.chat.id,
                        text=messages.get("callbacks", "ERROR_TXT", uid, e),
                    )

                await archive_msg.reply(messages.get("callbacks", "ERROR_TXT", None, e))
                shutil.rmtree(ext_files_dir)

                try:
                    await ClientSession().close()
                except:
                    pass

                LOGGER.error(e)
            except Exception as err:
                LOGGER.error(err)
                await archive_msg.reply(err)

    elif query.data.startswith("ext_f"):
        LOGGER.info(query.data)
        user_id = query.from_user.id
        spl_data = query.data.split("|")
        file_path = f"{Config.DOWNLOAD_LOCATION}/{spl_data[1]}/extracted"

        try:
            urled = spl_data[4] if isinstance(spl_data[4], bool) else False
        except:
            urled = False

        if urled:
            paths = spl_data[5].namelist()
        else:
            paths = await get_files(path=file_path)

        if not paths and not urled:
            if os.path.isdir(f"{Config.DOWNLOAD_LOCATION}/{spl_data[1]}"):
                shutil.rmtree(f"{Config.DOWNLOAD_LOCATION}/{spl_data[1]}")

            await del_ongoing_task(user_id)
            await query.message.edit(
                text=messages.get("callbacks", "NO_FILE_LEFT", uid),
                reply_markup=Buttons.RATE_ME,
            )

            return

        LOGGER.info("ext_f paths : " + str(paths))

        try:
            await query.message.edit(
                text=messages.get("callbacks", "UPLOADING_THIS_FILE", uid)
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
                full_path=f"{Config.DOWNLOAD_LOCATION}/{spl_data[1]}",
                log_msg=log_msg,
                split=False,
            )
        else:
            split = True

        if split:
            fname = file.split("/")[-1]
            smessage = await unzip_bot.send_message(
                chat_id=user_id, text=messages.get("callbacks", "SPLITTING", uid, fname)
            )
            splitteddir = f"{Config.DOWNLOAD_LOCATION}/splitted/{user_id}"
            os.makedirs(splitteddir, exist_ok=True)
            ooutput = f"{splitteddir}/{fname}"
            splittedfiles = await split_files(file, ooutput, Config.TG_MAX_SIZE)
            LOGGER.info(splittedfiles)

            if not splittedfiles:
                try:
                    shutil.rmtree(splitteddir)
                except:
                    pass

                await del_ongoing_task(user_id)
                await smessage.edit(messages.get("callbacks", "ERR_SPLIT", uid))

                return

            await smessage.edit(messages.get("callbacks", "SEND_ALL_PARTS", uid, fname))
            async_splittedfiles = async_generator(splittedfiles)

            async for file in async_splittedfiles:
                sent_files += 1
                await send_file(
                    unzip_bot=unzip_bot,
                    c_id=user_id,
                    doc_f=file,
                    query=query,
                    full_path=splitteddir,
                    log_msg=log_msg,
                    split=True,
                )

            try:
                shutil.rmtree(splitteddir)
                os.remove(file)
            except:
                pass

            try:
                await smessage.delete()
            except:
                pass

        await query.message.edit(messages.get("callbacks", "REFRESHING", uid))

        if urled:
            rpaths = paths.remove(paths[int(spl_data[3])])
        else:
            rpaths = await get_files(path=file_path)

        if not rpaths:
            try:
                shutil.rmtree(f"{Config.DOWNLOAD_LOCATION}/{spl_data[1]}")
            except:
                pass

            await del_ongoing_task(user_id)
            await query.message.edit(
                text=messages.get("callbacks", "NO_FILE_LEFT", uid),
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
                    messages.get("callbacks", "SELECT_FILES", uid),
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
                    messages.get("callbacks", "UNABLE_GATHER_FILES", uid),
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
                    messages.get("callbacks", "SELECT_FILES", uid),
                    reply_markup=i_e_buttons,
                )
            except ReplyMarkupTooLong:
                empty_buttons = await make_keyboard_empty(
                    user_id=user_id, chat_id=query.message.chat.id, unziphttp=False
                )
                await query.message.edit(
                    messages.get("callbacks", "UNABLE_GATHER_FILES", uid),
                    reply_markup=empty_buttons,
                )

        await update_uploaded(user_id, upload_count=sent_files)

    elif query.data.startswith("ext_a"):
        LOGGER.info(query.data)
        user_id = query.from_user.id
        spl_data = query.data.split("|")
        file_path = f"{Config.DOWNLOAD_LOCATION}/{spl_data[1]}/extracted"

        try:
            urled = spl_data[4] if isinstance(spl_data[3], bool) else False
        except:
            urled = False

        if urled:
            paths = spl_data[4].namelist()
        else:
            paths = await get_files(path=file_path)

        LOGGER.info("ext_a paths : " + str(paths))

        if not paths and not urled:
            try:
                shutil.rmtree(f"{Config.DOWNLOAD_LOCATION}/{spl_data[1]}")
            except:
                pass

            await del_ongoing_task(user_id)
            await query.message.edit(
                text=messages.get("callbacks", "NO_FILE_LEFT", uid),
                reply_markup=Buttons.RATE_ME,
            )

            return

        await query.message.edit(messages.get("callbacks", "SENDING_ALL_FILES", uid))
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
                    full_path=f"{Config.DOWNLOAD_LOCATION}/{spl_data[1]}",
                    log_msg=log_msg,
                    split=False,
                )
            else:
                split = True

            if split:
                fname = file.split("/")[-1]
                smessage = await unzip_bot.send_message(
                    chat_id=user_id,
                    text=messages.get("callbacks", "SPLITTING", uid, fname),
                )
                splitteddir = f"{Config.DOWNLOAD_LOCATION}/splitted/{user_id}"
                os.makedirs(splitteddir, exist_ok=True)
                ooutput = f"{splitteddir}/{fname}"
                splittedfiles = await split_files(file, ooutput, Config.TG_MAX_SIZE)
                LOGGER.info(splittedfiles)

                if not splittedfiles:
                    try:
                        shutil.rmtree(splitteddir)
                    except:
                        pass

                    await del_ongoing_task(user_id)
                    await smessage.edit(messages.get("callbacks", "ERR_SPLIT", uid))

                    return

                await smessage.edit(
                    messages.get("callbacks", "SEND_ALL_PARTS", uid, fname)
                )
                async_splittedfiles = async_generator(splittedfiles)

                async for s_file in async_splittedfiles:
                    sent_files += 1
                    await send_file(
                        unzip_bot=unzip_bot,
                        c_id=user_id,
                        doc_f=s_file,
                        query=query,
                        full_path=splitteddir,
                        log_msg=log_msg,
                        split=True,
                    )

                try:
                    shutil.rmtree(splitteddir)
                except:
                    pass

                try:
                    await smessage.delete()
                except:
                    pass

        try:
            await unzip_bot.send_message(
                chat_id=user_id,
                text=messages.get("callbacks", "UPLOADED", uid),
                reply_markup=Buttons.RATE_ME,
            )
            await query.message.edit(
                text=messages.get("callbacks", "UPLOADED", uid),
                reply_markup=Buttons.RATE_ME,
            )
        except:
            pass

        await log_msg.reply(
            messages.get("callbacks", "HOW_MANY_UPLOADED", None, sent_files)
        )
        await update_uploaded(user_id, upload_count=sent_files)
        await del_ongoing_task(user_id)

        try:
            shutil.rmtree(f"{Config.DOWNLOAD_LOCATION}/{spl_data[1]}")
        except Exception as e:
            await query.message.edit(messages.get("callbacks", "ERROR_TXT", uid, e))
            await archive_msg.reply(messages.get("callbacks", "ERROR_TXT", None, e))

    elif query.data == "cancel_dis":
        uid = query.from_user.id
        await del_ongoing_task(uid)
        await del_merge_task(uid)

        try:
            await query.message.edit(
                messages.get(
                    "callbacks",
                    "CANCELLED_TXT",
                    uid,
                    messages.get("callbacks", "PROCESS_CANCELLED", uid),
                )
            )
            shutil.rmtree(f"{Config.DOWNLOAD_LOCATION}/{uid}")
            await update_uploaded(user_id=uid, upload_count=sent_files)

            try:
                await log_msg.reply(
                    messages.get("callbacks", "HOW_MANY_UPLOADED", None, sent_files)
                )
            except:
                return
        except:
            await unzip_bot.send_message(
                chat_id=uid,
                text=messages.get(
                    "callbacks",
                    "CANCELLED_TXT",
                    uid,
                    messages.get("callbacks", "PROCESS_CANCELLED", uid),
                ),
            )

            return

    elif query.data == "nobully":
        await query.message.edit(messages.get("callbacks", "CANCELLED", uid))
