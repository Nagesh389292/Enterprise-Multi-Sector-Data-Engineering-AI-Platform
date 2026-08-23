"""
Hugging Face Sentence Embeddings Engine.

Generates dense vector embeddings using local Hugging Face model
('sentence-transformers/all-MiniLM-L6-v2') with a deterministic vector fallback.
"""

import os
import hashlib
import numpy as np
from typing import List

hf_available = False
try:
    from sentence_transformers import SentenceTransformer
    hf_available = True
except ImportError:
    SentenceTransformer = None


class HuggingFaceEmbeddings:
    """Generates 384-dimensional dense vector embeddings for RAG retrieval."""

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.dimension = 384
        self.model = None

        if hf_available:
            try:
                # Load sentence transformer model locally
                self.model = SentenceTransformer(self.model_name)
            except Exception as e:
                print(f"[Embeddings] Could not load Hugging Face model '{model_name}': {e}. Using vector fallback.")
                self.model = None

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """Embeds a batch of text strings into (N, 384) normalized numpy matrix."""
        if not texts:
            return np.empty((0, self.dimension), dtype=np.float32)

        if self.model is not None:
            try:
                embeddings = self.model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
                return embeddings.astype(np.float32)
            except Exception as e:
                print(f"[Embeddings] Encoding error: {e}. Falling back to hash vectors.")

        # Fallback deterministic hashing embedding generator (384-d)
        embeddings = []
        for text in texts:
            vec = self._hash_text_to_vector(text)
            embeddings.append(vec)

        return np.array(embeddings, dtype=np.float32)

    def embed_query(self, query: str) -> np.ndarray:
        """Embeds a single query string into (1, 384) vector."""
        res = self.embed_texts([query])
        return res[0:1]

    def _hash_text_to_vector(self, text: str) -> np.ndarray:
        """Generates normalized 384-d pseudo-semantic vector from text word hashes."""
        vec = np.zeros(self.dimension, dtype=np.float32)
        words = text.lower().split()
        if not words:
            return vec

        for word in words:
            h = int(hashlib.md5(word.encode("utf-8")).hexdigest(), 16)
            idx = h % self.dimension
            val = ((h >> 16) % 1000) / 500.0 - 1.0
            vec[idx] += val

        norm = np.linalg.norm(vec)
        if norm > 1e-6:
            vec /= norm
        return vec
