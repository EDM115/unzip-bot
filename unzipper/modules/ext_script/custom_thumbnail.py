# Copyright (c) 2022 EDM115

import os
import time

from pyrogram import Client, filters
from PIL import Image

# from pykeyboard import InlineKeyboard, InlineButton

from unzipper import LOGGER
from config import Config
from unzipper.modules.bot_data import Buttons, Messages

"""
async def thumb_keyboard():
    keyboard = InlineKeyboard(row_width=2)
    keyboard.add(
        InlineButton(Buttons.BROKEN, 'callback:1'),
    )
"""


async def silent_del(user_id):
    try:
        thumb_location = Config.THUMB_LOCATION + "/" + str(user_id) + ".jpg"
        os.remove(thumb_location)
    except:
        pass


async def add_thumb(_, message):
    user_id = str(message.from_user.id)
    if message.reply_to_message is not None:
        reply_message = message.reply_to_message
        if reply_message.media_group_id is not None:  # album sent
            LOGGER.warning(f"{user_id} tried to save a thumbnail from an album")
            return message.reply(
                "You can't use an album. Reply to a single picture sent as photo (not as document)"
            )
        else:
            thumb_location = Config.THUMB_LOCATION + "/" + user_id + ".jpg"
            pre_thumb = Config.THUMB_LOCATION + "/not_resized_" + user_id + ".jpg"
            final_thumb = Config.THUMB_LOCATION + "/waiting_" + user_id + ".jpg"
            if os.path.exists(thumb_location) and os.path.isfile(thumb_location):
                LOGGER.warning(f"Thumb exists for {user_id}")
                await message.reply(
                    text=Messages.EXISTING_THUMB, reply_markup=Buttons.THUMB_REPLACEMENT
                )
            else:
                await message.reply(
                    text=Messages.SAVING_THUMB, reply_markup=Buttons.THUMB_SAVE
                )
            LOGGER.warning(f"Downloading thumbnail of {user_id}…")
            await _.download_media(message=reply_message, file_name=pre_thumb)
            LOGGER.warning("Thumbnail downloaded")
            size = 320, 320
            try:
                previous = Image.open(pre_thumb)
                previous.thumbnail(size, Image.ANTIALIAS)
                previous.save(final_thumb, "JPEG")
                LOGGER.warning("Thumbnail saved")
            except:
                LOGGER.warning("Failed to generate thumb")
                try:
                    os.remove(pre_thumb)
                except:
                    pass
                try:
                    os.remove(final_thumb)
                except:
                    pass
                return await message.reply("Error happened 😕 Try again later")
    else:
        await _.send_message(
            chat_id=message.chat.id,
            text=Messages.PLS_REPLY,
            reply_to_message_id=message.id
        )
        LOGGER.warning("pls reply to an image")


"""
@pyrogram.Client.on_message(pyrogram.Filters.photo)
async def save_thumb(_, message):
    if message.media_group_id is not None:
        # album is sent
        download_location = Config.DOWNLOAD_LOCATION + "/" + str(message.from_user.id) + "/" + str(message.media_group_id) + "/"
        # create download directory, if not exist
        if not os.path.isdir(download_location):
            os.makedirs(download_location)
        await _.download_media(
            message=message,
            file_name=download_location
        )
    else:
        # received single photo
        download_location = Config.DOWNLOAD_LOCATION + "/" + str(message.from_user.id) + ".jpg"
        await _.download_media(
            message=message,
            file_name=download_location
        )
        await _.send_message(
            chat_id=message.chat.id,
            text=Messages.SAVED_THUMBNAIL,
            reply_to_message_id=message.id
        )
"""


async def del_thumb(_, message):
    thumb_location = Config.THUMB_LOCATION + "/" + str(message.from_user.id)
    try:
        os.remove(thumb_location + ".jpg")
    except:
        pass
    await _.send_message(
        chat_id=message.chat.id,
        text=Messages.DELETED_THUMB,
        reply_to_message_id=message.id
    )


async def thumb_exists(chat_id):
    thumb_location = Config.THUMB_LOCATION + "/" + str(chat_id) + ".jpg"
    return os.path.exists(thumb_location)
