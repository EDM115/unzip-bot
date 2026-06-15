from asyncio import sleep
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import base58check
from pyrogram.errors import FloodPremiumWait, FloodWait

from unzipbot import LOGGER, unzipbot_client
from unzipbot.config.config import Config
from unzipbot.db.migration import migrate_atlas_if_needed
from unzipbot.db.orm.base import Document, TableInterface
from unzipbot.db.orm.mongodb import MongoDBDatabase
from unzipbot.db.orm.sqlite import SQLiteDatabase
from unzipbot.db.schema import CANONICAL_TABLES, REMOTE_TABLES
from unzipbot.i18n.messages import Messages

DEFAULT_UPLOAD_MODE = "media"
DEFAULT_TASK_MESSAGE_ID = 0
DEFAULT_TASK_NB = 0
DEFAULT_VIP_DATE = "1970-01-01"


def get_lang(_user_id: int | None = None) -> str:
    return Config.BASE_LANGUAGE


messages = Messages(lang_fetcher=get_lang)


def _bool(value: Any) -> bool:
    return bool(value)


def _int_bool(value: Any) -> int:
    return int(bool(value))


def _with_legacy_user_key(user: Document) -> Document:
    return {"user_id": user["id"], **user}


def _with_legacy_task_keys(task: Document) -> Document:
    return {"user_id": task["uid"], **task}


def _with_legacy_thumb_keys(thumb: Document) -> Document:
    return {
        "_id": thumb["uid"],
        "file_id": thumb.get("file_id"),
        "temp": thumb.get("temp_id"),
        "slot": thumb.get("slot", 0),
        **thumb,
    }


class MirroredTable:
    def __init__(
        self, local_table: TableInterface, remote_table: TableInterface | None = None
    ) -> None:
        self.local_table = local_table
        self.remote_table = remote_table

    async def count(self, filter: Document | None = None) -> int:
        return await self.local_table.count(filter=filter)

    async def find(self, query: Document | None = None) -> list[Document]:
        return await self.local_table.find(query=query)

    async def find_one(self, query: Document) -> Document | None:
        return await self.local_table.find_one(query=query)

    async def get_all(self) -> list[Document]:
        return await self.local_table.get_all()

    async def insert(self, document: Document) -> None:
        await self.local_table.insert(document=document)
        if self.remote_table is not None:
            await self.remote_table.delete(query=_remote_identity(document))
            await self.remote_table.insert(document=document)

    async def update(
        self, query: Document, update: Document, unset: Iterable[str] | None = None
    ) -> None:
        await self.local_table.update(query=query, update=update, unset=unset)
        if self.remote_table is not None:
            await self.remote_table.update(query=query, update=update, unset=unset)

    async def delete(self, query: Document) -> None:
        await self.local_table.delete(query=query)
        if self.remote_table is not None:
            await self.remote_table.delete(query=query)

    async def delete_all(self) -> None:
        await self.local_table.delete_all()
        if self.remote_table is not None:
            await self.remote_table.delete_all()


def _remote_identity(document: Document) -> Document:
    if "uid" in document and "slot" in document:
        return {"uid": document["uid"], "slot": document["slot"]}
    if "uid" in document and "id" not in document:
        return {"uid": document["uid"]}
    if "vip_id" in document and "id" not in document:
        return {"vip_id": document["vip_id"]}
    for key in ("id", "uid", "type", "locale", "mean", "freq", "status"):
        if key in document:
            return {key: document[key]}
    return document


