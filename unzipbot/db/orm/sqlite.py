import re
from collections.abc import Iterable
from typing import Any

from aiosqlite import Connection, Row, connect

from unzipbot.db.schema import SEED_ROWS

from .base import DatabaseInterface, Document, TableInterface
from .migrator import AppliedMigration, SQLiteMigrator

_SQL_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _quote_identifier(identifier: str) -> str:
    if not _SQL_IDENTIFIER_RE.fullmatch(identifier):
        raise ValueError(f"Unsafe SQLite identifier: {identifier!r}")
    return f'"{identifier}"'


def _to_sql_value(value: Any) -> Any:
    if isinstance(value, bool):
        return int(value)
    return value


def _row_to_document(row: Row) -> Document:
    return {key: row[key] for key in row.keys()}


class SQLiteTable(TableInterface):
    def __init__(self, connection: Connection, table_name: str) -> None:
        self.conn: Connection = connection
        self.raw_table_name: str = table_name
        self.table_name: str = _quote_identifier(table_name)

    async def _columns(self) -> set[str]:
        async with self.conn.execute(f"PRAGMA table_info({self.table_name})") as cursor:
            rows: Iterable[Row] = await cursor.fetchall()
        return {row["name"] for row in rows}

    async def _filtered_document(self, document: Document) -> Document:
        columns = await self._columns()
        return {
            key: _to_sql_value(value)
            for key, value in document.items()
            if key in columns and key != "_id"
        }

    async def count(self, filter: Document | None = None) -> int:
        if not filter:
            async with self.conn.execute(
                f"SELECT COUNT(*) FROM {self.table_name}"  # noqa: S608
            ) as cursor:
                row: Row | None = await cursor.fetchone()
            return row[0] if row else 0

        return len(await self.find(filter))

    async def find(self, query: Document | None = None) -> list[Document]:
        query = await self._filtered_document(query or {})
        where, values = self._where_clause(query)
        async with self.conn.execute(
            f"SELECT * FROM {self.table_name}{where}",  # noqa: S608
            values,
        ) as cursor:
            rows: Iterable[Row] = await cursor.fetchall()
        return [_row_to_document(row) for row in rows]

    async def find_one(self, query: Document) -> Document | None:
        docs = await self.find(query=query)
        return docs[0] if docs else None

    async def get_all(self) -> list[Document]:
        return await self.find()

    async def insert(self, document: Document) -> None:
        document = await self._filtered_document(document)
        if not document:
            await self.conn.execute(f"INSERT OR REPLACE INTO {self.table_name} DEFAULT VALUES")  # noqa: S608
            await self.conn.commit()
            return

        columns = [_quote_identifier(column) for column in document]
        placeholders = ", ".join("?" for _ in document)
        await self.conn.execute(
            f"INSERT OR REPLACE INTO {self.table_name} "  # noqa: S608
            f"({', '.join(columns)}) VALUES ({placeholders})",
            tuple(document.values()),
        )
        await self.conn.commit()

    async def update(
        self, query: Document, update: Document, unset: Iterable[str] | None = None
    ) -> None:
        update = await self._filtered_document(update)
        columns = await self._columns()
        for key in unset or ():
            if key in columns:
                update[key] = None
        if not update:
            return

        query = await self._filtered_document(query)
        where, where_values = self._where_clause(query)
        assignments = ", ".join(f"{_quote_identifier(column)} = ?" for column in update)
        await self.conn.execute(
            f"UPDATE {self.table_name} SET {assignments}{where}",  # noqa: S608
            tuple(update.values()) + where_values,
        )
        await self.conn.commit()

    async def delete(self, query: Document) -> None:
        query = await self._filtered_document(query)
        where, values = self._where_clause(query)
        await self.conn.execute(f"DELETE FROM {self.table_name}{where}", values)  # noqa: S608
        await self.conn.commit()

    async def delete_all(self) -> None:
        await self.conn.execute(f"DELETE FROM {self.table_name}")  # noqa: S608
        await self.conn.commit()

    @staticmethod
    def _where_clause(query: Document) -> tuple[str, tuple[Any, ...]]:
        if not query:
            return "", ()

        clauses = []
        values = []
        for key, value in query.items():
            if value is None:
                clauses.append(f"{_quote_identifier(key)} IS NULL")
            else:
                clauses.append(f"{_quote_identifier(key)} = ?")
                values.append(_to_sql_value(value))
        return f" WHERE {' AND '.join(clauses)}", tuple(values)


class SQLiteDatabase(DatabaseInterface):
    def __init__(self, db_path: str) -> None:
        self.db_path: str = db_path
        self.conn: Connection | None = None

    @classmethod
    async def create(cls, db_path: str) -> "SQLiteDatabase":
        database = cls(db_path=db_path)
        await database.open()
        return database

    async def open(self) -> None:
        self.conn = await connect(database=self.db_path)
        self.conn.row_factory = Row
        await self.conn.execute("PRAGMA foreign_keys = ON")
        await self.conn.execute("PRAGMA journal_mode = WAL")

    async def close(self) -> None:
        if self.conn is not None:
            await self.conn.close()
            self.conn = None

    def table(self, table_name: str) -> TableInterface:
        if self.conn is None:
            raise RuntimeError("SQLite database is not open")
        return SQLiteTable(connection=self.conn, table_name=table_name)

    async def get_all_database(self) -> dict[str, list[Document]]:
        if self.conn is None:
            raise RuntimeError("SQLite database is not open")

        data: dict[str, list[Document]] = {}
        async with self.conn.execute("SELECT name FROM sqlite_master WHERE type='table'") as cursor:
            tables: Iterable[Row] = await cursor.fetchall()

        for table in tables:
            table_name: str = table["name"]
            if table_name in {"sqlite_sequence", "Schema_Migrations"}:
                continue
            data[table_name] = await self.table(table_name=table_name).get_all()

        return data

    async def create_table(self, table_name: str, schema: dict[str, str] | None = None) -> None:
        if self.conn is None:
            raise RuntimeError("SQLite database is not open")

        if schema is not None:
            columns = ", ".join(
                f"{_quote_identifier(name)} {definition}" for name, definition in schema.items()
            )
            await self.conn.execute(
                f"CREATE TABLE IF NOT EXISTS {_quote_identifier(table_name)} ({columns})"  # noqa: S608
            )
            await self.conn.commit()
            return

        await self.create_schema()

    async def create_schema(self) -> None:
        if self.conn is None:
            raise RuntimeError("SQLite database is not open")

        await self.run_migrations()
        await self.seed_reference_data()

    async def run_migrations(self) -> list[AppliedMigration]:
        if self.conn is None:
            raise RuntimeError("SQLite database is not open")

        return await SQLiteMigrator(connection=self.conn).run_pending()

    async def get_schema_migrations(self) -> list[AppliedMigration]:
        if self.conn is None:
            raise RuntimeError("SQLite database is not open")

        return await SQLiteMigrator(connection=self.conn).applied_migrations()

    async def seed_reference_data(self) -> None:
        for table_name, rows in SEED_ROWS.items():
            table = self.table(table_name)
            for row in rows:
                await table.insert(dict(row))
