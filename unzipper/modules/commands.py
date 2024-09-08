# Copyright (c) 2022 - 2024 EDM115
import ast
import io
import os
import re
import shutil
import time

import git
import psutil

from asyncio import create_subprocess_shell, sleep, subprocess
from contextlib import redirect_stderr, redirect_stdout
from pyrogram import enums, filters
from pyrogram.errors import FloodWait, RPCError
from pyrogram.types import Message
from sys import executable

from .bot_data import Buttons, Messages
from config import Config
from unzipper import boottime, LOGGER, unzipperbot
from unzipper.helpers.database import (
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
    get_maintenance,
    get_merge_task,
    get_ongoing_tasks,
    get_upload_mode,
    get_uploaded,
    get_users_list,
    set_maintenance,
)
from unzipper.helpers.unzip_help import humanbytes, timeformat_sec
from unzipper.modules.ext_script.custom_thumbnail import add_thumb, del_thumb
from unzipper.modules.ext_script.ext_helper import get_files

# Regex for urls
https_url_regex = r"((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*"


def sufficient_disk_space(required_space):
    disk_usage = psutil.disk_usage("/")
    free_space = disk_usage.free
    total_space = disk_usage.total
    five_percent_total = total_space * 0.05

    if free_space >= required_space and free_space >= five_percent_total:
        return True
    return False


@unzipperbot.on_message(filters.private)
async def _(_, message: Message):
    await check_user(message)
    uid = message.from_user.id
    if uid != Config.BOT_OWNER and await get_maintenance():
        await message.reply(Messages.MAINTENANCE_ON)
        return
    if uid == Config.BOT_OWNER:
        return
    if await count_ongoing_tasks() >= Config.MAX_CONCURRENT_TASKS:
        ogtasks = await get_ongoing_tasks()
        if not any(uid == task.get("user_id") for task in ogtasks):
            try:
                await message.reply(
                    text=Messages.MAX_TASKS.format(Config.MAX_CONCURRENT_TASKS),
                )
            except:
                await unzipperbot.send_message(
                    chat_id=uid,
                    text=Messages.MAX_TASKS.format(Config.MAX_CONCURRENT_TASKS),
                )
            return


@unzipperbot.on_message(filters.command("start"))
async def start_bot(_, message: Message):
    try:
        await message.reply_text(
            text=Messages.START_TEXT.format(message.from_user.mention),
            reply_markup=Buttons.START_BUTTON,
            disable_web_page_preview=True,
        )
    except FloodWait as f:
        await sleep(f.value)
        await start_bot(_, message)


@unzipperbot.on_message(filters.private & filters.command("clean"))
async def clean_my_files(_, message: Message):
    try:
        await message.reply_text(text=Messages.CLEAN_TXT, reply_markup=Buttons.CLN_BTNS)
    except FloodWait as f:
        await sleep(f.value)
        await clean_my_files(_, message)


@unzipperbot.on_message(filters.command("help"))
async def help_me(_, message: Message):
    try:
        await message.reply_text(
            text=Messages.HELP_TXT, reply_markup=Buttons.ME_GOIN_HOME
        )
    except FloodWait as f:
        await sleep(f.value)
        await help_me(_, message)


@unzipperbot.on_message(filters.command("about"))
async def about_me(_, message: Message):
    try:
        await message.reply_text(
            text=Messages.ABOUT_TXT,
            reply_markup=Buttons.ME_GOIN_HOME,
            disable_web_page_preview=True,
        )
    except FloodWait as f:
        await sleep(f.value)
        await about_me(_, message)


@unzipperbot.on_message(filters.command("privacy"))
async def privacy_text(_, message: Message):
    try:
        await message.reply_text(text=Messages.PRIVACY)
    except FloodWait as f:
        await sleep(f.value)
        await privacy_text(_, message)


