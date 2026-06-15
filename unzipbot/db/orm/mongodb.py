from collections.abc import Iterable

from pymongo import AsyncMongoClient
from pymongo.asynchronous.collection import AsyncCollection
from pymongo.asynchronous.cursor import AsyncCursor
from pymongo.asynchronous.database import AsyncDatabase

from .base import DatabaseInterface, Document, TableInterface


class MongoTable(TableInterface):
    def __init__(self, collection) -> None:
        self.collection: AsyncCollection = collection

    async def count(self, filter: Document | None = None) -> int:
        filter = filter or {}

        return await self.collection.count_documents(filter=filter)

    async def find(self, query: Document | None = None) -> list[Document]:
        cursor: AsyncCursor = self.collection.find(query or {})
        return [doc async for doc in cursor]

    async def find_one(self, query: Document) -> Document | None:
        return await self.collection.find_one(filter=query)

    async def get_all(self) -> list[Document]:
        return await self.find()

    async def insert(self, document: Document) -> None:
        await self.collection.insert_one(document=document)

    async def update(
        self, query: Document, update: Document, unset: Iterable[str] | None = None
    ) -> None:
        payload: dict[str, Document] = {}
        if update:
            payload["$set"] = update
        if unset:
            payload["$unset"] = {key: "" for key in unset}
        if payload:
            await self.collection.update_many(filter=query, update=payload)

    async def delete(self, query: Document) -> None:
        await self.collection.delete_one(filter=query)

    async def delete_all(self) -> None:
        await self.collection.delete_many(filter={})


class MongoDBDatabase(DatabaseInterface):
    def __init__(self, connection_str: str, db_name: str) -> None:
        self.connection_str: str = connection_str
        self.db_name: str = db_name
        self.client = AsyncMongoClient(host=self.connection_str)
        self.db: AsyncDatabase = self.client[self.db_name]

    async def open(self) -> None:
        self.client = AsyncMongoClient(host=self.connection_str)
        self.db = self.client[self.db_name]

    async def close(self) -> None:
        await self.client.close()

    def table(self, table_name: str) -> TableInterface:
        return MongoTable(collection=self.db[table_name])

    async def get_all_database(self) -> dict[str, list[Document]]:
        data: dict[str, list[Document]] = {}
        collections: list[str] = await self.db.list_collection_names()

        for coll in collections:
            cursor: AsyncCursor = self.db[coll].find({})
            data[coll] = [doc async for doc in cursor]

        return data
