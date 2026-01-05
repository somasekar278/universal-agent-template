"""Memory stores - Different types of memory storage."""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from .manager import MemoryEntry, MemoryType
import asyncio


class MemoryStore:
    """Base class for memory stores."""

    def __init__(self, capacity: Optional[int] = None):
        self.capacity = capacity
        self._memories: Dict[str, MemoryEntry] = {}

    async def add(self, memory: MemoryEntry) -> bool:
        """Add memory to store."""
        if self.capacity and len(self._memories) >= self.capacity:
            return False
        self._memories[memory.id] = memory
        return True

    async def get(self, memory_id: str) -> Optional[MemoryEntry]:
        """Get memory by ID."""
        memory = self._memories.get(memory_id)
        if memory:
            memory.metadata.update_access()
        return memory

    async def search(self, **kwargs) -> List[MemoryEntry]:
        """Search memories."""
        return list(self._memories.values())

    async def remove(self, memory_id: str) -> bool:
        """Remove memory."""
        if memory_id in self._memories:
            del self._memories[memory_id]
            return True
        return False

    async def clear(self):
        """Clear all memories."""
        self._memories.clear()

    def __len__(self):
        return len(self._memories)


class ShortTermMemory(MemoryStore):
    """
    Short-term/working memory.

    Holds immediate context with TTL.
    """

    def __init__(self, capacity: int = 20, ttl_seconds: int = 3600):
        super().__init__(capacity)
        self.ttl_seconds = ttl_seconds

    async def add(self, memory: MemoryEntry) -> bool:
        """Add to short-term memory."""
        # Evict expired
        await self._evict_expired()
        return await super().add(memory)

    async def _evict_expired(self):
        """Remove expired memories."""
        now = datetime.now()
        expired = [
            mid for mid, mem in self._memories.items()
            if (now - mem.metadata.created_at).total_seconds() > self.ttl_seconds
        ]
        for mid in expired:
            await self.remove(mid)


class LongTermMemory(MemoryStore):
    """
    Long-term memory.

    Persistent storage with importance-based retention.
    """

    def __init__(self, capacity: int = 10000):
        super().__init__(capacity)


class EpisodicMemory(MemoryStore):
    """
    Episodic memory for events and experiences.

    Stores temporal sequences of events.
    """

    def __init__(self):
        super().__init__()

    async def search_by_timerange(
        self,
        start: datetime,
        end: datetime
    ) -> List[MemoryEntry]:
        """Search by time range."""
        return [
            mem for mem in self._memories.values()
            if start <= mem.metadata.created_at <= end
        ]


class SemanticMemory(MemoryStore):
    """
    Semantic memory for facts and knowledge.

    Stores conceptual knowledge and relationships.
    """

    def __init__(self):
        super().__init__()


class ProceduralMemory(MemoryStore):
    """
    Procedural memory for skills and procedures.

    Stores how-to knowledge and action sequences.
    """

    def __init__(self):
        super().__init__()
