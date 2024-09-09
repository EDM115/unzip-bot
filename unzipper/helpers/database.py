# Copyright (c) 2022 - 2024 EDM115
import base58check

from asyncio import sleep
from motor.motor_asyncio import AsyncIOMotorClient
from pyrogram.errors import FloodWait

from config import Config
from unzipper import unzipperbot
from unzipper.modules.bot_data import Messages

mongodb = AsyncIOMotorClient(Config.MONGODB_URL)
unzipper_db = mongodb[Config.MONGODB_DBNAME]


# Users Database
user_db = unzipper_db["users_db"]


async def add_user(user_id):
    new_user_id = int(user_id)
    is_exist = await user_db.find_one({"user_id": new_user_id})
    if is_exist is not None and is_exist:
        return -1
    await user_db.insert_one({"user_id": new_user_id})


async def del_user(user_id):
    del_user_id = int(user_id)
    is_exist = await user_db.find_one({"user_id": del_user_id})
    if is_exist is not None and is_exist:
        await user_db.delete_one({"user_id": del_user_id})
    else:
        return -1


async def is_user_in_db(user_id):
    u_id = int(user_id)
    is_exist = await user_db.find_one({"user_id": u_id})
    if is_exist is not None and is_exist:
        return True
    return False


async def count_users():
    users = await user_db.count_documents({})
    return users


async def get_users_list():
    return [users_list async for users_list in user_db.find({})]


# Banned users database
b_user_db = unzipper_db["banned_users_db"]


async def add_banned_user(user_id):
    new_user_id = int(user_id)
    is_exist = await b_user_db.find_one({"banned_user_id": new_user_id})
    if is_exist is not None and is_exist:
        return -1
    await b_user_db.insert_one({"banned_user_id": new_user_id})


async def del_banned_user(user_id):
    del_user_id = int(user_id)
    is_exist = await b_user_db.find_one({"banned_user_id": del_user_id})
    if is_exist is not None and is_exist:
        await b_user_db.delete_one({"banned_user_id": del_user_id})
    else:
        return -1


async def is_user_in_bdb(user_id):
    u_id = int(user_id)
    is_exist = await b_user_db.find_one({"banned_user_id": u_id})
    if is_exist is not None and is_exist:
        return True
    return False


async def count_banned_users():
    users = await b_user_db.count_documents({})
    return users


async def get_banned_users_list():
    return [banned_users_list async for banned_users_list in b_user_db.find({})]


async def check_user(message):
    # Checking if user is banned
    is_banned = await is_user_in_bdb(message.from_user.id)
    if is_banned:
        await message.reply(Messages.BANNED)
        await message.stop_propagation()
        return
    # Checking if user already in db
    is_in_db = await is_user_in_db(message.from_user.id)
    if not is_in_db:
        await add_user(message.from_user.id)
        try:
            firstname = message.from_user.first_name
        except:
            firstname = " "
        try:
            lastname = message.from_user.last_name
        except:
            lastname = " "
        try:
            username = message.from_user.username
        except:
            username = " "
        if firstname == " " and lastname == " " and username == " ":
            uname = message.from_user.mention
            try:
                await unzipperbot.send_message(
                    chat_id=Config.LOGS_CHANNEL,
                    text=Messages.NEW_USER_BAD.format(uname),
                    disable_web_page_preview=False,
                )
            except FloodWait as f:
                await sleep(f.value)
                await unzipperbot.send_message(
                    chat_id=Config.LOGS_CHANNEL,
                    text=Messages.NEW_USER_BAD.format(uname),
                    disable_web_page_preview=False,
                )
        else:
            if firstname is None:
                firstname = " "
            if lastname is None:
                lastname = " "
            if username is None:
                username = " "
            uname = firstname + " " + lastname
            umention = " | @" + username
            try:
                await unzipperbot.send_message(
                    chat_id=Config.LOGS_CHANNEL,
                    text=Messages.NEW_USER.format(
                        uname,
                        umention,
                        message.from_user.id,
                        message.from_user.id,
                        message.from_user.id,
                    ),
                    disable_web_page_preview=False,
                )
            except FloodWait as f:
                await sleep(f.value)
                await unzipperbot.send_message(
                    chat_id=Config.LOGS_CHANNEL,
                    text=Messages.NEW_USER.format(
                        uname,
                        umention,
                        message.from_user.id,
                        message.from_user.id,
                        message.from_user.id,
                    ),
                    disable_web_page_preview=False,
                )
    await message.continue_propagation()


