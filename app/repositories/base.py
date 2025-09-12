from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import TypeVar
from uuid import UUID

from app.repositories.db import DB

T = TypeVar("T")


class BaseRepository[T](ABC):
    def __init__(self, db: DB) -> None:
        self.db = db

    @abstractmethod
    async def create(self, entity: T) -> T:
        raise NotImplementedError()

    @abstractmethod
    async def find(self, _id: UUID) -> T | None:
        raise NotImplementedError()

    @abstractmethod
    async def find_all(self) -> Sequence[T]:
        raise NotImplementedError()

    @abstractmethod
    async def update(self, entity: T) -> T | None:
        raise NotImplementedError()

    @abstractmethod
    async def delete(self, _id: UUID) -> int:
        raise NotImplementedError()
