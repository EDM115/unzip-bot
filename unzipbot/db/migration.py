from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

import base58check
from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase

from unzipbot.db.orm.base import Document
from unzipbot.db.schema import LEGACY_COLLECTIONS, OLD_DEFAULT_DBNAME, REMOTE_TABLES, SEED_ROWS

DEFAULT_TARGET_DBNAME = "unzip-bot"
DEFAULT_DATE = "1970-01-01"
NEW_SCHEMA_MARKERS = frozenset({"User", "System", "Upload_Modes", "Vip"})


@dataclass
class MigrationStats:
    source_db: str | None = None
    target_db: str | None = None
    source_schema: str = "missing"
    migrated: bool = False
    old_documents: int = 0
    new_documents: int = 0
    skipped_thumbs: int = 0
    tables: dict[str, int] = field(default_factory=dict)
    elapsed_seconds: float = 0

    @property
    def summary(self) -> str:
        action = "migrated" if self.migrated else "no migration needed"
        return (
            f"{action}: source={self.source_db or '-'} target={self.target_db or '-'} "
            f"schema={self.source_schema} old_docs={self.old_documents} "
            f"new_docs={self.new_documents} skipped_thumbs={self.skipped_thumbs} "
            f"elapsed={self.elapsed_seconds:.2f}s"
        )


def _clean_document(document: Document) -> Document:
    return {key: _clean_value(value) for key, value in document.items() if key != "_id"}


