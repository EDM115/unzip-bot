# TODO

import os
import shutil
from asyncio import sleep

from PIL import Image
from pyrogram.errors import FloodPremiumWait, FloodWait

from unzipbot import LOGGER
from unzipbot.config.config import Config
from unzipbot.db.functions import get_lang, update_temp_thumb
from unzipbot.i18n.buttons import Buttons
from unzipbot.i18n.messages import Messages

messages = Messages(lang_fetcher=get_lang)


async def silent_del(user_id):
    try:
        thumb_location = Config.THUMB_LOCATION + "/" + str(user_id) + ".jpg"
        os.remove(path=thumb_location)
    except:
        pass


async def add_thumb(_, message):
    try:
        uid = message.from_user.id
        user_id = str(uid)

        if message.reply_to_message is not None:
            reply_message = message.reply_to_message

            if reply_message.media_group_id is not None:  # album sent
                LOGGER.info(
                    msg=messages.get(file="custom_thumbnail", key="ALBUM", extra_args=user_id)
                )
                await message.reply(
                    messages.get(file="custom_thumbnail", key="ALBUM_NOPE", user_id=uid)
                )

                return

            thumb_location = Config.THUMB_LOCATION + "/" + user_id + ".jpg"
            pre_thumb = Config.THUMB_LOCATION + "/not_resized_" + user_id + ".jpg"
            final_thumb = Config.THUMB_LOCATION + "/waiting_" + user_id + ".jpg"
            LOGGER.info(
                msg=messages.get(file="custom_thumbnail", key="DL_THUMB", extra_args=user_id)
            )
            file = await _.download_media(message=reply_message)
            shutil.move(src=file, dst=pre_thumb)
            size = (320, 320)

            try:
                with Image.open(fp=pre_thumb) as previous:
                    previous.thumbnail(size=size, resample=Image.Resampling.LANCZOS)
                    previous.save(fp=final_thumb, format="JPEG")
                    LOGGER.info(msg=messages.get(file="custom_thumbnail", key="THUMB_SAVED"))
                savedpic = await _.send_photo(
                    chat_id=Config.LOGS_CHANNEL,
                    photo=final_thumb,
                    caption=messages.get(
                        file="custom_thumbnail",
                        key="THUMB_CAPTION",
                        user_id=uid,
                        extra_args=[user_id, user_id],
                    ),
                )

                try:
                    os.remove(path=pre_thumb)
                except:
                    pass

                await update_temp_thumb(
                    user_id=message.from_user.id, thumb_id=savedpic.photo.file_id
                )

                if os.path.exists(thumb_location) and os.path.isfile(thumb_location):
                    await message.reply(
                        text=messages.get(
                            file="custom_thumbnail", key="EXISTING_THUMB", user_id=uid
                        ),
                        reply_markup=Buttons.THUMB_REPLACEMENT,
                    )
                else:
                    await message.reply(
                        text=messages.get(file="custom_thumbnail", key="SAVING_THUMB", user_id=uid),
                        reply_markup=Buttons.THUMB_SAVE,
                    )
            except:
                LOGGER.info(msg=messages.get(file="custom_thumbnail", key="THUMB_FAILED"))

                try:
                    os.remove(path=final_thumb)
                except:
                    pass

                await message.reply(
                    messages.get(file="custom_thumbnail", key="THUMB_ERROR", user_id=uid)
                )
        else:
            await _.send_message(
                chat_id=message.chat.id,
                text=messages.get(file="custom_thumbnail", key="PLS_REPLY", user_id=uid),
                reply_to_message_id=message.id,
            )
    except (FloodWait, FloodPremiumWait) as f:
        await sleep(f.value)
        await add_thumb(_=_, message=message)


async def del_thumb(message):
    try:
        uid = message.from_user.id
        thumb_location = Config.THUMB_LOCATION + "/" + str(uid) + ".jpg"

        if not os.path.exists(thumb_location):
            await message.reply(
                text=messages.get(file="custom_thumbnail", key="NO_THUMB", user_id=uid)
            )
        else:
            await message.reply(
                text=messages.get(file="custom_thumbnail", key="DEL_CONFIRM_THUMB", user_id=uid),
                reply_markup=Buttons.THUMB_DEL,
            )
    except (FloodWait, FloodPremiumWait) as f:
        await sleep(f.value)
        await del_thumb(message)


async def thumb_exists(chat_id):
    thumb_location = Config.THUMB_LOCATION + "/" + str(chat_id) + ".jpg"

    return os.path.exists(thumb_location)
