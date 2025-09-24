import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

import aiosqlite
from fastapi import Request

from app.settings import settings

logger = logging.getLogger(__name__)

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
        self.conn: aiosqlite.Connection | None = None
        self._read_semaphore = asyncio.Semaphore(10)  # 10 concurrent reads
        self._write_lock = asyncio.Lock()  # single writer
        self._initialized = False

    async def initialize(self):
        """Initialize the database connection and setup"""
        if self._initialized:
            return

        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        try:
            self.conn = await aiosqlite.connect(
                self.db_path,
                check_same_thread=False,
            )

            await self.conn.execute("PRAGMA foreign_keys = ON")
            await self.conn.execute("PRAGMA journal_mode = WAL")
            await self.conn.executescript(_TABLES)
            await self.conn.commit()

            self._initialized = True
        except Exception:
            if self.conn:
                await self.conn.close()
                self.conn = None
            raise

    async def read_query(self, query: str, params=None):
        if not self._initialized:
            await self.initialize()

        async with self._read_semaphore:
            async with self.conn.execute(query, params or []) as cursor:
                return await cursor.fetchall()

    async def read_one(self, query: str, params=None):
        if not self._initialized:
            await self.initialize()

        async with self._read_semaphore:
            async with self.conn.execute(query, params or []) as cursor:
                return await cursor.fetchone()

    async def write_query(self, query: str, params=None):
        if not self._initialized:
            await self.initialize()

        async with self._write_lock:
            cursor = await self.conn.execute(query, params or [])
            await self.conn.commit()
            return cursor.rowcount

    async def begin_transaction(self):
        """Begin a new transaction."""
        if not self._initialized:
            await self.initialize()

        await self.conn.execute("BEGIN TRANSACTION")

    async def commit_transaction(self):
        """Commit the current transaction."""
        await self.conn.commit()

    async def rollback_transaction(self):
        """Rollback the current transaction."""
        await self.conn.rollback()

    async def execute_in_transaction(self, query: str, params=None):
        """Execute a query within the current transaction without auto-commit."""
        if not self._initialized:
            await self.initialize()

        async with self._write_lock:
            cursor = await self.conn.execute(query, params or [])
            return cursor.rowcount

    @asynccontextmanager
    async def transaction(self):
        """Context manager for database transactions."""
        await self.begin_transaction()
        try:
            yield self
            await self.commit_transaction()
        except Exception as e:
            logger.error(f"Transaction failed, rolling back: {str(e)}")
            await self.rollback_transaction()
            raise

    async def close(self):
        if self.conn:
            await self.conn.close()
            self.conn = None
            self._initialized = False


async def create_db():
    """Create and initialize a new DB instance."""
    db = DB(settings.db_path)
    await db.initialize()
    return db


def get_db(request: Request):
    """FastAPI dependency to get the DB instance from app state."""
    return request.app.state.db
