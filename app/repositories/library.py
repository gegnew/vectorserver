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

    async def create(self, entity: Library) -> Library:
        await self.db.write_query(
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

    async def find(self, id: UUID) -> Library | None:
        row = await self.db.read_one(
            """
            SELECT id, name, description, created_at, updated_at, metadata FROM
            libraries WHERE id = ?
            """,
            (str(id),),
        )

        if not row:
            return None

        return self.to_entity(row)

    async def find_all(self) -> Sequence[Library]:
        rows = await self.db.read_query(
            """
            SELECT id, name, description, created_at, updated_at, metadata FROM
            libraries
            """,
        )

        return [self.to_entity(row) for row in rows]

    async def update(self, entity: Library) -> Library | None:
        changes = await self.db.write_query(
            """
            UPDATE libraries
               SET name = ?,
               description = ?,
               updated_at = ?,
               metadata = ?
             WHERE libraries.id = ?;
            """,
            (
                entity.name,
                entity.description,
                datetime.now(UTC).timestamp(),
                json.dumps(entity.metadata) if entity.metadata else None,
                str(entity.id),
            ),
        )
        if changes != 1:
            raise KeyError(entity.id)

        return await self.find(entity.id)

    async def delete(self, id: UUID) -> int:
        changes = await self.db.write_query(
            "DELETE FROM libraries WHERE id = ?", (str(id),)
        )
        return changes

    async def create_transactional(self, entity: Library, db=None) -> Library:
        \"\"\"Create a library within an existing transaction.\"\"\"
        target_db = db or self.db
        await target_db.execute_in_transaction(
            \"\"\"
            INSERT INTO libraries (id, name, description, created_at,
            updated_at, metadata) VALUES (?, ?, ?, ?, ?, ?)
            \"\"\",
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

    async def delete_transactional(self, id: UUID, db=None) -> int:
        \"\"\"Delete a library within an existing transaction.\"\"\"
        target_db = db or self.db
        changes = await target_db.execute_in_transaction(
            "DELETE FROM libraries WHERE id = ?", (str(id),)
        )
        return changes
