"""
RAG Knowledge Base Tool for Enterprise Copilot.

Queries domain manuals (fraud policies, banking, healthcare, insurance, retail, platform architecture)
and returns verifiable source citations.
"""

from typing import Dict, Any, List
from ai.rag.rag_pipeline import RAGPipeline


class RAGKnowledgeTool:
    """Tool retrieving policy, compliance, and architectural documentation with citations."""

    def __init__(self):
        self.rag_pipeline = RAGPipeline()

    def query_policy_knowledge(self, question: str, top_k: int = 3) -> Dict[str, Any]:
        """Queries vector index and returns text context with source document citations."""
        return self.rag_pipeline.query_knowledge_base(question, top_k=top_k)
