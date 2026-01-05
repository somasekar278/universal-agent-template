"""Memory agents - Intelligent memory management agents."""

from typing import Optional, List, Dict, Any, Union
from .manager import MemoryEntry, MemoryType, MemoryImportance, MemoryMetadata


class MemoryAgent:
    """Base memory agent."""

    def __init__(self, memory_manager):
        self.memory_manager = memory_manager


class StorageDecisionAgent(MemoryAgent):
    """
    Decides where and how to store memories.

    Analyzes content and determines:
    - Which memory store to use
    - Importance level
    - Whether to compress/summarize
    - Tags and relationships
    """

    async def decide_and_store(
        self,
        content: Any,
        memory_type: Optional[MemoryType] = None,
        importance: Optional[MemoryImportance] = None,
        source: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> MemoryEntry:
        """Decide storage location and store memory."""

        # Auto-detect memory type if not provided
        if memory_type is None:
            memory_type = await self._detect_memory_type(content)

        # Auto-assess importance if not provided
        if importance is None:
            importance = await self._assess_importance(content)

        # Create memory entry
        metadata = MemoryMetadata(
            importance=importance,
            tags=tags or [],
            source=source
        )

        memory = MemoryEntry(
            memory_type=memory_type,
            content=content,
            metadata=metadata
        )

        # Store in appropriate memory
        store = self._get_store(memory_type)
        await store.add(memory)

        return memory

    async def _detect_memory_type(self, content: Any) -> MemoryType:
        """Detect memory type from content."""
        # Simple heuristic - can be enhanced with LLM
        if isinstance(content, dict):
            if "event" in content or "timestamp" in content:
                return MemoryType.EPISODIC
            elif "fact" in content or "knowledge" in content:
                return MemoryType.SEMANTIC
            elif "procedure" in content or "steps" in content:
                return MemoryType.PROCEDURAL

        # Default to short-term
        return MemoryType.SHORT_TERM

    async def _assess_importance(self, content: Any) -> MemoryImportance:
        """Assess content importance."""
        # Simple heuristic - can be enhanced with LLM
        if isinstance(content, dict):
            if content.get("critical") or content.get("importance") == "high":
                return MemoryImportance.HIGH

        return MemoryImportance.MEDIUM

    def _get_store(self, memory_type: MemoryType):
        """Get appropriate store for memory type."""
        stores = {
            MemoryType.SHORT_TERM: self.memory_manager.short_term,
            MemoryType.LONG_TERM: self.memory_manager.long_term,
            MemoryType.EPISODIC: self.memory_manager.episodic,
            MemoryType.SEMANTIC: self.memory_manager.semantic,
            MemoryType.PROCEDURAL: self.memory_manager.procedural,
        }
        return stores.get(memory_type, self.memory_manager.short_term)


class RetrievalAgent(MemoryAgent):
    """
    Intelligently retrieves relevant memories.

    Uses multiple strategies:
    - Semantic similarity
    - Recency
    - Importance
    - Access patterns
    """

    async def retrieve(
        self,
        query: Union[str, Dict[str, Any]],
        memory_types: Optional[List[MemoryType]] = None,
        limit: int = 10,
        strategy: Optional[str] = None
    ) -> List[MemoryEntry]:
        """Retrieve relevant memories."""

        # Get stores to search
        stores = self._get_stores(memory_types)

        # Collect all candidates
        candidates = []
        for store in stores:
            memories = await store.search()
            candidates.extend(memories)

        # Apply retrieval strategy
        if strategy == "recency":
            candidates.sort(key=lambda m: m.metadata.created_at, reverse=True)
        elif strategy == "importance":
            importance_order = {
                MemoryImportance.CRITICAL: 5,
                MemoryImportance.HIGH: 4,
                MemoryImportance.MEDIUM: 3,
                MemoryImportance.LOW: 2,
                MemoryImportance.TRIVIAL: 1,
            }
            candidates.sort(
                key=lambda m: importance_order.get(m.metadata.importance, 0),
                reverse=True
            )
        else:
            # Hybrid: recency + importance + access count
            candidates.sort(
                key=lambda m: (
                    m.metadata.access_count * 0.3 +
                    (5 - (m.metadata.created_at.timestamp() / 1000000)) * 0.4 +
                    self._importance_score(m.metadata.importance) * 0.3
                ),
                reverse=True
            )

        return candidates[:limit]

    def _get_stores(self, memory_types: Optional[List[MemoryType]]):
        """Get stores to search."""
        if memory_types is None:
            return [
                self.memory_manager.short_term,
                self.memory_manager.long_term,
                self.memory_manager.episodic,
                self.memory_manager.semantic,
            ]

        stores = []
        for mem_type in memory_types:
            if mem_type == MemoryType.SHORT_TERM:
                stores.append(self.memory_manager.short_term)
            elif mem_type == MemoryType.LONG_TERM:
                stores.append(self.memory_manager.long_term)
            elif mem_type == MemoryType.EPISODIC:
                stores.append(self.memory_manager.episodic)
            elif mem_type == MemoryType.SEMANTIC:
                stores.append(self.memory_manager.semantic)
            elif mem_type == MemoryType.PROCEDURAL:
                stores.append(self.memory_manager.procedural)

        return stores

    def _importance_score(self, importance: MemoryImportance) -> float:
        """Convert importance to numeric score."""
        scores = {
            MemoryImportance.CRITICAL: 1.0,
            MemoryImportance.HIGH: 0.8,
            MemoryImportance.MEDIUM: 0.6,
            MemoryImportance.LOW: 0.4,
            MemoryImportance.TRIVIAL: 0.2,
        }
        return scores.get(importance, 0.5)


class ReflectionAgent(MemoryAgent):
    """
    Reflects on memories to create insights.

    Performs:
    - Pattern identification
    - Memory consolidation
    - Summary generation
    - Insight promotion
    """

    async def reflect(self) -> Dict[str, Any]:
        """Perform reflection on recent memories."""

        # Get recent memories from short-term
        recent = await self.memory_manager.short_term.search()

        # Simple reflection: count by tags and importance
        summary = {
            "total_memories": len(recent),
            "by_importance": {},
            "by_tags": {},
            "insights": []
        }

        for memory in recent:
            # Count by importance
            imp = memory.metadata.importance.value
            summary["by_importance"][imp] = summary["by_importance"].get(imp, 0) + 1

            # Count by tags
            for tag in memory.metadata.tags:
                summary["by_tags"][tag] = summary["by_tags"].get(tag, 0) + 1

        # Generate insights (simplified)
        if summary["by_importance"].get("high", 0) > 5:
            summary["insights"].append("High number of important memories - may need review")

        return summary


class ForgetAgent(MemoryAgent):
    """
    Applies forgetting policies.

    Decides what to forget based on:
    - Time since last access
    - Importance
    - Capacity constraints
    - Relevance
    """

    async def apply_forgetting(
        self,
        criteria: Optional[Dict[str, Any]] = None
    ) -> int:
        """Apply forgetting policies."""

        forgotten_count = 0

        # Apply to short-term (expired memories)
        if self.memory_manager._short_term:
            short_term = self.memory_manager.short_term
            await short_term._evict_expired()

        # Apply capacity-based forgetting to long-term
        if self.memory_manager._long_term:
            long_term = self.memory_manager.long_term
            if len(long_term) > long_term.capacity * 0.9:  # 90% full
                # Remove least important, least accessed
                memories = await long_term.search()
                memories.sort(
                    key=lambda m: (
                        self._importance_score(m.metadata.importance),
                        m.metadata.access_count
                    )
                )

                # Remove bottom 10%
                to_remove = int(len(memories) * 0.1)
                for memory in memories[:to_remove]:
                    if memory.metadata.importance != MemoryImportance.CRITICAL:
                        await long_term.remove(memory.id)
                        forgotten_count += 1

        return forgotten_count

    def _importance_score(self, importance: MemoryImportance) -> float:
        """Convert importance to numeric score."""
        scores = {
            MemoryImportance.CRITICAL: 1.0,
            MemoryImportance.HIGH: 0.8,
            MemoryImportance.MEDIUM: 0.6,
            MemoryImportance.LOW: 0.4,
            MemoryImportance.TRIVIAL: 0.2,
        }
        return scores.get(importance, 0.5)
