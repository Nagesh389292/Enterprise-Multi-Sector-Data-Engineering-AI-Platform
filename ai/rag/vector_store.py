"""
FAISS Vector Store for Enterprise RAG Indexing.

Manages vector embeddings and document metadata persistence with top-K similarity search.
"""

import os
import json
import numpy as np
from typing import Dict, Any, List, Tuple

faiss_available = False
try:
    import faiss
    faiss_available = True
except ImportError:
    faiss = None

INDEX_DIR = os.path.join(os.getcwd(), "ai", "rag", "index_store")


class VectorStore:
    """FAISS vector store with numpy cosine similarity fallback."""

    def __init__(self, dimension: int = 384, index_dir: str = INDEX_DIR):
        self.dimension = dimension
        self.index_dir = index_dir
        os.makedirs(self.index_dir, exist_ok=True)

        self.faiss_index = None
        self.chunks_metadata = []
        self.vector_matrix = np.empty((0, self.dimension), dtype=np.float32)

        if faiss_available:
            # Inner Product (Cosine Similarity on normalized vectors)
            self.faiss_index = faiss.IndexFlatIP(self.dimension)

    def add_chunks(self, chunks: List[Dict[str, Any]], embeddings: np.ndarray):
        """Adds document chunks and corresponding embedding vectors to vector store."""
        if len(chunks) == 0 or len(embeddings) == 0:
            return

        if embeddings.shape[1] != self.dimension:
            raise ValueError(f"Embedding dimension mismatch: expected {self.dimension}, got {embeddings.shape[1]}")

        # Normalize vectors for cosine similarity
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1e-6
        normalized_embeds = (embeddings / norms).astype(np.float32)

        if faiss_available and self.faiss_index is not None:
            self.faiss_index.add(normalized_embeds)

        if self.vector_matrix.shape[0] == 0:
            self.vector_matrix = normalized_embeds
        else:
            self.vector_matrix = np.vstack([self.vector_matrix, normalized_embeds])

        self.chunks_metadata.extend(chunks)
        self.save_index()

    def search(self, query_vector: np.ndarray, top_k: int = 4) -> List[Tuple[Dict[str, Any], float]]:
        """Searches vector index for top-K most similar document chunks."""
        if len(self.chunks_metadata) == 0 or self.vector_matrix.shape[0] == 0:
            return []

        # Normalize query vector
        norm = np.linalg.norm(query_vector)
        if norm > 1e-6:
            query_vector = query_vector / norm
        query_vector = query_vector.astype(np.float32)

        if query_vector.ndim == 1:
            query_vector = query_vector.reshape(1, -1)

        k = min(top_k, len(self.chunks_metadata))

        if faiss_available and self.faiss_index is not None and self.faiss_index.ntotal > 0:
            scores, indices = self.faiss_index.search(query_vector, k)
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx >= 0 and idx < len(self.chunks_metadata):
                    results.append((self.chunks_metadata[idx], float(score)))
            return results

        # Numpy inner product fallback
        scores = np.dot(self.vector_matrix, query_vector.T).flatten()
        top_indices = np.argsort(scores)[::-1][:k]

        results = []
        for idx in top_indices:
            results.append((self.chunks_metadata[idx], float(scores[idx])))

        return results

    def save_index(self):
        """Persists metadata JSON and FAISS index to disk."""
        meta_path = os.path.join(self.index_dir, "chunks_metadata.json")
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(self.chunks_metadata, f, indent=2)

        if faiss_available and self.faiss_index is not None:
            index_path = os.path.join(self.index_dir, "faiss.index")
            try:
                faiss.write_index(self.faiss_index, index_path)
            except Exception as e:
                print(f"[VectorStore] Could not save FAISS index: {e}")

        # Save numpy vectors backup
        vec_path = os.path.join(self.index_dir, "vectors.npy")
        np.save(vec_path, self.vector_matrix)

    def load_index(self) -> bool:
        """Loads index and metadata from disk if available."""
        meta_path = os.path.join(self.index_dir, "chunks_metadata.json")
        vec_path = os.path.join(self.index_dir, "vectors.npy")

        if os.path.exists(meta_path) and os.path.exists(vec_path):
            try:
                with open(meta_path, "r", encoding="utf-8") as f:
                    self.chunks_metadata = json.load(f)

                self.vector_matrix = np.load(vec_path)

                index_path = os.path.join(self.index_dir, "faiss.index")
                if faiss_available and os.path.exists(index_path):
                    self.faiss_index = faiss.read_index(index_path)
                elif faiss_available:
                    self.faiss_index = faiss.IndexFlatIP(self.dimension)
                    if len(self.vector_matrix) > 0:
                        self.faiss_index.add(self.vector_matrix)

                return True
            except Exception as e:
                print(f"[VectorStore] Error loading index: {e}")

        return False
