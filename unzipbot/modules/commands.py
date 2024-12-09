import ast
import io
import os
import re
import shutil
import time
from asyncio import create_subprocess_shell, sleep, subprocess
from contextlib import redirect_stderr, redirect_stdout
from sys import executable

import git
import psutil
from pyrogram import enums, filters
from pyrogram.errors import FloodWait, RPCError
from pyrogram.types import Message

from config import Config
from unzipbot import LOGGER, boottime, unzipbot_client
from unzipbot.helpers.database import (
    add_banned_user,
    add_merge_task,
    add_user,
    check_user,
    count_banned_users,
    count_ongoing_tasks,
    count_users,
    del_banned_user,
    del_ongoing_task,
    del_user,
    get_lang,
    get_maintenance,
    get_merge_task,
    get_ongoing_tasks,
    get_upload_mode,
    get_uploaded,
    get_users_list,
    set_maintenance,
)
from unzipbot.helpers.unzip_help import (
    calculate_memory_limit,
    humanbytes,
    timeformat_sec,
)
from unzipbot.i18n.buttons import Buttons
from unzipbot.i18n.messages import Messages
from unzipbot.modules.ext_script.custom_thumbnail import add_thumb, del_thumb
from unzipbot.modules.ext_script.ext_helper import get_files


# Regex for urls
https_url_regex = r"((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*"

messages = Messages(lang_fetcher=get_lang)


def sufficient_disk_space(required_space):
    disk_usage = psutil.disk_usage("/")
    free_space = disk_usage.free
    total_space = disk_usage.total
    five_percent_total = total_space * 0.05

    if free_space >= required_space and free_space >= five_percent_total:
        return True

    return False


@unzipbot_client.on_message(filters.private)
async def _(_, message: Message):
    await check_user(message)
    uid = message.from_user.id

    if uid != Config.BOT_OWNER and await get_maintenance():
        await message.reply(messages.get("commands", "MAINTENANCE_ON", uid))

        return

    if uid == Config.BOT_OWNER:
        return

    if await count_ongoing_tasks() >= Config.MAX_CONCURRENT_TASKS:
        ogtasks = await get_ongoing_tasks()

        if not any(uid == task.get("user_id") for task in ogtasks):
            try:
                await message.reply(
                    text=messages.get(
                        "commands", "MAX_TASKS", uid, Config.MAX_CONCURRENT_TASKS
                    ),
                )
            except:
                await unzipbot_client.send_message(
                    chat_id=uid,
                    text=messages.get(
                        "commands", "MAX_TASKS", uid, Config.MAX_CONCURRENT_TASKS
                    ),
                )

            return


@unzipbot_client.on_message(filters.command("start"))
async def start_bot(_, message: Message):
    try:
        await message.reply_text(
            text=messages.get(
                "commands",
                "START_TEXT",
                message.from_user.id,
                message.from_user.mention,
            ),
            reply_markup=Buttons.START_BUTTON,
            disable_web_page_preview=True,
        )
    except FloodWait as f:
        await sleep(f.value)
        await start_bot(_, message)


@unzipbot_client.on_message(filters.private & filters.command("clean"))
async def clean_my_files(_, message: Message):
    try:
        await message.reply_text(
            text=messages.get("commands", "CLEAN_TXT", message.from_user.id),
            reply_markup=Buttons.CLN_BTNS,
        )
    except FloodWait as f:
        await sleep(f.value)
        await clean_my_files(_, message)


@unzipbot_client.on_message(filters.command("help"))
async def help_me(_, message: Message):
    try:
        await message.reply_text(
            text=messages.get("commands", "HELP_TXT", message.from_user.id),
            reply_markup=Buttons.ME_GOIN_HOME,
        )
    except FloodWait as f:
        await sleep(f.value)
        await help_me(_, message)


