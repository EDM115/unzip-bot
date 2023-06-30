# Copyright (c) 2023 EDM115

import os
import shutil

from pyrogram.errors import ReplyMarkupTooLong

from config import Config
from unzipper import LOGGER
from unzipper.helpers.database import del_ongoing_task, update_uploaded
from unzipper.modules.ext_script.ext_helper import get_files, make_keyboard, make_keyboard_empty
from unzipper.modules.ext_script.up_helper import send_file

async def ext_f(query, unzip_bot, log_msg, sent_files):
    user_id = query.from_user.id
    spl_data = query.data.split("|")
    LOGGER.warning("ext_f spl_data : " + str(spl_data))
    file_path = f"{Config.DOWNLOAD_LOCATION}/{spl_data[1]}/extracted"
    paths = await get_files(path=file_path)
    LOGGER.warning("ext_f paths : " + str(paths))
    if not paths:
        if os.path.isdir(f"{Config.DOWNLOAD_LOCATION}/{spl_data[1]}"):
            shutil.rmtree(f"{Config.DOWNLOAD_LOCATION}/{spl_data[1]}")
        await del_ongoing_task(user_id)
        return await query.message.edit("I've already sent you those files 🙂")
    await query.answer("Sending that file to you… Please wait")
    sent_files += 1
    await send_file(
        unzip_bot=unzip_bot,
        c_id=spl_data[2],
        doc_f=paths[int(spl_data[3])],
        query=query,
        full_path=f"{Config.DOWNLOAD_LOCATION}/{spl_data[1]}",
        log_msg=log_msg,
        split=False,
    )

    # if not err400:
    # theorically, err400 shouldn't be here because only ext_a can be used
    # Refreshing Inline keyboard
    await query.message.edit("Refreshing… ⏳")
    rpaths = await get_files(path=file_path)
    LOGGER.warning("ext_f rpaths : " + str(rpaths))
    # There are no files let's die
    if not rpaths:
        try:
            shutil.rmtree(f"{Config.DOWNLOAD_LOCATION}/{spl_data[1]}")
        except:
            pass
        await del_ongoing_task(user_id)
        return await query.message.edit("I've already sent you those files 🙂")
    try:
        i_e_buttons = await make_keyboard(
            paths=rpaths,
            user_id=query.from_user.id,
            chat_id=query.message.chat.id,
        )
        await query.message.edit(
            "Select files to upload 👇",
            reply_markup=i_e_buttons,
        )
    except ReplyMarkupTooLong:
        empty_buttons = await make_keyboard_empty(user_id=user_id, chat_id=query.message.chat.id)
        await query.message.edit(
            "Unable to gather the files to upload 😥\nChoose either to upload everything, or cancel the process",
            reply_markup=empty_buttons,
        )

    # Now theorically it refreshes normally
    await update_uploaded(user_id, upload_count=sent_files)
    global single_up
    single_up = True