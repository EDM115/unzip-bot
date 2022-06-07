import os
import time

from pyrogram import Client, filters
import numpy
from PIL import Image

from unzipper import LOGGER
from config import Config
from unzipper.modules.bot_data import Buttons, Messages

async def add_thumb(_, message):
    if message.reply_to_message is not None:
        reply_message = message.reply_to_message
        if reply_message.media_group_id is not None: # album sent
            LOGGER.warning("Album")
            return message.reply("You can't use an album. Reply to a single picture sent as photo (not as document)")
        else:
            thumb_location = Config.THUMB_LOCATION + "/" + str(message.from_user.id) + ".jpg"
            pre_thumb = Config.THUMB_LOCATION + "/not_resized_" + str(message.from_user.id) + ".jpg"
            if os.path.exists(thumb_location):
                # Add later buttons to delete or cancel + preview (TTK)
                message.reply("A thumbnail already exists. Replacing it with the new one…")
                LOGGER.warning("Thumb exists")
                try:
                    os.remove(thumb_location + ".jpg")
                except:
                    pass
            LOGGER.warning("DL thumb")
            await message.download_media(
                message=message,
                file_name=pre_thumb
            )
            LOGGER.warning("DL-ed")
            size = 320, 320
            try:
                previous = Image.open(pre_thumb)
                previous.thumbnail(size, Image.ANTIALIAS)
                previous.save(thumb_location, "JPEG")
            except:
                LOGGER.warning("Failed to generate thumb")
                return message.reply("Error happened")
            await _.send_message(
                chat_id=message.chat.id,
                text=Messages.SAVED_THUMBNAIL,
                reply_to_message_id=reply_message.message_id
            )
            """
            # This combine several pictures one to each other
            download_location = Config.THUMB_LOCATION + "/" + str(message.from_user.id) + "/" + str(reply_message.media_group_id) + "/"
            save_final_image = download_location + str(round(time.time())) + ".jpg"
            list_im = os.listdir(download_location)
            if len(list_im) == 2:
                imgs = [ Image.open(download_location + i) for i in list_im ]
                inm_aesph = sorted([(numpy.sum(i.size), i.size) for i in imgs])
                min_shape = inm_aesph[1][1]
                imgs_comb = numpy.hstack(numpy.asarray(i.resize(min_shape)) for i in imgs)
                imgs_comb = Image.fromarray(imgs_comb)
                # combine: https://stackoverflow.com/a/30228789/4723940
                imgs_comb.save(save_final_image)
                # send
                await _.send_photo(
                    chat_id=message.chat.id,
                    photo=save_final_image,
                    caption=Messages.SAVED_THUMBNAIL,
                    reply_to_message_id=message.message_id
                )
            else:
                await _.send_message(
                    chat_id=message.chat.id,
                    text=Messages.ERR_2_IN_ALBUM,
                    reply_to_message_id=message.message_id
                )
            
            try:
                [os.remove(download_location + i) for i in list_im ]
                os.remove(download_location)
            except:
                pass
        else:
            await _.send_message(
                chat_id=message.chat.id,
                text=Messages.PLS_REPLY,
                reply_to_message_id=message.message_id
            )
            """
    else:
        await _.send_message(
            chat_id=message.chat.id,
            text=Messages.PLS_REPLY,
            reply_to_message_id=message.message_id
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
            reply_to_message_id=message.message_id
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
        reply_to_message_id=message.message_id
    )

async def thumb_exists(_, message):
    thumb_location = Config.THUMB_LOCATION + "/" + str(message.from_user.id) + ".jpg"
    return os.path.exists(thumb_location)
