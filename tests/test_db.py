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


class TestDB:
    def test_db_creates_tables(self, vdb, sdb):
        res = sdb.execute(
            "SELECT name FROM sqlite_master WHERE type='table';"
        ).fetchall()
        assert ("libraries",) in res
        assert ("documents",) in res
        assert ("chunks",) in res
        assert len(res) == 3

    def test_create_library(self, vdb, sdb):
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
        assert Library.model_validate(m)
