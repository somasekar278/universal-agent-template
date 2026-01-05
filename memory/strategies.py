"""Retrieval strategies for memory search."""

from abc import ABC, abstractmethod
from typing import List
from .manager import MemoryEntry


class RetrievalStrategy(ABC):
    """Base retrieval strategy."""

    @abstractmethod
    async def retrieve(self, query: str, candidates: List[MemoryEntry], limit: int) -> List[MemoryEntry]:
        """Retrieve memories using this strategy."""
        pass


class SemanticRetrievalStrategy(RetrievalStrategy):
    """Semantic similarity-based retrieval."""

    async def retrieve(self, query: str, candidates: List[MemoryEntry], limit: int) -> List[MemoryEntry]:
        # Stub - would use embeddings
        return candidates[:limit]


class RecencyRetrievalStrategy(RetrievalStrategy):
    """Recency-based retrieval."""

    async def retrieve(self, query: str, candidates: List[MemoryEntry], limit: int) -> List[MemoryEntry]:
        sorted_candidates = sorted(candidates, key=lambda m: m.metadata.created_at, reverse=True)
        return sorted_candidates[:limit]


class ImportanceRetrievalStrategy(RetrievalStrategy):
    """Importance-based retrieval."""

    async def retrieve(self, query: str, candidates: List[MemoryEntry], limit: int) -> List[MemoryEntry]:
        # Sort by importance
        sorted_candidates = sorted(
            candidates,
            key=lambda m: m.metadata.importance.value,
            reverse=True
        )
        return sorted_candidates[:limit]


class HybridRetrievalStrategy(RetrievalStrategy):
    """Hybrid retrieval combining multiple factors."""

    async def retrieve(self, query: str, candidates: List[MemoryEntry], limit: int) -> List[MemoryEntry]:
        # Combine recency, importance, and access count
        scored = [
            (mem, self._score(mem))
            for mem in candidates
        ]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [mem for mem, _ in scored[:limit]]

    def _score(self, memory: MemoryEntry) -> float:
        """Calculate composite score."""
        recency_score = 1.0  # Simplified
        importance_scores = {"critical": 1.0, "high": 0.8, "medium": 0.6, "low": 0.4, "trivial": 0.2}
        importance_score = importance_scores.get(memory.metadata.importance.value, 0.5)
        access_score = min(memory.metadata.access_count / 10.0, 1.0)

        return recency_score * 0.4 + importance_score * 0.4 + access_score * 0.2
