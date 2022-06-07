# Copyright (c) 2022 EDM115

import os
import asyncio
import re
import shutil
import psutil
from os import execl
import time
from sys import executable

from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery
from pyrogram.errors import FloodWait, RPCError

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
from config import Config
from unzipper import LOGGER

# Regex for http/https urls
https_url_regex = ("((http|https)://)(www.)?" +
                   "[a-zA-Z0-9@:%._\\+~#?&//=]" +
                   "{2,256}\\.[a-z]" +
                   "{2,6}\\b([-a-zA-Z0-9@:%" +
                   "._\\+~#?&//=]*)")

# Function to check user status (is banned or not)
@Client.on_message(filters.private)
async def _(_, message: Message):
    await check_user(message)

@Client.on_message(filters.command("start"))
async def start_bot(_, message: Message):
    await message.reply_text(text=Messages.START_TEXT.format(message.from_user.mention), reply_markup=Buttons.START_BUTTON, disable_web_page_preview=True)

@Client.on_message(filters.private & filters.command("clean"))
async def clean_my_files(_, message: Message):
    await message.reply_text(text=Messages.CLEAN_TXT, reply_markup=Buttons.CLN_BTNS)

@Client.on_message(filters.command("help"))
async def help_me(_, message: Message):
    await message.reply_text(text=Messages.HELP_TXT, reply_markup=Buttons.ME_GOIN_HOME)

@Client.on_message(filters.command("about"))
async def about_me(_, message: Message):
    await message.reply_text(text=Messages.ABOUT_TXT, reply_markup=Buttons.ME_GOIN_HOME, disable_web_page_preview=True)

@Client.on_message(filters.incoming & filters.private & filters.regex(https_url_regex) | filters.document)
async def extract_archive(_, message: Message):
    unzip_msg = await message.reply("`Processing… ⏳`", reply_to_message_id=message.message_id)
    user_id = message.from_user.id
    download_path = f"{Config.DOWNLOAD_LOCATION}/{user_id}"
    if os.path.isdir(download_path):
        return await unzip_msg.edit("Already one process is running, don't spam 😐\n\nWanna clear your files from my server ? Then just send **/clean** command")
    if message.text and (re.match(https_url_regex, message.text)):
        await unzip_msg.edit("**Select the extraction mode for that URL 👀**", reply_markup=Buttons.CHOOSE_E_U__BTNS)
    elif message.document:
        await unzip_msg.edit("**Select the extraction mode for that file 👀**", reply_markup=Buttons.CHOOSE_E_F__BTNS)
    else:
        await unzip_msg.edit("Send a valid archive/URL 🙄")

# Database Commands
@Client.on_message(filters.private & filters.command(["mode", "setmode"]))
async def set_mode_for_user(_, message: Message):
    upload_mode = await get_upload_mode(message.from_user.id)
    await message.reply(text=Messages.SELECT_UPLOAD_MODE_TXT.format(upload_mode), reply_markup=Buttons.SET_UPLOAD_MODE_BUTTONS)

@Client.on_message(filters.command("stats") & (filters.user(Config.BOT_OWNER)) | filters.user(Config.LOGS_CHANNEL))
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
    disk_usage = psutil.disk_usage('/').percent
    uptime = timeformat_sec(int(psutil.cpu_times().user)) # Not divided thanks to timeformat_sec() funct
    total_users = await count_users()
    total_banned_users = await count_banned_users()
    await stats_msg.edit(f"""
**💫 Current bot stats 💫 [BETA]**

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
 ↳ **Uptime :** `{uptime}` (might be 69% wrong)"""
                         )
    
# Attempt to not make that available for non owner
#@Client.on_message(filters.private & filters.command("stats") & filters.user(!=Config.BOT_OWNER))
#async def send_stats(_, message: Message):
#    await message.reply("You are not owner 🧐 Stop that")

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
        return await bc_msg.edit("Reply to a message to broadcast 📡")
    users_list = await get_users_list()
    # trying to broadcast
    await bc_msg.edit("Broadcasting has started, this may take while 😪")
    success_no = 0
    failed_no = 0
    total_users = await count_users()
    for user in users_list:
        b_cast = await _do_broadcast(message=r_msg, user=user["user_id"])
        if b_cast == 200:
            success_no += 1
        else:
            failed_no += 1
    await bc_msg.edit(f"""
**Broadcast completed ✅**

**Total users :** `{total_users}`
**Successful responses :** `{success_no}`
**Failed responses :** `{failed_no}`
    """)

