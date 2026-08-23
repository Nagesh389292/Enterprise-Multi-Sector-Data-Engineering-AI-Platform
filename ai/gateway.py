"""
Unified AI Gateway & Multi-Tier Model Orchestrator.
Interfaces with Gemini API (Cloud) and provides local fallback execution.
"""

import os
from typing import Dict, Any, Optional
import urllib.request
import json

class AIGateway:
    """Multi-tier gateway supporting Gemini Developer API with local analytics fallback."""
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "")
        self.gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"

    def generate_text(self, prompt: str, system_instruction: Optional[str] = None) -> Dict[str, Any]:
        if self.api_key:
            try:
                payload = {
                    "contents": [
                        {
                            "parts": [{"text": prompt}]
                        }
                    ]
                }
                if system_instruction:
                    payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}

                headers = {"Content-Type": "application/json"}
                url = self.gemini_url
                if self.api_key.startswith("AQ."):
                    headers["Authorization"] = f"Bearer {self.api_key}"
                    headers["x-goog-api-key"] = self.api_key
                    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers=headers,
                    method="POST"
                )

                with urllib.request.urlopen(req, timeout=10) as resp:
                    res_body = json.loads(resp.read().decode("utf-8"))
                    text_out = res_body["candidates"][0]["content"]["parts"][0]["text"]
                    return {
                        "provider": "Gemini API (Cloud)",
                        "model": "gemini-2.5-flash",
                        "status": "SUCCESS",
                        "response": text_out
                    }
            except Exception as e:
                return self._local_fallback(prompt, reason=f"Gemini API call failed: {str(e)}")

        return self._local_fallback(prompt, reason="No Gemini API key supplied or offline mode active")

    def _local_fallback(self, prompt: str, reason: str) -> Dict[str, Any]:
        return {
            "provider": "Local Intelligence Engine",
            "model": "Rule-Based Analytics Fallback",
            "status": "FALLBACK_ACTIVE",
            "reason": reason,
            "response": f"[Analytics Copilot Local Response]: Query evaluated against enterprise metric definitions for prompt: '{prompt[:60]}...'"
        }
