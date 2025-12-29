"""
MCP tool schemas.

Common schemas used across MCP servers.
Does NOT import from parent project schemas!
"""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class MCPToolSchema(BaseModel):
    """
    Schema for MCP tool definition.
    
    Used to define tools in MCP servers.
    """
    
    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    input_schema: Dict[str, Any] = Field(..., description="JSON schema for tool input")


class MCPToolResult(BaseModel):
    """
    Result from MCP tool execution.
    
    Standardized result format across all tools.
    """
    
    success: bool = Field(..., description="Whether tool execution succeeded")
    data: Optional[Any] = Field(default=None, description="Tool result data")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata (latency, tokens, etc.)"
    )
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "success": True,
                    "data": {"rows": [...], "columns": [...]},
                    "error": None,
                    "metadata": {"latency_ms": 45.2, "rows_returned": 100}
                }
            ]
        }

