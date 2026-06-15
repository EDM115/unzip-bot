from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import Any

Document = dict[str, Any]


class TableInterface(ABC):
    @abstractmethod
    async def count(self, filter: Document | None = None) -> int:
        """
        Return the count of records matching the filter.
        """
        pass

    @abstractmethod
    async def find(self, query: Document | None = None) -> list[Document]:
        """
        Retrieve records matching the query.
        """
        pass

    @abstractmethod
    async def find_one(self, query: Document) -> Document | None:
        """
        Find and return a single record matching the query.
        """
        pass

    @abstractmethod
    async def get_all(self) -> list[Document]:
        """
        Retrieve all records from the table.
        """
        pass

    @abstractmethod
    async def insert(self, document: Document) -> None:
        """
        Insert a new record into the table.
        """
        pass

    @abstractmethod
    async def update(
        self, query: Document, update: Document, unset: Iterable[str] | None = None
    ) -> None:
        """
        Update record(s) matching the query.
        """
        pass

    @abstractmethod
    async def delete(self, query: Document) -> None:
        """
        Delete record(s) that match the query.
        """
        pass

    @abstractmethod
    async def delete_all(self) -> None:
        """
        Delete all records in the table.
        """
        pass


class DatabaseInterface(ABC):
    @abstractmethod
    async def open(self) -> None:
        """
        Open the database connection.
        """
        pass

    @abstractmethod
    async def close(self) -> None:
        """
        Close the database connection.
        """
        pass

    @abstractmethod
    def table(self, table_name: str) -> TableInterface:
        """
        Return a table handle for a given table or collection name.
        """
        pass

    @abstractmethod
    async def get_all_database(self) -> dict[str, list[Document]]:
        """
        Retrieve all data from the entire database.
        """
        pass
