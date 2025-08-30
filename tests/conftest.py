import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.db import VectorDB
from app.main import app
from app.models.chunk import Chunk
from app.models.document import Document
from app.models.library import Library


@pytest.fixture
def client():
    client = TestClient(app)
    return client


@pytest.fixture(scope="session")
def vdb():
    db_file = Path("data/test.sqlite")
    db = VectorDB(db_path=str(db_file))
    yield db
    db_file.unlink()


@pytest.fixture(scope="session")
def sdb():
    conn = sqlite3.connect(
        "data/test.sqlite",
    )
    return conn


@pytest.fixture(scope="class")
def test_library(vdb, sdb):
    lib = Library(name="Test Library")
    lib = vdb.create_library(lib)
    res = sdb.execute("SELECT * from libraries;").fetchall()
    m = dict(
        zip(
            ["id", "name", "description", "metadata", "created_at", "updated_at"],
            res[0],
            strict=False,
        )
    )
    return Library(**m)


@pytest.fixture(scope="class")
def test_document(vdb, sdb, test_library):
    doc = Document(title="Test Document", library_id=test_library.id)
    doc = vdb.create_document(doc)
    res = sdb.execute("SELECT * from documents;").fetchall()
    m = dict(
        zip(
            [
                "id",
                "library_id",
                "title",
                "content",
                "metadata",
                "created_at",
                "updated_at",
            ],
            res[0],
            strict=False,
        )
    )
    return Document(**m)


@pytest.fixture(scope="class")
def test_chunk(vdb, sdb, test_document):
    chunk = Chunk(content="Test chunk content", document_id=test_document.id)
    chunk = vdb.create_chunk(chunk)
    res = sdb.execute("SELECT * from chunks;").fetchall()
    m = dict(
        zip(
            [
                "id",
                "document_id",
                "content",
                "embedding",
                "metadata",
                "created_at",
                "updated_at",
            ],
            res[0],
            strict=False,
        )
    )
    return Chunk(**m)
