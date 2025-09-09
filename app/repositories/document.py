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

    def create(self, entity: Document) -> Document:
        self.db.conn.execute(
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

    def find_by_library(self, id: UUID) -> list[Document]:
        rows = self.db.conn.execute(
            """
            SELECT id, title, content, library_id, created_at, updated_at, metadata FROM
            documents WHERE library_id = ?
            """,
            (str(id),),
        ).fetchall()
        return [self.to_entity(row) for row in rows]

    def find(self, id: UUID) -> Document | None:
        row = self.db.conn.execute(
            """
            SELECT id, title, content, library_id, created_at, updated_at, metadata FROM
            documents WHERE id = ?
            """,
            (str(id),),
        ).fetchone()

        if not row:
            return None

        return self.to_entity(row)

    def find_all(self) -> Sequence[Document]:
        cursor = self.db.conn.execute(
            """
            SELECT id, title, content, library_id, created_at, updated_at, metadata FROM
            documents
            """,
        )

        return [self.to_entity(row) for row in cursor.fetchall()]

    def update(self, entity: Document) -> Document | None:

        res = self.db.conn.execute(
            """
            UPDATE documents
               SET title = ?,
               content = ?,
               library_id = ?,
               created_at = ?,
               updated_at = ?,
               metadata = ?
             WHERE documents.id = ?;
            """,
            (
                entity.title,
                entity.content,
                str(entity.library_id),
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
        cursor = self.db.conn.execute("DELETE FROM documents WHERE id = ?", (str(id),))
        return cursor.rowcount
