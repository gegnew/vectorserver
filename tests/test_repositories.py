from pathlib import Path

import numpy as np
import pytest
import pytest_asyncio

from app.models.chunk import Chunk
from app.models.document import Document
from app.models.library import Library
from app.repositories.chunk import ChunkRepository
from app.repositories.db import DB
from app.repositories.document import DocumentRepository
from app.repositories.library import LibraryRepository
from app.repositories.vector_index import FlatIndexRepository, IVFIndexRepository
from tests.conftest import create_test_chunk


@pytest_asyncio.fixture(scope="class")
async def test_db():
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    db = DB(db_path=db_path)
    await db.initialize()
    yield db
    await db.close()
    Path(db_path).unlink(missing_ok=True)


@pytest_asyncio.fixture
async def libs(test_db):
    return LibraryRepository(db=test_db)


@pytest_asyncio.fixture
async def docs(test_db):
    return DocumentRepository(db=test_db)


@pytest_asyncio.fixture
async def chunks(test_db):
    return ChunkRepository(db=test_db)


@pytest_asyncio.fixture
async def lib(libs):
    lib = await libs.create(Library(name="test lib"))
    yield lib


@pytest_asyncio.fixture
async def doc(lib, docs):
    doc = await docs.create(Document(title="Test Document", library_id=lib.id))
    yield doc


@pytest_asyncio.fixture
async def chunk(doc, chunks):
    chunk = await chunks.create(
        Chunk(
            content="test chunk",
            embedding=np.random.random(10).tobytes(),
            document_id=doc.id,
        )
    )
    yield chunk


class TestLibraryRepository:
    @pytest.mark.asyncio
    async def test_create(self, libs, lib):
        in_db = await libs.find(lib.id)
        assert in_db == lib

    @pytest.mark.asyncio
    async def test_find_all(self, libs, lib):
        all_libs = await libs.find_all()
        assert type(all_libs) is list
        assert type(all_libs[0]) is Library

    @pytest.mark.asyncio
    async def test_update(self, libs, lib):
        all_libs = await libs.find_all()
        lib = all_libs[0]

        lib.name = "New test lib name"
        updated_lib = await libs.update(lib)

        assert updated_lib.name == "New test lib name"
        is_in_db_lib = await libs.find(lib.id)
        assert is_in_db_lib.name == "New test lib name"

    @pytest.mark.asyncio
    async def test_delete(self, libs, lib):
        deleted = await libs.delete(lib.id)
        assert deleted == 1

    @pytest.mark.asyncio
    async def test_delete_cascade(self, libs, docs, chunks, lib, doc, chunk):
        # Given: Library with an associated Document and Chunk
        await libs.find(lib.id)
        doc_in_db = await docs.find(doc.id)
        chunk_in_db = await chunks.find(chunk.id)
        assert doc_in_db.library_id == lib.id
        assert chunk_in_db.document_id == doc.id

        # When: the Library is deleted
        await libs.delete(lib.id)

        # Then: the Document and Chunk should also be deleted
        assert await docs.find(doc.id) is None
        assert await chunks.find(chunk.id) is None


class TestDocumentRepository:
    @pytest.mark.asyncio
    async def test_create(self, docs, doc):
        in_db = await docs.find(doc.id)
        assert in_db == doc

    @pytest.mark.asyncio
    async def test_find_all(self, docs, doc):
        all_docs = await docs.find_all()
        assert type(all_docs) is list
        assert type(all_docs[0]) is Document

    @pytest.mark.asyncio
    async def test_update(self, docs, doc):
        all_docs = await docs.find_all()
        doc = all_docs[0]

        doc.title = "New Test Doc"
        updated_doc = await docs.update(doc)

        assert updated_doc.title == "New Test Doc"
        is_in_db_doc = await docs.find(doc.id)
        assert is_in_db_doc.title == "New Test Doc"

    @pytest.mark.asyncio
    async def test_delete(self, docs, doc):
        deleted = await docs.delete(doc.id)
        assert deleted == 1


class TestChunkRepository:
    @pytest.mark.asyncio
    async def test_create(self, chunks, chunk):
        in_db = await chunks.find(chunk.id)
        assert in_db == chunk

    @pytest.mark.asyncio
    async def test_find_all(self, chunks, chunk):
        all_chunks = await chunks.find_all()
        assert type(all_chunks) is list
        assert type(all_chunks[0]) is Chunk

    @pytest.mark.asyncio
    async def test_update(self, chunks, chunk):
        all_chunks = await chunks.find_all()
        chunk = all_chunks[0]

        chunk.content = "New Test Chunk"
        updated_chunk = await chunks.update(chunk)

        assert updated_chunk.content == "New Test Chunk"
        is_in_db_chunk = await chunks.find(chunk.id)
        assert is_in_db_chunk.content == "New Test Chunk"

    @pytest.mark.asyncio
    async def test_delete(self, chunks, chunk):
        deleted = await chunks.delete(chunk.id)
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
