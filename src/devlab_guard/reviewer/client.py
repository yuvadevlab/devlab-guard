"""Asynchronous and synchronous HTTP client communicating with local Ollama inference server.

Module: devlab_guard.reviewer.client
"""

import httpx

from devlab_guard.core.config import DEFAULT_OLLAMA_MODEL, DEFAULT_OLLAMA_URL


class OllamaClient:
    """Lightweight HTTP client interfacing with local Ollama REST endpoints."""

    def __init__(self, base_url: str = DEFAULT_OLLAMA_URL, model: str = DEFAULT_OLLAMA_MODEL):
        self.base_url = base_url.rstrip("/")
        self.model = model

    def is_available(self) -> bool:
        """Pings local Ollama service to check reachability."""
        try:
            with httpx.Client(timeout=1.5) as client:
                res = client.get(f"{self.base_url}/api/tags")
                return res.status_code == 200
        except Exception:
            return False

    def generate_fix(self, prompt: str) -> str | None:
        """Submits prompt to Ollama and retrieves generated text response.

        Args:
            prompt: Formatted instruction prompt.

        Returns:
            Generated response string, or None if Ollama is unreachable.
        """
        try:
            with httpx.Client(timeout=30.0) as client:
                res = client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {"temperature": 0.1},
                    },
                )
                if res.status_code == 200:
                    return res.json().get("response")
        except Exception:
            return None
        return None
