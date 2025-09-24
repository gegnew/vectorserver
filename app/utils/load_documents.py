from pathlib import Path


def load_documents_from_directory(docs_dir: Path) -> list[tuple[str, str]]:
    """Load all .txt files from directory and return list of (filename, content) tuples."""
    documents = []

    for file_path in docs_dir.glob("*.txt"):
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
            documents.append((file_path.stem, content))

    return documents
