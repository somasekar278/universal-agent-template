"""
Official A2A Protocol Integration Example

Demonstrates how to use the Linux Foundation Agent2Agent (A2A) protocol
for cross-framework agent communication.

Official A2A Resources:
- GitHub: https://github.com/a2aproject/A2A
- Website: https://a2a-protocol.org/
- Spec: https://a2a-protocol.org/docs/specification

Prerequisites:
    pip install agent-agent-framework[a2a]
"""

import asyncio
import sys
from pathlib import Path

# Add framework to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from agents.a2a import (
        A2AServer,
        A2AClient,
        A2AAgent,
        create_agent_card,
        A2A_AVAILABLE
    )
except ImportError:
    print("❌ A2A not available")
    print("Install with: pip install agent-agent-framework[a2a]")
    print("or: pip install a2a-sdk")
    sys.exit(1)

from agents.base import Agent
from shared.schemas import AgentInput, AgentOutput


# ============================================================================
# Example 1: Expose a SOTA Agent via A2A Protocol
# ============================================================================

class SimpleFraudAgent(Agent):
    """Simple fraud detection agent."""

    async def process(self, request: AgentInput) -> AgentOutput:
        # Simulate fraud detection
        transaction = request.transaction
        amount = transaction.get("amount", 0)

        # Simple rule-based detection
        risk_score = min(amount / 10000, 1.0)  # Higher amounts = higher risk

        return AgentOutput(
            risk_score=risk_score,
            narrative=f"Fraud analysis complete. Risk: {risk_score:.2f}"
        )


async def example_expose_agent_via_a2a():
    """Example: Expose SOTA agent via A2A protocol."""

    print("\n" + "="*70)
    print("Example 1: Expose SOTA Agent via A2A Protocol")
    print("="*70)

    # Create SOTA agent
    fraud_agent = SimpleFraudAgent()

    # Expose via A2A
    server = A2AServer(
        agent=fraud_agent,
        name="fraud_detector",
        description="Simple fraud detection agent for demo",
        skills=["fraud_detection", "risk_analysis"],
        port=8080
    )

    print(f"\n✅ A2A Server configured:")
    print(f"   Name: fraud_detector")
    print(f"   Skills: fraud_detection, risk_analysis")
    print(f"   Agent Card: http://localhost:8080/card.json")
    print(f"   A2A Endpoint: http://localhost:8080/a2a")
    print(f"\n💡 Other A2A-compliant agents can now discover and use this agent!")
    print(f"💡 Works with agents built on LangChain, AutoGPT, CrewAI, etc.")

    # Note: In production, you would await server.start()
    # For demo purposes, we just show the setup


# ============================================================================
# Example 2: Discover and Call External A2A Agents
# ============================================================================

async def example_call_external_a2a_agent():
    """Example: Discover and call external A2A agent."""

    print("\n" + "="*70)
    print("Example 2: Discover and Call External A2A Agent")
    print("="*70)

    # Create A2A client
    client = A2AClient()

    print(f"\n📡 Discovering external agent...")
    print(f"   (In production, you would fetch from actual URL)")

    # Example: Discover agent from card URL
    # card = await client.discover(
    #     "https://external-service.com/agent/card.json"
    # )

    # For demo, show what the discovery would return
    print(f"\n✅ Discovered agent:")
    print(f"   Name: risk_analyzer")
    print(f"   Skills: risk_analysis, compliance_check")
    print(f"   URL: http://external-service.com/a2a")

    # Example: Execute task
    # result = await client.execute_task(
    #     agent_url="http://external-service.com/a2a",
    #     skill="risk_analysis",
    #     input_data={"transaction": {"amount": 1000}},
    #     timeout=60.0
    # )

    print(f"\n💡 With A2A, your SOTA agents can call:")
    print(f"   - LangChain agents")
    print(f"   - AutoGPT agents")
    print(f"   - CrewAI agents")
    print(f"   - Any A2A-compliant agent!")


# ============================================================================
# Example 3: Agent Cards for Discovery
# ============================================================================

def example_agent_cards():
    """Example: Create and publish Agent Cards."""

    print("\n" + "="*70)
    print("Example 3: Agent Cards for Discovery")
    print("="*70)

    # Create Agent Card
    card = create_agent_card(
        name="fraud_detector",
        description="Advanced fraud detection agent",
        url="http://localhost:8080/a2a",
        skills=["fraud_detection", "risk_analysis", "pattern_detection"],
        author="SOTA Framework",
        version="1.0.0",
        supports_streaming=True,
        tags=["fraud", "finance", "security"]
    )

    print(f"\n✅ Agent Card Created:")
    print(card.to_json())

    print(f"\n💡 Agent Cards enable:")
    print(f"   - Discovery of agent capabilities")
    print(f"   - Automatic skill matching")
    print(f"   - Version management")
    print(f"   - Authentication info")


