"""
Tests for agent base classes.

Basic smoke tests to ensure core functionality works.
"""

import pytest
from datetime import datetime
from agents import (
    Agent,
    CriticalPathAgent,
    EnrichmentAgent,
    AgentType,
    ExecutionPriority,
)
from shared.schemas import AgentInput, AgentOutput, Transaction


class TestAgentInterface:
    """Test agent base interface."""
    
    def test_agent_types_exist(self):
        """Ensure agent types are defined."""
        assert AgentType.CRITICAL_PATH
        assert AgentType.ENRICHMENT
        assert AgentType.ORCHESTRATION
    
    def test_execution_priority_exists(self):
        """Ensure execution priorities are defined."""
        assert ExecutionPriority.CRITICAL
        assert ExecutionPriority.HIGH
        assert ExecutionPriority.NORMAL
        assert ExecutionPriority.LOW


class SimpleCriticalPathAgent(CriticalPathAgent):
    """Test implementation of critical path agent."""
    
    async def score(self, request: AgentInput) -> float:
        """Return dummy score."""
        return 0.5


class SimpleEnrichmentAgent(EnrichmentAgent):
    """Test implementation of enrichment agent."""
    
    async def enrich(self, request: AgentInput, risk_score: float) -> str:
        """Return dummy narrative."""
        return f"Risk score: {risk_score}"


class TestCriticalPathAgent:
    """Test critical path agent."""
    
    @pytest.mark.asyncio
    async def test_critical_path_agent_process(self):
        """Test critical path agent can process request."""
        agent = SimpleCriticalPathAgent()
        
        # Create dummy request
        request = AgentInput(
            request_id="test_123",
            transaction=Transaction(
                id="txn_123",
                timestamp=datetime.utcnow(),
                amount=100.0,
                currency="USD",
            )
        )
        
        # Process
        result = await agent.process(request)
        
        # Verify
        assert isinstance(result, AgentOutput)
        assert result.request_id == "test_123"
        assert result.risk_score == 0.5
        assert result.latency_ms is not None
    
    def test_critical_path_timeout_default(self):
        """Test critical path has tight timeout."""
        agent = SimpleCriticalPathAgent()
        assert agent.timeout_seconds <= 1  # Must be fast!


class TestEnrichmentAgent:
    """Test enrichment agent."""
    
    @pytest.mark.asyncio
    async def test_enrichment_agent_process(self):
        """Test enrichment agent can process request."""
        agent = SimpleEnrichmentAgent()
        
        # Create dummy request
        request = AgentInput(
            request_id="test_123",
            transaction=Transaction(
                id="txn_123",
                timestamp=datetime.utcnow(),
                amount=100.0,
                currency="USD",
                ml_risk_score=0.8,
            )
        )
        
        # Process
        result = await agent.process(request)
        
        # Verify
        assert isinstance(result, AgentOutput)
        assert result.request_id == "test_123"
        assert "Risk score" in result.risk_narrative
        assert result.latency_ms is not None
    
    def test_enrichment_timeout_relaxed(self):
        """Test enrichment has relaxed timeout."""
        agent = SimpleEnrichmentAgent()
        assert agent.timeout_seconds >= 10  # Can be slower


class TestAgentMetadata:
    """Test agent metadata."""
    
    def test_agent_metadata(self):
        """Test agent exposes metadata."""
        agent = SimpleCriticalPathAgent()
        
        metadata = agent.get_metadata()
        
        assert "class_name" in metadata
        assert "agent_type" in metadata
        assert "priority" in metadata
        assert metadata["agent_type"] == AgentType.CRITICAL_PATH.value


@pytest.mark.asyncio
async def test_agent_lifecycle():
    """Test agent initialization and cleanup."""
    agent = SimpleCriticalPathAgent()
    
    # Initialize
    await agent.initialize()
    
    # Use
    request = AgentInput(
        request_id="test_123",
        transaction=Transaction(
            id="txn_123",
            timestamp=datetime.utcnow(),
            amount=100.0,
            currency="USD",
        )
    )
    result = await agent.process(request)
    assert result is not None
    
    # Cleanup
    await agent.cleanup()

