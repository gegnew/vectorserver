import json
from collections.abc import Sequence
from datetime import UTC, datetime
from uuid import UUID

from app.models.library import Library
from app.repositories.base import BaseRepository


class LibraryRepository(BaseRepository[Library]):
    def to_entity(self, row):
        return Library(
            id=UUID(row[0]),
            name=row[1],
            description=row[2],
            created_at=datetime.fromtimestamp(row[3], tz=UTC),
            updated_at=datetime.fromtimestamp(row[4], tz=UTC) if row[4] else None,
            metadata=row[5],
        )

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
                json.dumps(entity.metadata) if entity.metadata else None,
            ),
        )
        return entity

    def find(self, id: UUID) -> Library | None:
        row = self.db.conn.execute(
            """
            SELECT id, name, description, created_at, updated_at, metadata FROM
            libraries WHERE id = ?
            """,
            (str(id),),
        ).fetchone()

        if not row:
            return None

        return self.to_entity(row)

    def find_all(self) -> Sequence[Library]:
        cursor = self.db.conn.execute(
            """
            SELECT id, name, description, created_at, updated_at, metadata FROM
            libraries
            """,
        )

        return [self.to_entity(row) for row in cursor.fetchall()]

    def update(self, entity: Library) -> Library | None:
        res = self.db.conn.execute(
            """
            UPDATE libraries
               SET name = ?,
               description = ?,
               created_at = ?,
               updated_at = ?,
               metadata = ?
             WHERE libraries.id = ?;
            """,
            (
                entity.name,
                entity.description,
                entity.created_at.timestamp(),
                datetime.now(UTC).timestamp(),
                json.dumps(entity.metadata) if entity.metadata else None,
                str(entity.id),
            ),
        )
        if res.rowcount != 1:
            raise KeyError(entity.id)

        return self.find(entity.id)

    def delete(self, id: UUID) -> int:
        cursor = self.db.conn.execute("DELETE FROM libraries WHERE id = ?", (str(id),))
        return cursor.rowcount
