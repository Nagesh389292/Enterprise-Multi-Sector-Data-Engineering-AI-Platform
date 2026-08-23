"""
Unit Test Suite for Milestone 4: Enterprise AI Copilot + RAG + Agentic Analytics.
"""

import os
import unittest
from ai.rag.document_loader import DocumentLoader
from ai.rag.chunker import DocumentChunker
from ai.rag.embeddings import HuggingFaceEmbeddings
from ai.rag.vector_store import VectorStore
from ai.rag.retriever import RAGRetriever
from ai.rag.rag_pipeline import RAGPipeline

from ai.llm.gemini_provider import GeminiProvider
from ai.llm.oxalpha_provider import OxAlphaProvider
from ai.llm.ollama_provider import OllamaProvider
from ai.llm.provider_factory import LLMProviderFactory

from ai.agent.sql_tool import ReadOnlySQLTool
from ai.agent.ml_tool import MLModelTool
from ai.agent.metrics_tool import MetricsTool
from ai.agent.rag_tool import RAGKnowledgeTool
from ai.agent.router import AgenticRouter


class TestAICopilotRAG(unittest.TestCase):
    """Test suite for Enterprise RAG, LLM Providers, Security, and Agent Router."""

    def setUp(self):
        self.sql_tool = ReadOnlySQLTool()
        self.ml_tool = MLModelTool()
        self.metrics_tool = MetricsTool()
        self.rag_pipeline = RAGPipeline()
        self.router = AgenticRouter()

    def test_rag_document_loader_and_chunker(self):
        """Verifies loading knowledge base documents and recursive chunking."""
        loader = DocumentLoader()
        docs = loader.load_documents()
        self.assertGreater(len(docs), 0, "Should load enterprise knowledge documents")

        chunker = DocumentChunker(chunk_size=300, chunk_overlap=50)
        chunks = chunker.chunk_documents(docs)
        self.assertGreater(len(chunks), 0, "Should split documents into chunks")

        sample_chunk = chunks[0]
        self.assertIn("chunk_id", sample_chunk)
        self.assertIn("source", sample_chunk)
        self.assertIn("section", sample_chunk)
        self.assertIn("content", sample_chunk)

    def test_rag_embeddings_and_vector_store(self):
        """Verifies Hugging Face embedding generation and vector search."""
        embedder = HuggingFaceEmbeddings()
        vecs = embedder.embed_texts(["Fraud investigation policy", "Bed occupancy rate"])
        self.assertEqual(vecs.shape[1], 384, "Embeddings should be 384-dimensional")

        vstore = VectorStore(dimension=384)
        chunks = [{"chunk_id": "c1", "source": "s1", "title": "t1", "section": "sec", "document_type": "credit_cards", "content": "Unusual geographic location fraud", "ingestion_timestamp": "2026-01-01"}]
        vstore.add_chunks(chunks, vecs[0:1])

        results = vstore.search(vecs[0:1], top_k=1)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0]["chunk_id"], "c1")

    def test_rag_pipeline_retrieval_and_citations(self):
        """Verifies end-to-end RAG retrieval and citation output."""
        res = self.rag_pipeline.query_knowledge_base("What does policy say about unusual locations?", top_k=2)
        self.assertIn("citations", res)
        self.assertIn("context_text", res)
        self.assertTrue(res["has_relevant_context"])
        
        if len(res["citations"]) > 0:
            cite = res["citations"][0]
            self.assertIn("citation_id", cite)
            self.assertIn("source", cite)
            self.assertIn("relevant_passage", cite)

    def test_sql_tool_security_validation(self):
        """Verifies SQL tool permits SELECT and blocks mutation/injection attempts."""
        # Valid SELECT
        valid_sql = "SELECT event_id, amount, risk_level FROM credit_card_transactions WHERE amount > 1000"
        is_val, msg = self.sql_tool.validate_sql(valid_sql)
        self.assertTrue(is_val)

        # Prohibited DROP
        drop_sql = "DROP TABLE credit_card_transactions"
        is_val, msg = self.sql_tool.validate_sql(drop_sql)
        self.assertFalse(is_val)
        self.assertTrue(len(msg) > 0)

        # Prohibited DELETE inside query
        del_sql = "SELECT * FROM credit_card_transactions WHERE 1=1; DELETE FROM credit_card_transactions;"
        is_val, msg = self.sql_tool.validate_sql(del_sql)
        self.assertFalse(is_val)
        self.assertTrue(len(msg) > 0)

        # Multi-statement injection
        multi_sql = "SELECT * FROM credit_card_transactions; DROP TABLE users;"
        is_val, msg = self.sql_tool.validate_sql(multi_sql)
        self.assertFalse(is_val)

    def test_sql_tool_execution(self):
        """Verifies read-only query execution returns structured rows."""
        res = self.sql_tool.execute_query("SELECT event_id, amount, risk_level FROM credit_card_transactions WHERE risk_level = 'HIGH'")
        self.assertTrue(res["success"])
        self.assertIn("rows", res)
        self.assertGreater(len(res["rows"]), 0)

    def test_ml_model_tool(self):
        """Verifies ML tool registry query and transaction risk explanation."""
        reg_info = self.ml_tool.get_model_registry_info()
        self.assertIn("champion_model", reg_info)
        self.assertIn("champion_metrics", reg_info)

        expl = self.ml_tool.explain_transaction_risk("TXN-45728")
        self.assertEqual(expl["transaction_id"], "TXN-45728")
        self.assertIn("risk_score", expl)
        self.assertIn("explanation_reasons", expl)
        self.assertIn("shap_attributions", expl)

    def test_llm_provider_factory_fallback(self):
        """Verifies multi-tier LLM router fallback behavior."""
        factory = LLMProviderFactory()
        res = factory.generate_response("Summarize fraud rules", evidence_context={"summary_metrics": {"fraud_rate_pct": 11.8}})
        self.assertIn("provider", res)
        self.assertIn("text", res)
        self.assertIn("status", res)

    def test_oxalpha_provider_availability(self):
        """Verifies OxAlpha cloud provider initialization and availability logic."""
        prov = OxAlphaProvider(api_key="sk-8tcBjFKP4IcSVercwy9LpT4LbS2EX5SUyeOQIsgms5mdxnSD")
        self.assertTrue(prov.is_available())
        self.assertEqual(prov.model, "oxalpha-flash-v1")

    def test_agentic_router_intents(self):
        """Verifies intent classification and execution across all 4 intent modes."""
        # 1. ML Analysis
        res1 = self.router.process_query("Why was TXN-45728 flagged?")
        self.assertEqual(res1["intent"], "ML_ANALYSIS")
        self.assertIn("ml_prediction", res1["evidence_layer"])

        # 2. SQL Analytics
        res2 = self.router.process_query("What are today's top 10 high-risk merchants?")
        self.assertEqual(res2["intent"], "SQL_ANALYTICS")
        self.assertIn("sql_results", res2["evidence_layer"])

        # 3. RAG Knowledge
        res3 = self.router.process_query("What does the fraud investigation policy say about unusual locations?")
        self.assertEqual(res3["intent"], "RAG_KNOWLEDGE")
        self.assertGreater(len(res3["citations"]), 0)

        # 4. Hybrid Analysis
        res4 = self.router.process_query("Why did fraud increase?")
        self.assertEqual(res4["intent"], "HYBRID_ANALYSIS")
        self.assertGreater(len(res4["tools_executed"]), 1)


if __name__ == "__main__":
    unittest.main()
