from pathlib import Path
from uuid import uuid4

import numpy as np
import pytest

from app.models.chunk import Chunk
from app.models.library import Library
from app.repositories.db import DB
from app.services.library_service import LibraryService

from app.services.vector_index_service import VectorIndexService
from app.settings import settings
from app.utils.load_documents import load_documents_from_directory

from tests.conftest import create_test_chunk

# TODO: move this to conftest
settings.db_path = "data/test.sqlite"


@pytest.fixture(scope="class", autouse=True)
def test_db():
    db_file = Path("data/test.sqlite")
    db = DB(db_path=str(db_file))
    yield db
    db_file.unlink()


class TestLibraryService:
    def test_create_library(self):
        service = LibraryService()

        docs_dir = Path("tests/docs/")
        library = service.create(
            Library(
                name="Test Document Library",
                description="""
                    Library containing test documents for chunking and embedding
                    """,
                metadata={
                    "source": "test_documents",
                    "processed_by": "pytest",
                },
            )
        )

        documents = load_documents_from_directory(docs_dir)

        for doc_name, content in documents:
            service.add_document(
                title=doc_name,
                content=content,
                library_id=library.id,
                metadata={
                    "original_length": len(content),
                    "source_file": f"{doc_name}.txt",
                },
            )

        documents = service.get_docs(library.id)
        chunks = service.chunks.find_by_library(library.id)
        assert len(documents) == 2
        assert documents[0].title == "machine_learning"
        assert len(chunks) == 29  # obviously not a great test
        assert type(chunks[0].embedding) is bytes
        assert chunks[0].metadata == {
            "chunk_number": 0,
            "total_chunks": 12,
            "character_count": 499,
            "embedding_model": "embed-v4.0",
            "embedding_dimension": 1024,
            "dtype": "float64",
        }
        assert chunks[1].metadata["chunk_number"] == 1

    def test_search_similar(self, service_with_documents):
        lib = service_with_documents.find_all()[-1]

        similar = service_with_documents.search(
            search_str="""
            like the north face of Mount Assiniboine and the Emperor Face of
            Mount Robson
            """,
            id=lib.id,
        )

        assert "Assiniboine" in similar.content

    def test_create_ivf_index(self, service_with_documents):
        service_with_documents.find_all()[-1]

        search_str = """
        like the north face of Mount Assiniboine and the Emperor Face of
        Mount Robson
        """

        service_with_documents.index(search_str)


class TestVectorIndexService:
    def test_service_with_flat_repository(self):
        service = VectorIndexService(index_type="flat")
        chunks = [create_test_chunk(i) for i in range(10)]

        service.fit(chunks)
        query = np.random.random(128).astype(np.float32)
        results = service.search(query, k=5)

        assert len(results) == 5
        assert all(isinstance(chunk, Chunk) for chunk in results)

    def test_operations(self):
        service = VectorIndexService(index_type="flat")
        initial_chunks = [create_test_chunk(i) for i in range(5)]

        # Fit initial chunks
        service.fit(initial_chunks)

        # Add chunks
        new_chunks = [create_test_chunk(i + 5) for i in range(3)]
        service.add_chunks(new_chunks)

        # Remove chunks
        chunk_ids_to_remove = [initial_chunks[0].id]
        service.remove_chunks(chunk_ids_to_remove)

        query = np.random.random(128).astype(np.float32)
        results = service.search(query, k=10)
        result_ids = [chunk.id for chunk in results]

        assert initial_chunks[0].id not in result_ids
        assert len(results) == 7  # 5 + 3 - 1
