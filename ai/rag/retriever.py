"""
Semantic Retriever for RAG Pipeline.

Interfaces query embedding with vector store search and metadata filtering.
"""

from typing import Dict, Any, List, Tuple, Optional
from ai.rag.embeddings import HuggingFaceEmbeddings
from ai.rag.vector_store import VectorStore


class RAGRetriever:
    """Retrieves top-K relevant document chunks with similarity score thresholding."""

    def __init__(self, embeddings: HuggingFaceEmbeddings, vector_store: VectorStore):
        self.embeddings = embeddings
        self.vector_store = vector_store

    def retrieve(self, query: str, top_k: int = 3, min_similarity: float = 0.15, document_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieves semantic chunks matching query, filtered by similarity threshold and optional document_type."""
        query_vector = self.embeddings.embed_query(query)
        search_results = self.vector_store.search(query_vector, top_k=top_k * 2)

        relevant_chunks = []
        for chunk, score in search_results:
            if score < min_similarity:
                continue

            if document_type and chunk.get("document_type") != document_type:
                continue

            chunk_copy = dict(chunk)
            chunk_copy["similarity_score"] = round(float(score), 4)
            relevant_chunks.append(chunk_copy)

            if len(relevant_chunks) >= top_k:
                break

        return relevant_chunks
