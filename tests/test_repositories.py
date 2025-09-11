from pathlib import Path

import numpy as np
import pytest

from app.models.chunk import Chunk
from app.models.document import Document
from app.models.library import Library
from app.repositories.chunk import ChunkRepository
from app.repositories.db import DB
from app.repositories.document import DocumentRepository
from app.repositories.library import LibraryRepository

# TODO: move this to conftest
from app.repositories.vector_index import FlatIndexRepository, IVFIndexRepository
from app.settings import settings
from tests.conftest import create_test_chunk

settings.db_path = "data/test.sqlite"


@pytest.fixture(scope="class", autouse=True)
def test_db():
    db_file = Path("data/test.sqlite")
    db = DB(db_path=str(db_file))
    yield db
    db_file.unlink()


@pytest.fixture
def libs(test_db):
    return LibraryRepository(db=test_db)


@pytest.fixture
def docs(test_db):
    return DocumentRepository(db=test_db)


@pytest.fixture
def chunks(test_db):
    return ChunkRepository(db=test_db)


@pytest.fixture
def lib(libs):
    yield libs.create(Library(name="test lib"))


@pytest.fixture
def doc(lib, docs):
    yield docs.create(Document(title="Test Document", library_id=lib.id))


@pytest.fixture
def chunk(doc, chunks):
    yield chunks.create(
        Chunk(
            content="test chunk",
            embedding=np.random.random(10).tobytes(),
            document_id=doc.id,
        )
    )


class TestLibraryRepository:
    def test_create(self, libs, lib):
        in_db = libs.find(lib.id)
        assert in_db == lib

    def test_find_all(self, libs, lib):
        all_libs = libs.find_all()
        assert type(all_libs) is list
        assert type(all_libs[0]) is Library

    def test_update(self, libs, lib):
        lib = libs.find_all()[0]

        lib.name = "New test lib name"
        updated_lib = libs.update(lib)

        assert updated_lib.name == "New test lib name"
        is_in_db_lib = libs.find(lib.id)
        assert is_in_db_lib.name == "New test lib name"

    def test_delete(self, libs, lib):
        deleted = libs.delete(lib.id)
        assert deleted == 1

    def test_delete_cascade(self, libs, docs, chunks, lib, doc, chunk):
        # Given: Library with an associated Document and Chunk
        libs.find(lib.id)
        doc_in_db = docs.find(doc.id)
        chunk_in_db = chunks.find(chunk.id)
        assert doc_in_db.library_id == lib.id
        assert chunk_in_db.document_id == doc.id

        # When: the Library is deleted
        libs.delete(lib.id)

        # Then: the Document and Chunk should also be deleted
        assert docs.find(doc.id) is None
        assert chunks.find(chunk.id) is None


class TestDocumentRepository:
    def test_create(self, docs, doc):
        in_db = docs.find(doc.id)
        assert in_db == doc

    def test_find_all(self, docs, doc):
        docs = docs.find_all()
        assert type(docs) is list
        assert type(docs[0]) is Document

    def test_update(self, docs, doc):
        doc = docs.find_all()[0]

        doc.title = "New Test Doc"
        updated_doc = docs.update(doc)

        assert updated_doc.title == "New Test Doc"
        is_in_db_doc = docs.find(doc.id)
        assert is_in_db_doc.title == "New Test Doc"

    def test_delete(self, docs, doc):
        deleted = docs.delete(doc.id)
        assert deleted == 1


class TestChunkRepository:
    def test_create(self, chunks, chunk):
        in_db = chunks.find(chunk.id)
        assert in_db == chunk

    def test_find_all(self, chunks, chunk):
        all_chunks = chunks.find_all()
        assert type(all_chunks) is list
        assert type(all_chunks[0]) is Chunk

    def test_update(self, chunks, chunk):
        chunk = chunks.find_all()[0]

        chunk.content = "New Test Chunk"
        updated_chunk = chunks.update(chunk)

        assert updated_chunk.content == "New Test Chunk"
        is_in_db_chunk = chunks.find(chunk.id)
        assert is_in_db_chunk.content == "New Test Chunk"

    def test_delete(self, chunks, chunk):
        deleted = chunks.delete(chunk.id)
        assert deleted == 1


@pytest.fixture
def flat_index_repository():
    yield FlatIndexRepository()


class TestFlatIndexRepository:
    def test_fit_and_search_chunks(self, flat_index_repository):
        chunks = [create_test_chunk(i) for i in range(5)]

        flat_index_repository.fit_chunks(chunks)
        query = np.random.random(128)
        results = flat_index_repository.search_chunks(query, k=3)

        assert len(results) == 3
        assert all(isinstance(chunk, Chunk) for chunk in results)

    def test_empty_chunks(self, flat_index_repository):
        query = np.random.random(128)
        results = flat_index_repository.search_chunks(query, k=5)

        assert results == []

    def test_add_chunks(self, flat_index_repository):
        initial_chunks = [create_test_chunk(i) for i in range(5)]
        flat_index_repository.fit_chunks(initial_chunks)

        new_chunks = [create_test_chunk(i + 5) for i in range(3)]
        flat_index_repository.add_chunks(new_chunks)

        query = np.random.random(128)
        results = flat_index_repository.search_chunks(query, k=8)
        assert len(results) == 8

    def test_remove_chunks(self, flat_index_repository):
        chunks = [create_test_chunk(i) for i in range(10)]
        flat_index_repository.fit_chunks(chunks)

        chunk_ids_to_remove = [chunks[0].id, chunks[1].id]
        flat_index_repository.remove_chunks(chunk_ids_to_remove)

        query = np.random.random(128)
        results = flat_index_repository.search_chunks(query, k=10)
        result_ids = [chunk.id for chunk in results]

        for chunk_id in chunk_ids_to_remove:
            assert chunk_id not in result_ids
        assert len(results) == 8


class TestIVFIndexRepository:
    def test_fit_and_search(self):
        chunks = [create_test_chunk(i) for i in range(50)]
        repo = IVFIndexRepository(n_partitions=5)

        repo.fit_chunks(chunks)
        query = np.random.random(128)
        results = repo.search_chunks(query, k=10)

        assert len(results) <= 10
        assert all(isinstance(chunk, Chunk) for chunk in results)

    def test_chunk_crud(self):
        initial_chunks = [create_test_chunk(i) for i in range(20)]
        repo = IVFIndexRepository(n_partitions=3)
        repo.fit_chunks(initial_chunks)

        # add chunks
        new_chunks = [create_test_chunk(i + 20) for i in range(5)]
        repo.add_chunks(new_chunks)

        # remove chunks
        chunk_ids_to_remove = [initial_chunks[0].id]
        repo.remove_chunks(chunk_ids_to_remove)

        query = np.random.random(128)
        results = repo.search_chunks(query, k=25)
        result_ids = [chunk.id for chunk in results]

        assert initial_chunks[0].id not in result_ids
