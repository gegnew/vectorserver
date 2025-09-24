import json
from collections.abc import Sequence
from datetime import UTC, datetime
from uuid import UUID

from app.models.document import Document
from app.repositories.base import BaseRepository


class DocumentRepository(BaseRepository[Document]):
    def to_entity(self, row):
        return Document(
            id=UUID(row[0]),
            title=row[1],
            content=row[2],
            library_id=row[3],
            created_at=datetime.fromtimestamp(row[4], tz=UTC),
            updated_at=datetime.fromtimestamp(row[5], tz=UTC) if row[5] else None,
            metadata=row[6],
        )

    async def create(self, entity: Document) -> Document:
        await self.db.write_query(
            """
            INSERT INTO documents (id, title, content, library_id, created_at,
            updated_at, metadata) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(entity.id),
                entity.title,
                entity.content,
                str(entity.library_id),
                entity.created_at.timestamp(),
                entity.updated_at.timestamp() if entity.updated_at else None,
                json.dumps(entity.metadata) if entity.metadata else None,
            ),
        )
        return entity

    async def find_by_library(self, id: UUID) -> list[Document]:
        rows = await self.db.read_query(
            """
            SELECT id, title, content, library_id, created_at, updated_at, metadata FROM
            documents WHERE library_id = ?
            """,
            (str(id),),
        )
        return [self.to_entity(row) for row in rows]

    async def find(self, id: UUID) -> Document | None:
        row = await self.db.read_one(
            """
            SELECT id, title, content, library_id, created_at, updated_at, metadata FROM
            documents WHERE id = ?
            """,
            (str(id),),
        )

        if not row:
            return None

        return self.to_entity(row)

    async def find_all(self) -> Sequence[Document]:
        rows = await self.db.read_query(
            """
            SELECT id, title, content, library_id, created_at, updated_at, metadata FROM
            documents
            """,
        )

        return [self.to_entity(row) for row in rows]

    async def update(self, entity: Document) -> Document | None:
        changes = await self.db.write_query(
            """
            UPDATE documents
               SET title = ?,
               content = ?,
               library_id = ?,
               updated_at = ?,
               metadata = ?
             WHERE documents.id = ?;
            """,
            (
                entity.title,
                entity.content,
                str(entity.library_id),
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
            "DELETE FROM documents WHERE id = ?", (str(id),)
        )
        return changes

    async def create_transactional(self, entity: Document, db=None) -> Document:
        """Create a document within an existing transaction."""
        target_db = db or self.db
        await target_db.execute_in_transaction(
            """
            INSERT INTO documents (id, title, content, library_id, created_at,
            updated_at, metadata) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(entity.id),
                entity.title,
                entity.content,
                str(entity.library_id),
                entity.created_at.timestamp(),
                entity.updated_at.timestamp() if entity.updated_at else None,
                json.dumps(entity.metadata) if entity.metadata else None,
            ),
        )
        return entity

    async def delete_transactional(self, id: UUID, db=None) -> int:
        """Delete a document within an existing transaction."""
        target_db = db or self.db
        changes = await target_db.execute_in_transaction(
            "DELETE FROM documents WHERE id = ?", (str(id),)
        )
        return changes
