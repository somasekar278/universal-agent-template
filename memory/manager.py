"""
Memory Manager - Central coordination of agent memory systems.
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import uuid


class MemoryType(str, Enum):
    """Types of memory."""
    SHORT_TERM = "short_term"        # Working memory, immediate context
    LONG_TERM = "long_term"          # Persistent memory
    EPISODIC = "episodic"            # Event/experience memories
    SEMANTIC = "semantic"            # Facts and knowledge
    PROCEDURAL = "procedural"        # Skills and procedures


class MemoryImportance(str, Enum):
    """Memory importance levels."""
    CRITICAL = "critical"    # Never forget
    HIGH = "high"           # Very important
    MEDIUM = "medium"       # Important
    LOW = "low"            # Can forget if needed
    TRIVIAL = "trivial"    # Forget soon


@dataclass
class MemoryMetadata:
    """Metadata for memory entries."""
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    importance: MemoryImportance = MemoryImportance.MEDIUM
    tags: List[str] = field(default_factory=list)
    source: Optional[str] = None  # Which agent created this
    related_memories: List[str] = field(default_factory=list)
    embedding: Optional[List[float]] = None

    def update_access(self):
        """Update access tracking."""
        self.last_accessed = datetime.now()
        self.access_count += 1


@dataclass
class MemoryEntry:
    """A single memory entry."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    memory_type: MemoryType = MemoryType.SHORT_TERM
    content: Any = None
    metadata: MemoryMetadata = field(default_factory=MemoryMetadata)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "memory_type": self.memory_type.value,
            "content": self.content,
            "metadata": {
                "created_at": self.metadata.created_at.isoformat(),
                "last_accessed": self.metadata.last_accessed.isoformat(),
                "access_count": self.metadata.access_count,
                "importance": self.metadata.importance.value,
                "tags": self.metadata.tags,
                "source": self.metadata.source,
                "related_memories": self.metadata.related_memories
            }
        }


@dataclass
class MemoryConfig:
    """Configuration for memory management."""

    # Short-term memory settings
    short_term_capacity: int = 20  # Max items in short-term
    short_term_ttl_seconds: int = 3600  # 1 hour

    # Long-term memory settings
    long_term_capacity: int = 10000  # Max items in long-term
    enable_compression: bool = True  # Compress old memories

    # Context window settings
    max_context_tokens: int = 8000  # Max tokens for LLM context
    context_reservation: float = 0.2  # Reserve 20% for system prompts

    # Reflection settings
    reflection_interval_hours: int = 24  # Reflect every 24 hours
    reflection_trigger_count: int = 100  # Or after 100 new memories
    enable_auto_reflection: bool = True

    # Forgetting settings
    enable_forgetting: bool = True
    min_importance_to_keep: MemoryImportance = MemoryImportance.LOW

    # Retrieval settings
    default_retrieval_limit: int = 10
    min_similarity_threshold: float = 0.7

    # Shared memory settings
    enable_cross_agent_memory: bool = True
    default_memory_visibility: str = "private"  # "private" or "shared"


