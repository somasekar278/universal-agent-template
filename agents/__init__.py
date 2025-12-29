"""
Agent framework for ephemeral fraud detection agents.

Provides:
- Base agent interfaces (Agent, CriticalPathAgent, EnrichmentAgent)
- Pluggable execution backends (in-process, Ray, process pool)
- Agent registry and routing
- Uniform invocation interface
- Configuration-driven deployment (plug-and-play)

Quick start (plug-and-play):
    from agents import AgentRouter
    
    # Load agents from config
    router = AgentRouter.from_yaml("config/agents.yaml")
    
    # Use in your pipeline
    result = await router.route("narrative", agent_input)
"""

from .base import (
    Agent,
    CriticalPathAgent,
    EnrichmentAgent,
    AgentType,
    ExecutionPriority,
    AgentExecutionError,
)

from .registry import (
    AgentRegistry,
    AgentRouter,
    AgentMetadata,
)

from .execution import (
    AgentRunner,
    ExecutionMode,
)

from .config import (
    AgentConfig,
    AgentConfigError,
)

from .mcp_client import (
    AgentMCPClient,
)

__all__ = [
    # Base classes
    "Agent",
    "CriticalPathAgent",
    "EnrichmentAgent",
    "AgentType",
    "ExecutionPriority",
    "AgentExecutionError",
    
    # Registry and routing
    "AgentRegistry",
    "AgentRouter",
    "AgentMetadata",
    
    # Execution
    "AgentRunner",
    "ExecutionMode",
    
    # Configuration
    "AgentConfig",
    "AgentConfigError",
    
    # MCP Client
    "AgentMCPClient",
]

