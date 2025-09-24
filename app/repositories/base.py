from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import TYPE_CHECKING, TypeVar
from uuid import UUID

if TYPE_CHECKING:
    from app.repositories.db import DB

T = TypeVar("T")


class BaseRepository[T](ABC):
    def __init__(self, db: DB) -> None:
        """Initialize repository with database connection."""
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

    @abstractmethod
    async def create_transactional(self, entity: T, db: DB) -> T:
        """Create entity within an existing transaction."""
        raise NotImplementedError()

    @abstractmethod
    async def update_transactional(self, entity: T, db: DB) -> T | None:
        """Update entity within an existing transaction."""
        raise NotImplementedError()

    @abstractmethod
    async def delete_transactional(self, _id: UUID, db: DB) -> int:
        """Delete entity within an existing transaction."""
        raise NotImplementedError()

    @abstractmethod
    async def find_transactional(self, _id: UUID, db: DB) -> T | None:
        """Find entity within an existing transaction."""
        raise NotImplementedError()

    @abstractmethod
    async def find_all_transactional(self, db: DB) -> Sequence[T]:
        """Find all entities within an existing transaction."""
        raise NotImplementedError()
