# Copyright (c) 2022 EDM115

from unzipper import unzipperbot as Client
from motor.motor_asyncio import AsyncIOMotorClient
from requests import post

from config import Config
from time import sleep
from unzipper import LOGGER

mongodb = AsyncIOMotorClient(Config.MONGODB_URL)
unzipper_db = mongodb["Unzipper_Bot"]

# Users Database
user_db = unzipper_db["users_db"]


async def add_user(user_id):
    new_user_id = int(user_id)
    is_exist = await user_db.find_one({"user_id": new_user_id})
    if is_exist:
        return
    await user_db.insert_one({"user_id": new_user_id})


async def del_user(user_id):
    del_user_id = int(user_id)
    is_exist = await user_db.find_one({"user_id": del_user_id})
    if is_exist:
        await user_db.delete_one({"user_id": del_user_id})
    else:
        return


async def is_user_in_db(user_id):
    u_id = int(user_id)
    is_exist = await user_db.find_one({"user_id": u_id})
    if is_exist:
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
    if is_exist:
        return
    await b_user_db.insert_one({"banned_user_id": new_user_id})


async def del_banned_user(user_id):
    del_user_id = int(user_id)
    is_exist = await b_user_db.find_one({"banned_user_id": del_user_id})
    if is_exist:
        await b_user_db.delete_one({"banned_user_id": del_user_id})
    else:
        return


async def is_user_in_bdb(user_id):
    u_id = int(user_id)
    is_exist = await b_user_db.find_one({"banned_user_id": u_id})
    if is_exist:
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
        await message.reply(
            "**Sorry you're banned 💀**\n\nReport this at @EDM115 if you think this is a mistake, I can unban you"
        )
        await message.stop_propagation()
        return
    # Cheking if user already in db
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
        else:
            if firstname == None:
                firstname = " "
            if lastname == None:
                lastname = " "
            if username == None:
                username = " "
            uname = firstname + " " + lastname + " | @" + username
        try:
            await Client.send_message(
                chat_id=Config.LOGS_CHANNEL,
                text=f"**#NEW_USER** 🎙 \n\n**User profile :** `{uname}` \n**User ID :** `{message.from_user.id}` \n**Profile URL :** [tg://user?id={message.from_user.id}](tg://user?id={message.from_user.id})",
                disable_web_page_preview=False
            )
        except AttributeError:
            await Client.send_message(
                chat_id=Config.LOGS_CHANNEL,
                text=f"**#NEW_USER** 🎙 \n\n**User profile :** `{uname}` \n**User ID :** `[AttributeError] Can't get it` \n**Profile URL :** Can't get it",
                disable_web_page_preview=False
            )
    await message.continue_propagation()


"""
    async def all_users():
    users = []
    banned = []
    for i in range(count_users()):
        users.append(
"""

# Upload mode
mode_db = unzipper_db["ulmode_db"]


async def set_upload_mode(user_id, mode):
    is_exist = await mode_db.find_one({"_id": user_id})
    if is_exist:
        await mode_db.update_one({"_id": user_id}, {"$set": {"mode": mode}})
    else:
        await mode_db.insert_one({"_id": user_id, "mode": mode})


async def get_upload_mode(user_id):
    umode = await mode_db.find_one({"_id": user_id})
    if umode:
        return umode["mode"]
    return "media"


# Db for how many files user uploaded
uploaded_db = unzipper_db["uploaded_count_db"]


async def get_uploaded(user_id):
    up_count = await uploaded_db.find_one({"_id": user_id})
    if up_count:
        return up_count["uploaded_files"]
    return 0


async def update_uploaded(user_id, upload_count):
    is_exist = await uploaded_db.find_one({"_id": user_id})
    if is_exist:
        new_count = await get_uploaded(user_id) + upload_count
        await uploaded_db.update_one(
            {"_id": user_id}, {"$set": {"uploaded_files": new_count}}
        )
    else:
        await uploaded_db.insert_one({"_id": user_id, "uploaded_files": upload_count})


# Db for cloud_upload
cloud_db = unzipper_db["cloud_db"]


async def get_cloud(user_id):
    return "https://api.bayfiles.com/upload"


# DB for thumbnails
thumb_db = unzipper_db["thumb_db"]


async def get_thumb(user_id):
    existing = await thumb_db.find_one({"_id": user_id})
    if existing:
        return existing["url"]
    return None


async def update_thumb(user_id, thumb_url, force):
    existing = await thumb_db.find_one({"_id": user_id})
    if existing:
        if not force:
            return existing["url"]
        await thumb_db.update_one({"_id": user_id}, {"$set": {"url": thumb_url}})
    else:
        await thumb_db.insert_one({"_id": user_id, "url": thumb_url})


async def upload_thumb(image):
    with open(image, "rb") as file:
        request = post(
            "https://telegra.ph/upload", files={"file": ("file", file, "image/jpeg")}
        ).json()[0]
        return f"https://telegra.ph{request['src']}"


async def get_thumb_users():
    return [thumb_list async for thumb_list in thumb_db.find({})]


async def count_thumb_users():
    users = await thumb_db.count_documents({})
    return users
