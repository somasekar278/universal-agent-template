"""
Dynamic Tool Registry Example

Demonstrates runtime tool registration, semantic search, and capability discovery.

Prerequisites:
    pip install agent-agent-framework
    pip install sentence-transformers  # Optional, for semantic search

Usage:
    python examples/dynamic_tool_registry.py
"""

import asyncio
from agents.tool_registry import DynamicToolRegistry, ToolStatus, get_global_registry


# Example: Register tools at runtime
def setup_tools():
    """Set up example tools with rich metadata."""

    registry = get_global_registry()

    # Tool 1: Fraud Detector
    @registry.register_tool(
        name="fraud_detector_v2",
        version="2.1.0",
        description="Detects fraudulent patterns in financial transactions using ML models and rule-based checks",
        input_schema={
            "type": "object",
            "properties": {
                "transaction_id": {"type": "string"},
                "amount": {"type": "number"},
                "merchant": {"type": "string"}
            },
            "required": ["transaction_id", "amount"]
        },
        output_schema={
            "type": "object",
            "properties": {
                "fraud_score": {"type": "number"},
                "risk_level": {"type": "string"}
            }
        },
        capabilities=["fraud_detection", "risk_analysis", "transaction_analysis"],
        tags=["financial", "security", "ml-powered"],
        category="security",
        estimated_latency_ms=250,
        estimated_cost=0.002,
        rate_limit=1000,
        status=ToolStatus.ACTIVE
    )
    async def detect_fraud(transaction_id: str, amount: float, merchant: str):
        """Detect fraud in transaction."""
        # Simulated fraud detection
        fraud_score = 0.25 if amount < 1000 else 0.75
        risk_level = "low" if fraud_score < 0.5 else "high"

        return {
            "fraud_score": fraud_score,
            "risk_level": risk_level,
            "indicators": ["amount_check", "merchant_verification"]
        }

    # Tool 2: Data Enrichment
    @registry.register_tool(
        name="data_enricher",
        version="1.5.0",
        description="Enriches transaction data with merchant details, customer history, and geographic information",
        input_schema={
            "type": "object",
            "properties": {
                "transaction_data": {"type": "object"}
            }
        },
        output_schema={
            "type": "object",
            "properties": {
                "enriched_data": {"type": "object"}
            }
        },
        capabilities=["data_enrichment", "merchant_lookup", "customer_analysis"],
        tags=["data", "preprocessing"],
        category="enrichment",
        estimated_latency_ms=150,
        estimated_cost=0.001,
        status=ToolStatus.ACTIVE
    )
    async def enrich_data(transaction_data: dict):
        """Enrich transaction data."""
        return {
            "enriched_data": {
                **transaction_data,
                "merchant_info": {"verified": True, "risk_score": 0.1},
                "customer_history": {"transaction_count": 50, "avg_amount": 250.00}
            }
        }

    # Tool 3: Risk Scorer
    @registry.register_tool(
        name="risk_scorer",
        version="3.0.0",
        description="Calculates comprehensive risk score combining multiple factors including fraud, credit, and compliance risks",
        input_schema={
            "type": "object",
            "properties": {
                "fraud_score": {"type": "number"},
                "credit_score": {"type": "number"},
                "compliance_score": {"type": "number"}
            }
        },
        output_schema={
            "type": "object",
            "properties": {
                "final_risk_score": {"type": "number"},
                "recommendation": {"type": "string"}
            }
        },
        capabilities=["risk_scoring", "risk_analysis", "decision_support"],
        tags=["risk", "scoring", "decision"],
        category="analysis",
        estimated_latency_ms=80,
        estimated_cost=0.0005,
        status=ToolStatus.ACTIVE
    )
    async def score_risk(fraud_score: float, credit_score: float = 0.5, compliance_score: float = 0.5):
        """Calculate risk score."""
        final_score = (fraud_score * 0.5 + credit_score * 0.3 + compliance_score * 0.2)
        recommendation = "approve" if final_score < 0.5 else "review"

        return {
            "final_risk_score": final_score,
            "recommendation": recommendation
        }

    # Tool 4: Deprecated tool (shows lifecycle management)
    @registry.register_tool(
        name="old_fraud_checker",
        version="1.0.0",
        description="Legacy fraud detection system (deprecated)",
        input_schema={"type": "object"},
        output_schema={"type": "object"},
        capabilities=["fraud_detection"],
        tags=["legacy"],
        category="security",
        estimated_latency_ms=500,
        estimated_cost=0.005,
        status=ToolStatus.DEPRECATED,
        deprecated=True,
        deprecated_in_favor_of="fraud_detector_v2"
    )
    async def old_fraud_check(data: dict):
        """Old fraud checker (deprecated)."""
        return {"message": "This tool is deprecated. Use fraud_detector_v2 instead."}

    return registry


async def example_1_semantic_search():
    """Example 1: Semantic tool discovery."""
    print("=" * 70)
    print("Example 1: Semantic Tool Search")
    print("=" * 70)
    print()

    registry = setup_tools()

    # Natural language queries
    queries = [
        "detect fraudulent transactions",
        "enrich data with customer information",
        "calculate risk for financial decision",
        "analyze transaction patterns"
    ]

    for query in queries:
        print(f"📝 Query: \"{query}\"")
        tools = registry.search_tools(query, top_k=2)

        if tools:
            print(f"   Found {len(tools)} relevant tools:")
            for tool in tools:
                print(f"   - {tool.name} (v{tool.version})")
                print(f"     {tool.description[:80]}...")
                print(f"     Capabilities: {', '.join(tool.capabilities[:3])}")
        else:
            print("   No matching tools found")
        print()


