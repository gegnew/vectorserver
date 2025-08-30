import sqlite3
from pathlib import Path

import pytest

from app.db import VectorDB
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


@pytest.fixture
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


class TestDB:
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

        assert "Test Delete Library" in [l.name for l in pre_del_libs]
        vdb.delete_library(lib.id)

        post_del_libs = vdb.list_libraries()
        assert "Test Delete Library" not in [l.name for l in post_del_libs]
