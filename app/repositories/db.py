from pathlib import Path
import sqlite3

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


class DB:
    def __init__(self, db_path: str):
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


def get_db():
    return DB(settings.db_path)
