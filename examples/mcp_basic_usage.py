"""
Basic MCP Integration Example

Demonstrates how to use MCP (Model Context Protocol) with SOTA Agent Framework.

Compatible with MCP v1.25.0+

Prerequisites:
    pip install sota-agent-framework[mcp]

Usage:
    python examples/mcp_basic_usage.py
    
Note:
    This example shows the API structure. To actually run MCP servers,
    you need to configure and start your MCP server processes.
"""

import asyncio
from agents import Agent, AgentType, ExecutionPriority
from shared.schemas import AgentInput, AgentOutput

# Optional: Import MCP client if available
try:
    from agents.mcp_client import AgentMCPClient
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("⚠️  MCP not available. Install with: pip install sota-agent-framework[mcp]")


class DataEnrichmentAgent(Agent):
    """
    Agent that enriches data using MCP servers.
    
    This example shows how to:
    1. Initialize MCP client
    2. Call MCP tools
    3. Handle MCP responses
    4. Gracefully fallback if MCP unavailable
    """
    
    agent_type = AgentType.ENRICHMENT
    execution_priority = ExecutionPriority.NORMAL
    timeout_seconds = 30
    
    def __init__(self, config: dict = None):
        super().__init__(config)
        self.mcp_enabled = MCP_AVAILABLE
        
        if self.mcp_enabled:
            # Initialize MCP client with configuration
            self.mcp_client = AgentMCPClient.from_config()
            print("✅ MCP client initialized")
        else:
            self.mcp_client = None
            print("ℹ️  Running without MCP")
    
    async def initialize(self) -> None:
        """Initialize agent resources."""
        await super().initialize()
        print(f"🚀 {self.name} initialized")
    
    async def execute(self, input_data: AgentInput) -> AgentOutput:
        """
        Execute enrichment with MCP tools.
        
        If MCP is available, enriches data using external tools.
        Otherwise, returns basic processing.
        """
        result = {
            "status": "processed",
            "agent": self.name,
            "mcp_enabled": self.mcp_enabled
        }
        
        if self.mcp_enabled and self.mcp_client:
            try:
                # Example 1: Query Databricks SQL
                sql_result = await self._query_data(input_data)
                result["sql_enrichment"] = sql_result
                
                # Example 2: Call enrichment service
                enrichment_result = await self._enrich_data(input_data)
                result["external_enrichment"] = enrichment_result
                
            except Exception as e:
                print(f"⚠️  MCP call failed: {e}")
                result["error"] = str(e)
                result["fallback"] = "Used local processing"
        else:
            # Fallback: basic processing without MCP
            result["processing"] = "local"
            result["data"] = input_data.request_data
        
        return AgentOutput(
            agent_name=self.name,
            result=result,
            confidence_score=0.85,
            metadata={
                "mcp_enabled": self.mcp_enabled,
                "execution_time_ms": 150
            }
        )
    
    async def _query_data(self, input_data: AgentInput) -> dict:
        """Query data using Databricks SQL MCP server."""
        if not self.mcp_client:
            return {}
        
        try:
            # Call MCP Databricks SQL server
            result = await self.mcp_client.call_databricks_sql(
                "query_table",
                {
                    "table": "transactions",
                    "query": f"SELECT * FROM transactions LIMIT 10",
                    "timeout": 30
                }
            )
            return {"rows": len(result.get("data", [])), "source": "databricks"}
        except Exception as e:
            print(f"⚠️  SQL query failed: {e}")
            return {"error": str(e)}
    
    async def _enrich_data(self, input_data: AgentInput) -> dict:
        """Enrich data using external enrichment MCP server."""
        if not self.mcp_client:
            return {}
        
        try:
            # Example: BIN lookup for credit card
            bin_number = input_data.request_data.get("card_bin", "559021")
            
            result = await self.mcp_client.call_enrichment(
                "lookup_bin",
                {
                    "bin": bin_number
                }
            )
            return {
                "bin": bin_number,
                "issuer": result.get("issuer", "unknown"),
                "country": result.get("country", "unknown"),
                "risk_level": result.get("risk_level", 0.0)
            }
        except Exception as e:
            print(f"⚠️  Enrichment failed: {e}")
            return {"error": str(e)}
    
    async def cleanup(self) -> None:
        """Cleanup agent resources."""
        await super().cleanup()
        if self.mcp_client:
            # Close MCP connections
            print("🔌 Closing MCP connections")


