"""
Pluggable execution backends for agents.

Enables running the same agent code in different execution modes:
- In-process (testing, low latency)
- Process pool (bin-packing, isolation)
- Ray (distributed, auto-scaling)
- Serverless (true ephemeral)

Agent code stays the same - just change the backend!
"""

from .runner import (
    AgentRunner,
    ExecutionMode,
    ExecutionBackend,
)

from .backends import (
    InProcessBackend,
    ProcessPoolBackend,
    RayBackend,
)

__all__ = [
    "AgentRunner",
    "ExecutionMode",
    "ExecutionBackend",
    "InProcessBackend",
    "ProcessPoolBackend",
    "RayBackend",
]