async def get_all_users():
    users = []
    banned = []
    for i in range(await count_users()):
        users.append((await get_users_list())[i]["user_id"])
    for j in range(await count_banned_users()):
        banned.append((await get_banned_users_list())[j]["banned_user_id"])
    return users, banned


# Upload mode
mode_db = unzipper_db["ulmode_db"]


async def set_upload_mode(user_id, mode):
    is_exist = await mode_db.find_one({"_id": user_id})
    if is_exist is not None and is_exist:
        await mode_db.update_one({"_id": user_id}, {"$set": {"mode": mode}})
    else:
        await mode_db.insert_one({"_id": user_id, "mode": mode})


async def get_upload_mode(user_id):
    umode = await mode_db.find_one({"_id": user_id})
    if umode is not None and umode:
        return umode.get("mode")
    return "media"


# Db for how many files user uploaded
uploaded_db = unzipper_db["uploaded_count_db"]


async def get_uploaded(user_id):
    up_count = await uploaded_db.find_one({"_id": user_id})
    if up_count is not None and up_count:
        return up_count.get("uploaded_files")
    return 0


async def update_uploaded(user_id, upload_count):
    is_exist = await uploaded_db.find_one({"_id": user_id})
    if is_exist is not None and is_exist:
        new_count = await get_uploaded(user_id) + upload_count
        await uploaded_db.update_one(
            {"_id": user_id}, {"$set": {"uploaded_files": new_count}}
        )
    else:
        await uploaded_db.insert_one({"_id": user_id, "uploaded_files": upload_count})


# DB for thumbnails
thumb_db = unzipper_db["thumb_db"]


async def get_thumb(user_id):
    existing = await thumb_db.find_one({"_id": user_id})
    if existing is not None and existing:
        return existing
    return None


async def update_temp_thumb(user_id, thumb_id):
    existing = await thumb_db.find_one({"_id": user_id})
    if existing is not None and existing:
        await thumb_db.update_one({"_id": user_id}, {"$set": {"temp": thumb_id}})
    else:
        await thumb_db.insert_one({"_id": user_id, "temp": thumb_id})


async def update_thumb(user_id):
    existing = await thumb_db.find_one({"_id": user_id})
    if existing is not None and existing:
        await thumb_db.update_one(
            {"_id": user_id}, {"$set": {"file_id": existing.get("temp")}}
        )
        await thumb_db.update_one({"_id": user_id}, {"$unset": {"temp": ""}})
        if existing.get("url") is not None:
            await thumb_db.update_one({"_id": user_id}, {"$unset": {"url": ""}})
    else:
        return


async def get_thumb_users():
    return [thumb_list async for thumb_list in thumb_db.find({})]


async def count_thumb_users():
    users = await thumb_db.count_documents({})
    return users


async def del_thumb_db(user_id):
    del_thumb_id = int(user_id)
    is_exist = await thumb_db.find_one({"_id": del_thumb_id})
    if is_exist is not None and is_exist:
        await thumb_db.delete_one({"_id": del_thumb_id})
    else:
        return


# DB for bot data
bot_data = unzipper_db["bot_data"]


async def get_boot():
    boot = await bot_data.find_one({"boot": True})
    if boot is not None and boot:
        return boot.get("time")
    return None


