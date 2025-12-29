"""
Shared utilities for MCP servers.

IMPORTANT: This is MCP-specific shared code only!
Does NOT import from parent project (agents/, shared/ at root).

Keeps MCP servers self-contained for easy extraction.
"""

from .auth import get_databricks_client, DatabricksAuth
from .schemas import MCPToolSchema, MCPToolResult

__all__ = [
    "get_databricks_client",
    "DatabricksAuth",
    "MCPToolSchema",
    "MCPToolResult",
]

