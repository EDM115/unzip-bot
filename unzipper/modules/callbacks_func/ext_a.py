# Copyright (c) 2023 EDM115

import shutil

from config import Config
from unzipper import LOGGER
from unzipper.helpers.database import del_ongoing_task, update_uploaded
from unzipper.modules.bot_data import Messages
from unzipper.modules.ext_script.ext_helper import get_files
from unzipper.modules.ext_script.up_helper import send_file

async def ext_a(query, unzip_bot, log_msg, sent_files, archive_msg):
	user_id = query.from_user.id
	spl_data = query.data.split("|")
	LOGGER.warning("ext_a spl_data : " + str(spl_data))
	file_path = f"{Config.DOWNLOAD_LOCATION}/{spl_data[1]}/extracted"
	paths = await get_files(path=file_path)
	LOGGER.warning("ext_a paths : " + str(paths))
	if not paths:
		try:
			shutil.rmtree(f"{Config.DOWNLOAD_LOCATION}/{spl_data[1]}")
		except:
			pass
		await del_ongoing_task(user_id)
		return await query.message.edit("I've already sent you those files 🙂")

	await query.answer("Trying to send all files to you… Please wait")
	for file in paths:
		LOGGER.info("ext_a file in paths : " + file)
		sent_files += 1
		await send_file(
			unzip_bot=unzip_bot,
			c_id=spl_data[2],
			doc_f=file,
			query=query,
			full_path=f"{Config.DOWNLOAD_LOCATION}/{spl_data[1]}",
			log_msg=log_msg,
			split=False,
		)

	await query.message.edit("**Successfully uploaded ✅**\n\n**Join @EDM115bots ❤️**")
	await log_msg.reply(Messages.HOW_MANY_UPLOADED.format(sent_files))
	await update_uploaded(user_id, upload_count=sent_files)
	await del_ongoing_task(user_id)
	try:
		shutil.rmtree(f"{Config.DOWNLOAD_LOCATION}/{spl_data[1]}")
	except Exception as e:
		await query.message.edit(Messages.ERROR_TXT.format(e))
		await archive_msg.reply(Messages.ERROR_TXT.format(e))