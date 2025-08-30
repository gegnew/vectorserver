import json
import sqlite3
from datetime import datetime
from pathlib import Path
from uuid import UUID

import numpy as np

from app.embeddings import Embedder
from app.models.chunk import Chunk
from app.models.document import Document
from app.models.library import Library
from app.settings import settings

_TABLES = """
CREATE TABLE IF NOT EXISTS libraries (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    metadata TEXT,
    created_at INT NOT NULL,
    updated_at INT
);

CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    library_id TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT,
    metadata TEXT,
    created_at INT NOT NULL,
    updated_at INT,
    FOREIGN KEY (library_id) REFERENCES libraries(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS chunks (
    id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL,
    content TEXT NOT NULL,
    embedding BLOB,
    metadata TEXT,
    created_at INT NOT NULL,
    updated_at INT,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
);
"""


class VectorDB:
    def __init__(self, db_path: str = "data/vectordb.sqlite"):
        self.db_path = db_path
        self.embedder = Embedder()

        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

        self.conn: sqlite3.Connection | None = sqlite3.connect(
            self.db_path,
            isolation_level=None,
            check_same_thread=False,
        )

        try:
            self.conn.cursor().execute(
                "PRAGMA foreign_keys = ON"
            )  # necessary for each connection
            self.conn.cursor().executescript(_TABLES)
            self.conn.commit()
        except:
            self.conn.close()
            self.conn = None
            raise

    def create_library(self, library: Library) -> Library:
        self.conn.execute(
            """
            INSERT INTO libraries (id, name, description, created_at,
            updated_at, metadata) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                str(library.id),
                library.name,
                library.description,
                library.created_at.timestamp(),
                library.updated_at.timestamp() if library.updated_at else None,
                json.dumps(library.metadata),
            ),
        )

        return library

    def get_library(self, library_id: UUID) -> Library | None:
        row = self.conn.execute(
            """
            SELECT id, name, description, created_at, updated_at, metadata FROM
            libraries WHERE id = ?
            """,
            (str(library_id),),
        ).fetchone()

        if not row:
            return None

        return Library(
            id=UUID(row[0]),
            name=row[1],
            description=row[2],
            created_at=datetime.fromtimestamp(row[3]),
            updated_at=datetime.fromtimestamp(row[4]) if row[4] else None,
            metadata=row[5],
        )

    def list_libraries(self) -> list[Library]:
        cursor = self.conn.execute(
            """
            SELECT id, name, description, created_at, updated_at, metadata FROM
            libraries
            """,
        )

        libraries = []
        for row in cursor.fetchall():
            libraries.append(
                Library(
                    id=UUID(row[0]),
                    name=row[1],
                    description=row[2],
                    created_at=datetime.fromtimestamp(row[3]),
                    updated_at=datetime.fromtimestamp(row[4]) if row[4] else None,
                    metadata=row[5],
                )
            )

        return libraries

    def delete_library(self, library_id: UUID) -> bool:
        cursor = self.conn.execute(
            "DELETE FROM libraries WHERE id = ?", (str(library_id),)
        )
        deleted = cursor.rowcount > 0

        return deleted

    def create_document(self, document: Document) -> Document:
        self.conn.execute(
            """
            INSERT INTO documents (id, title, content, library_id, created_at,
            updated_at, metadata) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(document.id),
                document.title,
                document.content,
                str(document.library_id),
                document.created_at.timestamp(),
                document.updated_at.timestamp() if document.updated_at else None,
                json.dumps(document.metadata) if document.metadata else None,
            ),
        )

        return document

    def get_document(self, document_id: UUID) -> Document | None:
        row = self.conn.execute(
            """
            SELECT id, title, content, library_id, created_at, updated_at,
            metadata FROM documents WHERE id = ?
            """,
            (str(document_id),),
        ).fetchone()

        if not row:
            return None

        return Document(
            id=UUID(row[0]),
            title=row[1],
            content=row[2],
            library_id=UUID(row[3]),
            created_at=datetime.fromtimestamp(row[4]),
            updated_at=datetime.fromtimestamp(row[5]) if row[5] else None,
            metadata=json.loads(row[6]) if row[6] else None,
        )

    def list_documents(self) -> list[Document]:
        cursor = self.conn.execute(
            """
            SELECT id, title, content, library_id, created_at, updated_at,
            metadata FROM documents
            """,
        )

        documents = []
        for row in cursor.fetchall():
            documents.append(
                Document(
                    id=UUID(row[0]),
                    title=row[1],
                    content=row[2],
                    library_id=UUID(row[3]),
                    created_at=datetime.fromtimestamp(row[4]),
                    updated_at=datetime.fromtimestamp(row[5]) if row[5] else None,
                    metadata=json.loads(row[6]) if row[6] else None,
                )
            )

        return documents

    def delete_document(self, document_id: UUID) -> bool:
        cursor = self.conn.execute(
            "DELETE FROM documents WHERE id = ?", (str(document_id),)
        )
        deleted = cursor.rowcount > 0

        return deleted

    def create_chunk(self, chunk: Chunk) -> Chunk:
        self.conn.execute(
            """
            INSERT INTO chunks (id, content, document_id, created_at,
            updated_at, embedding, metadata) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(chunk.id),
                chunk.content,
                str(chunk.document_id),
                chunk.created_at.timestamp(),
                chunk.updated_at.timestamp() if chunk.updated_at else None,
                chunk.embedding,
                json.dumps(chunk.metadata) if chunk.metadata else None,
            ),
        )

        return chunk

    def get_chunk(self, chunk_id: UUID) -> Chunk | None:
        row = self.conn.execute(
            """
            SELECT id, content, document_id, created_at, updated_at, embedding,
            metadata FROM chunks WHERE id = ?
            """,
            (str(chunk_id),),
        ).fetchone()

        if not row:
            return None

        return Chunk(
            id=UUID(row[0]),
            content=row[1],
            document_id=UUID(row[2]),
            created_at=datetime.fromtimestamp(row[3]),
            updated_at=datetime.fromtimestamp(row[4]) if row[4] else None,
            embedding=row[5],
            metadata=json.loads(row[6]) if row[6] else None,
        )

    def get_chunks(self, document_id: UUID | None = None) -> list[Chunk] | None:
        sql = """
        SELECT id, content, document_id, created_at, updated_at, embedding,
        metadata FROM chunks
        """
        params = []
        if document_id:
            sql += " WHERE document_id = ?"
            params += [document_id]
        res = self.conn.execute(sql, params).fetchall()

        return [
            Chunk(
                id=UUID(row[0]),
                content=row[1],
                document_id=UUID(row[2]),
                created_at=datetime.fromtimestamp(row[3]),
                updated_at=datetime.fromtimestamp(row[4]) if row[4] else None,
                embedding=row[5],
                metadata=json.loads(row[6]) if row[6] else None,
            )
            for row in res
        ]

    def list_chunks(self) -> list[Chunk]:
        cursor = self.conn.execute(
            """
            SELECT id, content, document_id, created_at, updated_at, embedding,
            metadata FROM chunks
            """,
        )

        chunks = []
        for row in cursor.fetchall():
            chunks.append(
                Chunk(
                    id=UUID(row[0]),
                    content=row[1],
                    document_id=UUID(row[2]),
                    created_at=datetime.fromtimestamp(row[3]),
                    updated_at=datetime.fromtimestamp(row[4]) if row[4] else None,
                    embedding=row[5],
                    metadata=json.loads(row[6]) if row[6] else None,
                )
            )

        return chunks

    def delete_chunk(self, chunk_id: UUID) -> bool:
        cursor = self.conn.execute("DELETE FROM chunks WHERE id = ?", (str(chunk_id),))
        deleted = cursor.rowcount > 0

        return deleted

    def process_and_store(self, document: Document):
        chunks, embeddings, chunk_lens = self.embedder.chunk_and_embed(document.content)

        for j, (chunk, embedding, chunk_len) in enumerate(
            zip(chunks, embeddings, chunk_lens, strict=False)
        ):

            embedding_bytes = embedding.tobytes()

            chunk = Chunk(
                content=chunk,
                document_id=document.id,
                embedding=embedding_bytes,
                metadata={
                    "chunk_number": j,
                    "total_chunks": len(chunks),
                    "character_count": chunk_len,
                    "embedding_model": self.embedder.model,
                    "embedding_dimension": len(embedding),
                    "dtype": str(embedding.dtype),
                },
            )

            chunk = self.create_chunk(chunk)

    def _flat_index(self, search_vector: list[float]):
        np.array(search_vector).reshape(1, -1)
        chunks = self.get_chunks()
        vectors = np.array([np.frombuffer(chunk.embedding) for chunk in chunks]).T

        similarities, indices = self.embedder.cosine_similarity(search_vector, vectors)

        return list(np.array(chunks)[indices])

    def search_similar(self, content: str, name: str = "Search"):
        library = self.create_library(Library(name=name))

        document = Document(
            library_id=library.id,
            title=name,
            content=content,
        )

        created_doc = self.create_document(document)
        _, embedding, _ = Embedder().chunk_and_embed(created_doc.content)
        chunk = self._flat_index(embedding)[0]
        document = self.get_document(chunk.document_id)
        return document


def get_db():
    return VectorDB(settings.db_path)
