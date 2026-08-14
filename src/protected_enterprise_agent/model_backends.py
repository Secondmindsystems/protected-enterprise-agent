from __future__ import annotations

import json
from dataclasses import dataclass
from urllib import error, request

from .models import ProviderUnavailable


@dataclass(frozen=True)
class OllamaModel:
    """Optional local model backend behind the existing protected dispatch boundary."""

    model: str = "gemma4:12b"
    base_url: str = "http://127.0.0.1:11434"
    timeout_seconds: float = 120.0
    backend_name: str = "ollama"

    @property
    def model_identifier(self) -> str:
        return self.model

    def __call__(self, prompt: str) -> str:
        payload = json.dumps({"model": self.model, "prompt": prompt, "stream": False}).encode("utf-8")
        http_request = request.Request(
            f"{self.base_url.rstrip('/')}/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with request.urlopen(http_request, timeout=self.timeout_seconds) as response:
                parsed = json.loads(response.read().decode("utf-8"))
        except (error.URLError, TimeoutError, json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise ProviderUnavailable("Ollama did not return a trustworthy response") from exc
        if not isinstance(parsed, dict) or not isinstance(parsed.get("response"), str) or not parsed["response"].strip():
            raise ProviderUnavailable("Ollama did not return a trustworthy response")
        return parsed["response"].strip()


def backend_identity(model: object) -> tuple[str, str]:
    backend = getattr(model, "backend_name", None)
    identifier = getattr(model, "model_identifier", None)
    if isinstance(backend, str) and backend:
        return backend, identifier if isinstance(identifier, str) and identifier else "unspecified"
    if getattr(model, "__name__", "") == "deterministic_model":
        return "deterministic", "protected-enterprise-agent"
    return "custom", "unspecified"
