# Copyright (c) 2023 EDM115
import os
import re
import shutil
import time
from asyncio import sleep
from sys import executable

import git
import psutil
from pyrogram import enums, filters
from pyrogram.errors import FloodWait, RPCError
from pyrogram.types import Message

from config import Config
from unzipper import LOGGER, boottime, unzipperbot
from unzipper.helpers.database import (
    add_merge_task,
    add_user,
    add_banned_user,
    add_vip_user,
    check_user,
    count_banned_users,
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
    count_ongoing_tasks,
    set_maintenance,
)
from unzipper.helpers.unzip_help import humanbytes, timeformat_sec
from unzipper.modules.ext_script.custom_thumbnail import add_thumb, del_thumb
from unzipper.modules.ext_script.ext_helper import get_files

from .bot_data import Buttons, Messages

# Regex for urls
https_url_regex = r"((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*"


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
        if not any(uid == task["user_id"] for task in ogtasks):
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
        await message.reply_text(text=Messages.HELP_TXT, reply_markup=Buttons.ME_GOIN_HOME)
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


@unzipperbot.on_message(
    filters.incoming & filters.private & filters.document
    | filters.regex(https_url_regex)
)
async def extract_archive(_, message: Message):
    try:
        if message.chat.type != enums.ChatType.PRIVATE:
            return
        unzip_msg = await message.reply(Messages.PROCESSING2, reply_to_message_id=message.id)
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
            await unzip_msg.edit(
                text=Messages.CHOOSE_EXT_MODE.format("file", "🗂️"),
                reply_markup=Buttons.CHOOSE_E_F__BTNS,
            )
        else:
            await unzip_msg.edit(Messages.UNVALID)
    except FloodWait as f:
        await sleep(f.value)
        await extract_archive(_, message)


@unzipperbot.on_message(filters.private & filters.command("cancel"))
async def cancel_task_by_user(_, message):
    idtodel = message.id - 1
    try:
        await unzipperbot.delete_messages(chat_id=message.from_user.id, message_ids=idtodel)
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
        await message.reply(
            Messages.DONE,
            reply_markup=Buttons.MERGE_THEM_ALL
        )
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
        b_cast = await _do_broadcast(message=r_msg, user=user["user_id"])
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
        await bc_msg.edit(Messages.BC_DONE.format(
            total_users,
            success_no,
            failed_no,
        ))
    except FloodWait as f:
        await sleep(f.value)
        await bc_msg.edit(Messages.BC_DONE.format(
            total_users,
            success_no,
            failed_no,
        ))


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
        await ban_msg.edit(Messages.BANNED.format(user_id))


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


@unzipperbot.on_message(filters.private & filters.command("maintenance") & filters.user(Config.BOT_OWNER))
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
        user_id = task["user_id"]
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
    open('file.txt', 'w').close()


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
    await message.reply_text(
        Messages.RESTARTED_AT.format(restarttime), quote=True
    )
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
    time.sleep(2)
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
    filters.private & filters.command("addvip") & filters.user(Config.BOT_OWNER)
)
async def add_vip(_, message: Message):
    if message.reply_to_message is None:
        await message.reply(Messages.VIP_REQUIRED_MESSAGE)
        return
    message = message.reply_to_message
    messagearray = message.text.splitlines()
    if len(messagearray) != 13:
        await message.reply(Messages.VIP_REQUIRED_MESSAGE)
        return
    if not messagearray[0].isdigit():
        await message.reply(Messages.VIP_REQUIRED_MESSAGE)
        return
    user_id = int(messagearray[0])
    dateregex = r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z"
    if not re.match(dateregex, messagearray[1]):
        await message.reply(Messages.VIP_REQUIRED_MESSAGE)
        return
    subscription = messagearray[1]
    if not re.match(dateregex, messagearray[2]):
        await message.reply(Messages.VIP_REQUIRED_MESSAGE)
        return
    ends = messagearray[2]
    if messagearray[3] not in ["paypal", "telegram", "sponsor", "bmac"]:
        await message.reply(Messages.VIP_REQUIRED_MESSAGE)
        return
    used = messagearray[3]
    if messagearray[4] not in ["monthly", "yearly"]:
        await message.reply(Messages.VIP_REQUIRED_MESSAGE)
        return
    billed = messagearray[4]
    if messagearray[5] not in ["True", "False"]:
        await message.reply(Messages.VIP_REQUIRED_MESSAGE)
        return
    early = messagearray[5] == "True"
    if messagearray[6] not in ["True", "False"]:
        await message.reply(Messages.VIP_REQUIRED_MESSAGE)
        return
    donator = messagearray[6] == "True"
    if not re.match(dateregex, messagearray[7]):
        await message.reply(Messages.VIP_REQUIRED_MESSAGE)
        return
    started = messagearray[7]
    if not messagearray[8].isdigit():
        await message.reply(Messages.VIP_REQUIRED_MESSAGE)
        return
    successful = int(messagearray[8])
    if messagearray[9] not in ["True", "False"]:
        await message.reply(Messages.VIP_REQUIRED_MESSAGE)
        return
    gap = messagearray[9] == "True"
    if messagearray[10] not in ["True", "False"]:
        await message.reply(Messages.VIP_REQUIRED_MESSAGE)
        return
    gifted = messagearray[10] == "True"
    if not re.match(r"[a-zA-Z0-9]{1,34}", messagearray[11]):
        await message.reply(Messages.VIP_REQUIRED_MESSAGE)
        return
    referral = messagearray[11]
    if messagearray[12] not in ["True", "False"]:
        await message.reply(Messages.VIP_REQUIRED_MESSAGE)
        return
    lifetime = messagearray[12] == "True"
    await add_vip_user(user_id, subscription, ends, used, billed, early, donator, started, successful, gap, gifted, referral, lifetime)
    await message.reply(Messages.VIP_ADDED_USER.format(user_id, subscription, ends, used, billed, early, donator, started, successful, gap, gifted, referral, lifetime))


