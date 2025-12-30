# MCP Integration Guide

**Model Context Protocol (MCP)** integration for SOTA Agent Framework.

**Compatible with MCP v1.25.0+**

## Overview

MCP enables agents to connect to external tools and data sources through a standardized protocol. The framework provides built-in MCP client support for seamless integration with stdio-based MCP servers.

## Quick Start

### 1. Install with MCP Support

```bash
pip install sota-agent-framework[mcp]
```

### 2. Use MCP Client in Your Agent

```python
from agents import Agent, AgentType
from agents.mcp_client import AgentMCPClient
from shared.schemas import AgentInput, AgentOutput

class MyAgent(Agent):
    agent_type = AgentType.ENRICHMENT
    
    def __init__(self, config: dict = None):
        super().__init__(config)
        # Initialize MCP client
        self.mcp_client = AgentMCPClient.from_config()
    
    async def execute(self, input_data: AgentInput) -> AgentOutput:
        # Call MCP server
        result = await self.mcp_client.call_databricks_sql(
            "query_table",
            {
                "table": "transactions",
                "query": "SELECT * FROM transactions LIMIT 10"
            }
        )
        
        return AgentOutput(
            agent_name=self.name,
            result=result,
            metadata={"mcp_enabled": True}
        )
```

## Configuration

### Environment Variables

```bash
# MCP server endpoints
export MCP_DATABRICKS_SQL_URL="http://localhost:8001"
export MCP_ENRICHMENT_URL="http://localhost:8002"
export MCP_GRAPH_URL="http://localhost:8003"

# Authentication (if needed)
export MCP_API_KEY="your-api-key"
```

### Configuration File

Create `config/mcp_config.yaml`:

```yaml
mcp_servers:
  databricks-sql:
    command: python
    args: ["mcp-servers/databricks_sql_server.py"]
    env:
      DATABRICKS_HOST: "${DATABRICKS_HOST}"
      DATABRICKS_TOKEN: "${DATABRICKS_TOKEN}"
    
  enrichment:
    command: python
    args: ["mcp-servers/enrichment_server.py"]
    env:
      API_KEY: "${ENRICHMENT_API_KEY}"
    
  lakebase:
    command: python
    args: ["mcp-servers/lakebase_server.py"]
    env:
      LAKEBASE_URL: "${LAKEBASE_URL}"
```

**Note**: MCP v1.25.0+ uses stdio-based communication with servers run as subprocesses.

## Available MCP Tools

### 1. Databricks SQL Server

Query Databricks tables and views:

```python
result = await mcp_client.call_databricks_sql(
    "query_table",
    {
        "table": "transactions",
        "query": "SELECT * WHERE amount > 1000",
        "limit": 100
    }
)
```

### 2. Enrichment Server

Enrich data with external APIs:

```python
result = await mcp_client.call_enrichment(
    "lookup_bin",
    {
        "bin": "559021"
    }
)
```

### 3. Graph Server

Query knowledge graphs:

```python
result = await mcp_client.call_graph(
    "find_connections",
    {
        "entity_id": "user_123",
        "depth": 2
    }
)
```

## Creating Custom MCP Servers

### 1. Server Structure

```
my-mcp-server/
├── server.py          # MCP server implementation
├── tools/            # Tool definitions
│   ├── __init__.py
│   └── my_tools.py
├── requirements.txt
└── README.md
```

### 2. Implement Server

```python
# server.py
from mcp.server import MCPServer
from tools.my_tools import MyToolSet

app = MCPServer(
    name="my-custom-server",
    version="1.0.0"
)

@app.tool("my_custom_tool")
async def my_custom_tool(param1: str, param2: int):
    """My custom MCP tool."""
    # Implementation
    return {"result": "success"}

if __name__ == "__main__":
    app.run(port=8004)
```

### 3. Register with Agent

```python
mcp_config = {
    "my_custom_server": {
        "url": "http://localhost:8004",
        "timeout": 30
    }
}

mcp_client = AgentMCPClient(mcp_config)
result = await mcp_client.call("my_custom_server", "my_custom_tool", {
    "param1": "value",
    "param2": 42
})
```

## Best Practices

### 1. Error Handling

```python
from agents.mcp_client import AgentMCPClient, MCPError

try:
    result = await mcp_client.call_databricks_sql("query_table", params)
except MCPError as e:
    # Handle MCP-specific errors
    logger.error(f"MCP call failed: {e}")
    # Fallback logic
```

### 2. Timeout Configuration

```python
# Configure per-call timeout
result = await mcp_client.call(
    "databricks_sql",
    "query_table",
    params,
    timeout=60  # Override default
)
```

### 3. Caching Results

```python
from functools import lru_cache

class MyAgent(Agent):
    @lru_cache(maxsize=100)
    def _cached_mcp_call(self, tool: str, params_hash: str):
        return self.mcp_client.call("server", tool, params)
```

### 4. Testing with Mock MCP

```python
# tests/test_my_agent.py
from unittest.mock import AsyncMock

async def test_agent_with_mcp():
    agent = MyAgent()
    agent.mcp_client.call = AsyncMock(return_value={"data": "test"})
    
    result = await agent.execute(test_input)
    
    assert result.success
    agent.mcp_client.call.assert_called_once()
```

## MCP Schema Integration

Use predefined MCP result schemas:

```python
from shared.schemas.mcp_tools import (
    BINLookupResult,
    IPGeolocationResult,
    DeviceFingerprintResult
)

# Parse MCP response
bin_data = BINLookupResult(**mcp_result)
print(f"Issuer: {bin_data.issuer}")
print(f"Country: {bin_data.country}")
print(f"Risk: {bin_data.risk_level}")
```

## Production Deployment

### 1. Service Discovery

Use environment-based configuration:

```python
# Production
MCP_DATABRICKS_SQL_URL=https://mcp.prod.company.com/databricks

# Staging
MCP_DATABRICKS_SQL_URL=https://mcp.staging.company.com/databricks

# Local
MCP_DATABRICKS_SQL_URL=http://localhost:8001
```

### 2. Load Balancing

```yaml
mcp_servers:
  databricks_sql:
    urls:
      - "https://mcp-1.prod.company.com/databricks"
      - "https://mcp-2.prod.company.com/databricks"
      - "https://mcp-3.prod.company.com/databricks"
    strategy: "round_robin"  # or "random", "least_connections"
```

### 3. Circuit Breaker

```python
from agents.mcp_client import AgentMCPClient

mcp_client = AgentMCPClient.from_config(
    circuit_breaker={
        "failure_threshold": 5,
        "recovery_timeout": 60,
        "half_open_max_calls": 3
    }
)
```

## Troubleshooting

### MCP Server Not Responding

```python
# Check MCP server health
status = await mcp_client.health_check("databricks_sql")
print(f"Server status: {status}")
```

### Connection Timeout

```bash
# Increase timeout in config
export MCP_TIMEOUT=120
```

### Authentication Errors

```bash
# Verify API key
export MCP_API_KEY="your-key"

# Or use token-based auth
export MCP_TOKEN="your-token"
```

## Examples

See working examples:
- `examples/mcp_basic_usage.py` - Basic MCP integration
- `examples/mcp_advanced.py` - Advanced patterns
- `examples/mcp_testing.py` - Testing strategies

## Resources

- [MCP Specification](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Framework MCP Client](../agents/mcp_client.py)
- [MCP Schemas](../shared/schemas/mcp_tools.py)

