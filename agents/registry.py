"""
Agent registry and routing.

Principle: Lightweight orchestration metadata
- Keeps agent definition separate from execution
- Central registry of all agent types
- Route requests to appropriate agents
"""

from typing import Type, Dict, Any, Optional
import logging

from .base import Agent, AgentType, ExecutionPriority, AgentExecutionError
from .execution import AgentRunner, ExecutionMode
from shared.schemas import AgentInput, AgentOutput


logger = logging.getLogger(__name__)


class AgentMetadata:
    """
    Metadata for registered agent.
    
    Keeps orchestration metadata separate from agent code.
    """
    
    def __init__(
        self,
        agent_class: Type[Agent],
        agent_type: AgentType,
        execution_mode: ExecutionMode,
        priority: ExecutionPriority,
        timeout: int,
        retry_policy: str = "exponential",
        max_retries: int = 3,
        config: Optional[Dict[str, Any]] = None
    ):
        self.agent_class = agent_class
        self.agent_type = agent_type
        self.execution_mode = execution_mode
        self.priority = priority
        self.timeout = timeout
        self.retry_policy = retry_policy
        self.max_retries = max_retries
        self.config = config or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "class_name": self.agent_class.__name__,
            "agent_type": self.agent_type.value,
            "execution_mode": self.execution_mode.value,
            "priority": self.priority.value,
            "timeout": self.timeout,
            "retry_policy": self.retry_policy,
            "max_retries": self.max_retries,
        }