@unzipbot_client.on_message(filters.command("about"))
async def about_me(_, message: Message):
    try:
        await message.reply_text(
            text=messages.get(
                "commands", "ABOUT_TXT", message.from_user.id, Config.VERSION
            ),
            reply_markup=Buttons.ME_GOIN_HOME,
            disable_web_page_preview=True,
        )
    except FloodWait as f:
        await sleep(f.value)
        await about_me(_, message)


@unzipbot_client.on_message(filters.command("privacy"))
async def privacy_text(_, message: Message):
    try:
        await message.reply_text(
            text=messages.get("commands", "PRIVACY", message.from_user.id)
        )
    except FloodWait as f:
        await sleep(f.value)
        await privacy_text(_, message)


@unzipbot_client.on_message(
    filters.incoming
    & filters.private
    & (filters.document | filters.regex(https_url_regex))
    & ~filters.command(["eval", "exec"])
)
async def extract_archive(_, message: Message):
    try:
        if message.chat.type != enums.ChatType.PRIVATE:
            return
        
        user_id = message.from_user.id

        if await get_merge_task(user_id):
            return

        if os.path.exists(Config.LOCKFILE):
            await message.reply(messages.get("commands", "STILL_STARTING", user_id))

            return
        
        download_path = f"{Config.DOWNLOAD_LOCATION}/{user_id}"

        if os.path.isdir(download_path):
            await message.reply(messages.get("commands", "PROCESS_RUNNING", user_id))

            return

        unzip_msg = await message.reply(
            messages.get("commands", "PROCESSING2", user_id),
            reply_to_message_id=message.id,
        )

        if message.text and (re.match(https_url_regex, message.text)):
            await unzip_msg.edit(
                text=messages.get("commands", "CHOOSE_EXT_MODE", user_id, "URL", "🔗"),
                reply_markup=Buttons.CHOOSE_E_U__BTNS,
            )
        elif message.document:
            if sufficient_disk_space(message.document.file_size):
                await unzip_msg.edit(
                    text=messages.get(
                        "commands", "CHOOSE_EXT_MODE", user_id, "file", "🗂️"
                    ),
                    reply_markup=Buttons.CHOOSE_E_F__BTNS,
                )
            else:
                await unzip_msg.edit(messages.get("commands", "NO_SPACE", user_id))
        else:
            await unzip_msg.edit(messages.get("commands", "INVALID", user_id))
    except FloodWait as f:
        await sleep(f.value)
        await extract_archive(_, message)


@unzipbot_client.on_message(filters.private & filters.command("cancel"))
async def cancel_task_by_user(_, message):
    idtodel = message.id - 1

    try:
        await unzipbot_client.delete_messages(
            chat_id=message.from_user.id, message_ids=idtodel
        )
    except:
        pass

    await message.reply(messages.get("commands", "CANCELLED", message.from_user.id))


@unzipbot_client.on_message(filters.private & filters.command("merge"))
async def merging(_, message: Message):
    try:
        merge_msg = await message.reply(
            messages.get("commands", "MERGE", message.from_user.id)
        )
        await add_merge_task(message.from_user.id, merge_msg.id)
    except FloodWait as f:
        await sleep(f.value)
        await merging(_, message)


@unzipbot_client.on_message(filters.private & filters.command("done"))
async def done_merge(_, message: Message):
    try:
        await message.reply(
            messages.get("commands", "DONE", message.from_user.id),
            reply_markup=Buttons.MERGE_THEM_ALL,
        )
    except FloodWait as f:
        await sleep(f.value)
        await done_merge(_, message)


@unzipbot_client.on_message(filters.private & filters.command("mode"))
async def set_mode_for_user(_, message: Message):
    try:
        upload_mode = await get_upload_mode(message.from_user.id)
        await message.reply(
            text=messages.get(
                "commands", "SELECT_UPLOAD_MODE_TXT", message.from_user.id, upload_mode
            ),
            reply_markup=Buttons.SET_UPLOAD_MODE_BUTTONS,
        )
    except FloodWait as f:
        await sleep(f.value)
        await set_mode_for_user(_, message)


