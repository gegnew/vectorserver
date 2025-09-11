from pathlib import Path
from uuid import uuid4

import numpy as np
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.chunk import Chunk
from app.models.library import Library
from app.services.library_service import LibraryService
from app.utils.load_documents import load_documents_from_directory


@pytest.fixture
def client():
    client = TestClient(app)
    return client


@pytest.fixture(scope="class")
def service_with_documents():
    """Add documents to the database for testing.

    Spins up and down for each class; this is a bit slow, but we can optimize it later.
    """
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
    return service


def create_test_chunk(i: int, embedding_dim: int = 128) -> Chunk:
    embedding = np.random.random(embedding_dim)
    return Chunk(
        id=uuid4(),
        content=f"test content {i}",
        document_id=uuid4(),
        embedding=embedding.tobytes(),
    )
