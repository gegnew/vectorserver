import json
from collections.abc import Sequence
from datetime import UTC, datetime
from uuid import UUID

from app.models.chunk import Chunk
from app.repositories.base import BaseRepository


class ChunkRepository(BaseRepository[Chunk]):
    def to_entity(self, row):
        return Chunk(
            id=UUID(row[0]),
            content=row[1],
            document_id=row[2],
            embedding=row[3],
            created_at=datetime.fromtimestamp(row[4], tz=UTC),
            updated_at=datetime.fromtimestamp(row[5], tz=UTC) if row[5] else None,
            metadata=row[6],
        )

    async def create(self, entity: Chunk) -> Chunk:
        await self.db.write_query(
            """
            INSERT INTO chunks (id, content, document_id, embedding,
            created_at, updated_at, metadata) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(entity.id),
                entity.content,
                str(entity.document_id),
                entity.embedding,
                entity.created_at.timestamp(),
                entity.updated_at.timestamp() if entity.updated_at else None,
                json.dumps(entity.metadata) if entity.metadata else None,
            ),
        )
        return entity

    async def find(self, id: UUID) -> Chunk | None:
        row = await self.db.read_one(
            """
            SELECT id, content, document_id, embedding, created_at, updated_at, metadata
            FROM chunks WHERE id = ?
            """,
            (str(id),),
        )

        if not row:
            return None

        return self.to_entity(row)

    async def find_all(self) -> Sequence[Chunk]:
        rows = await self.db.read_query(
            """
            SELECT id, content, document_id, embedding, created_at, updated_at, metadata
            FROM chunks
            """,
        )

        return [self.to_entity(row) for row in rows]

    async def update(self, entity: Chunk) -> Chunk | None:
        changes = await self.db.write_query(
            """
            UPDATE chunks
               SET content = ?,
               document_id = ?,
               embedding = ?,
               updated_at = ?,
               metadata = ?
             WHERE chunks.id = ?;
            """,
            (
                entity.content,
                str(entity.document_id),
                entity.embedding,
                datetime.now(UTC).timestamp(),
                json.dumps(entity.metadata) if entity.metadata else None,
                str(entity.id),
            ),
        )
        if changes != 1:
            raise KeyError(entity.id)

        return await self.find(entity.id)

    async def find_by_library(self, library_id: UUID) -> list[Chunk]:
        rows = await self.db.read_query(
            """
            SELECT c.id, c.content, c.document_id, c.embedding,
            c.created_at, c.updated_at, c.metadata
            FROM chunks c
            JOIN documents d ON c.document_id = d.id
            WHERE d.library_id = ?
            """,
            (str(library_id),),
        )
        return [self.to_entity(row) for row in rows]

    async def find_by_document(self, document_id: UUID) -> list[Chunk]:
        rows = await self.db.read_query(
            """
            SELECT id, content, document_id, embedding, created_at, updated_at, metadata
            FROM chunks WHERE document_id = ?
            """,
            (str(document_id),),
        )
        return [self.to_entity(row) for row in rows]

    async def delete(self, id: UUID) -> int:
        changes = await self.db.write_query(
            "DELETE FROM chunks WHERE id = ?", (str(id),)
        )
        return changes

    async def create_transactional(self, entity: Chunk, db=None) -> Chunk:
        \"\"\"Create a chunk within an existing transaction.\"\"\"
        target_db = db or self.db
        await target_db.execute_in_transaction(
            \"\"\"
            INSERT INTO chunks (id, content, document_id, embedding,
            created_at, updated_at, metadata) VALUES (?, ?, ?, ?, ?, ?, ?)
            \"\"\",
            (
                str(entity.id),
                entity.content,
                str(entity.document_id),
                entity.embedding,
                entity.created_at.timestamp(),
                entity.updated_at.timestamp() if entity.updated_at else None,
                json.dumps(entity.metadata) if entity.metadata else None,
            ),
        )
        return entity

    async def delete_transactional(self, id: UUID, db=None) -> int:
        \"\"\"Delete a chunk within an existing transaction.\"\"\"
        target_db = db or self.db
        changes = await target_db.execute_in_transaction(
            "DELETE FROM chunks WHERE id = ?", (str(id),)
        )
        return changes
