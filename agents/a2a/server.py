"""
A2A Protocol Server

Exposes SOTA agents via the official Agent2Agent protocol,
enabling communication with agents from any A2A-compliant framework.
"""

from typing import Optional, Dict, Any, List
import logging
from pathlib import Path

from agents.a2a import check_a2a_available, A2A_AVAILABLE

if A2A_AVAILABLE:
    from a2a import Server as A2AServerSDK, Task, TaskResponse

from agents.base import Agent
from agents.registry import AgentRouter
from .card import AgentCard, create_agent_card


logger = logging.getLogger(__name__)


class A2AServer:
    """
    A2A Protocol Server for SOTA Framework.
    
    Exposes SOTA agents via the official Agent2Agent protocol,
    enabling cross-framework agent communication.
    
    Features:
    - Automatic Agent Card generation
    - Task-based communication
    - JSON-RPC 2.0 over HTTP
    - Streaming support (SSE)
    - Integration with SOTA AgentRouter
    
    Usage:
        # Create server for agent
        server = A2AServer(
            agent=my_agent,
            name="fraud_detector",
            description="Fraud detection agent",
            port=8080
        )
        
        # Start server
        await server.start()
        
        # Agent Card available at http://localhost:8080/card.json
        # A2A endpoint at http://localhost:8080/a2a
    """
    
    def __init__(
        self,
        agent: Optional[Agent] = None,
        router: Optional[AgentRouter] = None,
        name: str = "sota_agent",
        description: str = "SOTA Framework Agent",
        skills: Optional[List[str]] = None,
        host: str = "0.0.0.0",
        port: int = 8080,
        card_path: Optional[str] = None,
        **card_kwargs
    ):
        """
        Initialize A2A server.
        
        Args:
            agent: Single agent to expose (or use router)
            router: AgentRouter with multiple agents
            name: Agent name
            description: Agent description
            skills: List of skills/capabilities
            host: Server host
            port: Server port
            card_path: Path to save Agent Card
            **card_kwargs: Additional Agent Card fields
        """
        check_a2a_available()
        
        if not agent and not router:
            raise ValueError("Must provide either agent or router")
        
        self.agent = agent
        self.router = router
        self.name = name
        self.description = description
        self.skills = skills or self._detect_skills()
        self.host = host
        self.port = port
        self.card_path = card_path or f"{name}_card.json"
        
        # Create Agent Card
        self.agent_card = create_agent_card(
            name=name,
            description=description,
            url=f"http://{host}:{port}/a2a",
            skills=self.skills,
            **card_kwargs
        )
        
        # Initialize A2A SDK server
        self.server = A2AServerSDK(
            agent_name=name,
            agent_description=description,
            skills=self.skills,
            port=port
        )
        
        # Register task handler
        self.server.on_task(self._handle_task)
        
        logger.info(
            f"A2A Server initialized for {name} on {host}:{port}"
        )
    
    def _detect_skills(self) -> List[str]:
        """Auto-detect skills from agent/router."""
        if self.agent:
            # Get skills from agent metadata
            metadata = self.agent.get_metadata()
            return [metadata.get("agent_type", "general")]
        elif self.router:
            # Get all registered agent types
            agents = self.router.registry.list_agents()
            return list(set(
                agents[name].get("agent_type", "general") 
                for name in agents
            ))
        return ["general"]
    
    async def _handle_task(self, task: Task) -> TaskResponse:
        """
        Handle incoming A2A task.
        
        Maps A2A task to SOTA agent execution.
        """
        try:
            logger.info(f"Handling A2A task: {task.id}")
            
            # Extract task data
            skill = task.skill
            input_data = task.input_data
            
            # Route to appropriate agent
            if self.agent:
                # Single agent mode
                result = await self.agent.process(input_data)
            elif self.router:
                # Router mode - route by skill
                result = await self.router.route(skill, input_data)
            else:
                raise ValueError("No agent or router configured")
            
            # Convert SOTA result to A2A response
            return TaskResponse(
                task_id=task.id,
                status="completed",
                output_data=result.model_dump() if hasattr(result, 'model_dump') else result,
                metadata={"framework": "SOTA"}
            )
            
        except Exception as e:
            logger.error(f"Error handling task {task.id}: {e}")
            return TaskResponse(
                task_id=task.id,
                status="failed",
                error=str(e),
                metadata={"framework": "SOTA"}
            )
    
    async def start(self):
        """Start A2A server."""
        # Save Agent Card
        self._save_agent_card()
        
        # Start server
        logger.info(f"Starting A2A server on {self.host}:{self.port}")
        logger.info(f"Agent Card: http://{self.host}:{self.port}/card.json")
        logger.info(f"A2A Endpoint: http://{self.host}:{self.port}/a2a")
        
        await self.server.start()
    
    async def stop(self):
        """Stop A2A server."""
        logger.info("Stopping A2A server")
        await self.server.stop()
    
    def _save_agent_card(self):
        """Save Agent Card to file."""
        card_file = Path(self.card_path)
        card_file.write_text(self.agent_card.to_json())
        logger.info(f"Agent Card saved to {card_file}")
    
    def get_agent_card(self) -> AgentCard:
        """Get Agent Card."""
        return self.agent_card
    
    def get_url(self) -> str:
        """Get A2A endpoint URL."""
        return f"http://{self.host}:{self.port}/a2a"


# Convenience function
async def serve_agent_via_a2a(
    agent: Agent,
    name: str,
    skills: List[str],
    port: int = 8080,
    **kwargs
) -> A2AServer:
    """
    Quick start: Serve an agent via A2A protocol.
    
    Args:
        agent: SOTA agent to expose
        name: Agent name
        skills: Agent skills/capabilities
        port: Server port
        **kwargs: Additional server options
        
    Returns:
        Running A2A server
        
    Example:
        from agents.a2a import serve_agent_via_a2a
        
        server = await serve_agent_via_a2a(
            agent=my_fraud_agent,
            name="fraud_detector",
            skills=["fraud_detection", "risk_analysis"],
            port=8080
        )
        
        # Agent now accessible via A2A protocol!
        # Other A2A agents can discover and use it
    """
    server = A2AServer(
        agent=agent,
        name=name,
        skills=skills,
        port=port,
        **kwargs
    )
    
    await server.start()
    return server

