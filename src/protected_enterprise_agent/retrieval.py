from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass


_TOKEN = re.compile(r"[A-Za-z0-9_:-]+")


def embed(text: str) -> Counter[str]:
    """Deterministic local sparse embedding used to keep the demo reproducible."""
    return Counter(token.lower() for token in _TOKEN.findall(text))


def cosine(left: Counter[str], right: Counter[str]) -> float:
    common = set(left) & set(right)
    numerator = sum(left[token] * right[token] for token in common)
    left_norm = math.sqrt(sum(value * value for value in left.values()))
    right_norm = math.sqrt(sum(value * value for value in right.values()))
    return numerator / (left_norm * right_norm) if left_norm and right_norm else 0.0


@dataclass(frozen=True)
class StoredDocument:
    fixture_id: str
    text: str
    metadata: dict[str, str]
    vector: Counter[str]


class LocalVectorStore:
    def __init__(self) -> None:
        self._documents: list[StoredDocument] = []

    def add(self, fixture_id: str, text: str, metadata: dict[str, str]) -> None:
        self._documents.append(StoredDocument(fixture_id, text, dict(metadata), embed(text)))

    def search(self, query: str, limit: int = 2) -> list[StoredDocument]:
        query_vector = embed(query)
        ranked = sorted(self._documents, key=lambda document: cosine(query_vector, document.vector), reverse=True)
        return ranked[:limit]

    @property
    def documents(self) -> tuple[StoredDocument, ...]:
        return tuple(self._documents)

