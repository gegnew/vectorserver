"""Persistent vector index implementations that can save/load from disk."""

import json
import logging
import pickle
from pathlib import Path
from typing import Any, Dict
from uuid import UUID

import numpy as np

from app.models.chunk import Chunk
from app.utils.flat_index import FlatIndex
from app.utils.ivf import IVF

logger = logging.getLogger(__name__)


class PersistentVectorIndex:
    """Base class for persistent vector indexes."""

    def __init__(self, storage_path: str):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def _get_index_file_path(self, library_id: UUID, index_type: str) -> Path:
        """Get the file path for storing an index."""
        return self.storage_path / f"{library_id}_{index_type}.pkl"

    def _get_metadata_file_path(self, library_id: UUID, index_type: str) -> Path:
        """Get the file path for storing index metadata."""
        return self.storage_path / f"{library_id}_{index_type}_metadata.json"

    def _save_index_data(self, library_id: UUID, index_type: str, data: Dict[str, Any]):
        """Save index data to disk."""
        try:
            index_file = self._get_index_file_path(library_id, index_type)
            metadata_file = self._get_metadata_file_path(library_id, index_type)

            # Save the main index data
            with open(index_file, 'wb') as f:
                pickle.dump(data, f)

            # Save metadata
            metadata = {
                'library_id': str(library_id),
                'index_type': index_type,
                'num_vectors': data.get('num_vectors', 0),
                'vector_dimension': data.get('vector_dimension', 0),
                'created_at': data.get('created_at'),
                'updated_at': data.get('updated_at')
            }
            
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)

            logger.info(f"Saved {index_type} index for library {library_id}")
        except Exception as e:
            logger.error(f"Failed to save index for library {library_id}: {str(e)}")
            raise

    def _load_index_data(self, library_id: UUID, index_type: str) -> Dict[str, Any] | None:
        """Load index data from disk."""
        try:
            index_file = self._get_index_file_path(library_id, index_type)
            
            if not index_file.exists():
                return None

            with open(index_file, 'rb') as f:
                data = pickle.load(f)
            
            logger.info(f"Loaded {index_type} index for library {library_id}")
            return data
        except Exception as e:
            logger.error(f"Failed to load index for library {library_id}: {str(e)}")
            return None

    def _delete_index_files(self, library_id: UUID, index_type: str):
        """Delete index files from disk."""
        try:
            index_file = self._get_index_file_path(library_id, index_type)
            metadata_file = self._get_metadata_file_path(library_id, index_type)
            
            if index_file.exists():
                index_file.unlink()
            if metadata_file.exists():
                metadata_file.unlink()
                
            logger.info(f"Deleted {index_type} index files for library {library_id}")
        except Exception as e:
            logger.error(f"Failed to delete index files for library {library_id}: {str(e)}")


