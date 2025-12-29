"""
Agent input/output schemas.

Data structures for agent execution, including inputs, outputs, reasoning traces,
and tool calling (MCP integration ready).
"""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field

from .transactions import Transaction
from .fraud_signals import FraudSignals
from .contexts import MerchantContext, CustomerContext


class ToolCall(BaseModel):
    """
    Represents a tool call made by an agent (MCP-ready).
    
    Designed to be compatible with MCP tool calling patterns.
    """
    
    tool_id: str = Field(..., description="Unique tool call ID")
    tool_name: str = Field(..., description="Name of tool/MCP server method")
    tool_server: Optional[str] = Field(default=None, description="MCP server name")
    
    arguments: Dict[str, Any] = Field(
        default_factory=dict,
        description="Tool arguments"
    )
    
    called_at: datetime = Field(default_factory=datetime.utcnow)
    

class ToolResult(BaseModel):
    """
    Result from a tool call (MCP-ready).
    """
    
    tool_call_id: str = Field(..., description="Associated tool call ID")
    
    success: bool = Field(..., description="Whether tool call succeeded")
    result: Optional[Any] = Field(default=None, description="Tool result data")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    
    latency_ms: float = Field(..., ge=0, description="Tool execution latency")
    completed_at: datetime = Field(default_factory=datetime.utcnow)


class ReasoningStep(BaseModel):
    """
    A step in the agent's chain-of-thought reasoning.
    """
    
    step_number: int = Field(..., ge=1)
    thought: str = Field(..., description="Agent's reasoning/thought")
    
    # Optional tool interaction
    tool_call: Optional[ToolCall] = Field(default=None)
    tool_result: Optional[ToolResult] = Field(default=None)
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AgentAction(str, Enum):
    """Recommended actions an agent can output."""
    APPROVE = "approve"
    DECLINE = "decline"
    REVIEW = "review"
    FLAG_HIGH_RISK = "flag_high_risk"
    REQUEST_VERIFICATION = "request_verification"


class AgentInput(BaseModel):
    """
    Complete input to an agent for fraud analysis.
    
    Aggregates transaction data, fraud signals, and contextual information.
    """
    
    request_id: str = Field(..., description="Unique request identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Core data
    transaction: Transaction = Field(..., description="Transaction to analyze")
    fraud_signals: FraudSignals = Field(..., description="Computed fraud signals")
    
    # Contextual data (retrieved via MCP in production)
    merchant_context: MerchantContext = Field(..., description="Merchant context")
    customer_context: CustomerContext = Field(..., description="Customer context")
    
    # Optional additional context
    similar_cases: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Similar historical fraud cases from Lakebase"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "req_abc123",
                "timestamp": "2025-12-25T14:30:10Z",
                "transaction": {"transaction_id": "txn_1234567890"},
                "fraud_signals": {"transaction_id": "txn_1234567890"},
                "merchant_context": {"merchant_id": "mch_retail_001"},
                "customer_context": {"customer_id": "cust_987654321"},
            }
        }


class AgentOutput(BaseModel):
    """
    Agent's fraud analysis output.
    
    Contains the risk narrative, recommended action, confidence score,
    and full reasoning trace for observability.
    """
    
    request_id: str = Field(..., description="Associated request ID")
    agent_id: str = Field(..., description="Agent instance identifier")
    
    # Core output
    risk_narrative: str = Field(
        ...,
        description="Human-readable fraud risk narrative",
        min_length=10
    )
    
    recommended_action: AgentAction = Field(..., description="Recommended action")
    
    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Agent confidence in recommendation"
    )
    
    risk_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Computed fraud risk score"
    )
    
    # Reasoning trace (for MLflow tracing)
    reasoning_steps: List[ReasoningStep] = Field(
        default_factory=list,
        description="Chain-of-thought reasoning steps"
    )
    
    # Tool usage summary
    tools_called: List[str] = Field(
        default_factory=list,
        description="List of tools/MCP servers called"
    )
    
    # Timing
    started_at: datetime = Field(..., description="Agent start time")
    completed_at: datetime = Field(default_factory=datetime.utcnow)
    latency_ms: float = Field(..., ge=0, description="Total agent latency")
    
    # Model info
    model_name: str = Field(..., description="LLM model used")
    prompt_tokens: Optional[int] = Field(default=None, ge=0)
    completion_tokens: Optional[int] = Field(default=None, ge=0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "req_abc123",
                "agent_id": "agent_narrative_xyz",
                "risk_narrative": "High-risk transaction detected: Customer showing velocity anomaly with 5 transactions in past hour. New device from different country (GB to RO) raises location mismatch concerns. Recommend manual review.",
                "recommended_action": "review",
                "confidence_score": 0.85,
                "risk_score": 0.78,
                "tools_called": ["merchant_context", "customer_context", "velocity_check"],
                "latency_ms": 245.5,
                "model_name": "meta-llama-3.1-70b-instruct",
            }
        }

