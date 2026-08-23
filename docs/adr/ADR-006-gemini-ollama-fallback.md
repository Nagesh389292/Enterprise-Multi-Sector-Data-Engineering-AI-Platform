# ADR-006: Multi-Tier LLM Architecture (Gemini API + OxAlpha API Fallback)

## Context & Problem Statement
The platform requires a high-reasoning LLM engine for AI Copilot queries, Text-to-SQL generation, and RAG policy synthesis. Cloud API rate limits, timeouts, or network outages must not degrade platform availability.

## Decision Drivers
* High-reasoning cloud LLM capabilities (Gemini 2.5 Flash / OxAlpha)
* Resilient multi-tier fallback without external service daemon dependencies
* Security AST validation for SQL queries before database execution

## Considered Options
1. Direct single-provider API calls (vulnerable to API rate limits and downtime)
2. Multi-tier provider gateway with deterministic fallback

## Decision Outcome
**Chosen Option: Multi-Tier Intent Router with Primary Gemini API, Secondary OxAlpha API & Deterministic Rule Engine Fallback**.
Queries are routed through `AgenticRouter`. If network latency or API key constraints prevent Gemini calls, the system gracefully falls back to secondary OxAlpha API or deterministic rule-based SQL synthesis.