@Client.on_message(filters.command("sendto") & filters.user(Config.BOT_OWNER))
async def send_this(_, message: Message):
    sd_msg = await message.reply("`Processing… ⏳`")
    r_msg = message.reply_to_message
    if not r_msg:
        return await sd_msg.edit("Reply to a message to send it 📡")
    try:
        user_id = message.text.split(None, 1)[1]
    except:
        return await sd_msg.edit("Give a user id to send a message")
    await sd_msg.edit("Sending it, please wait… 😪")
    send = await _do_broadcast(message=r_msg, user=user_id)
    if send == 200:
        await sd_msg.edit(f"Send message successfully to `{user_id}`")
    else:
        await sd_msg.edit(f"It failed 😣 Retry. If it fails again, it means that {user_id} haven't started bot yet, or he's private/banned/whatever")

@Client.on_message(filters.command("ban") & filters.user(Config.BOT_OWNER))
async def ban_user(_, message: Message):
    ban_msg = await message.reply("`Processing… ⏳`")
    try:
        user_id = message.text.split(None, 1)[1]
    except:
        return await ban_msg.edit("Give a user id to ban 😈")
    await add_banned_user(user_id)
    await ban_msg.edit(f"**Successfully banned that user ✅** \n\n**User ID :** `{user_id}`")

@Client.on_message(filters.command("unban") & filters.user(Config.BOT_OWNER))
async def unban_user(_, message: Message):
    unban_msg = await message.reply("`Processing… ⏳`")
    try:
        user_id = message.text.split(None, 1)[1]
    except:
        return await unban_msg.edit("Give a user id to unban 😇")
    await del_banned_user(user_id)
    await unban_msg.edit(f"**Successfully unbanned that user ✅** \n\n**User ID :** `{user_id}`")

@Client.on_message(filters.private & filters.command("me"))
async def me_stats(_, message: Message):
    me_info = await _.ask(chat_id=message.chat.id, text="This is a WIP command that would allow you to get more stats about your utilisation of me 🤓\n\nSend anything :")
    #r_message = query.message.reply_to_message
    await _.send_message(chat_id=message.chat.id, text=f"`{me_info}`")

@Client.on_message(filters.command("user") & filters.user(Config.BOT_OWNER))
async def info_user(_, message: Message):
    info_user_msg = await message.reply(f"`Processing… ⏳`")
    try:
        user_id = message.text.split(None, 1)[1]
    except:
        return await info_user_msg.edit("Give a user id 🙂")
    up_count = get_uploaded(user_id)
    await info_user_msg.edit(f"**User ID :** `{user_id}`\n`{up_count}` files uploaded\n…\n\nWIP")

@Client.on_message(filters.private & filters.command("db") & filters.user(Config.BOT_OWNER))
async def db_info(_, message: Message):
    users_list = await get_users_list()
    db_msg = await message.reply(f"🚧 There you go :\n\n`{users_list}`")

@Client.on_message(filters.private & filters.command("dbdive") & filters.user(Config.BOT_OWNER))
async def db_dive(_, message: Message):
    dburl = Config.MONGODB_URL
    db_dive_msg = await message.reply(f"🚧 Go on [MongoDB.com](https://account.mongodb.com/account/login?nds=true), u stupid 😐\n\n`{dburl}`")
    
@Client.on_message(filters.private & filters.command("redbutton") & filters.user(Config.BOT_OWNER))
async def red_alert(_, message: Message):
    await message.reply("🚧 WIP 🚧")
    # restart the whole bot, maybe using execl
    # but also need to stop currently ongoing processes…

@Client.on_message(filters.private & filters.command("addthumb"))
async def thumb_add(_, message: Message):
    await message.reply("🚧 WIP 🚧")
    await add_thumb(_, message)

