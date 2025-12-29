"""
Execution backend implementations.

Provides different ways to execute agents while keeping agent code unchanged.
"""

import asyncio
from concurrent.futures import ProcessPoolExecutor
from typing import Type, Optional, Dict, Any
import multiprocessing as mp

from .runner import ExecutionBackend, ExecutionMode
from agents.base import Agent
from shared.schemas import AgentInput, AgentOutput


class InProcessBackend(ExecutionBackend):
    """
    Execute agent in the same process.
    
    Use for:
    - Testing and development
    - Low-latency critical path agents
    - Simple deployments
    
    NOT truly ephemeral - same process.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._agent_cache = {}  # Cache agents for reuse
    
    async def execute(
        self,
        agent_class: Type[Agent],
        request: AgentInput,
        config: Optional[Dict[str, Any]] = None
    ) -> AgentOutput:
        """Execute agent in current process."""
        
        # Check cache (reuse agent if possible)
        cache_key = agent_class.__name__
        
        if cache_key not in self._agent_cache:
            # Instantiate agent
            agent = agent_class(config or self.config)
            await agent.initialize()
            self._agent_cache[cache_key] = agent
        else:
            agent = self._agent_cache[cache_key]
        
        # Execute
        result = await agent.process(request)
        
        return result
    
    async def initialize(self) -> None:
        """No initialization needed for in-process."""
        pass
    
    async def cleanup(self) -> None:
        """Clean up cached agents."""
        for agent in self._agent_cache.values():
            await agent.cleanup()
        self._agent_cache.clear()


class ProcessPoolBackend(ExecutionBackend):
    """
    Execute agent in process pool.
    
    Use for:
    - Bin-packing multiple agent types
    - Isolation between executions
    - CPU-bound agents
    
    More ephemeral than in-process, less than Ray.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.pool_size = config.get("pool_size", mp.cpu_count())
        self.executor: Optional[ProcessPoolExecutor] = None
    
    async def execute(
        self,
        agent_class: Type[Agent],
        request: AgentInput,
        config: Optional[Dict[str, Any]] = None
    ) -> AgentOutput:
        """Execute agent in process pool."""
        
        if self.executor is None:
            raise RuntimeError("Backend not initialized. Call initialize() first.")
        
        # Execute in process pool
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            self.executor,
            _execute_agent_in_process,
            agent_class,
            request,
            config or self.config
        )
        
        return result
    
    async def initialize(self) -> None:
        """Initialize process pool."""
        self.executor = ProcessPoolExecutor(
            max_workers=self.pool_size,
            mp_context=mp.get_context('spawn')  # Spawn for isolation
        )
    
    async def cleanup(self) -> None:
        """Shut down process pool."""
        if self.executor:
            self.executor.shutdown(wait=True)
            self.executor = None


def _execute_agent_in_process(
    agent_class: Type[Agent],
    request: AgentInput,
    config: Dict[str, Any]
) -> AgentOutput:
    """
    Execute agent in separate process.
    
    This function runs in a worker process, providing isolation.
    Agent is instantiated fresh each time (ephemeral!).
    """
    
    # Create new event loop for this process
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        # Instantiate agent (fresh!)
        agent = agent_class(config)
        
        # Initialize
        loop.run_until_complete(agent.initialize())
        
        # Execute
        result = loop.run_until_complete(agent.process(request))
        
        # Cleanup
        loop.run_until_complete(agent.cleanup())
        
        return result
    
    finally:
        loop.close()


class RayBackend(ExecutionBackend):
    """
    Execute agent using Ray (task or actor).
    
    Use for:
    - Distributed execution across cluster
    - True ephemeral agents (Ray tasks)
    - Auto-scaling
    - Best bin-packing
    
    Most sophisticated and scalable option.
    """
    
    def __init__(self, mode: ExecutionMode, config: Dict[str, Any]):
        self.mode = mode
        self.config = config
        self.ray_initialized = False
    
    async def execute(
        self,
        agent_class: Type[Agent],
        request: AgentInput,
        config: Optional[Dict[str, Any]] = None
    ) -> AgentOutput:
        """Execute agent using Ray."""
        
        if not self.ray_initialized:
            raise RuntimeError("Ray backend not initialized. Call initialize() first.")
        
        try:
            import ray
        except ImportError:
            raise RuntimeError(
                "Ray not installed. Install with: pip install ray[default]"
            )
        
        if self.mode == ExecutionMode.RAY_TASK:
            # Ephemeral Ray task
            result = await _execute_agent_ray_task.remote(
                agent_class,
                request,
                config or self.config
            )
            return await result
        
        elif self.mode == ExecutionMode.RAY_ACTOR:
            # Stateful Ray actor (hot pool)
            # TODO: Implement actor pool management
            raise NotImplementedError("Ray actor mode not yet implemented")
        
        else:
            raise ValueError(f"Unknown Ray mode: {self.mode}")
    
    async def initialize(self) -> None:
        """Initialize Ray."""
        try:
            import ray
            
            if not ray.is_initialized():
                # Connect to existing cluster or start local
                ray.init(
                    address=self.config.get("ray_address", "auto"),
                    ignore_reinit_error=True
                )
            
            self.ray_initialized = True
        
        except ImportError:
            raise RuntimeError(
                "Ray not installed. Install with: pip install ray[default]"
            )
    
    async def cleanup(self) -> None:
        """Cleanup Ray resources."""
        # Don't shutdown Ray - might be used by other components
        self.ray_initialized = False


# Ray remote function (must be defined at module level)
try:
    import ray
    
    @ray.remote
    async def _execute_agent_ray_task(
        agent_class: Type[Agent],
        request: AgentInput,
        config: Dict[str, Any]
    ) -> AgentOutput:
        """
        Execute agent as Ray task.
        
        TRUE EPHEMERAL:
        - Task spawned
        - Agent instantiated fresh
        - Executes
        - Task terminates
        - Resources freed
        """
        
        # Instantiate agent (ephemeral!)
        agent = agent_class(config)
        
        try:
            # Initialize
            await agent.initialize()
            
            # Execute
            result = await agent.process(request)
            
            return result
        
        finally:
            # Cleanup
            await agent.cleanup()

except ImportError:
    # Ray not installed - define placeholder
    def _execute_agent_ray_task(*args, **kwargs):
        raise RuntimeError("Ray not installed")

