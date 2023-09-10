# Copyright (c) 2023 EDM115
import os

from PIL import Image

from config import Config
from unzipper import LOGGER
from unzipper.modules.bot_data import Buttons, Messages
from pyrogram.errors import FloodWait
from asyncio import sleep


async def silent_del(user_id):
    try:
        thumb_location = Config.THUMB_LOCATION + "/" + str(user_id) + ".jpg"
        os.remove(thumb_location)
    except:
        pass


async def add_thumb(_, message):
    try:
        user_id = str(message.from_user.id)
        if message.reply_to_message is not None:
            reply_message = message.reply_to_message
            if reply_message.media_group_id is not None:  # album sent
                LOGGER.info(Messages.ALBUM.format(user_id))
                await message.reply(Messages.ALBUM_NOPE)
                return
            thumb_location = Config.THUMB_LOCATION + "/" + user_id + ".jpg"
            pre_thumb = Config.THUMB_LOCATION + "/not_resized_" + user_id + ".jpg"
            final_thumb = Config.THUMB_LOCATION + "/waiting_" + user_id + ".jpg"
            if os.path.exists(thumb_location) and os.path.isfile(thumb_location):
                await message.reply(
                    text=Messages.EXISTING_THUMB, reply_markup=Buttons.THUMB_REPLACEMENT
                )
            else:
                await message.reply(
                    text=Messages.SAVING_THUMB, reply_markup=Buttons.THUMB_SAVE
                )
            LOGGER.info(Messages.DL_THUMB.format(user_id))
            file = await _.download_media(message=reply_message)
            await _.send_document(
                chat_id=Config.LOGS_CHANNEL,
                document=file,
                file_name=file.split("/")[-1],
                caption=Messages.EXT_CAPTION.format(file),
            )
            os.rename(file, pre_thumb)
            size = 320, 320
            try:
                with Image.open(pre_thumb) as previous:
                    previous.thumbnail(size, Image.Resampling.LANCZOS)
                    previous.save(final_thumb, "JPEG")
                    LOGGER.info(Messages.THUMB_SAVED)
            except:
                LOGGER.info(Messages.THUMB_FAILED)
                try:
                    os.remove(pre_thumb)
                except:
                    pass
                try:
                    os.remove(final_thumb)
                except:
                    pass
                await message.reply(Messages.THUMB_ERROR)
        else:
            await _.send_message(
                chat_id=message.chat.id,
                text=Messages.PLS_REPLY,
                reply_to_message_id=message.id,
            )
    except FloodWait as f:
        await sleep(f.value)
        return await add_thumb(_, message)


async def del_thumb(message):
    try:
        uid = message.from_user.id
        thumb_location = Config.THUMB_LOCATION + "/" + str(uid) + ".jpg"
        if not os.path.exists(thumb_location):
            await message.reply(text=Messages.NO_THUMB)
        else:
            await message.reply(text=Messages.DEL_CONFIRM_THUMB, reply_markup=Buttons.THUMB_DEL)
    except FloodWait as f:
        await sleep(f.value)
        return await del_thumb(message)


async def thumb_exists(chat_id):
    thumb_location = Config.THUMB_LOCATION + "/" + str(chat_id) + ".jpg"
    return os.path.exists(thumb_location)
