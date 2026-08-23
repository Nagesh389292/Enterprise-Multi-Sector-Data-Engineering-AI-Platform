"""
Gemini Cloud LLM Provider.

Interfaces with Google Gemini API for high-reasoning text generation.
"""

import os
import json
import urllib.request
from typing import Dict, Any, Optional

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")


class GeminiProvider:
    """Cloud Gemini API LLM Provider."""

    def __init__(self, api_key: str = None, model: str = "gemini-2.5-flash"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.model = model
        self.endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"

    def is_available(self) -> bool:
        """Returns True if API key is present."""
        return bool(self.api_key and len(self.api_key.strip()) > 10)

    def generate(self, prompt: str, system_instruction: Optional[str] = None) -> Dict[str, Any]:
        """Executes REST request to Gemini API."""
        if not self.is_available():
            return {
                "success": False,
                "provider": "Gemini API",
                "error": "No Gemini API key supplied"
            }

        try:
            payload = {
                "contents": [{"parts": [{"text": prompt}]}]
            }
            if system_instruction:
                payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}

            req = urllib.request.Request(
                self.endpoint,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )

            with urllib.request.urlopen(req, timeout=10) as resp:
                res_body = json.loads(resp.read().decode("utf-8"))
                text_out = res_body["candidates"][0]["content"]["parts"][0]["text"]
                return {
                    "success": True,
                    "provider": "Gemini API (Cloud)",
                    "model": self.model,
                    "text": text_out.strip()
                }
        except Exception as e:
            return {
                "success": False,
                "provider": "Gemini API",
                "error": f"Gemini API request failed: {str(e)}"
            }
