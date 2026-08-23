"""
OxAlpha Cloud LLM Provider (via OpenRouter Gateway).

Interfaces with OpenRouter API for OxAlpha (stealth/ox-alpha) generation.
"""

import os
import json
import urllib.request
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

OXALPHA_API_KEY = os.getenv("OXALPHA_API_KEY", "")


class OxAlphaProvider:
    """Cloud OxAlpha API LLM Provider via OpenRouter Gateway."""

    def __init__(self, api_key: str = None, model: str = "stealth/ox-alpha"):
        self.api_key = api_key or os.getenv("OXALPHA_API_KEY", "")
        self.model = model
        self.endpoint = os.getenv("OXALPHA_ENDPOINT", "https://openrouter.ai/api/v1/chat/completions")

    def is_available(self) -> bool:
        """Returns True if OxAlpha API key is present."""
        return bool(self.api_key and len(self.api_key.strip()) > 10)

    def generate(self, prompt: str, system_instruction: Optional[str] = None) -> Dict[str, Any]:
        """Executes REST request to OxAlpha API via OpenRouter Gateway."""
        if not self.is_available():
            return {
                "success": False,
                "provider": "OxAlpha API",
                "error": "No OxAlpha API key supplied"
            }

        try:
            messages = []
            if system_instruction:
                messages.append({"role": "system", "content": system_instruction})
            messages.append({"role": "user", "content": prompt})

            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.2
            }

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "http://localhost:3000",
                "X-Title": "Enterprise Data Platform"
            }

            req = urllib.request.Request(
                self.endpoint,
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST"
            )

            with urllib.request.urlopen(req, timeout=12) as resp:
                res_body = json.loads(resp.read().decode("utf-8"))
                text_out = res_body["choices"][0]["message"]["content"]
                return {
                    "success": True,
                    "provider": "OxAlpha API (Cloud)",
                    "model": self.model,
                    "text": text_out.strip()
                }
        except Exception as e:
            logger.info("[OxAlphaProvider] Cloud call notice: %s. Using local fallback.", e)
            return {
                "success": False,
                "provider": "OxAlpha API",
                "error": f"OxAlpha API request notice: {str(e)}"
            }
