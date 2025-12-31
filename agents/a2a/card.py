"""
Agent Card Creation for A2A Protocol

Agent Cards are JSON documents that describe an agent's capabilities,
connection information, and interaction modalities.

Official Spec: https://a2a-protocol.org/docs/specification/agent-cards
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import json


@dataclass
class AgentCard:
    """
    Agent Card following official A2A specification.
    
    An Agent Card is a JSON document that describes:
    - Agent identity and metadata
    - Available skills/capabilities
    - Connection endpoints
    - Supported interaction modalities
    - Authentication requirements
    
    Official Schema: https://a2a-protocol.org/docs/specification/agent-cards
    """
    
    # Required fields
    name: str
    description: str
    url: str  # A2A endpoint URL
    skills: List[str]
    
    # Optional fields
    version: str = "1.0.0"
    author: Optional[str] = None
    license: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    
    # Interaction modalities
    supports_streaming: bool = False
    supports_push: bool = False
    media_types: List[str] = field(default_factory=lambda: ["text/plain", "application/json"])
    
    # Authentication
    auth_type: Optional[str] = None  # "bearer", "api_key", "oauth2", etc.
    auth_url: Optional[str] = None
    
    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to A2A Agent Card JSON format."""
        card = {
            "name": self.name,
            "description": self.description,
            "url": self.url,
            "version": self.version,
            "skills": self.skills,
            "modalities": {
                "streaming": self.supports_streaming,
                "push": self.supports_push,
                "mediaTypes": self.media_types
            }
        }
        
        # Optional fields
        if self.author:
            card["author"] = self.author
        if self.license:
            card["license"] = self.license
        if self.tags:
            card["tags"] = self.tags
        if self.auth_type:
            card["auth"] = {
                "type": self.auth_type,
                "url": self.auth_url
            }
        if self.metadata:
            card["metadata"] = self.metadata
        
        return card
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentCard":
        """Create AgentCard from dictionary."""
        modalities = data.get("modalities", {})
        auth = data.get("auth", {})
        
        return cls(
            name=data["name"],
            description=data["description"],
            url=data["url"],
            skills=data["skills"],
            version=data.get("version", "1.0.0"),
            author=data.get("author"),
            license=data.get("license"),
            tags=data.get("tags", []),
            supports_streaming=modalities.get("streaming", False),
            supports_push=modalities.get("push", False),
            media_types=modalities.get("mediaTypes", ["text/plain", "application/json"]),
            auth_type=auth.get("type"),
            auth_url=auth.get("url"),
            metadata=data.get("metadata", {})
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> "AgentCard":
        """Create AgentCard from JSON string."""
        return cls.from_dict(json.loads(json_str))


def create_agent_card(
    name: str,
    description: str,
    url: str,
    skills: List[str],
    **kwargs
) -> AgentCard:
    """
    Create an Agent Card for A2A protocol.
    
    Args:
        name: Agent name
        description: Agent description
        url: A2A endpoint URL (e.g., http://localhost:8080/a2a)
        skills: List of skills/capabilities
        **kwargs: Additional AgentCard fields
        
    Returns:
        AgentCard instance
        
    Example:
        card = create_agent_card(
            name="fraud_detector",
            description="Advanced fraud detection agent",
            url="http://localhost:8080/a2a",
            skills=["fraud_detection", "risk_analysis"],
            author="SOTA Framework",
            supports_streaming=True
        )
        
        # Publish card
        with open("agent_card.json", "w") as f:
            f.write(card.to_json())
    """
    return AgentCard(
        name=name,
        description=description,
        url=url,
        skills=skills,
        **kwargs
    )


def discover_agent_from_card(card_url: str) -> AgentCard:
    """
    Discover an agent by fetching its Agent Card.
    
    Args:
        card_url: URL to agent card JSON
        
    Returns:
        AgentCard instance
        
    Example:
        card = discover_agent_from_card(
            "https://example.com/agents/fraud_detector/card.json"
        )
        print(f"Found agent: {card.name}")
        print(f"Skills: {card.skills}")
    """
    import requests
    
    response = requests.get(card_url)
    response.raise_for_status()
    
    return AgentCard.from_dict(response.json())

