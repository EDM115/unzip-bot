from __future__ import annotations

from collections.abc import Iterable

CANONICAL_TABLES: tuple[str, ...] = (
    "Upload_Modes",
    "Languages",
    "Task_Types",
    "Payment_Means",
    "Payment_Frequencies",
    "Vip_Statuses",
    "User",
    "System",
    "Thumb",
    "Password",
    "Task",
    "Vip",
    "Vip_Payment",
    "Vip_Referral",
)

LOCAL_ONLY_TABLES: frozenset[str] = frozenset({"Task"})
REMOTE_TABLES: tuple[str, ...] = tuple(
    table for table in CANONICAL_TABLES if table not in LOCAL_ONLY_TABLES
)

LEGACY_COLLECTIONS: frozenset[str] = frozenset(
    {
        "users_db",
        "banned_users_db",
        "ulmode_db",
        "uploaded_count_db",
        "thumb_db",
        "bot_data",
        "maintenance_mode",
        "vip_users",
        "referrals",
    }
)

OLD_DEFAULT_DBNAME = "Unzipper_Bot"

SEED_ROWS: dict[str, tuple[dict[str, object], ...]] = {
    "Upload_Modes": ({"type": "media"}, {"type": "doc"}),
    "Languages": ({"locale": "en"}, {"locale": "fr"}),
    "Task_Types": ({"type": "extract"}, {"type": "merge"}),
    "Payment_Means": (
        {"mean": "paypal"},
        {"mean": "telegram"},
        {"mean": "gh"},
        {"mean": "bmac"},
        {"mean": "custom"},
    ),
    "Payment_Frequencies": ({"freq": "monthly"}, {"freq": "yearly"}),
    "Vip_Statuses": (
        {"status": "active"},
        {"status": "expired"},
        {"status": "cancelled"},
        {"status": "paused"},
    ),
    "System": ({"id": 0, "maintenance": 0},),
}


def table_names_for_remote(include_local: bool = False) -> Iterable[str]:
    return CANONICAL_TABLES if include_local else REMOTE_TABLES
