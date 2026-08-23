"""
Ollama Local LLM Provider.

Interfaces with local Ollama REST daemon (http://localhost:11434/api/generate).
"""

import os
import json
import urllib.request
from typing import Dict, Any, Optional

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")


class OllamaProvider:
    """Local Ollama REST API Provider."""

    def __init__(self, base_url: str = None, model: str = None):
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = model or os.getenv("OLLAMA_MODEL", "llama3")
        self.endpoint = f"{self.base_url.rstrip('/')}/api/generate"

    def is_available(self) -> bool:
        """Pings local Ollama service to check daemon availability."""
        try:
            req = urllib.request.Request(f"{self.base_url.rstrip('/')}/api/tags", method="GET")
            with urllib.request.urlopen(req, timeout=2) as resp:
                return resp.status == 200
        except Exception:
            return False

    def generate(self, prompt: str, system_instruction: Optional[str] = None) -> Dict[str, Any]:
        """Executes generation request to local Ollama daemon."""
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
            if system_instruction:
                payload["system"] = system_instruction

            req = urllib.request.Request(
                self.endpoint,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )

            with urllib.request.urlopen(req, timeout=12) as resp:
                res_body = json.loads(resp.read().decode("utf-8"))
                text_out = res_body.get("response", "").strip()
                return {
                    "success": True,
                    "provider": "Ollama (Local LLM)",
                    "model": self.model,
                    "text": text_out
                }
        except Exception as e:
            return {
                "success": False,
                "provider": "Ollama (Local LLM)",
                "error": f"Ollama daemon error: {str(e)}"
            }