# ============================================================================
# Example 4: A2A-Enabled Agent Calling External Agents
# ============================================================================

class SmartFraudAgent(A2AAgent):
    """
    Smart fraud agent that can call external A2A agents for help.
    """

    async def process(self, request: AgentInput) -> AgentOutput:
        # Do internal analysis
        transaction = request.transaction
        amount = transaction.get("amount", 0)
        my_risk_score = min(amount / 10000, 1.0)

        print(f"  🤖 My analysis: risk_score = {my_risk_score:.2f}")

        # If uncertain, call external agent
        if my_risk_score > 0.5 and my_risk_score < 0.8:
            print(f"  🤔 Uncertain... calling external risk analyzer")

            # In production:
            # external_result = await self.call_external_agent(
            #     agent_url="http://external-risk-service.com/a2a",
            #     skill="risk_analysis",
            #     input_data={"transaction": transaction}
            # )
            # my_risk_score = external_result["risk_score"]

            print(f"  ✅ Got second opinion from external agent")

        return AgentOutput(
            risk_score=my_risk_score,
            narrative="Combined analysis complete"
        )


async def example_smart_agent():
    """Example: Agent that calls external A2A agents."""

    print("\n" + "="*70)
    print("Example 4: Smart Agent Calling External Agents")
    print("="*70)

    # Create smart agent
    agent = SmartFraudAgent(
        name="smart_fraud_detector",
        skills=["fraud_detection"],
        description="Smart fraud detector with external consultation"
    )

    # Process transaction
    print(f"\n📊 Processing transaction...")
    result = await agent.process(AgentInput(
        transaction={"amount": 7500}  # Uncertain amount
    ))

    print(f"\n✅ Final result: {result.narrative}")
    print(f"   Risk Score: {result.risk_score:.2f}")

    print(f"\n💡 This agent can:")
    print(f"   - Do its own analysis")
    print(f"   - Call external A2A agents when uncertain")
    print(f"   - Discover agents by skill")
    print(f"   - Collaborate across frameworks")


# ============================================================================
# Main Demo
# ============================================================================

async def main():
    """Run all A2A examples."""

    print("\n" + "="*70)
    print("🌐 Official A2A Protocol Integration Examples")
    print("="*70)
    print("\nOfficial A2A Protocol (Linux Foundation):")
    print("  - GitHub: https://github.com/a2aproject/A2A")
    print("  - Website: https://a2a-protocol.org/")
    print("  - Maintained by: Google & Linux Foundation")
    print("\nWhat is A2A?")
    print("  An open protocol enabling communication between")
    print("  opaque agentic applications across different frameworks.")

    if not A2A_AVAILABLE:
        print("\n❌ A2A SDK not installed!")
        print("Install with: pip install agent-agent-framework[a2a]")
        print("or: pip install a2a-sdk")
        return

    # Run examples
    await example_expose_agent_via_a2a()
    await example_call_external_a2a_agent()
    example_agent_cards()
    await example_smart_agent()

    # Summary
    print("\n" + "="*70)
    print("📊 A2A Protocol Summary")
    print("="*70)
    print("""
Key Benefits:
  ✅ Cross-framework interoperability
  ✅ Industry standard (Linux Foundation)
  ✅ Agent discovery via Agent Cards
  ✅ Task-based collaboration
  ✅ Secure and scalable

When to Use:
  ✅ Building agent marketplaces
  ✅ Enterprise agent ecosystems
  ✅ Cross-platform agent communication
  ❌ Simple internal communication (use Router)
  ❌ Learning basics (start simple, add A2A at Level 5)

Integration with SOTA Framework:
  - Expose SOTA agents via A2A
  - Call external A2A agents from SOTA agents
  - Automatic Agent Card generation
  - Seamless with existing Router/LangGraph

Next Steps:
  1. See agents/a2a/ for full implementation
  2. Read https://a2a-protocol.org/docs/specification
  3. Try Level 5 in learning path (agent-learn start 5)
  4. Build cross-framework agent systems!
""")


if __name__ == "__main__":
    asyncio.run(main())
