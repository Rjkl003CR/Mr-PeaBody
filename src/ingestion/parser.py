"""Utilities for normalizing incoming notes and splitting them into chunks."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

URL_PATTERN = re.compile(r"https?://[^\s<>]+", re.IGNORECASE)


def find_urls(text: str) -> list[str]:
    """Return URLs found in text, without trailing sentence punctuation."""
    return [match.rstrip(".,!?;:)") for match in URL_PATTERN.findall(text)]


def normalize_text(text: str) -> str:
    """Collapse repeated whitespace while preserving word order."""
    return " ".join(text.split())


def chunk_text(text: str, chunk_size: int = 400) -> list[str]:
    """Split text into word chunks suitable for embedding and retrieval."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero")

    words = normalize_text(text).split()
    return [
        " ".join(words[start : start + chunk_size])
        for start in range(0, len(words), chunk_size)
    ]


def build_note_metadata(source: str | None = None) -> dict[str, Any]:
    """Create metadata shared by note and scraped-content chunks."""
    metadata: dict[str, Any] = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_type": "url" if source else "note",
    }
    if source:
        metadata["source"] = source
    return metadata