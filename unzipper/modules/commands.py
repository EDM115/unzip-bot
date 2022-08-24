# Copyright (c) 2022 EDM115

import os
import asyncio
import re
import shutil
import psutil
import time
from sys import executable

from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery
from pyrogram.errors import FloodWait, RPCError

from unzipper import boottime
from .bot_data import Buttons, Messages
from unzipper.helpers.database import (
    check_user,
    del_user,
    count_users,
    get_users_list,
    add_banned_user,
    del_banned_user,
    count_banned_users,
    get_upload_mode,
    get_uploaded
)
from unzipper.helpers.unzip_help import humanbytes, TimeFormatter, timeformat_sec
from unzipper.modules.ext_script.custom_thumbnail import add_thumb, del_thumb
from unzipper.modules.ext_script.ext_helper import get_files
from unzipper.modules.ext_script.up_helper import send_file
from config import Config
from unzipper import LOGGER, unzipperbot

# Regex for urls
https_url_regex = "((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*"

# Function to check user status (is banned or not)
@Client.on_message(filters.private)
async def _(_, message: Message):
    await check_user(message)


@Client.on_message(filters.command("start"))
async def start_bot(_, message: Message):
    await message.reply_text(
        text=Messages.START_TEXT.format(message.from_user.mention),
        reply_markup=Buttons.START_BUTTON,
        disable_web_page_preview=True
    )


@Client.on_message(filters.private & filters.command("clean"))
async def clean_my_files(_, message: Message):
    await message.reply_text(text=Messages.CLEAN_TXT, reply_markup=Buttons.CLN_BTNS)


@Client.on_message(filters.command("help"))
async def help_me(_, message: Message):
    await message.reply_text(text=Messages.HELP_TXT, reply_markup=Buttons.ME_GOIN_HOME)


@Client.on_message(filters.command("about"))
async def about_me(_, message: Message):
    await message.reply_text(
        text=Messages.ABOUT_TXT,
        reply_markup=Buttons.ME_GOIN_HOME,
        disable_web_page_preview=True
    )


@Client.on_message(
    filters.incoming & filters.private & filters.regex(https_url_regex)
    | filters.document
)
async def extract_archive(_, message: Message):
    unzip_msg = await message.reply("`Processing… ⏳`", reply_to_message_id=message.id)
    user_id = message.from_user.id
    download_path = f"{Config.DOWNLOAD_LOCATION}/{user_id}"
    if os.path.isdir(download_path):
        return await unzip_msg.edit(
            "Already one process is running, don't spam 😐\n\nWanna clear your files from my server ? Then just send **/clean** command"
        )
    if message.text and (re.match(https_url_regex, message.text)):
        await unzip_msg.edit(
            text=Messages.CHOOSE_EXT_MODE.format("URL", "🔗"),
            reply_markup=Buttons.CHOOSE_E_U__BTNS
        )
    elif message.document:
        await unzip_msg.edit(
            text=Messages.CHOOSE_EXT_MODE.format("file", "🗂️"),
            reply_markup=Buttons.CHOOSE_E_F__BTNS
        )
    else:
        await unzip_msg.edit("Send a valid archive/URL 🙄")


# Waiting for implementing CallbackQuery button for cancel
@Client.on_message(filters.private & filters.command("cancel"))
async def cancel_task_by_user(_, message):
    idtodel = message.id - 1
    try:
        await _.delete_messages(chat_id=message.from_user.id, message_ids=idtodel)
    except:
        pass
    await _.stop_transmission()
    await message.reply("Your task have successfully been canceled ❌")


# For splitted archives
@Client.on_message(filters.private & filters.command("merge"))
async def merging(_, message: Message):
    merge_msg = await message.reply(
        "Send me **all** the splitted files (.001, .002, .00×, …)\n\nOnce you sent them all, click on the `Merge 🛠️` button",
        reply_markup=Buttons.MERGE_THEM_ALL
    )
    startid = merge_msg.id + 1
    # Catch the files id + download + send to callbacks + cat + prompt dialog


# Database Commands
@Client.on_message(filters.private & filters.command("mode"))
async def set_mode_for_user(_, message: Message):
    upload_mode = await get_upload_mode(message.from_user.id)
    await message.reply(
        text=Messages.SELECT_UPLOAD_MODE_TXT.format(upload_mode),
        reply_markup=Buttons.SET_UPLOAD_MODE_BUTTONS
    )


