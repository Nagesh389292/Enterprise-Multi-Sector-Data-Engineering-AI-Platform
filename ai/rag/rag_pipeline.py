"""
End-to-End RAG Knowledge & Policy QA Pipeline.

Orchestrates document loading, chunking, Hugging Face embedding, vector indexing,
retrieval, and source citation generation.
"""

from typing import Dict, Any, List
from ai.rag.document_loader import DocumentLoader
from ai.rag.chunker import DocumentChunker
from ai.rag.embeddings import HuggingFaceEmbeddings
from ai.rag.vector_store import VectorStore
from ai.rag.retriever import RAGRetriever


class RAGPipeline:
    """Enterprise RAG query engine providing evidence-backed answers with strict citations."""

    def __init__(self):
        self.loader = DocumentLoader()
        self.chunker = DocumentChunker()
        self.embeddings = HuggingFaceEmbeddings()
        self.vector_store = VectorStore()
        self.retriever = RAGRetriever(self.embeddings, self.vector_store)
        
        self._initialize_knowledge_base()

    def _initialize_knowledge_base(self):
        """Loads documents and builds vector store index if not already cached."""
        if not self.vector_store.load_index() or len(self.vector_store.chunks_metadata) == 0:
            raw_docs = self.loader.load_documents()
            chunks = self.chunker.chunk_documents(raw_docs)

            if len(chunks) > 0:
                texts = [c["content"] for c in chunks]
                embed_matrix = self.embeddings.embed_texts(texts)
                self.vector_store.add_chunks(chunks, embed_matrix)

    def query_knowledge_base(self, query: str, top_k: int = 3) -> Dict[str, Any]:
        """Executes RAG retrieval and formats context chunks into citations and synthesis context."""
        retrieved_chunks = self.retriever.retrieve(query, top_k=top_k)

        citations = []
        context_snippets = []

        for idx, chunk in enumerate(retrieved_chunks, 1):
            source = chunk.get("source", "Unknown Document")
            section = chunk.get("section", "General")
            title = chunk.get("title", source)
            content = chunk.get("content", "").strip()

            citation_entry = {
                "citation_id": f"[{idx}]",
                "source": source,
                "title": title,
                "section": section,
                "document_type": chunk.get("document_type", "enterprise_policy"),
                "similarity_score": chunk.get("similarity_score", 0.0),
                "relevant_passage": content[:250] + ("..." if len(content) > 250 else "")
            }
            citations.append(citation_entry)
            context_snippets.append(f"Source [{idx}] ({source} -> {section}):\n{content}")

        context_text = "\n\n".join(context_snippets) if context_snippets else "No relevant enterprise policy documents found."

        return {
            "query": query,
            "context_text": context_text,
            "citations": citations,
            "chunks_retrieved_count": len(retrieved_chunks),
            "has_relevant_context": len(retrieved_chunks) > 0
        }
