# VectorServer - Document Embedding and Retrieval System

A FastAPI-based vector database system for document chunking, embedding, and semantic search using Cohere's embedding models.

## Overview

VectorServer is a document processing and retrieval system that:

- Stores documents in a hierarchical structure (Libraries > Documents > Chunks)
- Automatically chunks long documents into semantically meaningful segments
- Generates vector embeddings using Cohere's embed-v4.0 model
- Provides semantic search capabilities across document collections
- Offers a RESTful API for document management and search

## Architecture

### Data Model

The system uses a three-tier hierarchical structure:

```
Library (Collection of related documents)
  > Document (Individual files/texts)
    > Chunk (Text segments with embeddings)
```

**Libraries**: Top-level collections for organizing documents by topic, project, or source
**Documents**: Individual text files or content with metadata
**Chunks**: Text segments (~500 characters) with vector embeddings for semantic search

### Technical Choices

**Database**: SQLite with foreign key constraints for data integrity

- Lightweight, serverless, perfect for development and testing
- BLOB storage for binary vector embeddings
- Automatic cascade deletion maintains referential integrity

**Embedding Model**: Cohere embed-v4.0 (1024 dimensions)

- State-of-the-art multilingual embeddings
- Optimized for search and retrieval tasks
- Consistent 1024-dimensional vectors for all content

**Chunking Strategy**: Intelligent text segmentation

- 500-character chunks
- 50-character overlap (NOT IMPLEMENTED)
- Smart boundary detection (sentences > words > characters) (NOT IMPLEMENTED)
- Preserves context across chunk boundaries

**Framework**: FastAPI + Pydantic

- Type safety with automatic validation
- OpenAPI documentation generation
- High performance async capabilities (largely unused by `VectorDB` class)

## Installation

### Prerequisites

- Python 3.11+
- Cohere API key

### Setup

1. **Clone the repository**

```bash
git clone <repository-url>
cd vectorserver
```

2. **Environment Configuration**
   Create a `.env` file:

```env
COHERE_API_KEY=your_cohere_api_key_here
DB_PATH=data/vectordb.sqlite
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
# or with uv (recommended)
uv sync
```

4. **Initialize Database**

```bash
# TODO: script to load data into the database
```

## Usage

### Running the API Server

#### Option 1: Run with Docker

```bash
 docker-compose up --build
```

#### Option 2: Run in local environment

```bash
# Development server with hot reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production server
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000` with interactive docs at `/docs`.

<!-- ### Processing Test Documents -->
<!-- Process the included test documents (Python guide, ML fundamentals, alpine climbing): -->
<!---->
<!-- ```bash -->
<!-- python tests/process_documents.py -->
<!-- ``` -->
<!---->
<!-- This script will: -->
<!---->
<!-- 1. Load all `.txt` files from `tests/docs/` -->
<!-- 2. Create a test library -->
<!-- 3. Chunk each document intelligently -->
<!-- 4. Generate embeddings via Cohere API -->
<!-- 5. Store everything in SQLite -->

### Running Tests

```bash
# Run all tests
pytest

# Run specific test modules
pytest tests/test_db.py -v
pytest tests/test_main.py -v
```

### API Examples

**Create a Library**

```bash
curl -X POST "http://localhost:8000/libraries/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Research Papers",
    "description": "Collection of ML research papers",
    "metadata": {"topic": "machine_learning"}
  }'
```

**Upload and Process Document**

```bash
curl -X POST "http://localhost:8000/libraries/{library_id}/documents/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Attention Is All You Need",
    "content": "The dominant sequence transduction models...",
    "metadata": {"authors": ["Vaswani", "Shazeer"], "year": 2017}
  }'
```

**Semantic Search**

```bash
curl -X GET "http://localhost:8000/search?query=transformer+architecture"
```

## Project Structure

```
vectorserver/
├── app/
│   ├── models/           # Pydantic models
│   │   ├── library.py
│   │   ├── document.py
│   │   └── chunk.py
│   ├── routes/           # API endpoints
│   │   └── libraries.py
│   ├── db.py            # Database operations
│   ├── embeddings.py    # Cohere embedding integration
│   ├── settings.py      # Configuration
│   └── main.py         # FastAPI app
├── tests/
│   ├── docs/           # Test documents
│   ├── test_db.py      # Database tests
│   └── process_documents.py  # Document processing script
├── data/               # SQLite database files
└── README.md
```

## Key Features

### Intelligent Chunking

- ~Respects sentence and word boundaries~
- ~Maintains context across segments~
- Metadata tracking for chunk relationships

### Vector Search

- Cosine similarity-based retrieval
- Configurable result count
- Cross-document search capabilities
- Embedding caching for performance

### Data Management

- Complete CRUD operations for all entities (NOT QUITE)
- Cascade deletion maintains data integrity
- JSON metadata storage for flexible schema
- Timestamp tracking for audit trails

### API Features

- RESTful design with OpenAPI documentation
- Type-safe request/response models
- Error handling with detailed messages
- Async support for high concurrency

## License

This project is licensed under the MIT License - see the LICENSE file for details.
