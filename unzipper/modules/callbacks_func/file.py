# Copyright (c) 2023 EDM115

import os
import re

from fnmatch import fnmatch
from time import time

from config import Config
from unzipper.helpers.database import del_ongoing_task
from unzipper.helpers.unzip_help import progress_for_pyrogram, humanbytes, extentions_list
from unzipper.modules.bot_data import Messages
from unzipper.modules.callbacks import split_file_pattern

async def file(query, r_message, user_id, log_msg, splitted_data, download_path):
	if r_message.document is None:
		await del_ongoing_task(user_id)
		return await query.message.edit("Give me an archive to extract 😐")
	fname = r_message.document.file_name
	rfnamebro = fname
	archive_msg = await r_message.forward(chat_id=Config.LOGS_CHANNEL)
	await log_msg.edit(
		Messages.LOG_TXT.format(
			user_id, fname,
			humanbytes(r_message.document.file_size)
		)
	)
	# Checks if it's actually an archive
	# fext = (pathlib.Path(fname).suffix).casefold()
	if splitted_data[2] != "thumb":
		fext = fname.split(".")[-1].casefold()
		if (fnmatch(fext, extentions_list["split"][0]) or fext in extentions_list["split"] or bool(re.search(split_file_pattern, fname))):
			await del_ongoing_task(user_id)
			return await query.message.edit("Splitted archives can't be processed yet")
		if fext not in extentions_list["archive"]:
			await del_ongoing_task(user_id)
			return await query.message.edit("This file is NOT an archive 😐\nIf you believe it's an error, send the file to **@EDM115**")
	# Makes download dir
	os.makedirs(download_path)
	s_time = time()
	location = f"{download_path}/archive_from_{user_id}{os.path.splitext(fname)[1]}"
	archive = await r_message.download(
		file_name=location,
		progress=progress_for_pyrogram,
		progress_args=(
			"**Trying to download… Please wait** \n",
			query.message,
			s_time,
		),
	)
	e_time = time()