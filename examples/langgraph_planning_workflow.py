"""
LangGraph Planning Workflow Example

Demonstrates autonomous planning, execution, critique, and re-planning
using LangGraph integration with Agent Framework.

Prerequisites:
    pip install agent-agent-framework[agent-frameworks]

Usage:
    python examples/langgraph_planning_workflow.py
"""

import asyncio
from agents import Agent, AgentType, ExecutionPriority, AgentRouter
from shared.schemas import AgentInput, AgentOutput
from orchestration.langgraph import (
    AgentWorkflowGraph,
    WorkflowConfig,
    create_planning_workflow,
    create_simple_workflow
)


# Example agents for demonstration
class DataEnrichmentAgent(Agent):
    """Enriches data with additional context."""

    agent_type = AgentType.ENRICHMENT
    execution_priority = ExecutionPriority.HIGH

    async def execute(self, input_data: AgentInput) -> AgentOutput:
        """Simulate data enrichment."""
        return AgentOutput(
            agent_name=self.name,
            result={
                "enriched": True,
                "additional_data": {"source": "external_api", "confidence": 0.85}
            },
            confidence_score=0.85,
            metadata={"execution_time_ms": 120}
        )


class FraudAnalysisAgent(Agent):
    """Analyzes for fraud indicators."""

    agent_type = AgentType.CRITICAL_PATH
    execution_priority = ExecutionPriority.CRITICAL

    async def execute(self, input_data: AgentInput) -> AgentOutput:
        """Simulate fraud analysis."""
        # Access previous results from workflow
        previous_results = input_data.metadata.get("previous_results", [])

        return AgentOutput(
            agent_name=self.name,
            result={
                "fraud_score": 0.25,
                "risk_level": "low",
                "indicators": ["normal_pattern", "verified_merchant"],
                "used_enrichment": len(previous_results) > 0
            },
            confidence_score=0.92,
            metadata={"execution_time_ms": 250}
        )


class RiskScoring

Agent(Agent):
    """Calculates final risk score."""

    agent_type = AgentType.ENRICHMENT
    execution_priority = ExecutionPriority.NORMAL

    async def execute(self, input_data: AgentInput) -> AgentOutput:
        """Simulate risk scoring."""
        return AgentOutput(
            agent_name=self.name,
            result={
                "final_risk_score": 0.15,
                "recommendation": "approve",
                "confidence": 0.88
            },
            confidence_score=0.88,
            metadata={"execution_time_ms": 80}
        )


async def example_1_simple_workflow():
    """Example 1: Simple workflow without replanning."""
    print("=" * 70)
    print("Example 1: Simple Planning Workflow")
    print("=" * 70)
    print()

    # Create agents
    enrichment = DataEnrichmentAgent({"name": "data_enrichment"})
    analysis = FraudAnalysisAgent({"name": "fraud_analysis"})
    scoring = RiskScoringAgent({"name": "risk_scoring"})

    # Create router
    from agents.registry import AgentRegistry
    registry = AgentRegistry()
    registry.register("data_enrichment", enrichment)
    registry.register("fraud_analysis", analysis)
    registry.register("risk_scoring", scoring)

    router = AgentRouter(registry)

    # Create simple workflow
    workflow = create_simple_workflow(router, max_iterations=2)

    # Execute
    print("🚀 Executing workflow with objective: Analyze transaction for fraud")
    print()

    result = await workflow.execute({
        "request_id": "txn-001",
        "objective": "Analyze transaction for fraud indicators",
        "request_data": {
            "transaction_id": "txn-123",
            "amount": 500.00,
            "merchant": "Example Store"
        }
    })

    # Display results
    print("✅ Workflow completed!")
    print(f"   Success: {result['success']}")
    print(f"   Iterations: {result['iterations']}")
    print(f"   Steps executed: {len(result['execution_results'])}")
    print()

    print("📋 Execution Plan:")
    for i, step in enumerate(result.get('plan', []), 1):
        print(f"   {i}. {step.get('description', 'N/A')}")
    print()

    print("📊 Execution Results:")
    for res in result['execution_results']:
        print(f"   Step {res['step']}: {res['agent']}")
        print(f"      Confidence: {res.get('confidence', 'N/A')}")
        print(f"      Result: {res['result']}")
    print()

    print("🎯 Final Result:")
    print(f"   {result['final_result']}")
    print()


