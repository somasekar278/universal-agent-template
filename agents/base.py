"""
Base agent interface and abstractions.

Provides uniform interface for all agents, enabling pluggable execution backends
without changing agent code.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, Dict
from datetime import datetime
from enum import Enum

from shared.schemas import AgentInput, AgentOutput


class AgentType(str, Enum):
    """Agent type classification."""
    
    # Critical path agents (fast, required for decision)
    CRITICAL_PATH = "critical_path"
    
    # Enrichment agents (slower, adds context)
    ENRICHMENT = "enrichment"
    
    # Orchestration agents (coordinates other agents)
    ORCHESTRATION = "orchestration"


class ExecutionPriority(str, Enum):
    """Execution priority levels."""
    
    CRITICAL = "critical"  # <50ms SLA
    HIGH = "high"         # <100ms SLA
    NORMAL = "normal"     # <500ms SLA
    LOW = "low"           # Best effort


class Agent(ABC):
    """
    Base interface for all agents.
    
    All agents implement this interface, enabling:
    - Uniform invocation (process method)
    - Pluggable execution (in-process, Ray, serverless)
    - Consistent telemetry and tracing
    - Type safety via AgentInput/AgentOutput
    
    Principles implemented:
    1. Uniform agent interface - Standard process() method
    2. Async-first design - Primary interface is async
    3. Separation of concerns - Type classification
    """
    
    # Agent metadata (override in subclasses)
    agent_type: AgentType = AgentType.ENRICHMENT
    execution_priority: ExecutionPriority = ExecutionPriority.NORMAL
    timeout_seconds: int = 30
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize agent.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.agent_id = f"{self.__class__.__name__}_{id(self)}"
        self._initialized_at = datetime.utcnow()
    
    @abstractmethod
    async def process(self, request: AgentInput) -> AgentOutput:
        """
        Process request and return output.
        
        This is the PRIMARY interface all agents must implement.
        Async by default - enables non-blocking execution.
        
        Args:
            request: Standardized agent input
            
        Returns:
            Standardized agent output
            
        Raises:
            AgentExecutionError: If processing fails
        """
        pass
    
    async def initialize(self) -> None:
        """
        Initialize agent resources (hot pool setup).
        
        Called once when agent is loaded into hot pool:
        - Connect to Lakebase
        - Load prompts from Unity Catalog
        - Pre-fetch common data
        - Establish connections
        
        Override in subclasses if needed.
        """
        pass
    
    async def cleanup(self) -> None:
        """
        Clean up agent resources.
        
        Called when agent is being destroyed:
        - Close connections
        - Flush buffers
        - Release resources
        
        Override in subclasses if needed.
        """
        pass
    
    def process_sync(self, request: AgentInput) -> AgentOutput:
        """
        Synchronous wrapper for inline execution.
        
        USE SPARINGLY! Only for:
        - Critical path agents with tight SLAs
        - Agents with no I/O operations
        - Testing/debugging
        
        Prefer async process() method.
        
        Args:
            request: Standardized agent input
            
        Returns:
            Standardized agent output
        """
        import asyncio
        
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.process(request))
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get agent metadata for registry.
        
        Returns:
            Metadata dictionary
        """
        return {
            "class_name": self.__class__.__name__,
            "agent_type": self.agent_type.value,
            "priority": self.execution_priority.value,
            "timeout": self.timeout_seconds,
            "initialized_at": self._initialized_at.isoformat(),
        }


class CriticalPathAgent(Agent):
    """
    Base class for critical path agents.
    
    Critical path agents:
    - Must complete in <50ms
    - No LLM calls allowed
    - No external API calls
    - Fast ML model inference only
    - Required for decision-making
    
    Principle: Separation of concerns
    """
    
    agent_type = AgentType.CRITICAL_PATH
    execution_priority = ExecutionPriority.CRITICAL
    timeout_seconds = 1  # 1 second max (aim for <50ms)
    
    @abstractmethod
    async def score(self, request: AgentInput) -> float:
        """
        Fast scoring method.
        
        Returns risk score 0-1.
        Must complete in <50ms.
        """
        pass
    
    async def process(self, request: AgentInput) -> AgentOutput:
        """
        Process request with critical path constraints.
        
        Automatically tracks timing to ensure SLA compliance.
        """
        start_time = datetime.utcnow()
        
        # Get score (fast!)
        risk_score = await self.score(request)
        
        latency_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        # Warn if SLA violated
        if latency_ms > 50:
            import logging
            logging.warning(
                f"{self.__class__.__name__} exceeded 50ms SLA: {latency_ms:.2f}ms"
            )
        
        return AgentOutput(
            request_id=request.request_id,
            agent_id=self.agent_id,
            risk_score=risk_score,
            risk_narrative=f"Risk score: {risk_score:.3f}",
            recommended_action=self._score_to_action(risk_score),
            confidence_score=1.0,
            started_at=start_time,
            completed_at=datetime.utcnow(),
            latency_ms=latency_ms,
            model_name=self.__class__.__name__,
        )
    
    def _score_to_action(self, score: float) -> str:
        """Convert score to action."""
        if score > 0.8:
            return "decline"
        elif score > 0.5:
            return "review"
        else:
            return "approve"


class EnrichmentAgent(Agent):
    """
    Base class for enrichment agents.
    
    Enrichment agents:
    - Can take 200ms+
    - Can call LLMs
    - Can make external API calls
    - Generate narratives and context
    - Run asynchronously
    
    Principle: Separation of concerns
    """
    
    agent_type = AgentType.ENRICHMENT
    execution_priority = ExecutionPriority.NORMAL
    timeout_seconds = 30
    
    @abstractmethod
    async def enrich(self, request: AgentInput, risk_score: float) -> str:
        """
        Generate enrichment (narrative, context, etc.).
        
        Args:
            request: Agent input
            risk_score: Risk score from critical path
            
        Returns:
            Enrichment text (narrative, explanation, etc.)
        """
        pass
    
    async def process(self, request: AgentInput) -> AgentOutput:
        """
        Process with enrichment.
        
        Calls LLMs, generates narratives, etc.
        No tight SLA constraints.
        """
        start_time = datetime.utcnow()
        
        # Get risk score (might be in request metadata)
        risk_score = request.transaction.ml_risk_score or 0.5
        
        # Generate enrichment (can be slow)
        narrative = await self.enrich(request, risk_score)
        
        latency_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        return AgentOutput(
            request_id=request.request_id,
            agent_id=self.agent_id,
            risk_score=risk_score,
            risk_narrative=narrative,
            recommended_action=self._score_to_action(risk_score),
            confidence_score=0.8,
            started_at=start_time,
            completed_at=datetime.utcnow(),
            latency_ms=latency_ms,
            model_name=self.__class__.__name__,
        )
    
    def _score_to_action(self, score: float) -> str:
        """Convert score to action."""
        if score > 0.8:
            return "decline"
        elif score > 0.5:
            return "review"
        else:
            return "approve"


class AgentExecutionError(Exception):
    """Raised when agent execution fails."""
    
    def __init__(
        self,
        message: str,
        agent_id: str,
        request_id: str,
        original_error: Optional[Exception] = None
    ):
        super().__init__(message)
        self.agent_id = agent_id
        self.request_id = request_id
        self.original_error = original_error

