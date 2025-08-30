from pathlib import Path
import sqlite3
import shutil
import pytest

from app.db import VectorDB


@pytest.fixture
def db():
    db_file = Path("data/test.sqlite")
    db = VectorDB(db_path=str(db_file))
    yield db
    db_file.unlink()


class TestDB:
    def test_db_creates_tables(self, db):
        with sqlite3.connect("data/test.sqlite") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            res = cursor.fetchall()
            assert ("libraries",) in res
            assert ("documents",) in res
            assert ("chunks",) in res
            assert len(res) == 3
