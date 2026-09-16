"""Hybrid keyword and semantic search over stored memories."""

from __future__ import annotations

import re
from typing import Any

from src.memory.vector_store import MemoryStore


def _terms(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


class HybridSearch:
    """Combine Chroma similarity with exact token overlap."""

    def __init__(self, store: MemoryStore):
        self.store = store

    def search(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        if not query.strip():
            return []
        if limit <= 0:
            raise ValueError("limit must be greater than zero")

        count = self.store.collection.count()
        if count == 0:
            return []

        semantic_limit = min(count, max(limit * 3, limit))
        semantic = self.store.collection.query(
            query_texts=[query],
            n_results=semantic_limit,
        )
        semantic_documents = semantic.get("documents", [[]])[0]
        semantic_metadatas = semantic.get("metadatas", [[]])[0]
        semantic_distances = semantic.get("distances", [[]])[0]
        semantic_results = {
            document: (metadata, distance)
            for document, metadata, distance in zip(
                semantic_documents,
                semantic_metadatas,
                semantic_distances,
            )
        }

        all_memories = self.store.collection.get(include=["documents", "metadatas"])
        query_terms = _terms(query)
        ranked: list[dict[str, Any]] = []
        for document, metadata in zip(
            all_memories.get("documents", []),
            all_memories.get("metadatas", []),
        ):
            document_terms = _terms(document)
            keyword_score = (
                len(query_terms & document_terms) / len(query_terms)
                if query_terms
                else 0.0
            )
            semantic_metadata, distance = semantic_results.get(document, (metadata, None))
            semantic_score = 1 / (1 + distance) if distance is not None else 0.0
            score = (0.6 * semantic_score) + (0.4 * keyword_score)
            ranked.append(
                {
                    "text": document,
                    "metadata": semantic_metadata,
                    "distance": distance,
                    "score": score,
                }
            )

        return sorted(ranked, key=lambda item: item["score"], reverse=True)[:limit]