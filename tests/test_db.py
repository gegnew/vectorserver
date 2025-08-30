import sqlite3
from pathlib import Path

import pytest

from app.db import VectorDB
from app.models.chunk import Chunk
from app.models.document import Document
from app.models.library import Library


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


class TestLibraryCrud:
    def test_db_creates_tables(self, vdb, sdb):
        res = sdb.execute(
            "SELECT name FROM sqlite_master WHERE type='table';"
        ).fetchall()
        assert ("libraries",) in res
        assert ("documents",) in res
        assert ("chunks",) in res
        assert len(res) == 3

    def test_create_library(self, vdb, sdb, test_library):
        # logic in test_library fixture
        assert test_library

    def test_get_library(self, vdb, test_library):
        lib = vdb.get_library(test_library.id)
        assert lib.name == "Test Library"

    def test_list_libraries(self, vdb, test_library):
        libs = vdb.list_libraries()
        assert libs[0].name == "Test Library"

    def test_delete_library(self, vdb):
        lib = vdb.create_library(Library(name="Test Delete Library"))
        pre_del_libs = vdb.list_libraries()

        assert "Test Delete Library" in [lb.name for lb in pre_del_libs]
        vdb.delete_library(lib.id)

        post_del_libs = vdb.list_libraries()
        assert "Test Delete Library" not in [lb.name for lb in post_del_libs]


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


class TestDocumentCrud:
    def test_create_document(self, vdb, sdb, test_document):
        assert test_document

    def test_get_document(self, vdb, test_document):
        doc = vdb.get_document(test_document.id)
        assert doc.title == "Test Document"

    def test_list_documents(self, vdb, test_document):
        docs = vdb.list_documents()
        assert docs[0].title == "Test Document"

    def test_delete_document(self, vdb, test_library):
        doc = vdb.create_document(
            Document(title="Test Delete Document", library_id=test_library.id)
        )
        pre_del_docs = vdb.list_documents()

        assert "Test Delete Document" in [doc.title for doc in pre_del_docs]
        vdb.delete_document(doc.id)

        post_del_docs = vdb.list_documents()
        assert "Test Delete Document" not in [doc.title for doc in post_del_docs]


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


class TestChunkCrud:
    def test_create_chunk(self, vdb, sdb, test_chunk):
        assert test_chunk

    def test_get_chunk(self, vdb, test_chunk):
        chunk = vdb.get_chunk(test_chunk.id)
        assert chunk.content == "Test chunk content"

    def test_list_chunks(self, vdb, test_chunk):
        chunks = vdb.list_chunks()
        assert chunks[0].content == "Test chunk content"

    def test_delete_chunk(self, vdb, test_document):
        chunk = vdb.create_chunk(
            Chunk(content="Test Delete chunk content", document_id=test_document.id)
        )
        pre_del_chunks = vdb.list_chunks()

        assert "Test Delete chunk content" in [
            chunk.content for chunk in pre_del_chunks
        ]
        vdb.delete_chunk(chunk.id)

        post_del_chunks = vdb.list_chunks()
        assert "Test Delete chunk content" not in [
            chunk.content for chunk in post_del_chunks
        ]
