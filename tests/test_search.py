from pathlib import Path

import pytest

from app.embeddings import Embedder
from app.models.document import Document
from app.models.library import Library
from app.utils.load_documents import load_documents_from_directory


@pytest.fixture
def docs_in_db(vdb):
    docs_dir = Path("tests/docs/")
    library = vdb.create_library(
        Library(
            name="Test Document Library",
            description="Library containing test documents for chunking and embedding",
            metadata={
                "source": "test_documents",
                "processed_by": "pytest",
            },
        )
    )

    documents = load_documents_from_directory(docs_dir)

    for doc_name, content in documents:
        doc = vdb.create_document(
            Document(
                title=doc_name,
                content=content,
                library_id=library.id,
                metadata={
                    "original_length": len(content),
                    "source_file": f"{doc_name}.txt",
                },
            )
        )

        chunks = vdb.process_and_store(doc)
        return chunks


class TestSearch:
    def test_search(self, vdb, docs_in_db):
        library = Library(name="Search Library")
        created_lib = vdb.create_library(library)

        document = Document(
            library_id=created_lib.id,
            title="Search Document",
            content="""
            like the north face of Mount Assiniboine and the Emperor Face of
            Mount Robson
            """,
        )

        created_doc = vdb.create_document(document)
        _, embedding, _ = Embedder().chunk_and_embed(created_doc.content)

        similar = vdb._search_similar(embedding)
        assert "Assiniboine" in similar[0].content
