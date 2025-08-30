from app.models.chunk import Chunk
from app.models.document import Document
from app.models.library import Library
from pathlib import Path
from app.utils.load_documents import load_documents_from_directory


class TestLibraryCrud:
    def test_db_creates_tables(self, vdb, sdb):
        res = sdb.execute(
            "SELECT name FROM sqlite_master WHERE type='table';"
        ).fetchall()
        assert ("libraries",) in res
        assert ("documents",) in res
        assert ("chunks",) in res
        assert len(res) == 3

    def test_create_library(self, vdb, sdb, test_library):
        # logic in test_library fixture
        assert test_library

    def test_get_library(self, vdb, test_library):
        lib = vdb.get_library(test_library.id)
        assert lib.name == "Test Library"

    def test_list_libraries(self, vdb, test_library):
        libs = vdb.list_libraries()
        assert libs[0].name == "Test Library"

    def test_delete_library(self, vdb):
        lib = vdb.create_library(Library(name="Test Delete Library"))
        pre_del_libs = vdb.list_libraries()

        assert "Test Delete Library" in [lb.name for lb in pre_del_libs]
        vdb.delete_library(lib.id)

        post_del_libs = vdb.list_libraries()
        assert "Test Delete Library" not in [lb.name for lb in post_del_libs]


class TestDocumentCrud:
    def test_create_document(self, vdb, sdb, test_document):
        assert test_document

    def test_get_document(self, vdb, test_document):
        doc = vdb.get_document(test_document.id)
        assert doc.title == "Test Document"

    def test_list_documents(self, vdb, test_document):
        docs = vdb.list_documents()
        assert docs[0].title == "Test Document"

    def test_delete_document(self, vdb, test_library):
        doc = vdb.create_document(
            Document(title="Test Delete Document", library_id=test_library.id)
        )
        pre_del_docs = vdb.list_documents()

        assert "Test Delete Document" in [doc.title for doc in pre_del_docs]
        vdb.delete_document(doc.id)

        post_del_docs = vdb.list_documents()
        assert "Test Delete Document" not in [doc.title for doc in post_del_docs]


class TestChunkCrud:
    def test_create_chunk(self, vdb, sdb, test_chunk):
        assert test_chunk

    def test_get_chunk(self, vdb, test_chunk):
        chunk = vdb.get_chunk(test_chunk.id)
        assert chunk.content == "Test chunk content"

    def test_list_chunks(self, vdb, test_chunk):
        chunks = vdb.list_chunks()
        assert chunks[0].content == "Test chunk content"

    def test_delete_chunk(self, vdb, test_document):
        chunk = vdb.create_chunk(
            Chunk(content="Test Delete chunk content", document_id=test_document.id)
        )
        pre_del_chunks = vdb.list_chunks()

        assert "Test Delete chunk content" in [
            chunk.content for chunk in pre_del_chunks
        ]
        vdb.delete_chunk(chunk.id)

        post_del_chunks = vdb.list_chunks()
        assert "Test Delete chunk content" not in [
            chunk.content for chunk in post_del_chunks
        ]


class TestCreateEmbeddings:
    def test_create_embeddings(self, vdb):
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

        all_chunks = vdb.get_chunks()
        assert len(documents) == 2
        assert len(all_chunks) == 29  # obviously not a great test