async def set_boot(boottime):
    is_exist = await bot_data.find_one({"boot": True})
    if is_exist is not None and is_exist:
        await bot_data.update_one({"boot": True}, {"$set": {"time": boottime}})
    else:
        await bot_data.insert_one({"boot": True, "time": boottime})


async def set_old_boot(boottime):
    is_exist = await bot_data.find_one({"old_boot": True})
    if is_exist is not None and is_exist:
        await bot_data.update_one({"old_boot": True}, {"$set": {"time": boottime}})
    else:
        await bot_data.insert_one({"old_boot": True, "time": boottime})


async def get_old_boot():
    old_boot = await bot_data.find_one({"old_boot": True})
    if old_boot is not None and old_boot:
        return old_boot.get("time")
    return None


async def is_boot_different():
    different = True
    is_exist = await bot_data.find_one({"boot": True})
    is_exist_old = await bot_data.find_one({"old_boot": True})
    if is_exist and is_exist_old and is_exist.get("time") == is_exist_old.get("time"):
        different = False
    return different


# DB for ongoing tasks
ongoing_tasks = unzipper_db["ongoing_tasks"]


async def get_ongoing_tasks():
    return [ongoing_list async for ongoing_list in ongoing_tasks.find({})]


async def count_ongoing_tasks():
    tasks = await ongoing_tasks.count_documents({})
    return tasks


async def add_ongoing_task(user_id, start_time, task_type):
    await ongoing_tasks.insert_one(
        {"user_id": user_id, "start_time": start_time, "type": task_type}
    )


async def del_ongoing_task(user_id):
    is_exist = await ongoing_tasks.find_one({"user_id": user_id})
    if is_exist is not None and is_exist:
        await ongoing_tasks.delete_one({"user_id": user_id})
    else:
        return


async def clear_ongoing_tasks():
    await ongoing_tasks.delete_many({})


# DB for cancel tasks (that's stupid)
cancel_tasks = unzipper_db["cancel_tasks"]


async def get_cancel_tasks():
    return [cancel_list async for cancel_list in cancel_tasks.find({})]


async def count_cancel_tasks():
    tasks = await cancel_tasks.count_documents({})
    return tasks


async def add_cancel_task(user_id):
    if not await get_cancel_task(user_id):
        await cancel_tasks.insert_one({"user_id": user_id})


async def del_cancel_task(user_id):
    is_exist = await cancel_tasks.find_one({"user_id": user_id})
    if is_exist is not None and is_exist:
        await cancel_tasks.delete_one({"user_id": user_id})
    else:
        return


async def get_cancel_task(user_id):
    is_exist = await cancel_tasks.find_one({"user_id": user_id})
    return bool(is_exist is not None and is_exist)


async def clear_cancel_tasks():
    await cancel_tasks.delete_many({})


# DB for merge tasks

merge_tasks = unzipper_db["merge_tasks"]


async def get_merge_tasks():
    return [merge_list async for merge_list in merge_tasks.find({})]


async def count_merge_tasks():
    tasks = await merge_tasks.count_documents({})
    return tasks


async def add_merge_task(user_id, message_id):
    if not await get_merge_task(user_id):
        await merge_tasks.insert_one({"user_id": user_id, "message_id": message_id})
    else:
        await merge_tasks.update_one(
            {"user_id": user_id}, {"$set": {"message_id": message_id}}
        )


async def del_merge_task(user_id):
    is_exist = await merge_tasks.find_one({"user_id": user_id})
    if is_exist is not None and is_exist:
        await merge_tasks.delete_one({"user_id": user_id})
    else:
        return


async def get_merge_task(user_id):
    is_exist = await merge_tasks.find_one({"user_id": user_id})
    return bool(is_exist is not None and is_exist)


async def get_merge_task_message_id(user_id):
    is_exist = await merge_tasks.find_one({"user_id": user_id})
    if is_exist is not None and is_exist:
        return is_exist.get("message_id")
    return False


