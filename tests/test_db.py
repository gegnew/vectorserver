import asyncio
import tempfile
from pathlib import Path

import pytest
import pytest_asyncio
from aiosqlite import IntegrityError

from app.repositories.db import DB


@pytest_asyncio.fixture
async def db():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    db = DB(db_path)
    await db.initialize()

    yield db

    await db.close()
    Path(db_path).unlink(missing_ok=True)


@pytest.mark.asyncio
async def test_db_initialization(db):
    assert db._initialized
    assert db.conn is not None


@pytest.mark.asyncio
async def test_read_query_empty_table(db):
    rows = await db.read_query("SELECT * FROM libraries")
    assert rows == []


@pytest.mark.asyncio
async def test_write_and_read_query(db):
    await db.write_query(
        "INSERT INTO libraries (id, name, description, created_at) VALUES (?, ?, ?, ?)",
        ("test-id", "Test Library", "A test library", 1234567890),
    )

    rows = await db.read_query("SELECT * FROM libraries")
    assert len(rows) == 1
    assert rows[0][0] == "test-id"
    assert rows[0][1] == "Test Library"


@pytest.mark.asyncio
async def test_read_one_query(db):
    await db.write_query(
        "INSERT INTO libraries (id, name, description, created_at) VALUES (?, ?, ?, ?)",
        ("test-id", "Test Library", "A test library", 1234567890),
    )

    row = await db.read_one("SELECT * FROM libraries WHERE id = ?", ("test-id",))
    assert row is not None
    assert row[0] == "test-id"
    assert row[1] == "Test Library"


@pytest.mark.asyncio
async def test_concurrent_reads():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    db = DB(db_path)
    await db.initialize()

    try:
        await db.write_query(
            """
            INSERT INTO libraries (id, name, description, created_at)
            VALUES (?, ?, ?, ?)
            """,
            ("test-id", "Test Library", "A test library", 1234567890),
        )

        # Perform concurrent reads
        async def read_task():
            return await db.read_query("SELECT * FROM libraries")

        # Run 10 concurrent read operations
        tasks = [read_task() for _ in range(10)]
        results = await asyncio.gather(*tasks)

        # should return the same data
        for result in results:
            assert len(result) == 1
            assert result[0][0] == "test-id"

    finally:
        await db.close()
        Path(db_path).unlink(missing_ok=True)


@pytest.mark.asyncio
async def test_sequential_writes():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    db = DB(db_path)
    await db.initialize()

    try:
        for i in range(5):
            await db.write_query(
                """
                INSERT INTO libraries (id, name, description, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (f"test-id-{i}", f"Test Library {i}", f"Library {i}", 1234567890 + i),
            )

        rows = await db.read_query("SELECT COUNT(*) FROM libraries")
        assert rows[0][0] == 5

        rows = await db.read_query("SELECT * FROM libraries ORDER BY id")
        assert len(rows) == 5
        for i, row in enumerate(rows):
            assert row[0] == f"test-id-{i}"
            assert row[1] == f"Test Library {i}"

    finally:
        await db.close()
        Path(db_path).unlink(missing_ok=True)


@pytest.mark.asyncio
async def test_foreign_key_constraints(db):
    await db.write_query(
        "INSERT INTO libraries (id, name, description, created_at) VALUES (?, ?, ?, ?)",
        ("lib-1", "Test Library", "A test library", 1234567890),
    )

    await db.write_query(
        """
        INSERT INTO documents (id, library_id, title, content, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        ("doc-1", "lib-1", "Test Doc", "Content", 1234567890),
    )

    rows = await db.read_query("SELECT * FROM documents")
    assert len(rows) == 1

    # try to insert a document with invalid foreign key
    with pytest.raises(IntegrityError):
        await db.write_query(
            """
            INSERT INTO documents (id, library_id, title, content, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            ("doc-2", "nonexistent-lib", "Test Doc 2", "Content", 1234567890),
        )


@pytest.mark.asyncio
async def test_db_close():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    db = DB(db_path)
    await db.initialize()

    assert db._initialized
    assert db.conn is not None

    await db.close()

    assert not db._initialized
    assert db.conn is None

    Path(db_path).unlink(missing_ok=True)
