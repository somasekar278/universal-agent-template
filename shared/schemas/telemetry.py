"""
Telemetry and observability schemas.

Data structures for OTEL traces, Zerobus events, and agent observability.
Designed to be serialized to Delta Lake via Zerobus.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class EventType(str, Enum):
    """Types of telemetry events."""
    AGENT_START = "agent_start"
    AGENT_COMPLETE = "agent_complete"
    AGENT_ERROR = "agent_error"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    LLM_REQUEST = "llm_request"
    LLM_RESPONSE = "llm_response"
    STREAM_CHUNK = "stream_chunk"


class MCPToolTrace(BaseModel):
    """
    Trace data for MCP tool calls.
    
    Captured by OTEL and sent to Delta via Zerobus.
    """
    
    tool_call_id: str = Field(..., description="Unique tool call ID")
    tool_name: str = Field(..., description="MCP tool/method name")
    tool_server: str = Field(..., description="MCP server name")
    
    # Execution details
    arguments: Dict[str, Any] = Field(default_factory=dict)
    result: Optional[Any] = Field(default=None)
    error: Optional[str] = Field(default=None)
    success: bool = Field(...)
    
    # Timing
    started_at: datetime = Field(...)
    completed_at: datetime = Field(...)
    latency_ms: float = Field(..., ge=0)
    
    # Context
    request_id: str = Field(..., description="Parent request ID")
    agent_id: str = Field(..., description="Agent that made the call")
    
    # OTEL trace context
    trace_id: Optional[str] = Field(default=None)
    span_id: Optional[str] = Field(default=None)
    parent_span_id: Optional[str] = Field(default=None)


class LLMTrace(BaseModel):
    """
    Trace data for LLM inference calls.
    
    Tracks calls to Databricks Model Serving endpoints.
    """
    
    llm_call_id: str = Field(..., description="Unique LLM call ID")
    model_name: str = Field(..., description="Model serving endpoint name")
    
    # Request details
    prompt: str = Field(..., description="Prompt sent to LLM")
    prompt_tokens: int = Field(..., ge=0)
    
    # Response details
    completion: Optional[str] = Field(default=None, description="LLM completion")
    completion_tokens: Optional[int] = Field(default=None, ge=0)
    total_tokens: Optional[int] = Field(default=None, ge=0)
    
    # Execution
    success: bool = Field(...)
    error: Optional[str] = Field(default=None)
    
    # Timing
    started_at: datetime = Field(...)
    completed_at: datetime = Field(...)
    latency_ms: float = Field(..., ge=0)
    time_to_first_token_ms: Optional[float] = Field(default=None, ge=0)
    
    # Context
    request_id: str = Field(..., description="Parent request ID")
    agent_id: str = Field(..., description="Agent that made the call")
    
    # Model parameters
    temperature: Optional[float] = Field(default=None)
    max_tokens: Optional[int] = Field(default=None)
    
    # OTEL trace context
    trace_id: Optional[str] = Field(default=None)
    span_id: Optional[str] = Field(default=None)


class AgentTrace(BaseModel):
    """
    Complete trace for an agent execution.
    
    Top-level trace that contains tool calls and LLM calls.
    """
    
    trace_id: str = Field(..., description="Unique trace ID (OTEL trace_id)")
    request_id: str = Field(..., description="Request identifier")
    agent_id: str = Field(..., description="Agent instance ID")
    agent_type: str = Field(..., description="Agent type (e.g., narrative, collector)")
    
    # Transaction context
    transaction_id: str = Field(..., description="Associated transaction ID")
    merchant_id: str = Field(...)
    customer_id: str = Field(...)
    
    # Execution details
    started_at: datetime = Field(...)
    completed_at: Optional[datetime] = Field(default=None)
    latency_ms: Optional[float] = Field(default=None, ge=0)
    
    success: bool = Field(...)
    error: Optional[str] = Field(default=None)
    
    # Agent output
    recommended_action: Optional[str] = Field(default=None)
    risk_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    
    # Child traces
    tool_calls: List[MCPToolTrace] = Field(default_factory=list)
    llm_calls: List[LLMTrace] = Field(default_factory=list)
    
    # Resource usage
    total_prompt_tokens: int = Field(default=0, ge=0)
    total_completion_tokens: int = Field(default=0, ge=0)
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TelemetryEvent(BaseModel):
    """
    Generic telemetry event for Zerobus ingestion.
    
    This schema maps to a Unity Catalog Delta table via Zerobus protobuf.
    Follows the pattern from e2e-chatbot-zerobus reference.
    """
    
    # Event identification
    event_id: str = Field(..., description="Unique event ID")
    event_type: EventType = Field(..., description="Type of event")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Request context
    request_id: str = Field(..., description="Associated request ID")
    transaction_id: Optional[str] = Field(default=None)
    agent_id: Optional[str] = Field(default=None)
    
    # OTEL context
    trace_id: Optional[str] = Field(default=None)
    span_id: Optional[str] = Field(default=None)
    parent_span_id: Optional[str] = Field(default=None)
    
    # Event payload (flexible JSON)
    payload: Dict[str, Any] = Field(
        default_factory=dict,
        description="Event-specific data"
    )
    
    # Performance metrics
    latency_ms: Optional[float] = Field(default=None, ge=0)
    
    # Resource usage
    tokens_used: Optional[int] = Field(default=None, ge=0)
    cost_usd: Optional[float] = Field(default=None, ge=0)
    
    # Environment
    environment: str = Field(default="production", description="dev/staging/production")
    
    class Config:
        json_schema_extra = {
            "example": {
                "event_id": "evt_abc123",
                "event_type": "agent_complete",
                "timestamp": "2025-12-25T14:30:15Z",
                "request_id": "req_abc123",
                "transaction_id": "txn_1234567890",
                "agent_id": "agent_narrative_xyz",
                "trace_id": "otel_trace_456",
                "span_id": "otel_span_789",
                "payload": {
                    "risk_score": 0.78,
                    "action": "review",
                    "tools_used": ["merchant_context", "customer_context"],
                },
                "latency_ms": 245.5,
                "tokens_used": 1250,
                "environment": "production",
            }
        }

