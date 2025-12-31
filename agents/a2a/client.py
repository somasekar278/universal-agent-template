"""
A2A Protocol Client

Connect to and communicate with external A2A-compliant agents.
"""

from typing import Dict, Any, Optional, List
import logging

from agents.a2a import check_a2a_available, A2A_AVAILABLE

if A2A_AVAILABLE:
    from a2a import Client as A2AClientSDK, Task

from .card import AgentCard, discover_agent_from_card


logger = logging.getLogger(__name__)


class A2AClient:
    """
    A2A Protocol Client for connecting to external agents.
    
    Enables SOTA agents to discover and communicate with external
    A2A-compliant agents across different frameworks and platforms.
    
    Features:
    - Agent discovery via Agent Cards
    - Task submission and tracking
    - Streaming responses
    - Cross-framework communication
    
    Usage:
        # Discover external agent
        client = A2AClient()
        agent_card = await client.discover(
            "https://example.com/agents/risk_analyzer/card.json"
        )
        
        # Submit task
        result = await client.execute_task(
            agent_url=agent_card.url,
            skill="risk_analysis",
            input_data={"transaction": transaction_data}
        )
    """
    
    def __init__(self):
        """Initialize A2A client."""
        check_a2a_available()
        self.discovered_agents: Dict[str, AgentCard] = {}
        logger.info("A2A Client initialized")
    
    async def discover(self, card_url: str) -> AgentCard:
        """
        Discover an external agent by fetching its Agent Card.
        
        Args:
            card_url: URL to Agent Card JSON
            
        Returns:
            AgentCard with agent metadata and capabilities
            
        Example:
            card = await client.discover(
                "https://risk-service.com/agent/card.json"
            )
            print(f"Discovered: {card.name}")
            print(f"Skills: {card.skills}")
        """
        logger.info(f"Discovering agent from {card_url}")
        
        card = discover_agent_from_card(card_url)
        
        # Cache discovered agent
        self.discovered_agents[card.name] = card
        
        logger.info(
            f"Discovered agent: {card.name} with skills {card.skills}"
        )
        
        return card
    
    async def execute_task(
        self,
        agent_url: str,
        skill: str,
        input_data: Dict[str, Any],
        timeout: float = 60.0,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Execute a task on an external A2A agent.
        
        Args:
            agent_url: A2A endpoint URL
            skill: Skill to invoke
            input_data: Task input data
            timeout: Timeout in seconds
            stream: Enable streaming response
            
        Returns:
            Task result
            
        Example:
            result = await client.execute_task(
                agent_url="http://external-agent.com/a2a",
                skill="fraud_detection",
                input_data={
                    "transaction": {
                        "amount": 1000,
                        "merchant": "ABC Corp"
                    }
                }
            )
            
            print(f"Risk score: {result['risk_score']}")
        """
        logger.info(f"Executing task on {agent_url}: {skill}")
        
        # Create A2A SDK client
        sdk_client = A2AClientSDK(agent_url)
        
        # Create task
        task = Task(
            skill=skill,
            input_data=input_data
        )
        
        # Submit task
        if stream:
            # Streaming response
            async for chunk in sdk_client.execute_task_stream(task):
                yield chunk
        else:
            # Single response
            response = await sdk_client.execute_task(task, timeout=timeout)
            
            if response.status == "completed":
                logger.info(f"Task completed: {response.task_id}")
                return response.output_data
            else:
                error_msg = f"Task failed: {response.error}"
                logger.error(error_msg)
                raise Exception(error_msg)
    
    async def query_skill(
        self,
        agent_url: str,
        skill: str
    ) -> Dict[str, Any]:
        """
        Query if an agent supports a skill.
        
        Args:
            agent_url: A2A endpoint URL
            skill: Skill to query
            
        Returns:
            Skill information
            
        Example:
            info = await client.query_skill(
                "http://agent.com/a2a",
                "fraud_detection"
            )
            
            if info["supported"]:
                # Agent supports this skill
                pass
        """
        sdk_client = A2AClientSDK(agent_url)
        return await sdk_client.query_skill(skill)
    
    def list_discovered_agents(self) -> List[AgentCard]:
        """List all discovered agents."""
        return list(self.discovered_agents.values())
    
    def get_discovered_agent(self, name: str) -> Optional[AgentCard]:
        """Get a discovered agent by name."""
        return self.discovered_agents.get(name)
    
    async def discover_marketplace(
        self,
        marketplace_url: str
    ) -> List[AgentCard]:
        """
        Discover agents from an A2A marketplace.
        
        Args:
            marketplace_url: URL to marketplace API
            
        Returns:
            List of agent cards
            
        Example:
            agents = await client.discover_marketplace(
                "https://agent-marketplace.com/api/agents"
            )
            
            for agent in agents:
                if "fraud_detection" in agent.skills:
                    print(f"Found fraud detector: {agent.name}")
        """
        import requests
        
        logger.info(f"Discovering agents from marketplace: {marketplace_url}")
        
        response = requests.get(marketplace_url)
        response.raise_for_status()
        
        agents_data = response.json()
        agent_cards = [
            AgentCard.from_dict(agent_data) 
            for agent_data in agents_data
        ]
        
        # Cache discovered agents
        for card in agent_cards:
            self.discovered_agents[card.name] = card
        
        logger.info(f"Discovered {len(agent_cards)} agents from marketplace")
        
        return agent_cards
    
    async def find_agents_by_skill(
        self,
        skill: str,
        marketplace_url: Optional[str] = None
    ) -> List[AgentCard]:
        """
        Find agents that support a specific skill.
        
        Args:
            skill: Skill to search for
            marketplace_url: Optional marketplace to search
            
        Returns:
            List of matching agent cards
            
        Example:
            agents = await client.find_agents_by_skill(
                "risk_analysis",
                marketplace_url="https://marketplace.com/api/agents"
            )
            
            # Use first matching agent
            if agents:
                result = await client.execute_task(
                    agent_url=agents[0].url,
                    skill="risk_analysis",
                    input_data={...}
                )
        """
        # Discover from marketplace if provided
        if marketplace_url:
            await self.discover_marketplace(marketplace_url)
        
        # Filter by skill
        matching_agents = [
            card for card in self.discovered_agents.values()
            if skill in card.skills
        ]
        
        logger.info(
            f"Found {len(matching_agents)} agents with skill '{skill}'"
        )
        
        return matching_agents


# Convenience function
async def call_external_agent(
    agent_url: str,
    skill: str,
    input_data: Dict[str, Any],
    timeout: float = 60.0
) -> Dict[str, Any]:
    """
    Quick call to external A2A agent.
    
    Args:
        agent_url: A2A endpoint URL
        skill: Skill to invoke
        input_data: Task input
        timeout: Timeout in seconds
        
    Returns:
        Task result
        
    Example:
        from agents.a2a import call_external_agent
        
        result = await call_external_agent(
            agent_url="http://external-service.com/a2a",
            skill="fraud_detection",
            input_data={"transaction": {...}}
        )
    """
    client = A2AClient()
    return await client.execute_task(agent_url, skill, input_data, timeout)
