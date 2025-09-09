from collections.abc import Sequence
import json
from uuid import UUID
from app.models.library import Library
from app.repositories.base import BaseRepository
from app.repositories.db import get_db


class LibraryRepository(BaseRepository[Library]):
    def __init__(self) -> None:
        self.db = get_db()

    def create(self, entity: Library) -> Library:
        self.db.conn.execute(
            """
            INSERT INTO libraries (id, name, description, created_at,
            updated_at, metadata) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                str(entity.id),
                entity.name,
                entity.description,
                entity.created_at.timestamp(),
                entity.updated_at.timestamp() if entity.updated_at else None,
                json.dumps(entity.metadata),
            ),
        )
        return entity

    def find(self, id: UUID) -> Library:
        raise NotImplementedError()

    def find_all(self) -> Sequence[Library]:
        raise NotImplementedError()

    def update(self, entity: Library) -> Library:
        raise NotImplementedError()

    def delete(self, id: UUID) -> Library:
        raise NotImplementedError()
