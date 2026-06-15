from __future__ import annotations

import hashlib
import re
import time
from dataclasses import dataclass
from pathlib import Path

from aiosqlite import Connection, Row

MIGRATION_TABLE = "Schema_Migrations"
MIGRATIONS_DIR = Path(__file__).resolve().parents[1] / "migrations"
_DESCRIPTION_RE = re.compile(r"^--\s*description:\s*(?P<description>.+?)\s*$", re.MULTILINE)


@dataclass(frozen=True)
class MigrationFile:
    id: str
    name: str
    description: str
    checksum: str
    sql: str
    statement_count: int
    path: Path


@dataclass(frozen=True)
class AppliedMigration:
    id: str
    name: str
    description: str
    checksum: str
    applied_at: str
    execution_ms: int
    statement_count: int


class SQLiteMigrator:
    def __init__(self, connection: Connection, migrations_dir: Path | None = None) -> None:
        self.conn = connection
        self.migrations_dir = migrations_dir or MIGRATIONS_DIR

    async def run_pending(self) -> list[AppliedMigration]:
        await self.ensure_migration_table()
        applied = await self.applied_migrations()
        applied_by_id = {migration.id: migration for migration in applied}
        completed: list[AppliedMigration] = []

        for migration in self.available_migrations():
            previous = applied_by_id.get(migration.id)
            if previous is not None:
                if previous.checksum != migration.checksum:
                    raise RuntimeError(
                        "Applied SQLite migration checksum changed: "
                        f"{migration.id} ({previous.checksum} != {migration.checksum})"
                    )
                continue

            completed.append(await self.apply(migration))

        return completed

    async def ensure_migration_table(self) -> None:
        await self.conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {MIGRATION_TABLE} (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                checksum TEXT NOT NULL,
                applied_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
                execution_ms INTEGER NOT NULL,
                statement_count INTEGER NOT NULL
            )
            """
        )
        await self.conn.commit()

    async def applied_migrations(self) -> list[AppliedMigration]:
        await self.ensure_migration_table()
        async with self.conn.execute(
            """
            SELECT id, name, description, checksum, applied_at, execution_ms, statement_count
            FROM Schema_Migrations
            ORDER BY id
            """
        ) as cursor:
            rows: list[Row] = await cursor.fetchall()

        return [
            AppliedMigration(
                id=row["id"],
                name=row["name"],
                description=row["description"],
                checksum=row["checksum"],
                applied_at=row["applied_at"],
                execution_ms=row["execution_ms"],
                statement_count=row["statement_count"],
            )
            for row in rows
        ]

    def available_migrations(self) -> list[MigrationFile]:
        if not self.migrations_dir.exists():
            return []
        return [self._load_migration(path) for path in sorted(self.migrations_dir.glob("*.sql"))]

    async def apply(self, migration: MigrationFile) -> AppliedMigration:
        started = time.perf_counter()
        await self.conn.executescript(migration.sql)
        execution_ms = max(0, round((time.perf_counter() - started) * 1000))
        await self.conn.execute(
            """
            INSERT INTO Schema_Migrations
                (id, name, description, checksum, execution_ms, statement_count)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                migration.id,
                migration.name,
                migration.description,
                migration.checksum,
                execution_ms,
                migration.statement_count,
            ),
        )
        await self.conn.commit()

        applied = await self.applied_migrations()
        return next(item for item in applied if item.id == migration.id)

    @staticmethod
    def _load_migration(path: Path) -> MigrationFile:
        sql = path.read_text(encoding="utf-8")
        description_match = _DESCRIPTION_RE.search(sql)
        description = description_match.group("description") if description_match else ""
        return MigrationFile(
            id=path.stem,
            name=path.name,
            description=description,
            checksum=hashlib.sha256(sql.encode("utf-8")).hexdigest(),
            sql=sql,
            statement_count=_count_statements(sql),
            path=path,
        )


def _count_statements(sql: str) -> int:
    statements = []
    for statement in sql.split(";"):
        stripped_lines = [
            line
            for line in statement.splitlines()
            if line.strip() and not line.lstrip().startswith("--")
        ]
        if "".join(stripped_lines).strip():
            statements.append(statement)
    return len(statements)