class PersistentFlatIndex(PersistentVectorIndex):
    """Flat index with disk persistence."""

    def __init__(self, storage_path: str = "data/indexes"):
        super().__init__(storage_path)
        self.flat_index = FlatIndex()
        self._current_library_id = None
        self._chunks = []
        self._vectors = None
        self._chunk_to_index_map = {}

    def load_or_create_index(self, library_id: UUID, chunks: list[Chunk]):
        """Load existing index or create new one for the library."""
        self._current_library_id = library_id
        
        # Try to load existing index
        index_data = self._load_index_data(library_id, "flat")
        
        if index_data and self._is_index_valid(index_data, chunks):
            # Load existing index
            self._chunks = index_data['chunks']
            self._vectors = index_data['vectors']
            self._chunk_to_index_map = index_data['chunk_to_index_map']
            logger.info(f"Loaded existing flat index for library {library_id}")
        else:
            # Create new index
            self._build_index(chunks)
            self._save_current_index()
            logger.info(f"Created new flat index for library {library_id}")

    def _is_index_valid(self, index_data: Dict[str, Any], current_chunks: list[Chunk]) -> bool:
        """Check if the loaded index is still valid for the current chunks."""
        stored_chunk_ids = {chunk.id for chunk in index_data.get('chunks', [])}
        current_chunk_ids = {chunk.id for chunk in current_chunks}
        return stored_chunk_ids == current_chunk_ids

    def _build_index(self, chunks: list[Chunk]):
        """Build the index from chunks."""
        self._chunks = chunks
        if chunks:
            raw_vectors = self._chunks_to_vectors(chunks)
            self._vectors = self.flat_index.fit(raw_vectors)
            self._rebuild_index_map()

    def _save_current_index(self):
        """Save the current index state to disk."""
        if self._current_library_id:
            from datetime import datetime
            data = {
                'chunks': self._chunks,
                'vectors': self._vectors,
                'chunk_to_index_map': self._chunk_to_index_map,
                'num_vectors': len(self._chunks),
                'vector_dimension': self._vectors.shape[0] if self._vectors is not None else 0,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            self._save_index_data(self._current_library_id, "flat", data)

    def search_chunks(self, query_vector: np.ndarray, k: int = 5) -> list[Chunk]:
        """Search for similar chunks."""
        if self._vectors is None:
            return []
        
        indices = self.flat_index.search(query_vector, self._vectors, k=k)
        return [self._chunks[i] for i in indices if i < len(self._chunks)]

    def add_chunks(self, chunks: list[Chunk]):
        """Add new chunks to the index."""
        if not chunks:
            return
            
        start_index = len(self._chunks)
        self._chunks.extend(chunks)

        # Update mappings
        for i, chunk in enumerate(chunks):
            self._chunk_to_index_map[chunk.id] = start_index + i

        # Update vectors
        new_vectors = self._chunks_to_vectors(chunks)
        new_processed_vectors = self.flat_index.fit(new_vectors)
        
        if self._vectors is None:
            self._vectors = new_processed_vectors
        else:
            self._vectors = np.hstack([self._vectors, new_processed_vectors])

        # Save updated index
        self._save_current_index()

    def remove_chunks(self, chunk_ids: list[UUID]):
        """Remove chunks from the index."""
        if not chunk_ids:
            return
            
        chunk_ids_set = set(chunk_ids)
        
        # Remove chunks
        self._chunks = [c for c in self._chunks if c.id not in chunk_ids_set]
        
        # Rebuild vectors and mappings
        if self._chunks:
            raw_vectors = self._chunks_to_vectors(self._chunks)
            self._vectors = self.flat_index.fit(raw_vectors)
            self._rebuild_index_map()
        else:
            self._vectors = None
            self._chunk_to_index_map = {}

        # Save updated index
        self._save_current_index()

    def delete_index(self, library_id: UUID):
        """Delete the index for a library."""
        self._delete_index_files(library_id, "flat")
        if self._current_library_id == library_id:
            self._chunks = []
            self._vectors = None
            self._chunk_to_index_map = {}
            self._current_library_id = None

    def _chunks_to_vectors(self, chunks: list[Chunk]) -> np.ndarray:
        """Convert chunks to vector array."""
        return np.array([np.frombuffer(chunk.embedding) for chunk in chunks])

    def _rebuild_index_map(self):
        """Rebuild the chunk to index mapping."""
        self._chunk_to_index_map = {chunk.id: i for i, chunk in enumerate(self._chunks)}


class PersistentIVFIndex(PersistentVectorIndex):
    """IVF index with disk persistence."""

    def __init__(self, storage_path: str = "data/indexes", n_partitions: int = 16, max_iters: int = 32):
        super().__init__(storage_path)
        self.n_partitions = n_partitions
        self.max_iters = max_iters
        self.ivf = IVF(n_clusters=n_partitions, max_iters=max_iters)
        self._current_library_id = None
        self._chunks = []

    def load_or_create_index(self, library_id: UUID, chunks: list[Chunk]):
        """Load existing index or create new one for the library."""
        self._current_library_id = library_id
        
        # Try to load existing index
        index_data = self._load_index_data(library_id, "ivf")
        
        if index_data and self._is_index_valid(index_data, chunks):
            # Load existing index
            self._chunks = index_data['chunks']
            self.ivf = index_data['ivf_model']
            logger.info(f"Loaded existing IVF index for library {library_id}")
        else:
            # Create new index
            self._build_index(chunks)
            self._save_current_index()
            logger.info(f"Created new IVF index for library {library_id}")

    def _is_index_valid(self, index_data: Dict[str, Any], current_chunks: list[Chunk]) -> bool:
        """Check if the loaded index is still valid for the current chunks."""
        stored_chunk_ids = {chunk.id for chunk in index_data.get('chunks', [])}
        current_chunk_ids = {chunk.id for chunk in current_chunks}
        return stored_chunk_ids == current_chunk_ids

    def _build_index(self, chunks: list[Chunk]):
        """Build the index from chunks."""
        self._chunks = chunks
        if chunks:
            vectors = self._chunks_to_vectors(chunks)
            self.ivf.fit(vectors)
            self.ivf.create_index(vectors)

    def _save_current_index(self):
        """Save the current index state to disk."""
        if self._current_library_id:
            from datetime import datetime
            data = {
                'chunks': self._chunks,
                'ivf_model': self.ivf,
                'num_vectors': len(self._chunks),
                'vector_dimension': self._chunks[0].embedding.__len__() if self._chunks else 0,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            self._save_index_data(self._current_library_id, "ivf", data)

    def search_chunks(self, query_vector: np.ndarray, k: int = 5) -> list[Chunk]:
        """Search for similar chunks."""
        if not self._chunks:
            return []

        indices = self.ivf.search(query_vector)
        result_chunks = [self._chunks[i] for i in indices if i < len(self._chunks)]
        return result_chunks[:k]

    def add_chunks(self, chunks: list[Chunk]):
        """Add new chunks to the index."""
        if not chunks:
            return
            
        self._chunks.extend(chunks)
        # Rebuild index (IVF doesn't support incremental updates easily)
        self._build_index(self._chunks)
        self._save_current_index()

    def remove_chunks(self, chunk_ids: list[UUID]):
        """Remove chunks from the index."""
        if not chunk_ids:
            return
            
        chunk_ids_set = set(chunk_ids)
        self._chunks = [c for c in self._chunks if c.id not in chunk_ids_set]
        
        # Rebuild index
        if self._chunks:
            self._build_index(self._chunks)
        else:
            self.ivf = IVF(n_clusters=self.n_partitions, max_iters=self.max_iters)
        
        self._save_current_index()

    def delete_index(self, library_id: UUID):
        """Delete the index for a library."""
        self._delete_index_files(library_id, "ivf")
        if self._current_library_id == library_id:
            self._chunks = []
            self.ivf = IVF(n_clusters=self.n_partitions, max_iters=self.max_iters)
            self._current_library_id = None

    def _chunks_to_vectors(self, chunks: list[Chunk]) -> np.ndarray:
        """Convert chunks to vector array."""
        return np.array([np.frombuffer(chunk.embedding) for chunk in chunks])