def _clean_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _clean_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_clean_value(item) for item in value]
    if isinstance(value, tuple):
        return [_clean_value(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def _as_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _as_bool_int(value: Any) -> int:
    return int(bool(value))


def _date(value: Any) -> str:
    return str(value or DEFAULT_DATE)


async def detect_schema(database: AsyncDatabase) -> str:
    collections = set(await database.list_collection_names())
    if collections & NEW_SCHEMA_MARKERS:
        return "new"
    if collections & LEGACY_COLLECTIONS:
        return "old"
    return "empty"


async def _download_database(
    database: AsyncDatabase, collections: set[str]
) -> dict[str, list[Document]]:
    data: dict[str, list[Document]] = {}
    for collection in collections:
        cursor = database[collection].find({})
        docs = [_clean_document(document) async for document in cursor]
        if docs:
            data[collection] = docs
    return data


def _base_remote_data() -> dict[str, list[Document]]:
    data: dict[str, list[Document]] = {table: [] for table in REMOTE_TABLES}
    for table_name, rows in SEED_ROWS.items():
        if table_name in data:
            data[table_name] = [dict(row) for row in rows]
    return data


def migrate_legacy_data(
    legacy: dict[str, list[Document]], base_language: str
) -> tuple[MigrationStats, dict[str, list[Document]]]:
    stats = MigrationStats(source_schema="old")
    stats.old_documents = sum(len(documents) for documents in legacy.values())
    data = _base_remote_data()

    users: dict[int, Document] = {}

    def ensure_user(user_id: Any) -> Document:
        uid = _as_int(user_id)
        if uid not in users:
            users[uid] = {
                "id": uid,
                "is_banned": 0,
                "upload_mode": "media",
                "lang": base_language,
                "uploaded_count": 0,
            }
        return users[uid]

    for document in legacy.get("users_db", []):
        ensure_user(document.get("user_id"))

    for document in legacy.get("banned_users_db", []):
        ensure_user(document.get("banned_user_id"))["is_banned"] = 1

    for document in legacy.get("ulmode_db", []):
        user = ensure_user(document.get("_id"))
        mode = document.get("mode") or "media"
        user["upload_mode"] = mode if mode in {"media", "doc"} else "media"

    for document in legacy.get("uploaded_count_db", []):
        ensure_user(document.get("_id"))["uploaded_count"] = max(
            0, _as_int(document.get("uploaded_files"))
        )

    thumb_id = 1
    for document in legacy.get("thumb_db", []):
        uid = _as_int(document.get("_id"))
        ensure_user(uid)
        file_id = document.get("file_id") or document.get("temp")
        if not file_id:
            stats.skipped_thumbs += 1
            continue
        data["Thumb"].append(
            {
                "id": thumb_id,
                "uid": uid,
                "slot": 0,
                "file_id": str(file_id),
                "temp_id": document.get("temp"),
            }
        )
        thumb_id += 1

    system: Document = {"id": 0, "maintenance": 0}
    for document in legacy.get("bot_data", []):
        if document.get("boot"):
            system["boot_time"] = document.get("time")
        if document.get("old_boot"):
            system["old_boot_time"] = document.get("time")
    for document in legacy.get("maintenance_mode", []):
        if document.get("maintenance"):
            system["maintenance"] = _as_bool_int(document.get("val"))
    data["System"] = [system]

    _migrate_legacy_vip(legacy=legacy, data=data, ensure_user=ensure_user)
    _migrate_legacy_referrals(legacy=legacy, data=data, ensure_user=ensure_user)
    data["User"] = sorted(users.values(), key=lambda user: user["id"])

    stats.tables = {table: len(rows) for table, rows in data.items()}
    stats.new_documents = sum(stats.tables.values())
    return stats, data


def _migrate_legacy_vip(
    legacy: dict[str, list[Document]], data: dict[str, list[Document]], ensure_user
) -> None:
    vip_id = 1
    payment_id = 1
    for document in legacy.get("vip_users", []):
        uid = _as_int(document.get("_id"))
        ensure_user(uid)
        start = _date(document.get("started") or document.get("used"))
        end = _date(document.get("ends"))
        data["Vip"].append(
            {
                "id": vip_id,
                "uid": uid,
                "start": start,
                "end": end,
                "status": "active",
                "early": _as_bool_int(document.get("early")),
                "donator": _as_bool_int(document.get("donator")),
                "lifetime": _as_bool_int(document.get("lifetime")),
                "gifted": _as_bool_int(document.get("gifted")),
                "first_start": start,
                "nb_payments": max(0, _as_int(document.get("successful"), 1)),
                "gap": _as_bool_int(document.get("gap")),
            }
        )
        proof = str(document.get("billed") or document.get("used") or f"legacy-{uid}")
        existing_proofs = {payment["proof"] for payment in data["Vip_Payment"]}
        if proof in existing_proofs:
            proof = f"{proof}-{payment_id}"
        data["Vip_Payment"].append(
            {
                "id": payment_id,
                "vip_id": vip_id,
                "start": start,
                "end": end,
                "mean": "custom",
                "proof": proof,
                "frequency": "yearly" if document.get("subscription") == "yearly" else "monthly",
                "paid_at": _date(document.get("used") or start),
            }
        )
        if document.get("referral"):
            data["Vip_Referral"].append(
                {"id": vip_id, "vip_id": vip_id, "referral": str(document["referral"])}
            )
        vip_id += 1
        payment_id += 1


def _migrate_legacy_referrals(
    legacy: dict[str, list[Document]], data: dict[str, list[Document]], ensure_user
) -> None:
    existing_by_uid = {vip["uid"]: vip for vip in data["Vip"]}
    next_vip_id = max((vip["id"] for vip in data["Vip"]), default=0) + 1
    next_referral_id = max((referral["id"] for referral in data["Vip_Referral"]), default=0) + 1

    def ensure_vip(uid: int) -> Document:
        nonlocal next_vip_id
        if uid in existing_by_uid:
            return existing_by_uid[uid]
        ensure_user(uid)
        vip = {
            "id": next_vip_id,
            "uid": uid,
            "start": DEFAULT_DATE,
            "end": DEFAULT_DATE,
            "status": "expired",
            "early": 0,
            "donator": 0,
            "lifetime": 0,
            "gifted": 0,
            "first_start": DEFAULT_DATE,
            "nb_payments": 0,
            "gap": 0,
        }
        data["Vip"].append(vip)
        existing_by_uid[uid] = vip
        next_vip_id += 1
        return vip

    for document in legacy.get("referrals", []):
        uid = _as_int(document.get("_id"))
        vip = ensure_vip(uid)
        if any(referral["vip_id"] == vip["id"] for referral in data["Vip_Referral"]):
            continue

        if document.get("type") == "referrer":
            referees = document.get("referees") or []
            data["Vip_Referral"].append(
                {
                    "id": next_referral_id,
                    "vip_id": vip["id"],
                    "referral": _referral_code(uid),
                    "referee": ",".join(str(referee) for referee in referees),
                }
            )
        else:
            data["Vip_Referral"].append(
                {
                    "id": next_referral_id,
                    "vip_id": vip["id"],
                    "referral": str(document.get("referral_code") or _referral_code(uid)),
                }
            )
        next_referral_id += 1


def _referral_code(uid: int) -> str:
    return base58check.b58encode(
        val=base58check.b58encode(val=str(uid).encode(encoding="ascii"))
    ).decode(encoding="ascii")


async def _upload_new_data(database: AsyncDatabase, data: dict[str, list[Document]]) -> None:
    for table_name, documents in data.items():
        await database[table_name].delete_many({})
        if documents:
            await database[table_name].insert_many(documents)


async def migrate_atlas_if_needed(
    connection_str: str,
    target_db_name: str = DEFAULT_TARGET_DBNAME,
    source_db_name: str | None = None,
    base_language: str = "en",
) -> MigrationStats:
    start = time.perf_counter()
    client = AsyncMongoClient(host=connection_str)
    try:
        candidates = []
        for db_name in (source_db_name, target_db_name, DEFAULT_TARGET_DBNAME, OLD_DEFAULT_DBNAME):
            if db_name and db_name not in candidates:
                candidates.append(db_name)

        detected: list[tuple[str, str]] = []
        for db_name in candidates:
            schema = await detect_schema(client[db_name])
            detected.append((db_name, schema))
            if schema == "new":
                stats = MigrationStats(
                    source_db=db_name,
                    target_db=db_name,
                    source_schema="new",
                    migrated=False,
                    elapsed_seconds=time.perf_counter() - start,
                )
                return stats

        old_source = next(
            ((db_name, schema) for db_name, schema in detected if schema == "old"), None
        )
        if old_source is None:
            return MigrationStats(
                target_db=target_db_name,
                source_schema="empty",
                migrated=False,
                elapsed_seconds=time.perf_counter() - start,
            )

        source_db, source_schema = old_source
        legacy = await _download_database(client[source_db], set(LEGACY_COLLECTIONS))
        stats, new_data = migrate_legacy_data(legacy=legacy, base_language=base_language)
        stats.source_db = source_db
        stats.target_db = target_db_name
        stats.source_schema = source_schema
        await _upload_new_data(client[target_db_name], new_data)
        stats.migrated = True
        stats.elapsed_seconds = time.perf_counter() - start
        return stats
    finally:
        await client.close()
