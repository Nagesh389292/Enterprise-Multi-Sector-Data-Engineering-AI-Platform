# ADR-006: Multi-Tier LLM Architecture (Gemini API + Ollama Local Fallback)

## Context & Problem Statement
The Enterprise AI Copilot requires natural language SQL synthesis and metric reasoning with resilience against API rate limits or network offline states.

## Decision Drivers
- High precision reasoning via cloud LLM (Google Gemini API).
- Guaranteed local offline execution capability without external API dependency.
- Cost control via intent routing.

## Decision Outcome
**Chosen Option: Multi-Tier Intent Router with Primary Gemini & Local Ollama / Mock Fallback**.
Queries are routed through `AgenticRouter`. If network latency or API key constraints prevent Gemini calls, the system gracefully falls back to local Ollama / rule-based SQL synthesis.
