"""
Example: Using MCP client from agents.

Shows how agents should call MCP servers (via client, not direct imports).
Works whether MCP servers are local or remote!
"""

import asyncio
from agents.mcp_client import AgentMCPClient


async def example_agent_with_mcp():
    """
    Example agent using MCP client.

    Key points:
    - No imports from mcp-servers/
    - Uses MCP client API
    - Works locally or remotely
    - No code changes needed when MCP servers extracted
    """

    # Initialize MCP client (reads config based on environment)
    mcp_client = AgentMCPClient.from_config()

    # OR from environment variables
    # mcp_client = AgentMCPClient.from_env()

    # Example 1: Query merchant data
    merchant_result = await mcp_client.query_table(
        query="""
        SELECT *
        FROM fraud_detection.telemetry.merchant_context
        WHERE merchant_id = 'mch_001'
        """
    )
    print(f"Merchant data: {merchant_result}")

    # Example 2: Get customer context from Lakebase
    customer_context = await mcp_client.get_customer_context("cust_001")
    print(f"Customer context: {customer_context}")

    # Example 3: Store prompt in Unity Catalog
    prompt_result = await mcp_client.store_prompt(
        name="fraud_narrative_v2",
        prompt="You are a fraud detection analyst...",
        version="2.0.0"
    )
    print(f"Prompt stored: {prompt_result}")

    # Example 4: Generic tool call
    result = await mcp_client.call_tool(
        server="databricks-sql",
        tool="create_table",
        arguments={
            "table_name": "high_risk_transactions",
            "schema": {
                "transaction_id": "STRING",
                "risk_score": "DOUBLE",
                "timestamp": "TIMESTAMP"
            }
        }
    )
    print(f"Table created: {result}")


async def example_narrative_agent():
    """
    Example narrative agent that uses MCP tools.

    Demonstrates realistic fraud detection workflow.
    """

    mcp_client = AgentMCPClient.from_config()

    # Simulated transaction
    transaction_id = "txn_123"
    merchant_id = "mch_001"
    customer_id = "cust_001"

    print(f"Analyzing transaction {transaction_id}...")

    # Step 1: Get merchant context (from Lakebase)
    merchant_context = await mcp_client.get_merchant_context(merchant_id)
    print(f"✓ Merchant context retrieved: {merchant_context.get('risk_tier')}")

    # Step 2: Get customer context (from Lakebase)
    customer_context = await mcp_client.get_customer_context(customer_id)
    print(f"✓ Customer context retrieved: {customer_context.get('account_age_days')} days old")

    # Step 3: Query historical transactions (from Delta via SQL Warehouse)
    history = await mcp_client.query_table(f"""
        SELECT COUNT(*) as txn_count, AVG(amount) as avg_amount
        FROM fraud_detection.transactions
        WHERE merchant_id = '{merchant_id}'
        AND timestamp >= CURRENT_DATE - INTERVAL 30 DAYS
    """)
    print(f"✓ Historical data: {history}")

    # Step 4: Generate narrative (using LLM - not shown)
    narrative = f"""
    High risk transaction detected:
    - Merchant: {merchant_context.get('name')} (risk tier: {merchant_context.get('risk_tier')})
    - Customer: {customer_context.get('account_age_days')} days old
    - Historical: {history.get('txn_count')} transactions in 30 days
    """

    # Step 5: Store result (to Delta via SQL Warehouse)
    await mcp_client.call_databricks_sql(
        "insert_data",
        {
            "table": "fraud_detection.agent_outputs",
            "data": {
                "transaction_id": transaction_id,
                "narrative": narrative,
                "timestamp": "2025-12-26T00:00:00Z"
            }
        }
    )
    print(f"✓ Result stored")

    return narrative


if __name__ == "__main__":
    print("=" * 60)
    print("Example 1: Basic MCP Client Usage")
    print("=" * 60)
    asyncio.run(example_agent_with_mcp())

    print("\n" + "=" * 60)
    print("Example 2: Narrative Agent with MCP")
    print("=" * 60)
    asyncio.run(example_narrative_agent())
