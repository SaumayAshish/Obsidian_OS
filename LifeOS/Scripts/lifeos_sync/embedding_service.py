from __future__ import annotations

import hashlib
import math
import os
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class EmbeddingResult:
    model: str
    dimensions: int
    values: list[float]
    provider: str


class EmbeddingService:
    def embed(self, text: str) -> EmbeddingResult:
        raise NotImplementedError


class SentenceTransformerService(EmbeddingService):
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> None:
        from sentence_transformers import SentenceTransformer

        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

    def embed(self, text: str) -> EmbeddingResult:
        vector = self.model.encode(text, normalize_embeddings=True)
        values = [float(item) for item in vector.tolist()]
        return EmbeddingResult(self.model_name, len(values), values, "sentence-transformers")


class HashEmbeddingService(EmbeddingService):
    """Deterministic offline fallback. Useful for testing, not semantic-quality retrieval."""

    def __init__(self, dimensions: int = 384) -> None:
        self.dimensions = dimensions

    def embed(self, text: str) -> EmbeddingResult:
        values = [0.0] * self.dimensions
        for token in re.findall(r"[a-z0-9_-]{2,}", text.lower()):
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % self.dimensions
            values[index] += 1.0
        norm = math.sqrt(sum(value * value for value in values)) or 1.0
        return EmbeddingResult("hash-384", self.dimensions, [value / norm for value in values], "hash")


def build_embedding_service() -> EmbeddingService:
    provider = os.getenv("LIFEOS_EMBEDDING_PROVIDER", "sentence-transformers").lower()
    if provider == "hash":
        return HashEmbeddingService()
    model_name = os.getenv("LIFEOS_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    try:
        return SentenceTransformerService(model_name)
    except Exception:
        if os.getenv("LIFEOS_ALLOW_HASH_EMBEDDINGS", "true").lower() == "true":
            return HashEmbeddingService()
        raise
