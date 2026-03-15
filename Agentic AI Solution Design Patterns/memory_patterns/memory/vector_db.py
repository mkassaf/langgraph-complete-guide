"""
Simulated vector database for long-term memory storage.

From lesson: 'converts the new episodic and procedural records into
numerical vectors and stores them in a special database within the
shared agent memory system, which is usually a vector database'

Simplified: uses keyword matching as proxy for similarity.
"""

from dataclasses import dataclass
import math
from datetime import datetime


@dataclass
class VectorRecord:
    """A record in the vector database."""

    record_id: str
    record_type: str
    content: dict
    vector: list[float]
    timestamp: str


class VectorDatabase:
    def __init__(self):
        self.records: list[VectorRecord] = []

    def store(self, record: VectorRecord):
        self.records.append(record)
        print(f"[VECTOR DB] Stored {record.record_type}: {record.record_id}")

    def query(
        self,
        query_text: str,
        record_type: str | None = None,
        top_k: int = 3,
    ) -> list[VectorRecord]:
        """Find most relevant records. Simplified: keyword matching."""
        print(f'[VECTOR DB] Querying for: "{query_text[:50]}..."')
        filtered = [
            r
            for r in self.records
            if record_type is None or r.record_type == record_type
        ]
        query_lower = query_text.lower()
        scored = []
        for r in filtered:
            content_str = str(r.content).lower()
            score = sum(1 for w in query_lower.split() if w in content_str)
            scored.append((score, r))
        scored.sort(key=lambda x: -x[0])
        results = [r for _, r in scored[:top_k]]
        print(f"[VECTOR DB] Found {len(results)} relevant {record_type or 'memories'}")
        return results

    def _text_to_vector(self, text: str) -> list[float]:
        """Simplified text vectorization."""
        words = text.lower().split()
        return [hash(w) % 100 / 100.0 for w in words[:20]]

    def _similarity(self, v1: list[float], v2: list[float]) -> float:
        """Cosine similarity between vectors."""
        if not v1 or not v2:
            return 0.0
        dot = sum(a * b for a, b in zip(v1, v2))
        mag1 = math.sqrt(sum(a * a for a in v1))
        mag2 = math.sqrt(sum(b * b for b in v2))
        if mag1 * mag2 == 0:
            return 0.0
        return dot / (mag1 * mag2)