async def get_stats(id):
    total, used, free = shutil.disk_usage(".")
    total = humanbytes(total)
    used = humanbytes(used)
    free = humanbytes(free)
    sent = humanbytes(psutil.net_io_counters().bytes_sent)
    recv = humanbytes(psutil.net_io_counters().bytes_recv)
    cpu_usage = psutil.cpu_percent(interval=0.2)
    ram_usage = psutil.virtual_memory().percent
    disk_usage = psutil.disk_usage("/").percent
    uptime = timeformat_sec(time.time() - boottime)
    total_users = await count_users()
    total_banned_users = await count_banned_users()
    ongoing_tasks = await count_ongoing_tasks()

    if id == Config.BOT_OWNER:
        stats_string = messages.get(
            "commands",
            "STATS_OWNER",
            id,
            total_users,
            total_banned_users,
            total,
            used,
            disk_usage,
            free,
            ongoing_tasks,
            sent,
            recv,
            cpu_usage,
            ram_usage,
            uptime,
        )
    else:
        stats_string = messages.get(
            "commands",
            "STATS",
            id,
            total,
            used,
            disk_usage,
            free,
            ongoing_tasks,
            cpu_usage,
            ram_usage,
            uptime,
        )

    return stats_string


@unzipbot_client.on_message(filters.command("stats"))
async def send_stats(_, message: Message):
    try:
        stats_msg = await message.reply(
            messages.get("commands", "PROCESSING2", message.from_user.id)
        )
        stats_txt = await get_stats(message.from_user.id)
        await stats_msg.edit(text=stats_txt, reply_markup=Buttons.REFRESH_BUTTON)
    except FloodWait as f:
        await sleep(f.value)
        await send_stats(_, message)


async def __do_broadcast(message, user):
    try:
        await message.copy(chat_id=int(user))

        return 200
    except FloodWait as f:
        await sleep(f.value)

        return __do_broadcast(message, user)
    except Exception:
        await del_user(user)

        return 400


@unzipbot_client.on_message(
    filters.command("broadcast") & filters.user(Config.BOT_OWNER)
)
async def broadcast_this(_, message: Message):
    uid = message.from_user.id
    bc_msg = await message.reply(messages.get("commands", "PROCESSING2", uid))
    r_msg = message.reply_to_message

    if not r_msg:
        await bc_msg.edit(messages.get("commands", "BC_REPLY", uid))

        return

    users_list = await get_users_list()
    success_no = 0
    failed_no = 0
    done_no = 0
    total_users = await count_users()
    await bc_msg.edit(messages.get("commands", "BC_START", uid, done_no, total_users))

    for user in users_list:
        b_cast = await __do_broadcast(message=r_msg, user=user.get("user_id"))

        if b_cast == 200:
            success_no += 1
        else:
            failed_no += 1

        done_no += 1

        if done_no % 10 == 0 or done_no == total_users:
            try:
                await bc_msg.edit(
                    messages.get("commands", "BC_START", uid, done_no, total_users)
                )
            except FloodWait:
                pass
    try:
        await bc_msg.edit(
            messages.get(
                "commands",
                "BC_DONE",
                uid,
                total_users,
                success_no,
                failed_no,
            )
        )
    except FloodWait as f:
        await sleep(f.value)
        await bc_msg.edit(
            messages.get(
                "commands",
                "BC_DONE",
                uid,
                total_users,
                success_no,
                failed_no,
            )
        )


@unzipbot_client.on_message(filters.command("sendto") & filters.user(Config.BOT_OWNER))
async def send_this(_, message: Message):
    uid = message.from_user.id
    sd_msg = await message.reply(messages.get("commands", "PROCESSING2", uid))
    r_msg = message.reply_to_message

    if not r_msg:
        await sd_msg.edit(messages.get("commands", "SEND_REPLY", uid))

        return

    try:
        user_id = message.text.split(None, 1)[1]
    except:
        await sd_msg.edit(messages.get("commands", "PROVIDE_UID", uid))

        return

    await sd_msg.edit(messages.get("commands", "SENDING", uid))
    send = await __do_broadcast(message=r_msg, user=user_id)

    if send == 200:
        await sd_msg.edit(messages.get("commands", "SEND_SUCCESS", uid, user_id))
    else:
        await sd_msg.edit(messages.get("commands", "SEND_FAILED", uid, user_id))