@Client.on_message(filters.command("stats"))
async def send_stats(_, message: Message):
    stats_msg = await message.reply("`Processing… ⏳`")
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
    if message.from_user.id == Config.BOT_OWNER:
        await stats_msg.edit(
            f"""
**💫 Current bot stats 💫**

**👥 Users :** 
 ↳ **Users in database :** `{total_users}`
 ↳ **Total banned users :** `{total_banned_users}`

**💾 Disk usage :**
 ↳ **Total Disk Space :** `{total}`
 ↳ **Used :** `{used} - {disk_usage}%`
 ↳ **Free :** `{free}`

**🌐 Network usage :**
 ↳ **Uploaded :** `{sent}`
 ↳ **Downloaded :** `{recv}`

**🎛 Hardware usage :**
 ↳ **CPU usage :** `{cpu_usage}%`
 ↳ **RAM usage :** `{ram_usage}%`
 ↳ **Uptime :** `{uptime}`"""
        )
    else:
        await stats_msg.edit(
            f"""
**💫 Current bot stats 💫**

**💾 Disk usage :**
 ↳ **Total Disk Space :** `{total}`
 ↳ **Used :** `{used} - {disk_usage}%`
 ↳ **Free :** `{free}`

**🎛 Hardware usage :**
 ↳ **CPU usage :** `{cpu_usage}%`
 ↳ **RAM usage :** `{ram_usage}%`
 ↳ **Uptime :** `{uptime}`"""
        )


async def _do_broadcast(message, user):
    try:
        await message.copy(chat_id=int(user))
        return 200
    except FloodWait as e:
        asyncio.sleep(e.x)
        return _do_broadcast(message, user)
    except Exception:
        await del_user(user)


@Client.on_message(filters.command("broadcast") & filters.user(Config.BOT_OWNER))
async def broadcast_this(_, message: Message):
    bc_msg = await message.reply("`Processing… ⏳`")
    r_msg = message.reply_to_message
    if not r_msg:
        return await bc_msg.edit("Reply to a message to broadcast it 📡")
    users_list = await get_users_list()
    # trying to broadcast
    await bc_msg.edit("Broadcasting has started, this may take a while 😪")
    success_no = 0
    failed_no = 0
    total_users = await count_users()
    for user in users_list:
        b_cast = await _do_broadcast(message=r_msg, user=user["user_id"])
        if b_cast == 200:
            success_no += 1
        else:
            failed_no += 1
    await bc_msg.edit(
        f"""
**Broadcast completed ✅**

**Total users :** `{total_users}`
**Successful responses :** `{success_no}`
**Failed responses :** `{failed_no}`
    """
    )


@Client.on_message(filters.command("sendto") & filters.user(Config.BOT_OWNER))
async def send_this(_, message: Message):
    sd_msg = await message.reply("`Processing… ⏳`")
    r_msg = message.reply_to_message
    if not r_msg:
        return await sd_msg.edit("Reply to a message to send it 📡")
    try:
        user_id = message.text.split(None, 1)[1]
    except:
        return await sd_msg.edit("Give an user id to send a message")
    await sd_msg.edit("Sending it, please wait… 😪")
    send = await _do_broadcast(message=r_msg, user=user_id)
    if send == 200:
        await sd_msg.edit(f"Message successfully sent to `{user_id}`")
    else:
        await sd_msg.edit(
            f"It failed 😣 Retry\n\nIf it fails again, it means that {user_id} haven't started the bot yet, or he's private/banned/whatever"
        )


@Client.on_message(filters.command("ban") & filters.user(Config.BOT_OWNER))
async def ban_user(_, message: Message):
    ban_msg = await message.reply("`Processing… ⏳`")
    try:
        user_id = message.text.split(None, 1)[1]
    except:
        return await ban_msg.edit("Give an user id to ban 😈")
    await add_banned_user(user_id)
    await ban_msg.edit(
        f"**Successfully banned that user ✅** \n\n**User ID :** `{user_id}`"
    )


