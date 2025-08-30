import json
import sqlite3
from pathlib import Path

from app.models.library import Library

_TABLES = """
CREATE TABLE IF NOT EXISTS libraries (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    metadata TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT
);

CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    updated_at TEXT,
    library_id TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT,
    metadata TEXT,
    FOREIGN KEY (library_id) REFERENCES libraries(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS chunks (
    id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    updated_at TEXT,
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