class DatabaseRuntime:
    def __init__(self) -> None:
        self.local: SQLiteDatabase | None = None
        self.remote: MongoDBDatabase | None = None
        self.initialized = False

    async def initialize(self) -> None:
        if self.initialized:
            return

        Path(Config.SQLITE_DB_PATH).parent.mkdir(parents=True, exist_ok=True)

        if Config.AUTO_MIGRATE_ATLAS_SCHEMA and Config.MONGODB_URL:
            stats = await migrate_atlas_if_needed(
                connection_str=Config.MONGODB_URL,
                target_db_name=Config.MONGODB_DBNAME,
                base_language=Config.BASE_LANGUAGE,
            )
            LOGGER.info(msg=f"Atlas schema migration check: {stats.summary}")

        self.local = await SQLiteDatabase.create(db_path=Config.SQLITE_DB_PATH)
        await self.local.create_schema()

        if Config.MONGODB_URL:
            self.remote = MongoDBDatabase(
                connection_str=Config.MONGODB_URL, db_name=Config.MONGODB_DBNAME
            )
            await self.sync_remote_to_local()

        self.initialized = True

    async def close(self) -> None:
        if self.remote is not None:
            await self.remote.close()
            self.remote = None
        if self.local is not None:
            await self.local.close()
            self.local = None
        self.initialized = False

    async def table(self, table_name: str, mirror: bool | None = None) -> MirroredTable:
        await self.initialize()
        if self.local is None:
            raise RuntimeError("SQLite database is not initialized")

        should_mirror = table_name in REMOTE_TABLES if mirror is None else mirror
        remote_table = self.remote.table(table_name) if should_mirror and self.remote else None
        return MirroredTable(local_table=self.local.table(table_name), remote_table=remote_table)

    async def sync_remote_to_local(self) -> None:
        if self.local is None or self.remote is None:
            return

        remote_data = await self.remote.get_all_database()
        if not any(table in remote_data for table in REMOTE_TABLES):
            return

        for table_name in reversed(CANONICAL_TABLES):
            await self.local.table(table_name).delete_all()

        await self.local.seed_reference_data()

        for table_name in CANONICAL_TABLES:
            if table_name == "Task":
                continue
            for document in remote_data.get(table_name, []):
                clean_document = {key: value for key, value in document.items() if key != "_id"}
                await self.local.table(table_name).insert(document=clean_document)

        await self.local.seed_reference_data()

    async def export(self) -> dict[str, list[Document]]:
        await self.initialize()
        if self.local is None:
            return {}
        return await self.local.get_all_database()


runtime = DatabaseRuntime()


async def initialize_database() -> None:
    await runtime.initialize()


async def close_database() -> None:
    await runtime.close()


async def export_database() -> dict[str, list[Document]]:
    return await runtime.export()


async def _table(table_name: str, mirror: bool | None = None) -> MirroredTable:
    return await runtime.table(table_name=table_name, mirror=mirror)


async def _upsert(table_name: str, query: Document, document: Document) -> None:
    table = await _table(table_name)
    if await table.find_one(query=query):
        await table.update(query=query, update=document)
    else:
        await table.insert(document={**query, **document})


async def _ensure_user(user_id: int) -> None:
    user_id = int(user_id)
    table = await _table("User")
    if not await table.find_one({"id": user_id}):
        await table.insert(
            {
                "id": user_id,
                "is_banned": 0,
                "upload_mode": DEFAULT_UPLOAD_MODE,
                "lang": Config.BASE_LANGUAGE,
                "uploaded_count": 0,
            }
        )


async def add_user(user_id: int) -> int | None:
    user_id = int(user_id)
    if await is_user_in_db(user_id):
        return -1
    await _ensure_user(user_id)
    return None


async def del_user(user_id: int) -> int | None:
    user_id = int(user_id)
    if not await is_user_in_db(user_id):
        return -1
    await (await _table("User")).delete({"id": user_id})
    return None


async def is_user_in_db(user_id: int) -> bool:
    return await (await _table("User")).find_one({"id": int(user_id)}) is not None


async def count_users() -> int:
    return await (await _table("User")).count()


async def get_users_list() -> list[Document]:
    users = await (await _table("User")).get_all()
    return [_with_legacy_user_key(user) for user in users]


async def add_banned_user(user_id: int) -> int | None:
    user_id = int(user_id)
    await _ensure_user(user_id)
    if await is_user_in_bdb(user_id):
        return -1
    await (await _table("User")).update({"id": user_id}, {"is_banned": 1})
    return None


async def del_banned_user(user_id: int) -> int | None:
    user_id = int(user_id)
    if not await is_user_in_bdb(user_id):
        return -1
    await (await _table("User")).update({"id": user_id}, {"is_banned": 0})
    return None


async def is_user_in_bdb(user_id: int) -> bool:
    user = await (await _table("User")).find_one({"id": int(user_id)})
    return _bool(user.get("is_banned")) if user else False


async def count_banned_users() -> int:
    return await (await _table("User")).count({"is_banned": 1})


async def get_banned_users_list() -> list[Document]:
    users = await (await _table("User")).find({"is_banned": 1})
    return [{"banned_user_id": user["id"], **user} for user in users]


async def check_user(message) -> None:
    uid = message.from_user.id
    if await is_user_in_bdb(uid):
        await message.reply(messages.get(file="database", key="BANNED"))
        await message.stop_propagation()
        return

    if not await is_user_in_db(uid):
        await add_user(uid)
        await _log_new_user(message)

    await message.continue_propagation()