class AgentRegistry:
    """
    Central registry of all agent types.
    
    Manages:
    - Agent type registration
    - Metadata storage
    - Configuration
    
    Principle: Lightweight orchestration metadata
    """
    
    def __init__(self):
        self._agents: Dict[str, AgentMetadata] = {}
        logger.info("AgentRegistry initialized")
    
    def register(
        self,
        agent_name: str,
        agent_class: Type[Agent],
        execution_mode: ExecutionMode = ExecutionMode.RAY_TASK,
        timeout: Optional[int] = None,
        retry_policy: str = "exponential",
        max_retries: int = 3,
        config: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Register agent with metadata.
        
        Args:
            agent_name: Unique agent identifier
            agent_class: Agent class
            execution_mode: How to execute agent
            timeout: Timeout in seconds (uses agent default if None)
            retry_policy: Retry policy name
            max_retries: Maximum retry attempts
            config: Agent-specific configuration
        
        Example:
            registry.register(
                "narrative",
                NarrativeAgent,
                execution_mode=ExecutionMode.RAY_TASK,
                timeout=30
            )
        """
        
        # Get agent type and priority from class
        agent_type = agent_class.agent_type
        priority = agent_class.execution_priority
        
        # Use agent's default timeout if not specified
        if timeout is None:
            timeout = agent_class.timeout_seconds
        
        metadata = AgentMetadata(
            agent_class=agent_class,
            agent_type=agent_type,
            execution_mode=execution_mode,
            priority=priority,
            timeout=timeout,
            retry_policy=retry_policy,
            max_retries=max_retries,
            config=config
        )
        
        self._agents[agent_name] = metadata
        
        logger.info(
            f"Registered agent: {agent_name} "
            f"(type={agent_type.value}, mode={execution_mode.value})"
        )
    
    def get(self, agent_name: str) -> AgentMetadata:
        """
        Get agent metadata.
        
        Args:
            agent_name: Agent identifier
            
        Returns:
            Agent metadata
            
        Raises:
            KeyError: If agent not registered
        """
        if agent_name not in self._agents:
            raise KeyError(f"Agent not registered: {agent_name}")
        
        return self._agents[agent_name]
    
    def list_agents(self) -> Dict[str, Dict[str, Any]]:
        """
        List all registered agents.
        
        Returns:
            Dictionary of agent names to metadata
        """
        return {
            name: metadata.to_dict()
            for name, metadata in self._agents.items()
        }
    
    def get_by_type(self, agent_type: AgentType) -> Dict[str, AgentMetadata]:
        """
        Get all agents of specific type.
        
        Args:
            agent_type: Agent type filter
            
        Returns:
            Dictionary of matching agents
        """
        return {
            name: metadata
            for name, metadata in self._agents.items()
            if metadata.agent_type == agent_type
        }


class AgentRouter:
    """
    Route requests to appropriate agents.
    
    Provides:
    - Request routing based on agent name
    - Automatic execution backend selection
    - Retry logic
    - Telemetry integration
    
    Principle: Lightweight orchestration metadata
    
    Usage:
        # From YAML config (recommended for plug-and-play)
        router = AgentRouter.from_yaml("config/agents.yaml")
        
        # From dict config
        router = AgentRouter.from_config(config_dict)
        
        # Manual registry
        router = AgentRouter(registry)
    """
    
    def __init__(self, registry: AgentRegistry):
        """
        Initialize router.
        
        Args:
            registry: Agent registry
        """
        self.registry = registry
        self._runners: Dict[ExecutionMode, AgentRunner] = {}
        logger.info("AgentRouter initialized")
    
    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> "AgentRouter":
        """
        Create router from configuration dictionary.
        
        Enables plug-and-play deployment without code changes.
        
        Args:
            config: Configuration dictionary with agent definitions
            
        Returns:
            Configured AgentRouter
            
        Raises:
            AgentConfigError: If configuration is invalid
        
        Example:
            config = {
                "agents": {
                    "narrative": {
                        "class": "fraud_agents.NarrativeAgent",
                        "execution_mode": "async",
                        "enabled": True,
                        "timeout": 30
                    }
                }
            }
            router = AgentRouter.from_config(config)
        """
        from .config import AgentConfig
        
        # Create registry from config
        registry = AgentConfig.create_registry(config)
        
        # Create router
        return cls(registry)
    
    @classmethod
    def from_yaml(cls, path: str) -> "AgentRouter":
        """
        Create router from YAML configuration file.
        
        Enables plug-and-play deployment - customers just provide YAML config.
        
        Args:
            path: Path to YAML config file
            
        Returns:
            Configured AgentRouter
            
        Raises:
            AgentConfigError: If file not found or invalid
        
        Example:
            # config/agents.yaml:
            # agents:
            #   narrative:
            #     class: "fraud_agents.NarrativeAgent"
            #     execution_mode: "async"
            #     enabled: true
            
            router = AgentRouter.from_yaml("config/agents.yaml")
            result = await router.route("narrative", request)
        """
        from .config import AgentConfig
        
        # Load config from YAML
        config = AgentConfig.from_yaml(path)
        
        # Create router from config
        return cls.from_config(config)
    
    def _get_runner(self, mode: ExecutionMode) -> AgentRunner:
        """Get or create runner for execution mode."""
        
        if mode not in self._runners:
            self._runners[mode] = AgentRunner(mode=mode)
        
        return self._runners[mode]
    
    async def route(
        self,
        agent_name: str,
        request: AgentInput,
        override_timeout: Optional[float] = None
    ) -> AgentOutput:
        """
        Route request to agent.
        
        Args:
            agent_name: Agent to invoke
            request: Agent input
            override_timeout: Override configured timeout
            
        Returns:
            Agent output
            
        Raises:
            KeyError: If agent not registered
            AgentExecutionError: If execution fails
        
        Example:
            router = AgentRouter(registry)
            result = await router.route("narrative", agent_input)
        """
        
        # Get agent metadata
        metadata = self.registry.get(agent_name)
        
        # Get runner for execution mode
        runner = self._get_runner(metadata.execution_mode)
        
        # Determine timeout
        timeout = override_timeout or metadata.timeout
        
        logger.info(
            f"Routing to agent: {agent_name} "
            f"(mode={metadata.execution_mode.value}, timeout={timeout}s)"
        )
        
        # Execute with retries
        last_error = None
        for attempt in range(metadata.max_retries):
            try:
                result = await runner.execute(
                    agent_class=metadata.agent_class,
                    request=request,
                    timeout=timeout
                )
                
                logger.info(
                    f"Agent {agent_name} completed successfully "
                    f"(attempt {attempt + 1})"
                )
                
                return result
            
            except Exception as e:
                last_error = e
                logger.warning(
                    f"Agent {agent_name} failed (attempt {attempt + 1}): {str(e)}"
                )
                
                # Don't retry if max attempts reached
                if attempt == metadata.max_retries - 1:
                    break
                
                # Apply retry delay based on policy
                if metadata.retry_policy == "exponential":
                    import asyncio
                    delay = 2 ** attempt  # 1s, 2s, 4s, ...
                    await asyncio.sleep(delay)
        
        # All retries failed
        raise AgentExecutionError(
            message=f"Agent {agent_name} failed after {metadata.max_retries} attempts",
            agent_id=agent_name,
            request_id=request.request_id,
            original_error=last_error
        )
    
    async def route_critical_path(
        self,
        request: AgentInput
    ) -> AgentOutput:
        """
        Route to first available critical path agent.
        
        Critical path agents must be fast (<50ms) and return risk scores.
        
        Args:
            request: Agent input
            
        Returns:
            Agent output with risk score
        """
        
        # Get all critical path agents
        critical_agents = self.registry.get_by_type(AgentType.CRITICAL_PATH)
        
        if not critical_agents:
            raise ValueError("No critical path agents registered")
        
        # Use first critical path agent
        # TODO: Could implement load balancing here
        agent_name = next(iter(critical_agents.keys()))
        
        return await self.route(agent_name, request)
    
    async def route_enrichment(
        self,
        request: AgentInput,
        risk_score: float
    ) -> AgentOutput:
        """
        Route to appropriate enrichment agent based on risk score.
        
        High-risk transactions get immediate enrichment.
        Low-risk transactions can be enriched asynchronously.
        
        Args:
            request: Agent input
            request: Risk score from critical path
            
        Returns:
            Agent output with narrative
        """
        
        # Get all enrichment agents
        enrichment_agents = self.registry.get_by_type(AgentType.ENRICHMENT)
        
        if not enrichment_agents:
            raise ValueError("No enrichment agents registered")
        
        # Select agent based on risk score
        # TODO: Could implement more sophisticated routing
        agent_name = next(iter(enrichment_agents.keys()))
        
        # Add risk score to request metadata
        request.transaction.ml_risk_score = risk_score
        
        return await self.route(agent_name, request)
    
    async def initialize(self) -> None:
        """Initialize all runners."""
        for runner in self._runners.values():
            await runner.initialize()
    
    async def cleanup(self) -> None:
        """Clean up all runners."""
        for runner in self._runners.values():
            await runner.cleanup()
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.cleanup()

