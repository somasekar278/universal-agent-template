"""
Self-Improving Agent Using MCP Tools

This example demonstrates an agent that uses MCP tools for continuous self-improvement:
1. Monitors its own performance
2. Curates training data from high-quality traces
3. Triggers optimization when performance degrades

The agent uses the AgentMCPClient to interact with:
- MLflow MCP server (native) - for querying traces and metrics
- Databricks MCP server (custom) - for optimization and dataset curation
"""

import asyncio
import yaml
from pathlib import Path
from mcp import AgentMCPClient


async def main():
    """
    Example: Self-improving customer support agent
    """
    # Load configuration
    config_path = Path("config/agent_config.yaml")
    with open(config_path) as f:
        config = yaml.safe_load(f)

    # Create MCP client for the agent
    agent_name = "customer_support"
    client = AgentMCPClient(agent_name, config)

    print(f"\n{'='*80}")
    print(f"🤖 Self-Improving Agent Example: {agent_name}")
    print(f"{'='*80}\n")

    # Connect to MCP servers
    print("Connecting to MCP servers...")
    await client.connect()
    print("✅ Connected!\n")

    try:
        # ========================================================================
        # Pattern 1: Check Performance
        # ========================================================================
        print("=" * 80)
        print("Pattern 1: Performance Monitoring")
        print("=" * 80)

        performance = await client.check_my_performance(
            time_range_hours=24
        )

        print(f"\n📊 Performance Status: {performance.get('status', 'unknown').upper()}")
        print(f"   Metrics checked: {performance.get('time_range_hours')}h window")

        if performance.get("metrics"):
            for metric_name, metric_data in performance["metrics"].items():
                print(f"   - {metric_name}: {metric_data.get('current_value', 'N/A')}")

        if performance.get("violations"):
            print(f"\n⚠️  {len(performance['violations'])} threshold violations detected:")
            for violation in performance["violations"]:
                print(f"   - {violation['metric']}: {violation['current']} (threshold: {violation['threshold']})")
        else:
            print(f"\n✅ All metrics within acceptable ranges")

        # ========================================================================
        # Pattern 2: Query Best Traces
        # ========================================================================
        print("\n" + "=" * 80)
        print("Pattern 2: Learning from Best Executions")
        print("=" * 80)

        best_traces = await client.query_my_traces(
            filter_string="assessments.Correctness > 0.95",
            time_range_hours=24,
            limit=10
        )

        if best_traces.get("traces"):
            print(f"\n📈 Found {len(best_traces['traces'])} high-quality traces")
            print("   Top 3 examples:")
            for i, trace in enumerate(best_traces["traces"][:3], 1):
                correctness = trace.get("assessments", {}).get("Correctness", "N/A")
                print(f"   {i}. Correctness: {correctness}")
                print(f"      Input: {trace.get('inputs', {}).get('input', '')[:60]}...")
        else:
            print("\n📊 No high-quality traces found in the last 24h")

        # ========================================================================
        # Pattern 3: Auto-Curate Training Data
        # ========================================================================
        print("\n" + "=" * 80)
        print("Pattern 3: Automatic Dataset Curation")
        print("=" * 80)

        curation = await client.curate_from_my_traces(
            min_quality_score=0.95,
            time_range_hours=24,
            max_examples=50
        )

        if curation.get("success"):
            examples_added = curation.get("examples_added", 0)
            total_examples = curation.get("total_examples", 0)
            print(f"\n📚 Curation Results:")
            print(f"   - Examples added: {examples_added}")
            print(f"   - Total in dataset: {total_examples}")
        else:
            print(f"\n❌ Curation failed: {curation.get('error')}")

        # ========================================================================
        # Pattern 4: Analyze Trends
        # ========================================================================
        print("\n" + "=" * 80)
        print("Pattern 4: Performance Trend Analysis")
        print("=" * 80)

        trend = await client.analyze_my_trend(
            metric_name="Correctness",
            time_range_hours=168,  # 7 days
            bucket_hours=24
        )

        if trend.get("success"):
            direction = trend.get("trend_direction", "unknown")
            change = trend.get("change_percent", 0)

            print(f"\n📉 Trend Analysis (7 days):")
            print(f"   - Direction: {direction.upper()}")
            print(f"   - Change: {change:+.1f}%")
            print(f"   - Current: {trend.get('current_value', 'N/A')}")
            print(f"   - Previous: {trend.get('previous_value', 'N/A')}")

            if direction == "degrading" and abs(change) > 10:
                print(f"\n⚠️  Significant degradation detected!")

        # ========================================================================
        # Pattern 5: Trigger Optimization if Needed
        # ========================================================================
        print("\n" + "=" * 80)
        print("Pattern 5: Conditional Optimization")
        print("=" * 80)

        # Check if optimization is needed
        needs_optimization = (
            performance.get("status") == "critical" or
            (trend.get("trend_direction") == "degrading" and abs(trend.get("change_percent", 0)) > 15)
        )

        if needs_optimization:
            print("\n🚀 Optimization needed! Triggering...")

            reason = []
            if performance.get("status") == "critical":
                violations = [v["metric"] for v in performance.get("violations", [])]
                reason.append(f"Critical violations: {', '.join(violations)}")
            if trend.get("trend_direction") == "degrading":
                reason.append(f"Degrading trend: {trend.get('change_percent', 0):.1f}%")

            optimization = await client.trigger_my_optimization(
                reason=" | ".join(reason),
                optimization_method="both"
            )

            if optimization.get("success"):
                print(f"   ✅ Optimization started!")
                print(f"   - Job ID: {optimization.get('job_id', 'N/A')}")
                print(f"   - Status: {optimization.get('status', 'N/A')}")
                print(f"   - Reason: {optimization.get('reason', 'N/A')}")
            else:
                print(f"   ❌ Failed: {optimization.get('error')}")
        else:
            print("\n✅ Performance is acceptable - no optimization needed")

        # ========================================================================
        # Pattern 6: Full Improvement Cycle
        # ========================================================================
        print("\n" + "=" * 80)
        print("Pattern 6: Complete Self-Improvement Cycle")
        print("=" * 80)

        print("\n🔄 Running automated improvement cycle...")
        cycle_result = await client.run_self_improvement_cycle()

        print(f"\n📋 Cycle Summary:")
        print(f"   - Agent: {cycle_result.get('agent_name')}")
        print(f"   - Time: {cycle_result.get('timestamp')}")
        print(f"   - Result: {cycle_result.get('summary')}")

    finally:
        # Disconnect
        print("\n" + "=" * 80)
        print("Disconnecting from MCP servers...")
        await client.disconnect()
        print("✅ Disconnected")
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
