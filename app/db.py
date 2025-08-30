import sqlite3
from pathlib import Path

_TABLES = """
CREATE TABLE IF NOT EXISTS libraries (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    documents 
    metadata TEXT
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
            self.conn.cursor().executescript(_TABLES)
            self.conn.commit()
        except:
            self.conn.close()
            self.conn = None
            raise