@unzipperbot.on_message(
    filters.incoming
    & filters.private
    & (filters.document | filters.regex(https_url_regex))
    & ~filters.command(["eval", "exec"])
)
async def extract_archive(_, message: Message):
    try:
        if message.chat.type != enums.ChatType.PRIVATE:
            return
        unzip_msg = await message.reply(
            Messages.PROCESSING2, reply_to_message_id=message.id
        )
        user_id = message.from_user.id
        download_path = f"{Config.DOWNLOAD_LOCATION}/{user_id}"
        if os.path.isdir(download_path):
            await unzip_msg.edit(Messages.PROCESS_RUNNING)
            return
        if await get_merge_task(user_id):
            await unzip_msg.delete()
            return
        if message.text and (re.match(https_url_regex, message.text)):
            await unzip_msg.edit(
                text=Messages.CHOOSE_EXT_MODE.format("URL", "🔗"),
                reply_markup=Buttons.CHOOSE_E_U__BTNS,
            )
        elif message.document:
            if sufficient_disk_space(message.document.file_size):
                await unzip_msg.edit(
                    text=Messages.CHOOSE_EXT_MODE.format("file", "🗂️"),
                    reply_markup=Buttons.CHOOSE_E_F__BTNS,
                )
            else:
                await unzip_msg.edit(Messages.NO_SPACE)
        else:
            await unzip_msg.edit(Messages.UNVALID)
    except FloodWait as f:
        await sleep(f.value)
        await extract_archive(_, message)


@unzipperbot.on_message(filters.private & filters.command("cancel"))
async def cancel_task_by_user(_, message):
    idtodel = message.id - 1
    try:
        await unzipperbot.delete_messages(
            chat_id=message.from_user.id, message_ids=idtodel
        )
    except:
        pass
    await message.reply(Messages.CANCELLED)


@unzipperbot.on_message(filters.private & filters.command("merge"))
async def merging(_, message: Message):
    try:
        merge_msg = await message.reply(Messages.MERGE)
        await add_merge_task(message.from_user.id, merge_msg.id)
    except FloodWait as f:
        await sleep(f.value)
        await merging(_, message)


@unzipperbot.on_message(filters.private & filters.command("done"))
async def done_merge(_, message: Message):
    try:
        await message.reply(Messages.DONE, reply_markup=Buttons.MERGE_THEM_ALL)
    except FloodWait as f:
        await sleep(f.value)
        await done_merge(_, message)


