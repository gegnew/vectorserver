from pathlib import Path
from uuid import UUID

import pytest
from app.models.library import Library
from app.repositories.base import BaseRepository
from app.repositories.db import DB
from app.repositories.library import LibraryRepository


# TODO: move this to conftest
from app.settings import settings

settings.db_path = "data/test.sqlite"


@pytest.fixture(scope="class", autouse=True)
def test_db():
    db_file = Path("data/test.sqlite")
    db = DB(db_path=str(db_file))
    yield db
    db_file.unlink()


class TestLibraryRepository:
    def test_create(self, test_db):
        rep = LibraryRepository()
        test_lib = Library(name="test lib")
        lib = rep.create(test_lib)

        row = test_db.conn.execute(
            """
            SELECT id, name, description, created_at, updated_at, metadata FROM
            libraries WHERE id = ?
            """,
            (str(lib.id),),
        ).fetchone()
        assert (
            Library(
                id=row[0],
                name=row[1],
                description=row[2],
                created_at=row[3],
                updated_at=row[4],
                metadata=row[5],
            )
            == lib
        )
