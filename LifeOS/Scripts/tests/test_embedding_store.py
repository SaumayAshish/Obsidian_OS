from __future__ import annotations

from lifeos_sync.embedding_store import TextEmbeddingStore


def test_text_embedding_round_trip() -> None:
    store = TextEmbeddingStore()
    values = [0.1, 0.2, 0.3]

    assert store.deserialize(store.serialize(values)) == values

