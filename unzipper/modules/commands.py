# Copyright (c) 2022 EDM115

import os
import asyncio
import re
import shutil
import psutil

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait

from .bot_data import Buttons, Messages
from unzipper.helpers.unzip_help import humanbytes
from config import Config


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

@Client.on_message(filters.private & filters.command("me"))
async def me_stats(_, message: Message):
    me_msg = await message.reply("This is a WIP command that would allow you to get more stats about your utilisation of me 🤓")
    me_info = await unzip_bot.ask(chat_id=query.message.chat.id ,text="Send anything :")
    await unzip_bot.send_message(chat_id=query.message.chat.id, text=me_info)
