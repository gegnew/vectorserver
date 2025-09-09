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

    def create(self, entity: Chunk) -> Chunk:
        self.db.conn.execute(
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

    def find(self, id: UUID) -> Chunk | None:
        row = self.db.conn.execute(
            """
            SELECT id, content, document_id, embedding, created_at, updated_at, metadata
            FROM chunks WHERE id = ?
            """,
            (str(id),),
        ).fetchone()

        if not row:
            return None

        return self.to_entity(row)

    def find_all(self) -> Sequence[Chunk]:
        cursor = self.db.conn.execute(
            """
            SELECT id, content, document_id, embedding, created_at, updated_at, metadata
            FROM chunks
            """,
        )

        return [self.to_entity(row) for row in cursor.fetchall()]

    def update(self, entity: Chunk) -> Chunk | None:

        res = self.db.conn.execute(
            """
            UPDATE chunks
               SET content = ?,
               document_id = ?,
               embedding = ?,
               created_at = ?,
               updated_at = ?,
               metadata = ?
             WHERE chunks.id = ?;
            """,
            (
                entity.content,
                str(entity.document_id),
                entity.embedding,
                entity.created_at.timestamp(),
                datetime.now(UTC).timestamp(),
                json.dumps(entity.metadata) if entity.metadata else None,
                str(entity.id),
            ),
        )
        if res.rowcount != 1:
            raise KeyError(entity.id)

        return self.find(entity.id)

    def find_by_library(self, library_id: UUID) -> list[Chunk]:
        rows = self.db.conn.execute(
            """
            SELECT c.id, c.content, c.document_id, c.embedding,
            c.created_at, c.updated_at, c.metadata
            FROM chunks c
            JOIN documents d ON c.document_id = d.id
            WHERE d.library_id = ?
            """,
            (str(library_id),),
        ).fetchall()
        return [self.to_entity(row) for row in rows]

    def delete(self, id: UUID) -> int:
        cursor = self.db.conn.execute("DELETE FROM chunks WHERE id = ?", (str(id),))
        return cursor.rowcount