@Client.on_message(filters.private & filters.command("delthumb"))
async def thumb_del(_, message: Message):
    await message.reply("🚧 WIP 🚧")
    await del_thumb(_, message)

@Client.on_message(filters.private & filters.command("cleanall") & filters.user(Config.BOT_OWNER))
async def del_everything(_, message: Message):
    await message.reply("🚧 WIP 🚧\n\nCleaning…")
    try:
        shutil.rmtree(os.path.dirname(os.path.abspath(__file__)))
        await message.reply("The whole server have been cleaned 😌")
    except:
        await message.reply("An error happened 😕 probably because command is unstable")

@Client.on_message(filters.private & filters.command("logs") & filters.user(Config.BOT_OWNER))
async def send_logs(_, message: Message):
    with open('unzip-log.txt', 'rb') as doc_f:
        try:
            await _.send_document(
                chat_id=message.chat.id,
                document=doc_f,
                file_name=doc_f.name,
                reply_to_message_id=message.message_id
            )
            LOGGER.info(f"Log file sent to {message.from_user.id}")
        except FloodWait as e:
            sleep(e.x)
        except RPCError as e:
            message.reply_text(e, quote=True)

@Client.on_message(filters.private & filters.command("restart") & filters.user(Config.BOT_OWNER))
async def restart(client, message):
    folder_to_del = Config.DOWNLOAD_LOCATION
    shutil.rmtree(folder_to_del)
    LOGGER.info("Deleted {folder_to_del} folder successfully")
    restarttime = time.strftime("%Y/%m/%d - %H:%M:%S")
    await message.reply_text(f"**ℹ️ Bot restarted successfully at **`{restarttime}`", quote=True)
    LOGGER.info(f"{message.from_user.id} : Restarting…")
    execl(executable, executable, "-m", "unzipper")

@Client.on_message(filters.private & filters.command("dbexport") & filters.user(Config.BOT_OWNER))
async def export_db(client, message):
    await message.reply("🚧 WIP 🚧")
    # Will use https://www.mongodb.com/docs/database-tools/mongoexport/ on command to export as CSV

@Client.on_message(filters.command("commands"))
async def getall_cmds(client, message):
    await message.reply("""
Here is the list of the commands you can use (only in private btw) :

**{send any file or URL}** : Prompt the extract dialog
**/start** : To know if I'm online. Also useful for fixing bugs and using the latest version of me
**/help** : Gives a simple help
**/about** : Know more about me
**/clean** : Remove your files from my server. Also useful if a task failed
**/mode** : Change your upload mode (either `doc` or `video`)
**/me** : Useless commands. At least you can know on which Telegram DataCenter your profile is stored
**/addthumb** : Upload with a permanant custom thumbnail. Don't work for now
**/delthumb** : Removes your thumbnail
**/commands** : This message

**/admincmd** : Only if you are the Owner
    """)

@Client.on_message(filters.command("admincmd") & filters.user(Config.BOT_OWNER))
async def getadmin_cmds(client, message):
    await message.reply("""
Here's all the commands that only the owner (you) can use :

**/commands** : For all the other commands
**/stats** : Know all the current stats about me. If you're running on Heroku, it's reset every day (dynos yeah…)
**/broadcast** : Send something to all the users
**/sendto {user_id}** : Same as broadcast but for a single user. Don't handle replies for now…
**/ban {user_id}** : Ban an user. He no longer can use your bot, except if…
**/unban {user_id}** : …you unban him. All his stats and settings stays saved after a ban
**/user {user_id}** : Know more about the use of your bot by a single user
**/db** : Sends an unorganized list of all the user's id. I need to sort that
**/dbdive** : Useless. Will provide a way to see it online, but MongoDB already does it
**/redbutton** : Will fully restart bot + server
**/cleanall** : Same as `/clean`, but for the whole server
**/logs** : Send you the logs (all of them). Useful for bug tracking. Send them to **@EDM115** if you don't understand them/need help
**/restart** : Does a basic restart, less intrusive as the `/redbutton` one
**/dbexport** : Exports the whole database as CSV
**/admincmd** : This message
    """)

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