@unzipbot_client.on_message(filters.command("report"))
async def report_this(_, message: Message):
    uid = message.from_user.id
    sd_msg = await message.reply(messages.get("commands", "PROCESSING2", uid))
    r_msg = message.reply_to_message

    if not r_msg:
        await sd_msg.edit(messages.get("commands", "REPORT_REPLY", uid))

        return

    await sd_msg.edit(messages.get("commands", "SENDING", uid))
    await unzipbot_client.send_message(
        chat_id=Config.LOGS_CHANNEL,
        text=messages.get("commands", "REPORT_TEXT", uid, uid, r_msg.text.markdown),
    )
    await sd_msg.edit(messages.get("commands", "REPORT_DONE", uid))


@unzipbot_client.on_message(filters.command("ban") & filters.user(Config.BOT_OWNER))
async def ban_user(_, message: Message):
    uid = message.from_user.id
    ban_msg = await message.reply(messages.get("commands", "PROCESSING2", uid))

    try:
        user_id = message.text.split(None, 1)[1]
    except:
        await ban_msg.edit(messages.get("commands", "BAN_ID", uid))

        return

    bdb = await add_banned_user(user_id)
    db = await del_user(user_id)
    text = ""

    if bdb == -1:
        text += messages.get("commands", "ALREADY_BANNED", uid, user_id)

    if db == -1:
        text += messages.get("commands", "ALREADY_REMOVED", uid, user_id)

    if text != "":
        await ban_msg.edit(text)
    else:
        await ban_msg.edit(messages.get("commands", "USER_BANNED", uid, user_id))


@unzipbot_client.on_message(filters.command("unban") & filters.user(Config.BOT_OWNER))
async def unban_user(_, message: Message):
    uid = message.from_user.id
    unban_msg = await message.reply(messages.get("commands", "PROCESSING2", uid))

    try:
        user_id = message.text.split(None, 1)[1]
    except:
        await unban_msg.edit(messages.get("commands", "UNBAN_ID", uid))

        return

    db = await add_user(user_id)
    bdb = await del_banned_user(user_id)
    text = ""

    if db == -1:
        text += messages.get("commands", "ALREADY_ADDED", uid, user_id)

    if bdb == -1:
        text += messages.get("commands", "ALREADY_UNBANNED", uid, user_id)

    if text != "":
        await unban_msg.edit(text)
    else:
        await unban_msg.edit(messages.get("commands", "UNBANNED", uid, user_id))


@unzipbot_client.on_message(filters.command("info"))
async def me_stats(_, message: Message):
    me_info = await unzipbot_client.ask(
        chat_id=message.chat.id,
        text=messages.get("commands", "INFO", message.from_user.id),
    )
    await unzipbot_client.send_message(chat_id=message.chat.id, text=f"`{me_info}`")


@unzipbot_client.on_message(filters.command("user") & filters.user(Config.BOT_OWNER))
async def info_user(_, message: Message):
    uid = message.from_user.id
    await message.reply(messages.get("commands", "USER", uid))
    info_user_msg = await message.reply(messages.get("commands", "PROCESSING2", uid))

    try:
        user_id = message.text.split(None, 1)[1]
    except:
        await info_user_msg.edit(messages.get("commands", "PROVIDE_UID", uid))

        return

    up_count = get_uploaded(user_id)

    if up_count == "":
        up_count = messages.get("commands", "UNABLE_FETCH", uid)

    await info_user_msg.edit(
        messages.get("commands", "USER_INFO", uid, user_id, up_count)
    )


