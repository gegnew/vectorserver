from pathlib import Path

import pytest

from app.services.library_service import LibraryService
from app.models.library import Library
from app.repositories.db import DB

# TODO: move this to conftest
from app.settings import settings
from app.utils.load_documents import load_documents_from_directory

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
