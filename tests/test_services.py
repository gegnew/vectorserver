import tempfile
from pathlib import Path

import pytest
import pytest_asyncio

from app.models.library import Library
from app.repositories.db import DB
from app.services.library_service import LibraryService
from app.utils.load_documents import load_documents_from_directory


@pytest_asyncio.fixture(scope="class")
async def test_db():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    db = DB(db_path=db_path)
    await db.initialize()
    yield db
    await db.close()
    Path(db_path).unlink(missing_ok=True)


@pytest_asyncio.fixture
async def service(test_db):
    return LibraryService(test_db)


class TestLibraryService:
    @pytest.mark.asyncio
    async def test_create_library(self, service):
        docs_dir = Path("tests/docs/")
        library = await service.create_library(
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
            await service.add_document(
                title=doc_name,
                content=content,
                library_id=library.id,
                metadata={
                    "original_length": len(content),
                    "source_file": f"{doc_name}.txt",
                },
            )

        docs = await service.get_library_documents(library.id)
        assert len(docs) == len(documents)

    @pytest.mark.asyncio
    async def test_search_flat_index(self, service):
        docs_dir = Path("tests/docs/")
        library = await service.create_library(
            Library(
                name="Test Document Library",
                description="Library for testing flat index search",
                metadata={
                    "source": "test_documents",
                    "processed_by": "pytest",
                },
            )
        )

        documents = load_documents_from_directory(docs_dir)

        for doc_name, content in documents:
            await service.add_document(
                title=doc_name,
                content=content,
                library_id=library.id,
                metadata={
                    "original_length": len(content),
                    "source_file": f"{doc_name}.txt",
                },
            )

        result = await service.search(
            search_str="machine learning algorithms", id=library.id, index_type="flat"
        )

        assert result is not None

    @pytest.mark.asyncio
    async def test_create_ivf_index(self, service):
        docs_dir = Path("tests/docs/")
        library = await service.create_library(
            Library(
                name="Test Document Library for IVF",
                description="Library for testing IVF index",
                metadata={
                    "source": "test_documents",
                    "processed_by": "pytest",
                },
            )
        )

        documents = load_documents_from_directory(docs_dir)

        for doc_name, content in documents:
            await service.add_document(
                title=doc_name,
                content=content,
                library_id=library.id,
                metadata={
                    "original_length": len(content),
                    "source_file": f"{doc_name}.txt",
                },
            )

        result = await service.search(
            search_str="artificial intelligence", id=library.id, index_type="ivf"
        )

        assert result is not None