@unzipperbot.on_message(filters.command("delvip") & filters.user(Config.BOT_OWNER))
async def del_vip(_, message: Message):
    del_msg = await message.reply(Messages.PROVIDE_UID)
    try:
        user_id = message.text.split(None, 1)[1]
    except:
        await del_msg.edit(Messages.UNBAN_ID)
        return
    db = await add_user(user_id)
    bdb = await del_banned_user(user_id)
    text = ""
    if db == -1:
        text += Messages.ALREADY_ADDED.format(user_id)
    if bdb == -1:
        text += Messages.ALREADY_UNBANNED.format(user_id)
    if text != "":
        await del_msg.edit(text)
    else:
        await del_msg.edit(Messages.UNBANNED.format(user_id))


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


disabled = """ async def exec_message_f(client, message):
    if message.from_user.id in AUTH_CHANNEL:
        DELAY_BETWEEN_EDITS = 0.3
        PROCESS_RUN_TIME = 100
        cmd = message.text.split(" ", maxsplit=1)[1]

        reply_to_id = message.message_id
        if message.reply_to_message:
            reply_to_id = message.reply_to_message.message_id

        start_time = time.time() + PROCESS_RUN_TIME
        process = await asyncio.create_subprocess_shell(
            cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        e = stderr.decode()
        if not e:
            e = "No Error"
        o = stdout.decode()
        if not o:
            o = "No Output"
        else:
            _o = o.split("\n")
            o = "`\n".join(_o)
        OUTPUT = f"**QUERY:**\n__Command:__\n`{cmd}` \n__PID:__\n`{process.pid}`\n\n**stderr:** \n`{e}`\n**Output:**\n{o}"

        if len(OUTPUT) > MAX_MESSAGE_LENGTH:
            with io.BytesIO(str.encode(OUTPUT)) as out_file:
                out_file.name = "exec.text"
                await client.send_document(
                    chat_id=message.chat.id,
                    document=out_file,
                    caption=cmd,
                    disable_notification=True,
                    reply_to_message_id=reply_to_id,
                )
            await message.delete()
        else:
            await message.reply_text(OUTPUT)

async def eval_message_f(client, message):
    if message.from_user.id in AUTH_CHANNEL:
        status_message = await message.reply_text("Processing ...")
        cmd = message.text.split(" ", maxsplit=1)[1]

        reply_to_id = message.message_id
        if message.reply_to_message:
            reply_to_id = message.reply_to_message.message_id

        old_stderr = sys.stderr
        old_stdout = sys.stdout
        redirected_output = sys.stdout = io.StringIO()
        redirected_error = sys.stderr = io.StringIO()
        stdout, stderr, exc = None, None, None

        try:
            await aexec(cmd, client, message)
        except Exception:
            exc = traceback.format_exc()

        stdout = redirected_output.getvalue()
        stderr = redirected_error.getvalue()
        sys.stdout = old_stdout
        sys.stderr = old_stderr

        evaluation = ""
        if exc:
            evaluation = exc
        elif stderr:
            evaluation = stderr
        elif stdout:
            evaluation = stdout
        else:
            evaluation = "Success"

        final_output = (
            "<b>EVAL</b>: <code>{}</code>\n\n<b>OUTPUT</b>:\n<code>{}</code> \n".format(
                cmd, evaluation.strip()
            )
        )

        if len(final_output) > MAX_MESSAGE_LENGTH:
            with open("eval.text", "w+", encoding="utf8") as out_file:
                out_file.write(str(final_output))
            await message.reply_document(
                document="eval.text",
                caption=cmd,
                disable_notification=True,
                reply_to_message_id=reply_to_id,
            )
            os.remove("eval.text")
            await status_message.delete()
        else:
            await status_message.edit(final_output)

async def aexec(code, client, message):
    exec(
        f"async def __aexec(client, message): "
        + "".join(f"\n {l}" for l in code.split("\n"))
    )
    return await locals()["__aexec"](client, message) """
