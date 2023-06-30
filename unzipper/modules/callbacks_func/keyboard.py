import shutil

from pyrogram.errors import ReplyMarkupTooLong

from unzipper import LOGGER
from unzipper.modules.ext_script.ext_helper import (
    make_keyboard,
    make_keyboard_empty,
)
from unzipper.modules.ext_script.up_helper import answer_query
from unzipper.modules.bot_data import Messages
from unzipper.helpers.database import del_ongoing_task

async def keyboard(query, paths, user_id, unzip_bot, archive_msg, ext_files_dir, already_removed):
    try:
        i_e_buttons = await make_keyboard(
            paths=paths,
            user_id=user_id,
            chat_id=query.message.chat.id)
        try:
            await query.message.edit("Select files to upload 👇",
                                        reply_markup=i_e_buttons)
        except ReplyMarkupTooLong:
            empty_buttons = await make_keyboard_empty(
                user_id=user_id, chat_id=query.message.chat.id)
            await query.message.edit(
                "Unable to gather the files to upload 😥\nChoose either to upload everything, or cancel the process",
                reply_markup=empty_buttons,
            )
    except:
        try:
            await query.message.delete()
            i_e_buttons = await make_keyboard(
                paths=paths,
                user_id=user_id,
                chat_id=query.message.chat.id)
            await unzip_bot.send_message(
                chat_id=query.message.chat.id,
                text="Select files to upload 👇",
                reply_markup=i_e_buttons,
            )
        except:
            try:
                await query.message.delete()
                empty_buttons = await make_keyboard_empty(
                    user_id=user_id, chat_id=query.message.chat.id)
                await unzip_bot.send_message(
                    chat_id=query.message.chat.id,
                    text=
                    "Unable to gather the files to upload 😥\nChoose either to upload everything, or cancel the process",
                    reply_markup=empty_buttons,
                )
            except:
                await answer_query(query,
                                    Messages.EXT_FAILED_TXT,
                                    unzip_client=unzip_bot)
                await archive_msg.reply(Messages.EXT_FAILED_TXT)
                shutil.rmtree(ext_files_dir)
                already_removed = True
                LOGGER.error("Fatal error : uncorrect archive format")
                global err400
                err400 = True
                await del_ongoing_task(user_id)
                return