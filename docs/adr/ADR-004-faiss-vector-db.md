# ADR-004: Selection of FAISS for Enterprise RAG Vector Store

## Context & Problem Statement
The Enterprise AI Copilot requires fast semantic similarity search over structured metric catalogs, schema documentation, and operational logs.

## Decision Drivers
- High-performance L2 & Cosine vector indexing.
- In-memory execution with zero external cloud billing dependency.
- Seamless integration with Hugging Face sentence transformers.

## Decision Outcome
**Chosen Option: Local FAISS Vector Store (`faiss-cpu`)**.
FAISS enables microsecond vector similarity search without requiring cloud vector database subscriptions (Pinecone, Weaviate), keeping the platform fully self-contained and reproducible.