class MemoryManager:
    """
    Central memory management system.

    Coordinates:
    - Multiple memory stores (short-term, long-term, episodic, etc.)
    - Memory agents (storage, retrieval, reflection, forgetting)
    - Context window budgeting
    - Cross-agent memory sharing

    Usage:
        manager = MemoryManager()

        # Store memory
        await manager.store(
            content="User prefers dark mode",
            memory_type=MemoryType.SEMANTIC,
            importance=MemoryImportance.HIGH
        )

        # Retrieve memories
        memories = await manager.retrieve(
            query="What are user preferences?",
            limit=5
        )

        # Reflect and summarize
        summary = await manager.reflect()
    """

    def __init__(self, config: Optional[MemoryConfig] = None):
        """
        Initialize memory manager.

        Args:
            config: Memory configuration
        """
        self.config = config or MemoryConfig()

        # Memory stores (lazy-loaded)
        self._short_term = None
        self._long_term = None
        self._episodic = None
        self._semantic = None
        self._procedural = None

        # Memory agents (lazy-loaded)
        self._storage_agent = None
        self._retrieval_agent = None
        self._reflection_agent = None
        self._forget_agent = None

        # Context manager
        self._context_manager = None

        # Shared memory coordinator
        self._shared_coordinator = None

        # Statistics
        self.stats = {
            "total_stored": 0,
            "total_retrieved": 0,
            "total_forgotten": 0,
            "reflections_count": 0
        }

    @property
    def short_term(self):
        """Get short-term memory store."""
        if self._short_term is None:
            from .stores import ShortTermMemory
            self._short_term = ShortTermMemory(
                capacity=self.config.short_term_capacity,
                ttl_seconds=self.config.short_term_ttl_seconds
            )
        return self._short_term

    @property
    def long_term(self):
        """Get long-term memory store."""
        if self._long_term is None:
            from .stores import LongTermMemory
            self._long_term = LongTermMemory(
                capacity=self.config.long_term_capacity
            )
        return self._long_term

    @property
    def episodic(self):
        """Get episodic memory store."""
        if self._episodic is None:
            from .stores import EpisodicMemory
            self._episodic = EpisodicMemory()
        return self._episodic

    @property
    def semantic(self):
        """Get semantic memory store."""
        if self._semantic is None:
            from .stores import SemanticMemory
            self._semantic = SemanticMemory()
        return self._semantic

    @property
    def procedural(self):
        """Get procedural memory store."""
        if self._procedural is None:
            from .stores import ProceduralMemory
            self._procedural = ProceduralMemory()
        return self._procedural

    @property
    def storage_agent(self):
        """Get storage decision agent."""
        if self._storage_agent is None:
            from .agents import StorageDecisionAgent
            self._storage_agent = StorageDecisionAgent(self)
        return self._storage_agent

    @property
    def retrieval_agent(self):
        """Get retrieval agent."""
        if self._retrieval_agent is None:
            from .agents import RetrievalAgent
            self._retrieval_agent = RetrievalAgent(self)
        return self._retrieval_agent

    @property
    def reflection_agent(self):
        """Get reflection agent."""
        if self._reflection_agent is None:
            from .agents import ReflectionAgent
            self._reflection_agent = ReflectionAgent(self)
        return self._reflection_agent

    @property
    def forget_agent(self):
        """Get forgetting agent."""
        if self._forget_agent is None:
            from .agents import ForgetAgent
            self._forget_agent = ForgetAgent(self)
        return self._forget_agent

    @property
    def context_manager(self):
        """Get context window manager."""
        if self._context_manager is None:
            from .context import ContextWindowManager
            self._context_manager = ContextWindowManager(
                max_tokens=self.config.max_context_tokens,
                reservation=self.config.context_reservation
            )
        return self._context_manager

    @property
    def shared_coordinator(self):
        """Get shared memory coordinator."""
        if self._shared_coordinator is None:
            from .shared import SharedMemoryCoordinator
            self._shared_coordinator = SharedMemoryCoordinator()
        return self._shared_coordinator

    async def store(
        self,
        content: Any,
        memory_type: Optional[MemoryType] = None,
        importance: Optional[MemoryImportance] = None,
        source: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> MemoryEntry:
        """
        Store a memory (agent-governed).

        The storage agent decides where and how to store based on:
        - Content importance
        - Memory type
        - Current capacity
        - Existing memories

        Args:
            content: Content to store
            memory_type: Type of memory (auto-detected if None)
            importance: Importance level (auto-assessed if None)
            source: Source agent ID
            tags: Tags for categorization

        Returns:
            Created memory entry
        """
        # Delegate to storage agent
        memory = await self.storage_agent.decide_and_store(
            content=content,
            memory_type=memory_type,
            importance=importance,
            source=source,
            tags=tags
        )

        self.stats["total_stored"] += 1

        return memory

    async def retrieve(
        self,
        query: Union[str, Dict[str, Any]],
        memory_types: Optional[List[MemoryType]] = None,
        limit: Optional[int] = None,
        strategy: Optional[str] = None
    ) -> List[MemoryEntry]:
        """
        Retrieve memories (agent-governed).

        The retrieval agent intelligently finds relevant memories using:
        - Semantic similarity
        - Recency
        - Importance
        - Access patterns

        Args:
            query: Search query (text or structured)
            memory_types: Filter by memory types
            limit: Max memories to return
            strategy: Retrieval strategy name

        Returns:
            List of relevant memory entries
        """
        memories = await self.retrieval_agent.retrieve(
            query=query,
            memory_types=memory_types,
            limit=limit or self.config.default_retrieval_limit,
            strategy=strategy
        )

        self.stats["total_retrieved"] += len(memories)

        return memories

    async def reflect(self) -> Dict[str, Any]:
        """
        Perform reflection on memories.

        The reflection agent:
        - Analyzes recent memories
        - Identifies patterns
        - Creates summaries
        - Consolidates related memories
        - Promotes important insights to semantic memory

        Returns:
            Reflection summary
        """
        summary = await self.reflection_agent.reflect()

        self.stats["reflections_count"] += 1

        return summary

    async def forget(self, criteria: Optional[Dict[str, Any]] = None) -> int:
        """
        Apply forgetting policies.

        The forget agent decides what to remove based on:
        - Time since last access
        - Importance
        - Capacity constraints
        - Relevance to current goals

        Args:
            criteria: Optional specific forgetting criteria

        Returns:
            Number of memories forgotten
        """
        if not self.config.enable_forgetting:
            return 0

        count = await self.forget_agent.apply_forgetting(criteria)

        self.stats["total_forgotten"] += count

        return count

    async def build_context(
        self,
        query: str,
        include_system: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Build context for LLM with budget management.

        Args:
            query: Current query
            include_system: System prompt to include

        Returns:
            Context dict with messages and token counts
        """
        return await self.context_manager.build_context(
            query=query,
            memory_manager=self,
            system_prompt=include_system
        )

    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        return {
            **self.stats,
            "short_term_count": len(self.short_term) if self._short_term else 0,
            "long_term_count": len(self.long_term) if self._long_term else 0,
            "config": {
                "short_term_capacity": self.config.short_term_capacity,
                "long_term_capacity": self.config.long_term_capacity,
                "max_context_tokens": self.config.max_context_tokens
            }
        }

    async def clear(self, memory_types: Optional[List[MemoryType]] = None):
        """
        Clear memories.

        Args:
            memory_types: Specific types to clear (all if None)
        """
        if memory_types is None or MemoryType.SHORT_TERM in memory_types:
            await self.short_term.clear()
        if memory_types is None or MemoryType.LONG_TERM in memory_types:
            await self.long_term.clear()
        if memory_types is None or MemoryType.EPISODIC in memory_types:
            await self.episodic.clear()
        if memory_types is None or MemoryType.SEMANTIC in memory_types:
            await self.semantic.clear()
        if memory_types is None or MemoryType.PROCEDURAL in memory_types:
            await self.procedural.clear()
