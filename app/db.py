import json
import sqlite3
from pathlib import Path
from uuid import UUID
from datetime import datetime

from app.models.library import Library

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
    created_at INT NOT NULL,
    updated_at INT,
    library_id TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT,
    metadata TEXT,
    FOREIGN KEY (library_id) REFERENCES libraries(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS chunks (
    id TEXT PRIMARY KEY,
    created_at INT NOT NULL,
    updated_at INT,
    document_id TEXT NOT NULL,
    content TEXT NOT NULL,
    vector BLOB,
    metadata TEXT,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
);
"""


class VectorDB:
    def __init__(self, db_path: str = "data/vectordb.sqlite"):
        self.db_path = db_path

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
            INSERT INTO libraries (id, name, description, created_at, updated_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
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
            "SELECT id, name, description, created_at, updated_at, metadata FROM libraries WHERE id = ?",
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
            "SELECT id, name, description, created_at, updated_at, metadata FROM libraries"
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
