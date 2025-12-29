"""
Agent execution runner with pluggable backends.

Principle: Pluggable execution engine
- Agent code stays the same
- Execution mode determined by runner configuration
- Easy to switch backends for different environments
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Type, Optional, Dict, Any
import asyncio

from agents.base import Agent, AgentExecutionError
from shared.schemas import AgentInput, AgentOutput


class ExecutionMode(str, Enum):
    """Execution backend modes."""
    
    IN_PROCESS = "in_process"      # Same process (testing, low latency)
    PROCESS_POOL = "process_pool"  # Process pool (bin-packing)
    RAY_TASK = "ray_task"          # Ray task (distributed, ephemeral)
    RAY_ACTOR = "ray_actor"        # Ray actor (stateful)
    SERVERLESS = "serverless"      # Serverless function (true ephemeral)


class ExecutionBackend(ABC):
    """
    Abstract execution backend.
    
    All backends implement this interface, enabling pluggable execution.
    """
    
    @abstractmethod
    async def execute(
        self,
        agent_class: Type[Agent],
        request: AgentInput,
        config: Optional[Dict[str, Any]] = None
    ) -> AgentOutput:
        """
        Execute agent and return output.
        
        Args:
            agent_class: Agent class to instantiate and run
            request: Agent input
            config: Optional execution config
            
        Returns:
            Agent output
            
        Raises:
            AgentExecutionError: If execution fails
        """
        pass
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize backend resources."""
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """Clean up backend resources."""
        pass


class AgentRunner:
    """
    Agent execution runner with pluggable backends.
    
    Usage:
        # Create runner with specific backend
        runner = AgentRunner(mode=ExecutionMode.RAY_TASK)
        
        # Execute agent - code stays the same regardless of backend!
        result = await runner.execute(NarrativeAgent, request)
        
        # Change backend - NO AGENT CODE CHANGES
        runner = AgentRunner(mode=ExecutionMode.PROCESS_POOL)
        result = await runner.execute(NarrativeAgent, request)
    
    Principles implemented:
    - Pluggable execution engine
    - Uniform agent interface
    """
    
    def __init__(
        self,
        mode: ExecutionMode = ExecutionMode.IN_PROCESS,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize runner with execution backend.
        
        Args:
            mode: Execution mode
            config: Backend-specific configuration
        """
        self.mode = mode
        self.config = config or {}
        self.backend = self._create_backend(mode)
    
    def _create_backend(self, mode: ExecutionMode) -> ExecutionBackend:
        """Create backend based on mode."""
        
        from .backends import (
            InProcessBackend,
            ProcessPoolBackend,
            RayBackend,
        )
        
        if mode == ExecutionMode.IN_PROCESS:
            return InProcessBackend(self.config)
        
        elif mode == ExecutionMode.PROCESS_POOL:
            return ProcessPoolBackend(self.config)
        
        elif mode in [ExecutionMode.RAY_TASK, ExecutionMode.RAY_ACTOR]:
            return RayBackend(mode, self.config)
        
        elif mode == ExecutionMode.SERVERLESS:
            # Placeholder for serverless backend
            raise NotImplementedError(
                "Serverless backend not yet implemented. "
                "Use RAY_TASK for similar ephemeral behavior."
            )
        
        else:
            raise ValueError(f"Unknown execution mode: {mode}")
    
    async def execute(
        self,
        agent_class: Type[Agent],
        request: AgentInput,
        timeout: Optional[float] = None
    ) -> AgentOutput:
        """
        Execute agent using configured backend.
        
        Args:
            agent_class: Agent class to execute
            request: Agent input
            timeout: Optional timeout in seconds (overrides agent default)
            
        Returns:
            Agent output
            
        Raises:
            AgentExecutionError: If execution fails
            asyncio.TimeoutError: If execution exceeds timeout
        """
        
        # Determine timeout
        if timeout is None:
            # Use agent's default timeout
            timeout = agent_class.timeout_seconds
        
        try:
            # Execute with timeout
            result = await asyncio.wait_for(
                self.backend.execute(agent_class, request, self.config),
                timeout=timeout
            )
            
            return result
        
        except asyncio.TimeoutError:
            raise AgentExecutionError(
                message=f"Agent execution exceeded timeout: {timeout}s",
                agent_id=agent_class.__name__,
                request_id=request.request_id,
            )
        
        except Exception as e:
            raise AgentExecutionError(
                message=f"Agent execution failed: {str(e)}",
                agent_id=agent_class.__name__,
                request_id=request.request_id,
                original_error=e,
            )
    
    async def initialize(self) -> None:
        """Initialize backend resources."""
        await self.backend.initialize()
    
    async def cleanup(self) -> None:
        """Clean up backend resources."""
        await self.backend.cleanup()
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.cleanup()