@unzipbot_client.on_message(filters.command("user2") & filters.user(Config.BOT_OWNER))
async def info_user2(_, message: Message):
    uid = message.from_user.id
    user2_msg = await message.reply(messages.get("commands", "PROCESSING2", uid))

    try:
        user_id = message.text.split(None, 1)[1]
    except:
        await user2_msg.edit(messages.get("commands", "PROVIDE_UID2", uid))

        return

    try:
        infos = await unzipbot_client.get_users(user_id)
    except:
        await user2_msg.edit(messages.get("commands", "UID_UNAME_INVALID", uid))

        return

    if not isinstance(user_id, int):
        try:
            user_id = infos.id
        except:
            pass

    await user2_msg.edit(messages.get("commands", "USER2_INFO", uid, infos, user_id))


@unzipbot_client.on_message(filters.command("self") & filters.user(Config.BOT_OWNER))
async def info_self(_, message: Message):
    self_infos = await unzipbot_client.get_me()
    await message.reply(f"`{self_infos}`")


@unzipbot_client.on_message(
    filters.command("getthumbs") & filters.user(Config.BOT_OWNER)
)
async def get_all_thumbs(_, message: Message):
    uid = message.from_user.id
    paths = await get_files(path=Config.THUMB_LOCATION)

    if not paths:
        await message.reply(messages.get("commands", "NO_THUMBS", uid))

    for doc_f in paths:
        try:
            await unzipbot_client.send_document(
                chat_id=message.chat.id,
                document=doc_f,
                file_name=doc_f.split("/")[-1],
                reply_to_message_id=message.id,
                caption=messages.get("commands", "EXT_CAPTION", uid, doc_f),
            )
        except FloodWait as f:
            await sleep(f.value)
            await unzipbot_client.send_document(
                chat_id=message.chat.id,
                document=doc_f,
                file_name=doc_f.split("/")[-1],
                reply_to_message_id=message.id,
                caption=messages.get("commands", "EXT_CAPTION", uid, doc_f),
            )
        except RPCError as e:
            LOGGER.error(e)


@unzipbot_client.on_message(
    filters.command("redbutton") & filters.user(Config.BOT_OWNER)
)
async def red_alert(_, message: Message):
    # restart the whole bot, maybe using execl
    # but also need to stop currently ongoing processes…
    await message.reply("🚧 WIP 🚧")


@unzipbot_client.on_message(
    filters.command("maintenance") & filters.user(Config.BOT_OWNER)
)
async def maintenance_mode(_, message: Message):
    mstatus = await get_maintenance()
    uid = message.from_user.id
    text = (
        messages.get("commands", "MAINTENANCE", uid, mstatus)
        + "\n\n"
        + messages.get("commands", "MAINTENANCE_ASK", uid)
    )
    mess = await message.reply(text)

    try:
        newstate = message.text.split(None, 1)[1]
    except:
        await mess.edit(messages.get("commands", "MAINTENANCE_FAIL", uid))

        return

    if newstate not in ["True", "False"]:
        await mess.edit(messages.get("commands", "MAINTENANCE_FAIL", uid))

        return

    await set_maintenance(newstate == "True")
    await message.reply(messages.get("commands", "MAINTENANCE_DONE", uid, newstate))


@unzipbot_client.on_message(filters.private & filters.command("addthumb"))
async def thumb_add(_, message: Message):
    await add_thumb(unzipbot_client, message)


@unzipbot_client.on_message(filters.private & filters.command("delthumb"))
async def thumb_del(_, message: Message):
    await del_thumb(message)


@unzipbot_client.on_message(
    filters.command("cleanall") & filters.user(Config.BOT_OWNER)
)
async def del_everything(_, message: Message):
    uid = message.from_user.id
    cleaner = await message.reply(messages.get("commands", "ERASE_ALL", uid))

    try:
        shutil.rmtree(Config.DOWNLOAD_LOCATION)
        await cleaner.edit(messages.get("commands", "CLEANED", uid))
        os.mkdir(Config.DOWNLOAD_LOCATION)
    except:
        await cleaner.edit(messages.get("commands", "NOT_CLEANED", uid))