async def clear_merge_tasks():
    await merge_tasks.delete_many({})


# DB for maintenance mode

maintenance_mode = unzipper_db["maintenance_mode"]


async def get_maintenance():
    maintenance = await maintenance_mode.find_one({"maintenance": True})
    if maintenance is not None and maintenance:
        return maintenance.get("val")
    return False


async def set_maintenance(val):
    is_exist = await maintenance_mode.find_one({"maintenance": True})
    if is_exist is not None and is_exist:
        await maintenance_mode.update_one({"maintenance": True}, {"$set": {"val": val}})
    else:
        await maintenance_mode.insert_one({"maintenance": True, "val": val})


# DB for VIP users

vip_users = unzipper_db["vip_users"]


async def add_vip_user(
    uid,
    subscription,
    ends,
    used,
    billed,
    early,
    donator,
    started,
    successful,
    gap,
    gifted,
    referral,
    lifetime,
):
    is_exist = await vip_users.find_one({"_id": uid})
    if is_exist is not None and is_exist:
        await vip_users.update_one(
            {"_id": uid},
            {
                "$set": {
                    "subscription": subscription,
                    "ends": ends,
                    "used": used,
                    "billed": billed,
                    "early": early,
                    "donator": donator,
                    "started": started,
                    "successful": successful,
                    "gap": gap,
                    "gifted": gifted,
                    "referral": referral,
                    "lifetime": lifetime,
                }
            },
        )
    else:
        await vip_users.insert_one(
            {
                "_id": uid,
                "subscription": subscription,
                "ends": ends,
                "used": used,
                "billed": billed,
                "early": early,
                "donator": donator,
                "started": started,
                "successful": successful,
                "gap": gap,
                "gifted": gifted,
                "referral": referral,
                "lifetime": lifetime,
            }
        )


async def remove_vip_user(uid):
    is_exist = await vip_users.find_one({"_id": uid})
    if is_exist is not None and is_exist:
        await vip_users.delete_one({"_id": uid})
    else:
        return


async def is_vip(uid):
    is_exist = await vip_users.find_one({"_id": uid})
    return bool(is_exist is not None and is_exist)


async def get_vip_users():
    return [vip_list async for vip_list in vip_users.find({})]


async def count_vip_users():
    users = await vip_users.count_documents({})
    return users


async def get_vip_user(uid):
    is_exist = await vip_users.find_one({"_id": uid})
    if is_exist is not None and is_exist:
        return is_exist
    return None


# DB for referrals

referrals = unzipper_db["referrals"]


async def add_referee(uid, referral_code):
    is_exist = await referrals.find_one({"_id": uid})
    if is_exist is not None and is_exist:
        await referrals.update_one(
            {"_id": uid}, {"$set": {"type": "referee", "referral_code": referral_code}}
        )
    else:
        await referrals.insert_one(
            {"_id": uid, "type": "referee", "referral_code": referral_code}
        )


async def add_referrer(uid, referees):
    is_exist = await referrals.find_one({"_id": uid})
    if is_exist is not None and is_exist:
        await referrals.update_one(
            {"_id": uid}, {"$set": {"type": "referrer", "referees": referees}}
        )
    else:
        await referrals.insert_one(
            {"_id": uid, "type": "referrer", "referees": referees}
        )


async def get_referee(uid):
    is_exist = await referrals.find_one({"_id": uid})
    if is_exist is not None and is_exist:
        return is_exist
    return None


async def get_referrer(uid):
    is_exist = await referrals.find_one({"_id": uid})
    if is_exist is not None and is_exist:
        return is_exist
    return None


def get_referral_code(uid):
    return base58check.b58encode(
        base58check.b58encode(str(uid).encode("ascii"))
    ).decode("ascii")


def get_referral_uid(referral_code):
    return int(
        base58check.b58decode(
            base58check.b58decode(referral_code).decode("ascii")
        ).decode("ascii")
    )
