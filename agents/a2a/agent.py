"""
A2A-enabled Agent Wrapper

Wraps SOTA agents to make them A2A-compatible.
"""

from typing import Dict, Any, List, Optional
import logging

from agents.base import Agent
from shared.schemas import AgentInput, AgentOutput
from .client import A2AClient


logger = logging.getLogger(__name__)


class A2AAgent(Agent):
    """
    A2A-enabled Agent.
    
    Wraps a SOTA agent to enable:
    - Exposing via A2A protocol
    - Calling external A2A agents
    - Cross-framework communication
    
    Usage:
        # Wrap existing agent
        fraud_agent = MyFraudAgent()
        a2a_agent = A2AAgent(
            agent=fraud_agent,
            name="fraud_detector",
            skills=["fraud_detection", "risk_analysis"]
        )
        
        # Expose via A2A
        from agents.a2a import serve_agent_via_a2a
        server = await serve_agent_via_a2a(
            agent=a2a_agent,
            name="fraud_detector",
            skills=a2a_agent.skills,
            port=8080
        )
        
        # Now accessible via A2A protocol!
    """
    
    def __init__(
        self,
        agent: Optional[Agent] = None,
        name: str = "agent",
        skills: Optional[List[str]] = None,
        description: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize A2A-enabled agent.
        
        Args:
            agent: Existing SOTA agent to wrap (optional)
            name: Agent name
            skills: List of skills/capabilities
            description: Agent description
            **kwargs: Additional Agent parameters
        """
        super().__init__(**kwargs)
        
        self.wrapped_agent = agent
        self.name = name
        self.skills = skills or []
        self.description = description or f"A2A-enabled {name}"
        
        # A2A client for calling external agents
        self.a2a_client = A2AClient()
        
        logger.info(f"A2AAgent '{name}' initialized with skills: {self.skills}")
    
    async def process(self, request: AgentInput) -> AgentOutput:
        """
        Process request.
        
        If wrapped agent exists, delegates to it.
        Otherwise, implement custom logic.
        """
        if self.wrapped_agent:
            return await self.wrapped_agent.process(request)
        else:
            # Implement custom A2A agent logic here
            raise NotImplementedError(
                "Either provide a wrapped_agent or override process() method"
            )
    
    async def call_external_agent(
        self,
        agent_url: str,
        skill: str,
        input_data: Dict[str, Any],
        timeout: float = 60.0
    ) -> Dict[str, Any]:
        """
        Call an external A2A agent.
        
        Args:
            agent_url: External agent A2A endpoint
            skill: Skill to invoke
            input_data: Task input
            timeout: Timeout
            
        Returns:
            Task result
            
        Example:
            class MyAgent(A2AAgent):
                async def process(self, request):
                    # Do my analysis
                    my_result = self.analyze(request)
                    
                    # Call external agent for additional insight
                    external_result = await self.call_external_agent(
                        agent_url="http://external.com/a2a",
                        skill="deep_analysis",
                        input_data={"data": request}
                    )
                    
                    # Combine results
                    return self.combine(my_result, external_result)
        """
        return await self.a2a_client.execute_task(
            agent_url=agent_url,
            skill=skill,
            input_data=input_data,
            timeout=timeout
        )
    
    async def discover_external_agent(
        self,
        card_url: str
    ):
        """
        Discover an external A2A agent.
        
        Args:
            card_url: URL to agent card
            
        Returns:
            AgentCard
            
        Example:
            card = await agent.discover_external_agent(
                "https://external-service.com/card.json"
            )
            
            if "fraud_detection" in card.skills:
                # Can collaborate with this agent
                result = await self.call_external_agent(
                    agent_url=card.url,
                    skill="fraud_detection",
                    input_data={...}
                )
        """
        return await self.a2a_client.discover(card_url)
    
    async def find_agents_with_skill(
        self,
        skill: str,
        marketplace_url: Optional[str] = None
    ):
        """
        Find external agents with a specific skill.
        
        Args:
            skill: Skill to search for
            marketplace_url: Optional marketplace URL
            
        Returns:
            List of AgentCards
            
        Example:
            # Find all agents that can do risk analysis
            agents = await self.find_agents_with_skill(
                "risk_analysis",
                marketplace_url="https://marketplace.com/api/agents"
            )
            
            # Use first match
            if agents:
                result = await self.call_external_agent(
                    agent_url=agents[0].url,
                    skill="risk_analysis",
                    input_data={...}
                )
        """
        return await self.a2a_client.find_agents_by_skill(
            skill=skill,
            marketplace_url=marketplace_url
        )
    
    def get_skills(self) -> List[str]:
        """Get agent skills."""
        return self.skills
    
    def get_description(self) -> str:
        """Get agent description."""
        return self.description

