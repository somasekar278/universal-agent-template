"""
Agent-Governed Memory Management System

Comprehensive memory layer for AI agents with:
- Agent-controlled storage decisions
- Memory retrieval strategies
- Short/long-term memory split
- Reflection and summarization
- Context window budgeting
- Forgetting policies
- Cross-agent shared and private memory

Install:
    pip install sota-agent-framework[all]

Usage:
    from memory import MemoryManager, MemoryAgent

    memory = MemoryManager()
    agent = MemoryAgent(memory)

    # Agent decides what to store
    await agent.process_and_store(interaction)

    # Agent retrieves relevant context
    context = await agent.retrieve_context(query)
"""

from .manager import (
    MemoryManager,
    MemoryConfig,
    MemoryType,
    MemoryImportance,
    MemoryEntry,
    MemoryMetadata
)

from .stores import (
    ShortTermMemory,
    LongTermMemory,
    EpisodicMemory,
    SemanticMemory,
    ProceduralMemory
)

from .agents import (
    MemoryAgent,
    StorageDecisionAgent,
    RetrievalAgent,
    ReflectionAgent,
    ForgetAgent
)

from .strategies import (
    RetrievalStrategy,
    SemanticRetrievalStrategy,
    RecencyRetrievalStrategy,
    ImportanceRetrievalStrategy,
    HybridRetrievalStrategy
)

from .policies import (
    ForgettingPolicy,
    TimeBasedForgetting,
    ImportanceBasedForgetting,
    CapacityBasedForgetting,
    RelevanceBasedForgetting
)

from .context import (
    ContextWindowManager,
    ContextBudget,
    ContextPrioritization
)

from .shared import (
    SharedMemoryCoordinator,
    PrivateMemory,
    SharedMemory,
    MemoryAccess
)

from .embeddings import (
    EmbeddingProvider,
    SentenceTransformerEmbeddings,
    OpenAIEmbeddings,
    DatabricksEmbeddings,
    CachedEmbeddings,
    SemanticMemorySearch
)

from .graphs import (
    MemoryGraph,
    MemoryRelation,
    RelationType,
    AutoRelationDetector
)

__all__ = [
    # Core
    "MemoryManager",
    "MemoryConfig",
    "MemoryType",
    "MemoryImportance",
    "MemoryEntry",
    "MemoryMetadata",

    # Stores
    "ShortTermMemory",
    "LongTermMemory",
    "EpisodicMemory",
    "SemanticMemory",
    "ProceduralMemory",

    # Agents
    "MemoryAgent",
    "StorageDecisionAgent",
    "RetrievalAgent",
    "ReflectionAgent",
    "ForgetAgent",

    # Strategies
    "RetrievalStrategy",
    "SemanticRetrievalStrategy",
    "RecencyRetrievalStrategy",
    "ImportanceRetrievalStrategy",
    "HybridRetrievalStrategy",

    # Policies
    "ForgettingPolicy",
    "TimeBasedForgetting",
    "ImportanceBasedForgetting",
    "CapacityBasedForgetting",
    "RelevanceBasedForgetting",

    # Context
    "ContextWindowManager",
    "ContextBudget",
    "ContextPrioritization",

    # Shared
    "SharedMemoryCoordinator",
    "PrivateMemory",
    "SharedMemory",
    "MemoryAccess",

    # Embeddings
    "EmbeddingProvider",
    "SentenceTransformerEmbeddings",
    "OpenAIEmbeddings",
    "DatabricksEmbeddings",
    "CachedEmbeddings",
    "SemanticMemorySearch",

    # Graphs
    "MemoryGraph",
    "MemoryRelation",
    "RelationType",
    "AutoRelationDetector",
]
