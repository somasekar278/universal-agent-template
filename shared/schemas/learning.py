"""
Generic Schemas for Learning Path (Levels 1-5)

Domain-agnostic schemas that work across different use cases:
chatbots, APIs, workflows, multi-agent systems.

These schemas are designed for the learning path but can be used
in production for generic agent applications.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


# ============================================================================
# Level 1: Simple Chatbot Schemas
# ============================================================================

class ChatInput(BaseModel):
    """
    Input for simple chatbot agents (Level 1).
    
    Generic enough to work for any conversational agent.
    """
    question: str = Field(..., description="User's question or message")
    user_id: str = Field(..., description="User identifier")
    session_id: Optional[str] = Field(None, description="Conversation session ID")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context")


class ChatOutput(BaseModel):
    """
    Output from chatbot agents (Level 1).
    
    Generic response format for conversational agents.
    """
    answer: str = Field(..., description="Agent's response")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Response confidence")
    sources: List[str] = Field(default_factory=list, description="Information sources used")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


# ============================================================================
# Level 2: Context-Aware Schemas (with Memory)
# ============================================================================

class ContextAwareInput(BaseModel):
    """
    Input for context-aware agents with memory (Level 2).
    
    Includes conversation history and context retrieval.
    """
    message: str = Field(..., description="Current user message")
    user_id: str = Field(..., description="User identifier")
    session_id: str = Field(..., description="Session identifier for context")
    conversation_history: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Previous messages in conversation"
    )
    retrieve_context: bool = Field(True, description="Whether to retrieve from memory")
    max_context_items: int = Field(5, description="Max items to retrieve from memory")


class ContextAwareOutput(BaseModel):
    """
    Output from context-aware agents (Level 2).
    
    Includes response with context information.
    """
    response: str = Field(..., description="Agent's response")
    confidence: float = Field(..., ge=0.0, le=1.0)
    context_used: List[str] = Field(default_factory=list, description="Context items used")
    stored_to_memory: bool = Field(False, description="Whether interaction was stored")
    memory_summary: Optional[str] = Field(None, description="Summary of what was remembered")


# ============================================================================
# Level 3: Production API Schemas
# ============================================================================

class APIRequest(BaseModel):
    """
    Generic API request schema (Level 3).
    
    Flexible schema for production APIs.
    """
    endpoint: str = Field(..., description="API endpoint or action")
    data: Dict[str, Any] = Field(..., description="Request data")
    user_id: Optional[str] = Field(None, description="User making the request")
    request_id: str = Field(..., description="Unique request identifier")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Request metadata")


class APIResponse(BaseModel):
    """
    Generic API response schema (Level 3).
    
    Standard response format for production APIs.
    """
    success: bool = Field(..., description="Whether request succeeded")
    data: Dict[str, Any] = Field(default_factory=dict, description="Response data")
    error: Optional[str] = Field(None, description="Error message if failed")
    request_id: str = Field(..., description="Original request ID")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Response metadata")


class HealthCheckResponse(BaseModel):
    """Health check response for production APIs."""
    status: str = Field(..., description="Service status (healthy, degraded, down)")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = Field(..., description="Service version")
    checks: Dict[str, bool] = Field(
        default_factory=dict,
        description="Individual health checks"
    )


# ============================================================================
# Level 4: Complex Workflow Schemas (Plan-Act-Critique)
# ============================================================================

class TaskStatus(str, Enum):
    """Task execution status."""
    PENDING = "pending"
    PLANNING = "planning"
    EXECUTING = "executing"
    CRITIQUING = "critiquing"
    REPLANNING = "replanning"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskStep(BaseModel):
    """Single step in a task plan."""
    step_id: str = Field(..., description="Step identifier")
    action: str = Field(..., description="Action to perform")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Step parameters")
    dependencies: List[str] = Field(default_factory=list, description="Dependent step IDs")
    status: TaskStatus = Field(TaskStatus.PENDING, description="Step status")
    result: Optional[Dict[str, Any]] = Field(None, description="Step result")


class WorkflowInput(BaseModel):
    """
    Input for complex workflow agents (Level 4).
    
    Supports Plan-Act-Critique loops with LangGraph.
    """
    objective: str = Field(..., description="High-level objective")
    context: Dict[str, Any] = Field(..., description="Task context and data")
    constraints: Dict[str, Any] = Field(
        default_factory=dict,
        description="Constraints (time, cost, etc.)"
    )
    max_iterations: int = Field(5, description="Max Plan-Act-Critique iterations")
    require_critique: bool = Field(True, description="Whether to critique results")


class WorkflowOutput(BaseModel):
    """
    Output from complex workflow agents (Level 4).
    
    Includes plan, execution results, and critiques.
    """
    objective: str = Field(..., description="Original objective")
    plan: List[TaskStep] = Field(..., description="Generated plan")
    execution_results: Dict[str, Any] = Field(..., description="Execution results")
    critiques: List[str] = Field(default_factory=list, description="Critiques of execution")
    final_status: TaskStatus = Field(..., description="Final task status")
    iterations: int = Field(..., description="Number of iterations performed")
    total_time_seconds: float = Field(..., description="Total execution time")
    optimizations_applied: List[str] = Field(
        default_factory=list,
        description="Optimizations that were applied"
    )


# ============================================================================
# Level 5: Multi-Agent Collaboration Schemas
# ============================================================================

class AgentCapabilityInfo(BaseModel):
    """Agent capability information for multi-agent systems."""
    agent_id: str = Field(..., description="Agent identifier")
    agent_name: str = Field(..., description="Agent name")
    capabilities: List[str] = Field(..., description="List of capabilities")
    availability: float = Field(1.0, ge=0.0, le=1.0, description="Availability (0-1)")
    performance_score: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Historical performance"
    )


class CollaborationRequest(BaseModel):
    """
    Request for multi-agent collaboration (Level 5).
    
    Supports A2A protocol, MCP, and cross-framework communication.
    """
    task_id: str = Field(..., description="Task identifier")
    initiating_agent: str = Field(..., description="Agent initiating collaboration")
    required_capabilities: List[str] = Field(..., description="Required capabilities")
    task_data: Dict[str, Any] = Field(..., description="Task data")
    collaboration_mode: str = Field(
        "sequential",
        description="Mode: sequential, parallel, consensus"
    )
    timeout_seconds: float = Field(60.0, description="Collaboration timeout")
    use_a2a: bool = Field(False, description="Use A2A protocol for external agents")


class CollaborationResponse(BaseModel):
    """
    Response from multi-agent collaboration (Level 5).
    
    Aggregates results from multiple agents.
    """
    task_id: str = Field(..., description="Task identifier")
    participating_agents: List[str] = Field(..., description="Agents that participated")
    individual_results: Dict[str, Any] = Field(
        ...,
        description="Results from each agent"
    )
    aggregated_result: Dict[str, Any] = Field(..., description="Combined result")
    consensus_reached: bool = Field(..., description="Whether consensus was reached")
    collaboration_time_seconds: float = Field(..., description="Total collaboration time")
    a2a_agents_used: List[str] = Field(
        default_factory=list,
        description="External A2A agents that were called"
    )


# ============================================================================
# Universal Agent Input/Output (All Levels)
# ============================================================================

class UniversalInput(BaseModel):
    """
    Universal input schema that works across all levels.
    
    Use this for maximum flexibility when you don't know
    the specific level or want to support multiple levels.
    """
    data: Dict[str, Any] = Field(..., description="Input data (flexible)")
    user_id: Optional[str] = Field(None, description="User identifier")
    request_id: Optional[str] = Field(None, description="Request identifier")
    agent_level: Optional[int] = Field(None, ge=1, le=5, description="Learning level (1-5)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class UniversalOutput(BaseModel):
    """
    Universal output schema that works across all levels.
    
    Use this for maximum flexibility.
    """
    result: Dict[str, Any] = Field(..., description="Result data (flexible)")
    success: bool = Field(True, description="Whether operation succeeded")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence score")
    error: Optional[str] = Field(None, description="Error message if failed")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


# ============================================================================
# Helper Functions
# ============================================================================

def get_input_schema_for_level(level: int):
    """Get appropriate input schema for learning level."""
    schemas = {
        1: ChatInput,
        2: ContextAwareInput,
        3: APIRequest,
        4: WorkflowInput,
        5: CollaborationRequest
    }
    return schemas.get(level, UniversalInput)


def get_output_schema_for_level(level: int):
    """Get appropriate output schema for learning level."""
    schemas = {
        1: ChatOutput,
        2: ContextAwareOutput,
        3: APIResponse,
        4: WorkflowOutput,
        5: CollaborationResponse
    }
    return schemas.get(level, UniversalOutput)

