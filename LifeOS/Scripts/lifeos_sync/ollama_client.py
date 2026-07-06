from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import requests


@dataclass(frozen=True)
class OllamaSettings:
    base_url: str
    model: str


def load_ollama_settings() -> OllamaSettings:
    return OllamaSettings(
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/"),
        model=os.getenv("OLLAMA_MODEL", "llama3.1"),
    )


def generate(prompt: str, settings: OllamaSettings | None = None) -> str:
    active = settings or load_ollama_settings()
    response = requests.post(
        f"{active.base_url}/api/generate",
        json={"model": active.model, "prompt": prompt, "stream": False},
        timeout=120,
    )
    response.raise_for_status()
    data: dict[str, Any] = response.json()
    return str(data.get("response", "")).strip()

