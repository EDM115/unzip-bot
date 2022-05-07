# Copyright (c) 2022 EDM115

import os
import asyncio
import re
import shutil
import psutil
from os import execl
from time import sleep, time
from sys import executable

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait, RPCError

from .bot_data import Buttons, Messages
from unzipper.helpers.database import (
    check_user,
    del_user,
    count_users,
    get_users_list,
    # Banned Users db
    add_banned_user,
    del_banned_user,
    count_banned_users,
    get_upload_mode
)
from unzipper.helpers.unzip_help import humanbytes, TimeFormatter
from config import Config
from .callbacks import *
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

@Client.on_message(filters.private & filters.command("start"))
async def start_bot(_, message: Message):
    await message.reply_text(text=Messages.START_TEXT.format(message.from_user.mention), reply_markup=Buttons.START_BUTTON, disable_web_page_preview=True)

@Client.on_message(filters.private & filters.command("clean"))
async def clean_ma_files(_, message: Message):
    await message.reply_text(text=Messages.CLEAN_TXT, reply_markup=Buttons.CLN_BTNS)

@Client.on_message(filters.private & filters.command("help"))
async def help_meh(_, message: Message):
    await message.reply_text(text=Messages.HELP_TXT, reply_markup=Buttons.ME_GOIN_HOME)

@Client.on_message(filters.private & filters.command("about"))
async def about_meee(_, message: Message):
    await message.reply_text(text=Messages.ABOUT_TXT, reply_markup=Buttons.ME_GOIN_HOME, disable_web_page_preview=True)

@Client.on_message(filters.incoming & filters.private & filters.regex(https_url_regex) | filters.document)
async def extract_dis_archive(_, message: Message):
    unzip_msg = await message.reply("`Processing… ⏳`", reply_to_message_id=message.message_id)
    user_id = message.from_user.id
    download_path = f"{Config.DOWNLOAD_LOCATION}/{user_id}"
    if os.path.isdir(download_path):
        return await unzip_msg.edit("Already one process is running, don't spam 😐\n\nWanna clear your files from my server ? Then just send **/clean** command")
    if message.text and (re.match(https_url_regex, message.text)):
        await unzip_msg.edit("**What do you want 🤔**", reply_markup=Buttons.CHOOSE_E_U__BTNS)
    elif message.document:
        await unzip_msg.edit("**What do you want 🤔**", reply_markup=Buttons.CHOOSE_E_F__BTNS)
    else:
        await unzip_msg.edit("Hold up ! What should I extract there 😳")

# Database Commands
@Client.on_message(filters.private & filters.command(["mode", "setmode"]))
async def set_up_mode_for_user(_, message: Message):
    upload_mode = await get_upload_mode(message.from_user.id)
    await message.reply(Messages.SELECT_UPLOAD_MODE_TXT.format(upload_mode), reply_markup=Buttons.SET_UPLOAD_MODE_BUTTONS)

@Client.on_message(filters.private & filters.command("stats") & filters.user(Config.BOT_OWNER))
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
    # uptime = TimeFormatter(int(psutil.cpu_times().system)*1000)
    uptime = psutil.cpu_times().system
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
 ↳ **Uptime :** `{uptime}` (might be wrong)"""
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

@Client.on_message(filters.private & filters.command("broadcast") & filters.user(Config.BOT_OWNER))
async def broadcast_dis(_, message: Message):
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

@Client.on_message(filters.private & filters.command("ban") & filters.user(Config.BOT_OWNER))
async def ban_user(_, message: Message):
    ban_msg = await message.reply("`Processing… ⏳`")
    try:
        user_id = message.text.split(None, 1)[1]
    except:
        return await ban_msg.edit("Give a user id to ban 😈")
    await add_banned_user(user_id)
    await ban_msg.edit(f"**Successfully banned that user ✅** \n\n**User ID :** `{user_id}`")

@Client.on_message(filters.private & filters.command("unban") & filters.user(Config.BOT_OWNER))
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
    me_info = await message.ask(chat_id=query.message.chat.id, text="This is a WIP command that would allow you to get more stats about your utilisation of me 🤓\n\nSend anything :")
    await Client.send_message(chat_id=query.message.chat.id, text=f"`{me_info}`")

@Client.on_message(filters.private & filters.command("user") & filters.user(Config.BOT_OWNER))
async def info_user(_, message: Message):
    info_user_msg = await message.reply(f"`Processing… ⏳`")
    try:
        user_id = message.text.split(None, 1)[1]
    except:
        return await info_user_msg.edit("`Give a user id 🙂`")
    await info_user_msg.edit(f"**User ID :** `{user_id}`…\n\nWIP")

@Client.on_message(filters.private & filters.command("db") & filters.user(Config.BOT_OWNER))
async def db_info(_, message: Message):
    users_list = await get_users_list()
    db_msg = await message.reply(f"🚧 There you go :\n\n`{users_list}`")

@Client.on_message(filters.private & filters.command("dbdive") & filters.user(Config.BOT_OWNER))
async def db_dive(_, message: Message):
    dburl = Config.MONGODB_URL
    db_dive_msg = await message.reply(f"🚧 Go on [MongoDB.com](https://mongodb.com/cloud/atlas/register), u stupid 😐\n\n`{dburl}`")
    
@Client.on_message(filters.private & filters.command("redbutton") & filters.user(Config.BOT_OWNER))
async def red_alert(_, message: Message):
    await message.reply(f"WIP")

@Client.on_message(filters.private & filters.command("addthumb"))
async def thumb_add(_, message: Message):
    await message.reply(f"WIP")

@Client.on_message(filters.private & filters.command("delthumb"))
async def thumb_del(_, message: Message):
    await message.reply(f"WIP")

@Client.on_message(filters.private & filters.command("cleanall") & filters.user(Config.BOT_OWNER))
async def del_everything(_, message: Message):
    await message.reply(f"WIP")

@Client.on_message(filters.private & filters.command("logs") & filters.user(Config.BOT_OWNER))
async def send_logs(_, message: Message):
    with open('log.txt', 'rb') as doc_f:
        try:
            await Client.send_document(
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
    shutil.rmtree(Config.DOWNLOAD_LOCATION)
    LOGGER.info("Deleted {Config.DOWNLOAD_LOCATION} folder successfully")
    restarttime = TimeFormatter(time())
    await message.reply_text(f"**ℹ️ Bot restarted successfully at **`{restarttime}`", quote=True)
    LOGGER.info(f"{message.from_user.id} : Restarting…")
    execl(executable, executable, "-m", "unzipper")