@unzipbot_client.on_message(
    filters.command("cleantasks") & filters.user(Config.BOT_OWNER)
)
async def del_tasks(_, message: Message):
    ongoing_tasks = await get_ongoing_tasks()
    number = len(ongoing_tasks)
    uid = message.from_user.id
    cleaner = await message.reply(messages.get("commands", "ERASE_TASKS", uid, number))

    for task in ongoing_tasks:
        user_id = task.get("user_id")
        await del_ongoing_task(user_id)

        try:
            shutil.rmtree(f"{Config.DOWNLOAD_LOCATION}/{user_id}")
        except:
            pass

    await cleaner.edit(messages.get("commands", "ERASE_TASKS_SUCCESS", uid, number))


async def send_logs(user_id):
    with open("unzip-bot.log", "rb") as doc_f:
        message = None

        try:
            message = await unzipbot_client.send_document(
                chat_id=user_id,
                document=doc_f,
                file_name=doc_f.name,
            )
            LOGGER.info(messages.get("commands", "LOG_SENT", None, user_id))
        except FloodWait as f:
            await sleep(f.value)
            message = await unzipbot_client.send_document(
                chat_id=user_id,
                document=doc_f,
                file_name=doc_f.name,
            )
        except RPCError as e:
            await unzipbot_client.send_message(chat_id=user_id, text=e)
        finally:
            doc_f.close()

            return message


def clear_logs():
    with open("file.txt", "w") as f:
        f.close()


@unzipbot_client.on_message(filters.command("logs") & filters.user(Config.BOT_OWNER))
async def logz(_, message: Message):
    await send_logs(message.from_user.id)


@unzipbot_client.on_message(filters.command("restart") & filters.user(Config.BOT_OWNER))
async def restart(_, message: Message):
    try:
        folder_to_del = os.path.dirname(os.path.abspath(Config.DOWNLOAD_LOCATION))
        shutil.rmtree(Config.DOWNLOAD_LOCATION)
        LOGGER.info(messages.get("commands", "DELETED_FOLDER", None, folder_to_del))
    except:
        pass

    restarttime = time.strftime("%Y/%m/%d - %H:%M:%S")
    await message.reply_text(
        messages.get("commands", "RESTARTED_AT", message.from_user.id, restarttime),
        quote=True,
    )
    log_message = await send_logs(message.from_user.id)

    if log_message:
        await log_message.forward(chat_id=Config.LOGS_CHANNEL)

    LOGGER.info(messages.get("commands", "RESTARTING", None, message.from_user.id))
    clear_logs()
    os.execl(executable, executable, "-m", "unzipbot")


@unzipbot_client.on_message(filters.command("gitpull") & filters.user(Config.BOT_OWNER))
async def pull_updates(_, message: Message):
    uid = message.from_user.id
    git_reply = await message.reply(messages.get("commands", "PULLING", uid))
    repo = git.Repo("/app")
    current = repo.head.commit
    repo.remotes.origin.pull()

    if current != repo.head.commit:
        await git_reply.edit(messages.get("commands", "PULLED", uid))
        await restart(_, message)
    else:
        await git_reply.edit(messages.get("commands", "NO_PULL", uid))


@unzipbot_client.on_message(filters.command("donate"))
async def donate_help(_, message: Message):
    await message.reply(messages.get("commands", "DONATE_TEXT", message.from_user.id))


@unzipbot_client.on_message(filters.command("vip"))
async def vip_help(_, message: Message):
    await message.reply(messages.get("commands", "VIP_INFO", message.from_user.id))


@unzipbot_client.on_message(
    filters.command("dbexport") & filters.user(Config.BOT_OWNER)
)
async def export_db(_, message):
    # Will use https://www.mongodb.com/docs/database-tools/mongoexport/ on command to export as CSV
    await message.reply("🚧 WIP 🚧")


