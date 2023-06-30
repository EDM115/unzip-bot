# Copyright (c) 2023 EDM115

import shutil

from pyrogram.types import CallbackQuery

from config import Config
from unzipper.helpers.database import del_ongoing_task, update_uploaded
from unzipper.modules.bot_data import Messages


async def cancel(query: CallbackQuery, single_up, sent_files, already_removed, log_msg):
    uid = query.from_user.id
    await del_ongoing_task(uid)
    try:
        shutil.rmtree(f"{Config.DOWNLOAD_LOCATION}/{uid}")
        await query.message.edit(Messages.CANCELLED_TXT.format("❌ Process cancelled"))
        if single_up:
            await update_uploaded(user_id=uid, upload_count=sent_files)
            try:
                await log_msg.reply(Messages.HOW_MANY_UPLOADED.format(sent_files))
            except:
                return
    except:
        if not already_removed:
            return await query.answer("There is nothing to remove 💀", show_alert=True)