async def example_2_planning_with_critique():
    """Example 2: Planning workflow with critique and potential replanning."""
    print("=" * 70)
    print("Example 2: Planning Workflow with Critique & Re-planning")
    print("=" * 70)
    print()

    # Create agents (same as above)
    enrichment = DataEnrichmentAgent({"name": "data_enrichment"})
    analysis = FraudAnalysisAgent({"name": "fraud_analysis"})
    scoring = RiskScoringAgent({"name": "risk_scoring"})

    from agents.registry import AgentRegistry
    registry = AgentRegistry()
    registry.register("data_enrichment", enrichment)
    registry.register("fraud_analysis", analysis)
    registry.register("risk_scoring", scoring)

    router = AgentRouter(registry)

    # Create planning workflow with higher iterations
    workflow = create_planning_workflow(
        router,
        max_iterations=5,
        critique_threshold=0.85
    )

    print("🚀 Executing workflow with complex objective")
    print("   This workflow can replan if results don't meet quality threshold")
    print()

    result = await workflow.execute({
        "request_id": "txn-002",
        "objective": "Comprehensive fraud analysis with high confidence",
        "request_data": {
            "transaction_id": "txn-456",
            "amount": 2500.00,
            "merchant": "Unknown Merchant",
            "customer_id": "cust-789"
        }
    })

    # Display results
    print("✅ Workflow completed!")
    print(f"   Success: {result['success']}")
    print(f"   Iterations: {result['iterations']}")
    print(f"   Steps executed: {len(result['execution_results'])}")
    print()

    if result.get('critique'):
        print("🔍 Critique:")
        critique = result['critique']
        print(f"   Confidence: {critique.get('confidence', 'N/A')}")
        print(f"   Feedback: {critique.get('feedback', 'N/A')}")
        if critique.get('recommendations'):
            print(f"   Recommendations:")
            for rec in critique['recommendations']:
                print(f"      - {rec}")
    print()


async def example_3_streaming_workflow():
    """Example 3: Stream workflow execution events."""
    print("=" * 70)
    print("Example 3: Streaming Workflow Execution")
    print("=" * 70)
    print()

    # Create agents
    enrichment = DataEnrichmentAgent({"name": "data_enrichment"})
    analysis = FraudAnalysisAgent({"name": "fraud_analysis"})

    from agents.registry import AgentRegistry
    registry = AgentRegistry()
    registry.register("data_enrichment", enrichment)
    registry.register("fraud_analysis", analysis)

    router = AgentRouter(registry)
    workflow = create_simple_workflow(router)

    print("🌊 Streaming workflow execution events...")
    print()

    async for event in workflow.stream_execute({
        "request_id": "txn-003",
        "objective": "Quick fraud check",
        "request_data": {"transaction_id": "txn-789", "amount": 100.00}
    }):
        # Print each state update
        for node_name, state_update in event.items():
            status = state_update.get('status', 'unknown')
            step = state_update.get('current_step', 0)
            print(f"   📍 Node: {node_name}, Status: {status}, Step: {step}")

    print()
    print("✅ Streaming complete!")
    print()


async def main():
    """Run all examples."""

    print("\n")
    print("🤖 " + "=" * 68)
    print("🤖 LangGraph Planning Workflow Examples")
    print("🤖 " + "=" * 68)
    print("\n")

    try:
        # Example 1
        await example_1_simple_workflow()

        # Example 2
        await example_2_planning_with_critique()

        # Example 3
        await example_3_streaming_workflow()

    except ImportError as e:
        print("❌ LangGraph not installed!")
        print("   Install with: pip install agent-agent-framework[agent-frameworks]")
        print(f"   Error: {e}")
        return
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return

    print("=" * 70)
    print("✨ All examples completed successfully!")
    print("=" * 70)
    print()
    print("📚 Key Takeaways:")
    print("   1. Plan → Execute → Critique → Replan loops")
    print("   2. Autonomous task decomposition")
    print("   3. Self-correcting workflows")
    print("   4. Quality-aware execution")
    print()
    print("📖 Learn more:")
    print("   - docs/LANGGRAPH_INTEGRATION.md")
    print("   - orchestration/langgraph/")
    print()


if __name__ == "__main__":
    asyncio.run(main())