@unzipperbot.on_message(filters.private & filters.command("mode"))
async def set_mode_for_user(_, message: Message):
    try:
        upload_mode = await get_upload_mode(message.from_user.id)
        await message.reply(
            text=Messages.SELECT_UPLOAD_MODE_TXT.format(upload_mode),
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
        stats_string = Messages.STATS_OWNER.format(
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
        stats_string = Messages.STATS.format(
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


@unzipperbot.on_message(filters.command("stats"))
async def send_stats(_, message: Message):
    try:
        stats_msg = await message.reply(Messages.PROCESSING2)
        stats_txt = await get_stats(message.from_user.id)
        await stats_msg.edit(text=stats_txt, reply_markup=Buttons.REFRESH_BUTTON)
    except FloodWait as f:
        await sleep(f.value)
        await send_stats(_, message)


async def _do_broadcast(message, user):
    try:
        await message.copy(chat_id=int(user))
        return 200
    except FloodWait as f:
        await sleep(f.value)
        return _do_broadcast(message, user)
    except Exception:
        await del_user(user)
        return 400


@unzipperbot.on_message(filters.command("broadcast") & filters.user(Config.BOT_OWNER))
async def broadcast_this(_, message: Message):
    bc_msg = await message.reply(Messages.PROCESSING2)
    r_msg = message.reply_to_message
    if not r_msg:
        await bc_msg.edit(Messages.BC_REPLY)
        return
    users_list = await get_users_list()
    success_no = 0
    failed_no = 0
    done_no = 0
    total_users = await count_users()
    await bc_msg.edit(Messages.BC_START.format(done_no, total_users))
    for user in users_list:
        b_cast = await _do_broadcast(message=r_msg, user=user.get("user_id"))
        if b_cast == 200:
            success_no += 1
        else:
            failed_no += 1
        done_no += 1
        if done_no % 10 == 0 or done_no == total_users:
            try:
                await bc_msg.edit(Messages.BC_START.format(done_no, total_users))
            except FloodWait:
                pass
    try:
        await bc_msg.edit(
            Messages.BC_DONE.format(
                total_users,
                success_no,
                failed_no,
            )
        )
    except FloodWait as f:
        await sleep(f.value)
        await bc_msg.edit(
            Messages.BC_DONE.format(
                total_users,
                success_no,
                failed_no,
            )
        )


@unzipperbot.on_message(filters.command("sendto") & filters.user(Config.BOT_OWNER))
async def send_this(_, message: Message):
    sd_msg = await message.reply(Messages.PROCESSING2)
    r_msg = message.reply_to_message
    if not r_msg:
        await sd_msg.edit(Messages.SEND_REPLY)
        return
    try:
        user_id = message.text.split(None, 1)[1]
    except:
        await sd_msg.edit(Messages.PROVIDE_UID)
        return
    await sd_msg.edit(Messages.SENDING)
    send = await _do_broadcast(message=r_msg, user=user_id)
    if send == 200:
        await sd_msg.edit(Messages.SEND_SUCCESS.format(user_id))
    else:
        await sd_msg.edit(Messages.SEND_FAILED.format(user_id))


@unzipperbot.on_message(filters.command("report"))
async def report_this(_, message: Message):
    sd_msg = await message.reply(Messages.PROCESSING2)
    r_msg = message.reply_to_message
    u_id = message.from_user.id
    if not r_msg:
        await sd_msg.edit(Messages.REPORT_REPLY)
        return
    await sd_msg.edit(Messages.SENDING)
    await unzipperbot.send_message(
        chat_id=Config.LOGS_CHANNEL,
        text=Messages.REPORT_TEXT.format(u_id, r_msg.text.markdown),
    )
    await sd_msg.edit(Messages.REPORT_DONE)


@unzipperbot.on_message(filters.command("ban") & filters.user(Config.BOT_OWNER))
async def ban_user(_, message: Message):
    ban_msg = await message.reply(Messages.PROCESSING2)
    try:
        user_id = message.text.split(None, 1)[1]
    except:
        await ban_msg.edit(Messages.BAN_ID)
        return
    bdb = await add_banned_user(user_id)
    db = await del_user(user_id)
    text = ""
    if bdb == -1:
        text += Messages.ALREADY_BANNED.format(user_id)
    if db == -1:
        text += Messages.ALREADY_REMOVED.format(user_id)
    if text != "":
        await ban_msg.edit(text)
    else:
        await ban_msg.edit(Messages.USER_BANNED.format(user_id))


@unzipperbot.on_message(filters.command("unban") & filters.user(Config.BOT_OWNER))
async def unban_user(_, message: Message):
    unban_msg = await message.reply(Messages.PROCESSING2)
    try:
        user_id = message.text.split(None, 1)[1]
    except:
        await unban_msg.edit(Messages.UNBAN_ID)
        return
    db = await add_user(user_id)
    bdb = await del_banned_user(user_id)
    text = ""
    if db == -1:
        text += Messages.ALREADY_ADDED.format(user_id)
    if bdb == -1:
        text += Messages.ALREADY_UNBANNED.format(user_id)
    if text != "":
        await unban_msg.edit(text)
    else:
        await unban_msg.edit(Messages.UNBANNED.format(user_id))


@unzipperbot.on_message(filters.private & filters.command("info"))
async def me_stats(_, message: Message):
    me_info = await unzipperbot.ask(
        chat_id=message.chat.id,
        text=Messages.INFO,
    )
    await unzipperbot.send_message(chat_id=message.chat.id, text=f"`{me_info}`")


@unzipperbot.on_message(filters.command("user") & filters.user(Config.BOT_OWNER))
async def info_user(_, message: Message):
    await message.reply(Messages.USER)
    info_user_msg = await message.reply(Messages.PROCESSING2)
    try:
        user_id = message.text.split(None, 1)[1]
    except:
        await info_user_msg.edit(Messages.PROVIDE_UID)
        return
    up_count = get_uploaded(user_id)
    if up_count == "":
        up_count = Messages.UNABLE_FETCH
    await info_user_msg.edit(Messages.USER_INFO.format(user_id, up_count))


@unzipperbot.on_message(filters.command("user2") & filters.user(Config.BOT_OWNER))
async def info_user2(_, message: Message):
    user2_msg = await message.reply(Messages.PROCESSING2)
    try:
        user_id = message.text.split(None, 1)[1]
    except:
        await user2_msg.edit(Messages.PROVIDE_UID2)
        return
    try:
        infos = await unzipperbot.get_users(user_id)
    except:
        await user2_msg.edit(Messages.UID_UNAME_INVALID)
        return
    if not isinstance(user_id, int):
        try:
            user_id = infos.id
        except:
            pass
    await user2_msg.edit(Messages.USER2_INFO.format(infos, user_id))


@unzipperbot.on_message(filters.command("self") & filters.user(Config.BOT_OWNER))
async def info_self(_, message: Message):
    self_infos = await unzipperbot.get_me()
    await message.reply(f"`{self_infos}`")


@unzipperbot.on_message(
    filters.private & filters.command("getthumbs") & filters.user(Config.BOT_OWNER)
)
async def get_all_thumbs(_, message: Message):
    paths = await get_files(path=Config.THUMB_LOCATION)
    if not paths:
        await message.reply(Messages.NO_THUMBS)
    for doc_f in paths:
        try:
            await unzipperbot.send_document(
                chat_id=message.chat.id,
                document=doc_f,
                file_name=doc_f.split("/")[-1],
                reply_to_message_id=message.id,
                caption=Messages.EXT_CAPTION.format(doc_f),
            )
        except FloodWait as f:
            await sleep(f.value)
            await unzipperbot.send_document(
                chat_id=message.chat.id,
                document=doc_f,
                file_name=doc_f.split("/")[-1],
                reply_to_message_id=message.id,
                caption=Messages.EXT_CAPTION.format(doc_f),
            )
        except RPCError as e:
            LOGGER.error(e)


@unzipperbot.on_message(
    filters.private & filters.command("redbutton") & filters.user(Config.BOT_OWNER)
)
async def red_alert(_, message: Message):
    await message.reply("🚧 WIP 🚧")
    # restart the whole bot, maybe using execl
    # but also need to stop currently ongoing processes…


@unzipperbot.on_message(
    filters.private & filters.command("maintenance") & filters.user(Config.BOT_OWNER)
)
async def maintenance_mode(_, message: Message):
    mstatus = await get_maintenance()
    text = Messages.MAINTENANCE.format(mstatus) + "\n\n" + Messages.MAINTENANCE_ASK
    mess = await message.reply(text)
    try:
        newstate = message.text.split(None, 1)[1]
    except:
        await mess.edit(Messages.MAINTENANCE_FAIL)
        return
    if newstate not in ["True", "False"]:
        await mess.edit(Messages.MAINTENANCE_FAIL)
        return
    await set_maintenance(newstate == "True")
    await message.reply(Messages.MAINTENANCE_DONE.format(newstate))


@unzipperbot.on_message(filters.private & filters.command("addthumb"))
async def thumb_add(_, message: Message):
    await add_thumb(unzipperbot, message)


@unzipperbot.on_message(filters.private & filters.command("delthumb"))
async def thumb_del(_, message: Message):
    await del_thumb(message)


@unzipperbot.on_message(
    filters.private & filters.command("cleanall") & filters.user(Config.BOT_OWNER)
)
async def del_everything(_, message: Message):
    cleaner = await message.reply(Messages.ERASE_ALL)
    try:
        shutil.rmtree(Config.DOWNLOAD_LOCATION)
        await cleaner.edit(Messages.CLEANED)
        os.mkdir(Config.DOWNLOAD_LOCATION)
    except:
        await cleaner.edit(Messages.NOT_CLEANED)


@unzipperbot.on_message(
    filters.private & filters.command("cleantasks") & filters.user(Config.BOT_OWNER)
)
async def del_tasks(_, message: Message):
    ongoing_tasks = await get_ongoing_tasks()
    number = len(ongoing_tasks)
    cleaner = await message.reply(Messages.ERASE_TASKS.format(number))

    for task in ongoing_tasks:
        user_id = task.get("user_id")
        await del_ongoing_task(user_id)
        try:
            shutil.rmtree(f"{Config.DOWNLOAD_LOCATION}/{user_id}")
        except:
            pass

    await cleaner.edit(Messages.ERASE_TASKS_SUCCESS.format(number))


async def send_logs(user_id):
    with open("unzip-log.txt", "rb") as doc_f:
        try:
            await unzipperbot.send_document(
                chat_id=user_id,
                document=doc_f,
                file_name=doc_f.name,
            )
            LOGGER.info(Messages.LOG_SENT.format(user_id))
        except FloodWait as f:
            await sleep(f.value)
            await unzipperbot.send_document(
                chat_id=user_id,
                document=doc_f,
                file_name=doc_f.name,
            )
        except RPCError as e:
            await unzipperbot.send_message(chat_id=user_id, text=e)


def clear_logs():
    with open("file.txt", "w") as f:
        f.close()


@unzipperbot.on_message(
    filters.private & filters.command("logs") & filters.user(Config.BOT_OWNER)
)
async def logz(_, message: Message):
    await send_logs(message.from_user.id)


@unzipperbot.on_message(
    filters.private & filters.command("restart") & filters.user(Config.BOT_OWNER)
)
async def restart(_, message: Message):
    try:
        folder_to_del = os.path.dirname(os.path.abspath(Config.DOWNLOAD_LOCATION))
        shutil.rmtree(Config.DOWNLOAD_LOCATION)
        LOGGER.info(Messages.DELETED_FOLDER.format(folder_to_del))
    except:
        pass
    restarttime = time.strftime("%Y/%m/%d - %H:%M:%S")
    await message.reply_text(Messages.RESTARTED_AT.format(restarttime), quote=True)
    await send_logs(message.from_user.id)
    LOGGER.info(Messages.RESTARTING.format(message.from_user.id))
    clear_logs()
    os.execl(executable, executable, "-m", "unzipper")


@unzipperbot.on_message(
    filters.private & filters.command("gitpull") & filters.user(Config.BOT_OWNER)
)
async def pull_updates(_, message: Message):
    git_reply = await message.reply(Messages.PULLING)
    repo = git.Repo("/app")
    current = repo.head.commit
    repo.remotes.origin.pull()
    if current != repo.head.commit:
        await git_reply.edit(Messages.PULLED)
        await restart(_, message)
    else:
        await git_reply.edit(Messages.NO_PULL)


@unzipperbot.on_message(filters.command("donate"))
async def donate_help(_, message: Message):
    await message.reply(Messages.DONATE_TEXT)


@unzipperbot.on_message(filters.command("vip"))
async def vip_help(_, message: Message):
    await message.reply(Messages.VIP_INFO)


@unzipperbot.on_message(
    filters.private & filters.command("dbexport") & filters.user(Config.BOT_OWNER)
)
async def export_db(_, message):
    await message.reply("🚧 WIP 🚧")
    # Will use https://www.mongodb.com/docs/database-tools/mongoexport/ on command to export as CSV


@unzipperbot.on_message(filters.command("commands"))
async def getall_cmds(_, message):
    await message.reply(
        Messages.COMMANDS_LIST,
        disable_web_page_preview=True,
    )


@unzipperbot.on_message(filters.command("admincmd") & filters.user(Config.BOT_OWNER))
async def getadmin_cmds(_, message):
    await message.reply(
        Messages.ADMINCMD,
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


@unzipperbot.on_message(filters.command("eval") & filters.user(Config.BOT_OWNER))
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


@unzipperbot.on_message(filters.command("exec") & filters.user(Config.BOT_OWNER))
async def exec_command(_, message):
    cmd = message.text.split(" ", maxsplit=1)[1]
    process = await create_subprocess_shell(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    e = stderr.decode()
    o = stdout.decode()

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