async def _log_new_user(message) -> None:
    uid = message.from_user.id
    firstname = getattr(message.from_user, "first_name", " ") or " "
    lastname = getattr(message.from_user, "last_name", " ") or " "
    username = getattr(message.from_user, "username", " ") or " "

    if firstname == " " and lastname == " " and username == " ":
        text = messages.get(
            file="database", key="NEW_USER_BAD", user_id=uid, extra_args=message.from_user.mention
        )
    else:
        text = messages.get(
            file="database",
            key="NEW_USER",
            user_id=uid,
            extra_args=[firstname + " " + lastname, " | @" + username, uid, uid, uid],
        )

    try:
        await unzipbot_client.send_message(
            chat_id=Config.LOGS_CHANNEL, text=text, disable_web_page_preview=False
        )
    except (FloodWait, FloodPremiumWait) as flood:
        await sleep(flood.value)
        await unzipbot_client.send_message(
            chat_id=Config.LOGS_CHANNEL, text=text, disable_web_page_preview=False
        )


async def get_all_users() -> tuple[list[int], list[int]]:
    users = [user["id"] for user in await (await _table("User")).get_all()]
    banned = [user["id"] for user in await (await _table("User")).find({"is_banned": 1})]
    return users, banned


async def set_upload_mode(user_id: int, mode: str) -> None:
    await _ensure_user(user_id)
    await (await _table("User")).update({"id": int(user_id)}, {"upload_mode": mode})


async def get_upload_mode(user_id: int) -> str:
    user = await (await _table("User")).find_one({"id": int(user_id)})
    return user.get("upload_mode", DEFAULT_UPLOAD_MODE) if user else DEFAULT_UPLOAD_MODE


async def get_uploaded(user_id: int) -> int:
    user = await (await _table("User")).find_one({"id": int(user_id)})
    return int(user.get("uploaded_count", 0)) if user else 0


async def update_uploaded(user_id: int, upload_count: int) -> None:
    await _ensure_user(user_id)
    await (await _table("User")).update(
        {"id": int(user_id)}, {"uploaded_count": await get_uploaded(user_id) + upload_count}
    )


async def get_thumb(user_id: int, slot: int = 0) -> Document | None:
    thumb = await (await _table("Thumb")).find_one({"uid": int(user_id), "slot": slot})
    return _with_legacy_thumb_keys(thumb) if thumb else None


async def update_temp_thumb(user_id: int, thumb_id: str, slot: int = 0) -> None:
    await _ensure_user(user_id)
    await _upsert(
        "Thumb", {"uid": int(user_id), "slot": slot}, {"file_id": thumb_id, "temp_id": thumb_id}
    )


async def update_thumb(user_id: int, slot: int = 0) -> None:
    existing = await (await _table("Thumb")).find_one({"uid": int(user_id), "slot": slot})
    if not existing:
        return
    await (await _table("Thumb")).update(
        {"uid": int(user_id), "slot": slot},
        {"file_id": existing.get("temp_id") or existing.get("file_id")},
        unset=["temp_id"],
    )


async def get_thumb_users() -> list[Document]:
    table = await _table("Thumb")
    thumb_users = []
    for thumb in await table.get_all():
        if thumb.get("file_id") is None:
            await table.delete(query={"id": thumb["id"]})
        else:
            thumb_users.append(_with_legacy_thumb_keys(thumb))
    return thumb_users


async def count_thumb_users() -> int:
    return await (await _table("Thumb")).count()


async def del_thumb_db(user_id: int) -> None:
    await (await _table("Thumb")).delete({"uid": int(user_id), "slot": 0})


async def get_boot() -> Any:
    system = await (await _table("System")).find_one({"id": 0})
    return system.get("boot_time") if system else None


async def set_boot(boottime: float) -> None:
    await _upsert("System", {"id": 0}, {"boot_time": boottime})


async def set_old_boot(boottime: float) -> None:
    await _upsert("System", {"id": 0}, {"old_boot_time": boottime})


async def get_old_boot() -> Any:
    system = await (await _table("System")).find_one({"id": 0})
    return system.get("old_boot_time") if system else None


async def is_boot_different() -> bool:
    boot = await get_boot()
    old_boot = await get_old_boot()
    return not (boot is not None and old_boot is not None and boot == old_boot)


