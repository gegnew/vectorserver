from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import TypeVar
from uuid import UUID

T = TypeVar("T")


class BaseRepository[T](ABC):
    @abstractmethod
    def create(self, entity: T) -> T:
        raise NotImplementedError()

    @abstractmethod
    def find(self, _id: UUID) -> T:
        raise NotImplementedError()

    @abstractmethod
    def find_all(self) -> Sequence[T]:
        raise NotImplementedError()

    @abstractmethod
    def update(self, entity: T) -> T:
        raise NotImplementedError()

    @abstractmethod
    def delete(self, _id: UUID) -> T:
        raise NotImplementedError()
