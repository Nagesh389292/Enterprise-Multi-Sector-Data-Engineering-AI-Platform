"""
Multi-Tier LLM Provider Router & Fallback Factory.

Priority Order:
1. Gemini Cloud API (if GEMINI_API_KEY valid)
2. Ollama Local LLM (if Ollama daemon responsive)
3. Deterministic Analytics Engine Fallback (labeled explicitly as OFFLINE_DETERMINISTIC_FALLBACK)
"""

import os
from typing import Dict, Any, Optional
from ai.llm.gemini_provider import GeminiProvider
from ai.llm.ollama_provider import OllamaProvider


class LLMProviderFactory:
    """Tiered provider router executing Gemini -> Ollama -> Deterministic Fallback."""

    def __init__(self):
        self.gemini = GeminiProvider()
        self.ollama = OllamaProvider()

    def generate_response(self, prompt: str, system_instruction: Optional[str] = None, evidence_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Routes prompt to available LLM or generates explicit deterministic fallback."""
        
        # 1. Try Gemini Cloud
        if self.gemini.is_available():
            res = self.gemini.generate(prompt, system_instruction)
            if res.get("success"):
                return {
                    "provider": res["provider"],
                    "model": res["model"],
                    "status": "ONLINE_CLOUD",
                    "text": res["text"]
                }

        # 2. Try Local Ollama
        if self.ollama.is_available():
            res = self.ollama.generate(prompt, system_instruction)
            if res.get("success"):
                return {
                    "provider": res["provider"],
                    "model": res["model"],
                    "status": "ONLINE_LOCAL",
                    "text": res["text"]
                }

        # 3. Deterministic Analytics Synthesis Fallback
        return self._build_deterministic_fallback(prompt, evidence_context)

    def _build_deterministic_fallback(self, prompt: str, evidence: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Synthesizes factual output directly from evidence layer when LLM APIs are offline."""
        summary = "Enterprise Data Copilot Analysis: Query processed against live platform database metrics."

        if evidence:
            if "sql_results" in evidence:
                rows = evidence["sql_results"]
                summary = f"SQL Query Analysis: Retained {len(rows)} matching record(s) from database. Summary metrics: {json_compact(rows[:2])}"
            elif "ml_prediction" in evidence:
                pred = evidence["ml_prediction"]
                summary = f"Transaction {pred.get('event_id', '')} scored with fraud probability {pred.get('fraud_probability', 0)*100:.1f}% (Risk Score: {pred.get('risk_score')}/100, Level: {pred.get('risk_level')}). Top reasons: {', '.join(pred.get('explanation_reasons', []))}"
            elif "rag_citations" in evidence:
                cites = evidence["rag_citations"]
                if cites:
                    summary = f"Knowledge Retrieval Policy Summary: Document '{cites[0]['source']}' (Section: '{cites[0]['section']}'): {cites[0]['relevant_passage']}"

        return {
            "provider": "Local Deterministic Analytics Engine",
            "model": "Rule-Based Synthesis Engine",
            "status": "OFFLINE_DETERMINISTIC_FALLBACK",
            "text": summary
        }


def json_compact(obj: Any) -> str:
    import json
    return json.dumps(obj)