async def get_ongoing_tasks() -> list[Document]:
    tasks = await (await _table("Task", mirror=False)).find({"started": 1, "cancelled": 0})
    return [_with_legacy_task_keys(task) for task in tasks]


async def count_ongoing_tasks() -> int:
    return await (await _table("Task", mirror=False)).count({"started": 1, "cancelled": 0})


async def _next_user_task_nb(user_id: int) -> int:
    tasks = await (await _table("Task", mirror=False)).find({"uid": int(user_id)})
    return max((int(task.get("user_task_nb", 0)) for task in tasks), default=0) + 1


async def add_ongoing_task(
    user_id: int, start_time: float, task_type: str, message_id: int = DEFAULT_TASK_MESSAGE_ID
) -> None:
    await _ensure_user(user_id)
    await _upsert(
        "Task",
        {"uid": int(user_id), "type": task_type, "message_id": int(message_id)},
        {
            "user_task_nb": await _next_user_task_nb(user_id),
            "started": 1,
            "start_time": start_time,
            "cancelled": 0,
        },
    )


async def del_ongoing_task(user_id: int) -> None:
    await (await _table("Task", mirror=False)).delete({"uid": int(user_id), "started": 1})


async def clear_ongoing_tasks() -> None:
    await (await _table("Task", mirror=False)).delete({"started": 1})


async def get_cancel_tasks() -> list[Document]:
    tasks = await (await _table("Task", mirror=False)).find({"cancelled": 1})
    return [_with_legacy_task_keys(task) for task in tasks]


async def count_cancel_tasks() -> int:
    return await (await _table("Task", mirror=False)).count({"cancelled": 1})


async def add_cancel_task(user_id: int) -> None:
    await _ensure_user(user_id)
    task_table = await _table("Task", mirror=False)
    tasks = await task_table.find({"uid": int(user_id), "started": 1})
    if tasks:
        await task_table.update({"uid": int(user_id), "started": 1}, {"cancelled": 1})
        return
    await _upsert(
        "Task",
        {"uid": int(user_id), "type": "extract", "message_id": DEFAULT_TASK_MESSAGE_ID},
        {"user_task_nb": DEFAULT_TASK_NB, "started": 0, "start_time": 0, "cancelled": 1},
    )


async def del_cancel_task(user_id: int) -> None:
    await (await _table("Task", mirror=False)).update({"uid": int(user_id)}, {"cancelled": 0})


async def get_cancel_task(user_id: int) -> bool:
    return (
        await (await _table("Task", mirror=False)).find_one({"uid": int(user_id), "cancelled": 1})
        is not None
    )


async def clear_cancel_tasks() -> None:
    await (await _table("Task", mirror=False)).update({"cancelled": 1}, {"cancelled": 0})


async def get_merge_tasks() -> list[Document]:
    tasks = await (await _table("Task", mirror=False)).find({"type": "merge"})
    return [_with_legacy_task_keys(task) for task in tasks]


async def count_merge_tasks() -> int:
    return await (await _table("Task", mirror=False)).count({"type": "merge"})


async def add_merge_task(user_id: int, message_id: int) -> None:
    await _ensure_user(user_id)
    await _upsert(
        "Task",
        {"uid": int(user_id), "type": "merge", "message_id": int(message_id)},
        {"user_task_nb": await _next_user_task_nb(user_id), "started": 0, "start_time": 0},
    )


async def del_merge_task(user_id: int) -> None:
    await (await _table("Task", mirror=False)).delete({"uid": int(user_id), "type": "merge"})


async def get_merge_task(user_id: int) -> bool:
    return (
        await (await _table("Task", mirror=False)).find_one({"uid": int(user_id), "type": "merge"})
        is not None
    )


async def get_merge_task_message_id(user_id: int) -> int | bool:
    task = await (await _table("Task", mirror=False)).find_one(
        {"uid": int(user_id), "type": "merge"}
    )
    return task.get("message_id") if task else False


async def clear_merge_tasks() -> None:
    await (await _table("Task", mirror=False)).delete({"type": "merge"})


async def get_maintenance() -> bool:
    system = await (await _table("System")).find_one({"id": 0})
    return _bool(system.get("maintenance")) if system else False


async def set_maintenance(val: bool) -> None:
    await _upsert("System", {"id": 0}, {"maintenance": _int_bool(val)})


