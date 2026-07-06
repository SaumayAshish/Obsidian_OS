from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class StoredEmbedding:
    chunk_id: int
    model: str
    embedding_text: str
    dimensions: int


class EmbeddingStore(Protocol):
    def serialize(self, values: list[float]) -> str:
        ...

    def deserialize(self, value: str) -> list[float]:
        ...


class TextEmbeddingStore:
    """Phase 3 fallback store. Phase 4 can replace this with pgvector operations."""

    def serialize(self, values: list[float]) -> str:
        return json.dumps(values, separators=(",", ":"))

    def deserialize(self, value: str) -> list[float]:
        data = json.loads(value)
        if not isinstance(data, list):
            raise ValueError("Stored embedding is not a list")
        return [float(item) for item in data]