@Client.on_message(filters.command("unban") & filters.user(Config.BOT_OWNER))
async def unban_user(_, message: Message):
    unban_msg = await message.reply("`Processing… ⏳`")
    try:
        user_id = message.text.split(None, 1)[1]
    except:
        return await unban_msg.edit("Give an user id to unban 😇")
    await del_banned_user(user_id)
    await unban_msg.edit(
        f"**Successfully unbanned that user ✅** \n\n**User ID :** `{user_id}`"
    )


@Client.on_message(filters.private & filters.command("info"))
async def me_stats(_, message: Message):
    me_info = await _.ask(
        chat_id=message.chat.id,
        text="Send a text (shorter possible) from any user/chat. And you will have infos about it 👀"
    )
    await _.send_message(chat_id=message.chat.id, text=f"`{me_info}`")


@Client.on_message(filters.command("user") & filters.user(Config.BOT_OWNER))
async def info_user(_, message: Message):
    await message.reply(
        "This is a WIP command that would allow you to get more stats about your utilisation of me 🤓"
    )
    info_user_msg = await message.reply(f"`Processing… ⏳`")
    try:
        user_id = message.text.split(None, 1)[1]
    except:
        return await info_user_msg.edit("Give an user id 🙂")
    up_count = get_uploaded(user_id)
    if up_count == "":
        up_count = "Unable to fetch"
    await info_user_msg.edit(
        f"**User ID :** `{user_id}`\n`{up_count}` files uploaded\n…\n\nWIP"
    )


@Client.on_message(filters.command("user2") & filters.user(Config.BOT_OWNER))
async def info_user2(_, message: Message):
    user2_msg = await message.reply(f"`Processing… ⏳`")
    try:
        user_id = message.text.split(None, 1)[1]
    except:
        return await user2_msg.edit("Give an user id 🙂")
    try:
        infos = await _.get_users(user_id)
    except:
        return await user2_msg.edit("Error happened. The user ID is probably invalid")
    await user2_msg.edit(f"`{infos}`")


@Client.on_message(filters.command("self") & filters.user(Config.BOT_OWNER))
async def info_self(_, message: Message):
    self_infos = await _.get_me()
    await message.reply(f"`{self_infos}`")


@Client.on_message(
    filters.private & filters.command("db") & filters.user(Config.BOT_OWNER)
)
async def db_info(_, message: Message):
    users_list = await get_users_list()
    try:
        db_msg = await message.reply(f"🚧 There you go :\n\n`{users_list}`")
    except:
        await message.reply("too much users, don't fit into 1 message")


@Client.on_message(
    filters.private & filters.command("dbdive") & filters.user(Config.BOT_OWNER)
)
async def db_dive(_, message: Message):
    dburl = Config.MONGODB_URL
    db_dive_msg = await message.reply(
        f"🚧 Go on [MongoDB.com](https://account.mongodb.com/account/login?nds=true), u stupid 😐\n\nCreds here : `{dburl}`"
    )


@Client.on_message(
    filters.private & filters.command("getthumbs") & filters.user(Config.BOT_OWNER)
)
async def get_all_thumbs(_, message: Message):
    paths = await get_files(path=Config.THUMB_LOCATION)
    if not paths:
        await message.reply("No thumbnails on the server yet")
    for doc_f in paths:
        try:
            location = Config.THUMB_LOCATION + paths[doc_f]
            await _.send_document(
                chat_id=message.chat.id,
                document=location,
                file_name=paths[doc_f],
                reply_to_message_id=message.id,
                caption=Messages.EXT_CAPTION.format(paths[doc_f])
            )
        except FloodWait as e:
            sleep(e.x)
        except RPCError as e:
            message.reply_text(e, quote=True)


@Client.on_message(
    filters.private & filters.command("redbutton") & filters.user(Config.BOT_OWNER)
)
async def red_alert(_, message: Message):
    await message.reply("🚧 WIP 🚧")
    # restart the whole bot, maybe using execl
    # but also need to stop currently ongoing processes…


@Client.on_message(filters.private & filters.command("addthumb"))
async def thumb_add(_, message: Message):
    await add_thumb(_, message)


@Client.on_message(filters.private & filters.command("delthumb"))
async def thumb_del(_, message: Message):
    await del_thumb(_, message)


@Client.on_message(
    filters.private & filters.command("cleanall") & filters.user(Config.BOT_OWNER)
)
async def del_everything(_, message: Message):
    cleaner = await message.reply("🚧 WIP 🚧\n\nCleaning…")
    try:
        # shutil.rmtree(os.path.dirname(os.path.abspath(__file__)))
        shutil.rmtree(Config.DOWNLOAD_LOCATION)
        await cleaner.edit("The whole server have been cleaned 😌")
    except:
        await cleaner.edit("An error happened 😕 probably because command is unstable")