async def add_vip_user(
    uid: int,
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
) -> None:
    uid = int(uid)
    await _ensure_user(uid)
    start = str(started or used or DEFAULT_VIP_DATE)
    end = str(ends or DEFAULT_VIP_DATE)
    await _upsert(
        "Vip",
        {"uid": uid},
        {
            "start": start,
            "end": end,
            "status": "active",
            "early": _int_bool(early),
            "donator": _int_bool(donator),
            "lifetime": _int_bool(lifetime),
            "gifted": _int_bool(gifted),
            "first_start": start,
            "nb_payments": int(successful or 1),
            "gap": _int_bool(gap),
        },
    )
    vip = await (await _table("Vip")).find_one({"uid": uid})
    if not vip:
        return

    proof = str(used or billed or f"legacy-{uid}")
    await _upsert(
        "Vip_Payment",
        {"proof": proof},
        {
            "vip_id": vip["id"],
            "start": start,
            "end": end,
            "mean": "custom",
            "frequency": "monthly" if subscription != "yearly" else "yearly",
            "paid_at": str(used or start),
        },
    )
    if referral:
        await _upsert(
            "Vip_Referral", {"vip_id": vip["id"]}, {"referral": str(referral), "referee": None}
        )


async def remove_vip_user(uid: int) -> None:
    await (await _table("Vip")).delete({"uid": int(uid)})


async def is_vip(uid: int) -> bool:
    return await (await _table("Vip")).find_one({"uid": int(uid)}) is not None


async def get_vip_users() -> list[Document]:
    return await (await _table("Vip")).get_all()


async def count_vip_users() -> int:
    return await (await _table("Vip")).count()


async def get_vip_user(uid: int) -> Document | None:
    return await (await _table("Vip")).find_one({"uid": int(uid)})


async def add_referee(uid: int, referral_code: str) -> None:
    await _ensure_user(uid)
    vip = await (await _table("Vip")).find_one({"uid": int(uid)})
    if not vip:
        await add_vip_user(
            uid=uid,
            subscription="monthly",
            ends=DEFAULT_VIP_DATE,
            used=DEFAULT_VIP_DATE,
            billed=referral_code,
            early=False,
            donator=False,
            started=DEFAULT_VIP_DATE,
            successful=0,
            gap=False,
            gifted=False,
            referral=referral_code,
            lifetime=False,
        )
        vip = await (await _table("Vip")).find_one({"uid": int(uid)})
    if vip:
        await _upsert(
            "Vip_Referral", {"vip_id": vip["id"]}, {"referral": referral_code, "referee": None}
        )


async def add_referrer(uid: int, referees: list[int]) -> None:
    await _ensure_user(uid)
    vip = await (await _table("Vip")).find_one({"uid": int(uid)})
    if not vip:
        await add_vip_user(
            uid=uid,
            subscription="monthly",
            ends=DEFAULT_VIP_DATE,
            used=DEFAULT_VIP_DATE,
            billed=f"legacy-referrer-{uid}",
            early=False,
            donator=False,
            started=DEFAULT_VIP_DATE,
            successful=0,
            gap=False,
            gifted=False,
            referral=get_referral_code(uid),
            lifetime=False,
        )
        vip = await (await _table("Vip")).find_one({"uid": int(uid)})
    if vip:
        await _upsert(
            "Vip_Referral",
            {"vip_id": vip["id"]},
            {"referral": get_referral_code(uid), "referee": ",".join(map(str, referees))},
        )


async def get_referee(uid: int) -> Document | None:
    vip = await (await _table("Vip")).find_one({"uid": int(uid)})
    if not vip:
        return None
    referral = await (await _table("Vip_Referral")).find_one({"vip_id": vip["id"]})
    return {"_id": uid, "type": "referee", **referral} if referral else None


async def get_referrer(uid: int) -> Document | None:
    vip = await (await _table("Vip")).find_one({"uid": int(uid)})
    if not vip:
        return None
    referral = await (await _table("Vip_Referral")).find_one({"vip_id": vip["id"]})
    if not referral:
        return None
    referees = []
    if referral.get("referee"):
        referees = [int(item) for item in str(referral["referee"]).split(",") if item]
    return {"_id": uid, "type": "referrer", "referees": referees, **referral}


def get_referral_code(uid: int) -> str:
    return base58check.b58encode(
        val=base58check.b58encode(val=str(uid).encode(encoding="ascii"))
    ).decode(encoding="ascii")


def get_referral_uid(referral_code: str) -> int:
    return int(
        base58check.b58decode(
            val=base58check.b58decode(val=referral_code).decode(encoding="ascii")
        ).decode(encoding="ascii")
    )