class MCPAwareOrchestrator(Agent):
    """
    Orchestrator that coordinates multiple MCP-enabled agents.
    """
    
    agent_type = AgentType.ORCHESTRATION
    execution_priority = ExecutionPriority.HIGH
    
    def __init__(self, config: dict = None):
        super().__init__(config)
        self.enrichment_agent = DataEnrichmentAgent({"name": "enrichment_1"})
    
    async def execute(self, input_data: AgentInput) -> AgentOutput:
        """Orchestrate multiple MCP calls."""
        
        # Initialize sub-agent
        await self.enrichment_agent.initialize()
        
        # Execute enrichment
        enrichment_result = await self.enrichment_agent.execute(input_data)
        
        # Aggregate results
        result = {
            "orchestration": "complete",
            "enrichment_status": enrichment_result.result.get("status"),
            "mcp_enabled": enrichment_result.result.get("mcp_enabled"),
            "confidence": enrichment_result.confidence_score
        }
        
        # Cleanup
        await self.enrichment_agent.cleanup()
        
        return AgentOutput(
            agent_name=self.name,
            result=result,
            confidence_score=0.9,
            metadata={"agents_executed": 1}
        )


async def main():
    """Main example execution."""
    
    print("=" * 60)
    print("MCP Integration Example")
    print("=" * 60)
    print()
    
    # Example 1: Single MCP-enabled agent
    print("📋 Example 1: Single Agent with MCP")
    print("-" * 60)
    
    agent = DataEnrichmentAgent({"name": "mcp_enrichment_agent"})
    await agent.initialize()
    
    # Create test input
    test_input = AgentInput(
        request_id="test-001",
        request_data={
            "card_bin": "559021",
            "amount": 1500.00,
            "merchant": "Test Merchant"
        },
        metadata={"test": True}
    )
    
    # Execute agent
    result = await agent.execute(test_input)
    
    print(f"\n✅ Result:")
    print(f"   Status: {result.result.get('status')}")
    print(f"   MCP Enabled: {result.result.get('mcp_enabled')}")
    print(f"   Confidence: {result.confidence_score}")
    
    if "sql_enrichment" in result.result:
        print(f"   SQL Enrichment: {result.result['sql_enrichment']}")
    if "external_enrichment" in result.result:
        print(f"   External Enrichment: {result.result['external_enrichment']}")
    
    await agent.cleanup()
    
    print()
    
    # Example 2: Orchestrator with MCP-enabled agents
    print("📋 Example 2: Orchestrator with MCP Agents")
    print("-" * 60)
    
    orchestrator = MCPAwareOrchestrator({"name": "mcp_orchestrator"})
    result = await orchestrator.execute(test_input)
    
    print(f"\n✅ Result:")
    print(f"   Orchestration: {result.result.get('orchestration')}")
    print(f"   Enrichment Status: {result.result.get('enrichment_status')}")
    print(f"   MCP Enabled: {result.result.get('mcp_enabled')}")
    print(f"   Overall Confidence: {result.confidence_score}")
    
    print()
    print("=" * 60)
    print("✨ Example completed successfully!")
    print("=" * 60)
    
    # Print next steps
    print("\n📚 Next Steps:")
    if not MCP_AVAILABLE:
        print("   1. Install MCP: pip install sota-agent-framework[mcp]")
        print("   2. Configure MCP servers (see docs/MCP_INTEGRATION.md)")
        print("   3. Run this example again")
    else:
        print("   1. Configure MCP servers (see docs/MCP_INTEGRATION.md)")
        print("   2. Start MCP servers locally or connect to remote ones")
        print("   3. Update MCP configuration with server URLs")
        print("   4. Build your own MCP-enabled agents!")
    
    print("\n📖 Documentation:")
    print("   - MCP Integration Guide: docs/MCP_INTEGRATION.md")
    print("   - MCP Client API: agents/mcp_client.py")
    print("   - MCP Schemas: shared/schemas/mcp_tools.py")


if __name__ == "__main__":
    asyncio.run(main())