async def send_logs(user_id):
    with open("unzip-log.txt", "rb") as doc_f:
        try:
            await unzipperbot.send_document(
                chat_id=user_id,
                document=doc_f,
                file_name=doc_f.name,
            )
            LOGGER.info(f"Log file sent to {user_id}")
        except FloodWait as e:
            sleep(e.x)
        except RPCError as e:
            unzipperbot.send_message(chat_id=chat_id, text=e)


@Client.on_message(
    filters.private & filters.command("logs") & filters.user(Config.BOT_OWNER)
)
async def logz(_, message: Message):
    await send_logs(message.from_user.id)


@Client.on_message(
    filters.private & filters.command("restart") & filters.user(Config.BOT_OWNER)
)
async def restart(_, message: Message):
    folder_to_del = os.path.dirname(os.path.abspath(Config.DOWNLOAD_LOCATION))
    shutil.rmtree(Config.DOWNLOAD_LOCATION)
    LOGGER.info(f"Deleted {folder_to_del} folder successfully")
    restarttime = time.strftime("%Y/%m/%d - %H:%M:%S")
    await message.reply_text(
        f"**ℹ️ Bot restarted successfully at **`{restarttime}`", quote=True
    )
    await send_logs(message.from_user.id)
    LOGGER.info(f"{message.from_user.id} : Restarting…")
    os.execl(executable, executable, "-m", "unzipper")


@Client.on_message(
    filters.private & filters.command("dbexport") & filters.user(Config.BOT_OWNER)
)
async def export_db(client, message):
    await message.reply("🚧 WIP 🚧")
    # Will use https://www.mongodb.com/docs/database-tools/mongoexport/ on command to export as CSV


@Client.on_message(filters.command("commands"))
async def getall_cmds(client, message):
    await message.reply(
        """
Here is the list of the commands you can use (only in private btw) :

**{send any file or URL}** : Prompt the extract dialog
**/start** : To know if I'm online
**/help** : Gives a simple help
**/about** : Know more about me
**/clean** : Remove your files from my server. Also useful if a task failed
**/mode** : Change your upload mode (either `doc` or `media`)
**/stats** : Know all the current stats about me. If you're running on Heroku, it's reset every day
**/info** : Get full info about a [Message](https://docs.pyrogram.org/api/types/Message) (info returned by Pyrogram)
**/addthumb** : Upload with a custom thumbnail (not permanant yet)
**/delthumb** : Removes your thumbnail
**/commands** : This message

**/admincmd** : Only if you are the Owner
        """,
        disable_web_page_preview=True
    )


@Client.on_message(filters.command("admincmd") & filters.user(Config.BOT_OWNER))
async def getadmin_cmds(client, message):
    await message.reply(
        """
Here's all the commands that only the owner (you) can use :

**/commands** : For all the other commands
**/broadcast** : Send something to all the users
**/sendto {user_id}** : Same as broadcast but for a single user. Don't handle replies for now…
**/ban {user_id}** : Ban an user. He no longer can use your bot, except if…
**/unban {user_id}** : …you unban him. All his stats and settings stays saved after a ban
**/user {user_id}** : Know more about the use of your bot by a single user
**/user2 {user_id}** : Get full info about an [User](https://docs.pyrogram.org/api/types/User) (info returned by Pyrogram)
**/self** : Get full info about me (info returned by Pyrogram)
**/db** : Sends an unorganized list of all the user's id. I need to sort that
**/dbdive** : Useless. Will provide a way to see it online, but MongoDB already does it
**/redbutton** : Will fully restart bot + server
**/cleanall** : Same as `/clean`, but for the whole server
**/logs** : Send you the logs (all of them). Useful for bug tracking. Send them to **@EDM115** if you don't understand them/need help
**/restart** : Does a basic restart, less intrusive as the `/redbutton` one
**/dbexport** : Exports the whole database as CSV
**/admincmd** : This message
        """,
        disable_web_page_preview=True
    )


"""
async def exec_message_f(client, message):
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
    return await locals()["__aexec"](client, message)
"""
