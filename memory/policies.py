"""Forgetting policies for memory management."""

from abc import ABC, abstractmethod
from typing import List
from datetime import datetime, timedelta
from .manager import MemoryEntry, MemoryImportance


class ForgettingPolicy(ABC):
    """Base forgetting policy."""

    @abstractmethod
    async def should_forget(self, memory: MemoryEntry) -> bool:
        """Determine if memory should be forgotten."""
        pass


class TimeBasedForgetting(ForgettingPolicy):
    """Forget memories based on age."""

    def __init__(self, max_age_days: int = 30):
        self.max_age_days = max_age_days

    async def should_forget(self, memory: MemoryEntry) -> bool:
        age = datetime.now() - memory.metadata.created_at
        return age > timedelta(days=self.max_age_days)


class ImportanceBasedForgetting(ForgettingPolicy):
    """Forget low-importance memories."""

    def __init__(self, min_importance: MemoryImportance = MemoryImportance.LOW):
        self.min_importance = min_importance

    async def should_forget(self, memory: MemoryEntry) -> bool:
        importance_order = {
            MemoryImportance.CRITICAL: 5,
            MemoryImportance.HIGH: 4,
            MemoryImportance.MEDIUM: 3,
            MemoryImportance.LOW: 2,
            MemoryImportance.TRIVIAL: 1,
        }
        return importance_order.get(memory.metadata.importance, 0) < importance_order.get(self.min_importance, 2)


class CapacityBasedForgetting(ForgettingPolicy):
    """Forget when capacity is exceeded."""

    def __init__(self, capacity_threshold: float = 0.9):
        self.capacity_threshold = capacity_threshold

    async def should_forget(self, memory: MemoryEntry) -> bool:
        # This would need access to store capacity
        return False


class RelevanceBasedForgetting(ForgettingPolicy):
    """Forget based on relevance to current context."""

    async def should_forget(self, memory: MemoryEntry) -> bool:
        # Would analyze relevance - stub for now
        return memory.metadata.access_count == 0
