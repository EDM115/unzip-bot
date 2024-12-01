import os
import shutil
from asyncio import sleep

from PIL import Image
from pyrogram.errors import FloodWait

from config import Config
from unzipbot import LOGGER
from unzipbot.helpers.database import get_lang, update_temp_thumb
from unzipbot.i18n.buttons import Buttons
from unzipbot.i18n.messages import Messages


messages = Messages(lang_fetcher=get_lang)


async def silent_del(user_id):
    try:
        thumb_location = Config.THUMB_LOCATION + "/" + str(user_id) + ".jpg"
        os.remove(thumb_location)
    except:
        pass


async def add_thumb(_, message):
    try:
        uid = message.from_user.id
        user_id = str(uid)

        if message.reply_to_message is not None:
            reply_message = message.reply_to_message

            if reply_message.media_group_id is not None:  # album sent
                LOGGER.info(messages.get("custom_thumbnail", "ALBUM", None, user_id))
                await message.reply(messages.get("custom_thumbnail", "ALBUM_NOPE", uid))

                return

            thumb_location = Config.THUMB_LOCATION + "/" + user_id + ".jpg"
            pre_thumb = Config.THUMB_LOCATION + "/not_resized_" + user_id + ".jpg"
            final_thumb = Config.THUMB_LOCATION + "/waiting_" + user_id + ".jpg"
            LOGGER.info(messages.get("custom_thumbnail", "DL_THUMB", None, user_id))
            file = await _.download_media(message=reply_message)
            shutil.move(file, pre_thumb)
            size = (320, 320)

            try:
                with Image.open(pre_thumb) as previous:
                    previous.thumbnail(size, Image.Resampling.LANCZOS)
                    previous.save(final_thumb, "JPEG")
                    LOGGER.info(messages.get("custom_thumbnail", "THUMB_SAVED"))
                savedpic = await _.send_photo(
                    chat_id=Config.LOGS_CHANNEL,
                    photo=final_thumb,
                    caption=messages.get(
                        "custom_thumbnail", "THUMB_CAPTION", uid, user_id, user_id
                    ),
                )

                try:
                    os.remove(pre_thumb)
                except:
                    pass

                await update_temp_thumb(message.from_user.id, savedpic.photo.file_id)

                if os.path.exists(thumb_location) and os.path.isfile(thumb_location):
                    await message.reply(
                        text=messages.get("custom_thumbnail", "EXISTING_THUMB", uid),
                        reply_markup=Buttons.THUMB_REPLACEMENT,
                    )
                else:
                    await message.reply(
                        text=messages.get("custom_thumbnail", "SAVING_THUMB", uid),
                        reply_markup=Buttons.THUMB_SAVE,
                    )
            except:
                LOGGER.info(messages.get("custom_thumbnail", "THUMB_FAILED"))

                try:
                    os.remove(final_thumb)
                except:
                    pass

                await message.reply(
                    messages.get("custom_thumbnail", "THUMB_ERROR", uid)
                )
        else:
            await _.send_message(
                chat_id=message.chat.id,
                text=messages.get("custom_thumbnail", "PLS_REPLY", uid),
                reply_to_message_id=message.id,
            )
    except FloodWait as f:
        await sleep(f.value)
        await add_thumb(_, message)


async def del_thumb(message):
    try:
        uid = message.from_user.id
        thumb_location = Config.THUMB_LOCATION + "/" + str(uid) + ".jpg"

        if not os.path.exists(thumb_location):
            await message.reply(text=messages.get("custom_thumbnail", "NO_THUMB", uid))
        else:
            await message.reply(
                text=messages.get("custom_thumbnail", "DEL_CONFIRM_THUMB", uid),
                reply_markup=Buttons.THUMB_DEL,
            )
    except FloodWait as f:
        await sleep(f.value)
        await del_thumb(message)


async def thumb_exists(chat_id):
    thumb_location = Config.THUMB_LOCATION + "/" + str(chat_id) + ".jpg"

    return os.path.exists(thumb_location)