async def example_2_capability_search():
    """Example 2: Capability-based discovery."""
    print("=" * 70)
    print("Example 2: Capability-Based Search")
    print("=" * 70)
    print()

    registry = setup_tools()

    # Find all capabilities
    capabilities = registry.list_capabilities()
    print(f"📋 Available capabilities ({len(capabilities)}):")
    for cap in capabilities:
        print(f"   - {cap}")
    print()

    # Search by specific capability
    capability = "fraud_detection"
    print(f"🔍 Tools with capability: {capability}")
    tools = registry.find_by_capability(capability)

    for tool in tools:
        print(f"   - {tool.name} (v{tool.version})")
        print(f"     Status: {tool.status.value}")
        print(f"     Deprecated: {tool.deprecated}")
        if tool.deprecated_in_favor_of:
            print(f"     Use instead: {tool.deprecated_in_favor_of}")
    print()


async def example_3_cost_optimization():
    """Example 3: Cost-aware tool selection."""
    print("=" * 70)
    print("Example 3: Cost-Aware Tool Selection")
    print("=" * 70)
    print()

    registry = setup_tools()

    capability = "risk_analysis"

    # Find cheapest tool
    cheapest = registry.get_cheapest_tool(capability)
    if cheapest:
        print(f"💰 Cheapest tool for '{capability}':")
        print(f"   {cheapest.name}")
        print(f"   Cost: ${cheapest.estimated_cost:.4f} per call")
        print(f"   Latency: {cheapest.estimated_latency_ms}ms")
    print()

    # Find fastest tool
    fastest = registry.get_fastest_tool(capability)
    if fastest:
        print(f"⚡ Fastest tool for '{capability}':")
        print(f"   {fastest.name}")
        print(f"   Latency: {fastest.estimated_latency_ms}ms")
        print(f"   Cost: ${fastest.estimated_cost:.4f} per call")
    print()


async def example_4_lifecycle_management():
    """Example 4: Tool lifecycle management."""
    print("=" * 70)
    print("Example 4: Lifecycle Management")
    print("=" * 70)
    print()

    registry = setup_tools()

    # Get active tools only
    active_tools = registry.get_active_tools()
    print(f"✅ Active tools: {len(active_tools)}")
    for tool in active_tools:
        print(f"   - {tool.name} (v{tool.version})")
    print()

    # Find deprecated tools
    all_tools = list(registry.tools.values())
    deprecated_tools = [t for t in all_tools if t.deprecated]

    print(f"⚠️  Deprecated tools: {len(deprecated_tools)}")
    for tool in deprecated_tools:
        print(f"   - {tool.name} (v{tool.version})")
        if tool.deprecated_in_favor_of:
            print(f"     → Migrate to: {tool.deprecated_in_favor_of}")
    print()


async def example_5_detailed_info():
    """Example 5: Get detailed tool information."""
    print("=" * 70)
    print("Example 5: Detailed Tool Information")
    print("=" * 70)
    print()

    registry = setup_tools()

    tool_name = "fraud_detector_v2"
    info = registry.get_tool_info(tool_name)

    if info:
        print(f"📄 Tool: {tool_name}")
        print(f"   Version: {info['version']}")
        print(f"   Description: {info['description'][:100]}...")
        print(f"   Capabilities: {', '.join(info['capabilities'])}")
        print(f"   Category: {info.get('category', 'N/A')}")
        print(f"   Status: {info['status']}")
        print()
        print(f"   Performance:")
        print(f"   - Latency: {info.get('estimated_latency_ms', 'N/A')}ms")
        print(f"   - Cost: ${info.get('estimated_cost', 'N/A')}")
        print()
        print(f"   Input Schema:")
        import json
        print(f"   {json.dumps(info['input_schema'], indent=6)[:200]}...")
    print()


async def example_6_registry_export():
    """Example 6: Export registry metadata."""
    print("=" * 70)
    print("Example 6: Registry Export")
    print("=" * 70)
    print()

    registry = setup_tools()

    # Export registry
    export = registry.export_registry()

    print(f"📦 Registry Export:")
    print(f"   Total tools: {len(export['tools'])}")
    print(f"   Capabilities: {len(export['capabilities'])}")
    print(f"   Categories: {len(export['categories'])}")
    print()

    print(f"   All categories: {', '.join(export['categories'])}")
    print(f"   All capabilities:")
    for cap in export['capabilities'][:5]:
        print(f"      - {cap}")
    if len(export['capabilities']) > 5:
        print(f"      ... and {len(export['capabilities']) - 5} more")
    print()


async def main():
    """Run all examples."""
    print("\n")
    print("🔧 " + "=" * 68)
    print("🔧 Dynamic Tool Registry Examples")
    print("🔧 " + "=" * 68)
    print("\n")

    try:
        await example_1_semantic_search()
        await example_2_capability_search()
        await example_3_cost_optimization()
        await example_4_lifecycle_management()
        await example_5_detailed_info()
        await example_6_registry_export()

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return

    print("=" * 70)
    print("✨ All examples completed successfully!")
    print("=" * 70)
    print()
    print("📚 Key Features:")
    print("   1. Runtime tool registration")
    print("   2. Semantic search (natural language)")
    print("   3. Capability-based discovery")
    print("   4. Cost-aware selection")
    print("   5. Lifecycle management (deprecation)")
    print("   6. Rich metadata (schemas, cost, latency)")
    print()
    print("📖 Learn more:")
    print("   - docs/TOOL_REGISTRY.md")
    print("   - agents/tool_registry.py")
    print()


if __name__ == "__main__":
    asyncio.run(main())
