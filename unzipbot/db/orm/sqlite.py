from collections.abc import Iterable
from typing import Any, LiteralString

from aiosqlite import Connection, Row, connect
from base import DatabaseInterface, TableInterface


class SQLiteTable(TableInterface):
    def __init__(self, connection, table_name: str) -> None:
        self.conn: Connection = connection
        self.table_name: str = table_name

    async def count(self, filter: dict | None = None) -> int:
        where_clause: str
        params: list
        where_clause, params = self.__build_where_clause(filter=filter)
        sql: str = f"SELECT COUNT(*) FROM {self.table_name} {where_clause}"

        async with self.conn.execute(sql, params) as cursor:
            row: Row | None = await cursor.fetchone()

        return row[0] if row else 0

    async def find_one(self, query: dict) -> dict | None:
        where_clause: str
        params: list
        where_clause, params = self.__build_where_clause(filter=query)
        sql: str = f"SELECT * FROM {self.table_name} {where_clause} LIMIT 1"

        async with self.conn.execute(sql, params) as cursor:
            row: Row | None = await cursor.fetchone()

        return dict(row) if row else None

    async def get_all(self) -> list:
        sql: str = f"SELECT * FROM {self.table_name}"

        async with self.conn.execute(sql) as cursor:
            rows: Iterable[Row] = await cursor.fetchall()

        return [dict(row) for row in rows]

    async def insert(self, document: dict) -> None:
        columns: LiteralString = ", ".join(document.keys())
        placeholders: str = ", ".join(["?"] * len(document))
        sql: str = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"
        await self.conn.execute(sql, tuple(document.values()))
        await self.conn.commit()

    async def update(self, query: dict, update: dict) -> None:
        set_clause: str
        set_params: list
        where_clause: str
        where_params: list
        set_clause, set_params = self.__build_set_clause(update=update)
        where_clause, where_params = self.__build_where_clause(filter=query)
        sql: str = f"UPDATE {self.table_name} SET {set_clause} {where_clause}"
        await self.conn.execute(sql, tuple(set_params + where_params))
        await self.conn.commit()

    async def delete(self, query: dict[str, Any]) -> None:
        where_clause: str
        params: list[Any]
        where_clause, params = self.__build_where_clause(filter=query)
        sql: str = f"DELETE FROM {self.table_name} {where_clause}"
        await self.conn.execute(sql, params)
        await self.conn.commit()

    async def delete_all(self) -> None:
        sql: str = f"DELETE FROM {self.table_name}"
        await self.conn.execute(sql)
        await self.conn.commit()

    def __build_where_clause(self, filter: dict | None) -> tuple[str, list]:
        if not filter:
            return "", []

        clause: str = " AND ".join([f"{key} = ?" for key in filter.keys()])

        return "WHERE " + clause, list(filter.values())

    def __build_set_clause(self, update: dict) -> tuple[str, list]:
        clause: str = ", ".join([f"{key} = ?" for key in update.keys()])

        return clause, list(update.values())


class SQLiteDatabase(DatabaseInterface):
    async def __init__(self, db_path: str) -> None:
        self.db_path: str = db_path
        self.conn: Connection = await connect(database=self.db_path)
        self.conn.row_factory = Row

    async def open(self) -> None:
        self.conn = await connect(database=self.db_path)
        self.conn.row_factory = Row

    async def close(self) -> None:
        await self.conn.close()

    def table(self, table_name: str) -> TableInterface:
        return SQLiteTable(connection=self.conn, table_name=table_name)

    async def get_all_database(self) -> dict:
        data: dict = {}
        sql = "SELECT name FROM sqlite_master WHERE type='table'"

        async with self.conn.execute(sql) as cursor:
            tables: Iterable[Row] = await cursor.fetchall()

        for table in tables:
            table_name: str = table[0]
            table_obj: TableInterface = self.table(table_name=table_name)
            data[table_name] = await table_obj.get_all()

        return data

    async def create_table(self, table_name: str, schema: dict) -> None:
        """
        Helper method for creating a table given a schema dict
        ex : {"id": "INTEGER PRIMARY KEY", "name": "TEXT"}.
        """
        columns_def: str = ", ".join(
            [f"{col} {dtype}" for col, dtype in schema.items()]
        )
        sql: str = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_def})"
        await self.conn.execute(sql)
        await self.conn.commit()