@unzipbot_client.on_message(filters.command("commands"))
async def getall_cmds(_, message):
    await message.reply(
        messages.get("commands", "COMMANDS_LIST", message.from_user.id),
        disable_web_page_preview=True,
    )


@unzipbot_client.on_message(
    filters.command("admincmd") & filters.user(Config.BOT_OWNER)
)
async def getadmin_cmds(_, message):
    await message.reply(
        messages.get("commands", "ADMINCMD", message.from_user.id),
        disable_web_page_preview=True,
    )


async def aexec(code, client, message):
    stdout = io.StringIO()
    stderr = io.StringIO()
    result = None

    with redirect_stdout(stdout), redirect_stderr(stderr):
        try:
            try:
                result = ast.literal_eval(code)
            except SyntaxError:
                exec(
                    "async def __aexec(client, message): "
                    + "".join(f"\n {line}" for line in code.split("\n"))
                )
                await locals()["__aexec"](client, message)
            except ValueError as e:
                stderr.write(f"ValueError : {str(e)}\n")
            except TypeError as e:
                stderr.write(f"TypeError : {str(e)}\n")
            except MemoryError as e:
                stderr.write(f"MemoryError : {str(e)}\n")
            except RecursionError as e:
                stderr.write(f"RecursionError : {str(e)}\n")
        except Exception as e:
            stderr.write(f"{type(e).__name__}: {str(e)}\n")

    return stdout.getvalue(), stderr.getvalue(), result


@unzipbot_client.on_message(filters.command("eval") & filters.user(Config.BOT_OWNER))
async def eval_command(_, message):
    status_message = await message.reply_text("Processing ...")
    cmd = message.text.split(" ", maxsplit=1)[1]

    stdout, stderr, result = await aexec(cmd, _, message)
    LOGGER.info("stdout: " + stdout)
    LOGGER.info("stderr: " + stderr)

    if result is not None:
        evaluation = str(result)
    elif stderr.strip():
        evaluation = stderr.strip()
    elif stdout.strip():
        evaluation = stdout.strip()
    else:
        evaluation = "Success"

    final_output = f"<b>EVAL</b> : <code>{cmd}</code>\n\n<b>OUTPUT</b> :\n<code>{evaluation}</code> \n"

    if len(final_output) > Config.MAX_MESSAGE_LENGTH:
        trimmed_output = f"EVAL : {cmd}\n\nOUTPUT :\n{evaluation}"

        with open("eval.txt", "w+", encoding="utf8") as out_file:
            out_file.write(str(trimmed_output))

        await message.reply_document(
            document="eval.txt",
            caption=cmd,
            reply_to_message_id=message.id,
        )
        await status_message.delete()
        os.remove("eval.txt")
    else:
        await status_message.edit(final_output)


@unzipbot_client.on_message(filters.command("exec") & filters.user(Config.BOT_OWNER))
async def exec_command(_, message):
    cmd = message.text.split(" ", maxsplit=1)[1]
    memlimit = calculate_memory_limit()
    cpulimit = Config.MAX_CPU_CORES_COUNT * Config.MAX_CPU_USAGE
    ulimit_cmd = ["ulimit", "-v", str(memlimit), "&&", "cpulimit", "-l", str(cpulimit), "--", cmd]
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

    e = e or "No error"
    o = o or "No output"
    OUTPUT = f"**COMMAND :**\n`{cmd}`\n\n**OUTPUT :**\n`{o}`\n\n**ERROR :**\n`{e}`"

    if len(OUTPUT) > Config.MAX_MESSAGE_LENGTH:
        T_OUTPUT = f"COMMAND :\n{cmd}\n\nOUTPUT :\n{o}\n\nERROR :\n{e}"

        with io.BytesIO(str.encode(T_OUTPUT)) as out_file:
            out_file.name = "exec.txt"
            await message.reply_document(
                document=out_file,
                caption=f"`{cmd}`",
                reply_to_message_id=message.id,
            )
    else:
        await message.reply_text(OUTPUT)
