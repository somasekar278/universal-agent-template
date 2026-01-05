# Using Existing MCP Servers

Guide to configuring your agents to use existing/managed MCP servers.

---

## What Are MCP Servers?

MCP (Model Context Protocol) servers expose **tools** that agents can call. These could be:
- Data retrieval tools
- Action execution tools
- Integration with external services
- Custom business logic

---

## Where to Find MCP Servers

### 1. Databricks-Managed MCP Servers (Native)

**[Databricks provides 4 ready-to-use managed MCP servers](https://docs.databricks.com/aws/en/generative-ai/mcp/managed-mcp) (Beta):**

#### a) Unity Catalog Functions MCP

Run predefined SQL queries via Unity Catalog functions.

- **Endpoint:** `https://<workspace-hostname>/api/2.0/mcp/functions/{catalog}/{schema}`
- **Use for:** Custom business logic (account lookups, data transformations)
- **Example:** `https://workspace.cloud.databricks.com/api/2.0/mcp/functions/prod/billing`

**Configuration:**
```yaml
external:
  uc_functions_billing:
    endpoint: "https://workspace.cloud.databricks.com/api/2.0/mcp/functions/prod/billing"
    timeout_seconds: 30
    auth:
      type: "bearer_token"
      token: "${DATABRICKS_TOKEN}"
```

#### b) Vector Search MCP

Query Databricks Vector Search indexes (only indexes with Databricks managed embeddings).

- **Endpoint:** `https://<workspace-hostname>/api/2.0/mcp/vector-search/{catalog}/{schema}`
- **Use for:** Semantic search over unstructured data (support tickets, documentation)
- **Example:** `https://workspace.cloud.databricks.com/api/2.0/mcp/vector-search/prod/customer_support`

**Configuration:**
```yaml
external:
  vector_search_support:
    endpoint: "https://workspace.cloud.databricks.com/api/2.0/mcp/vector-search/prod/customer_support"
    timeout_seconds: 30
    auth:
      type: "bearer_token"
      token: "${DATABRICKS_TOKEN}"
```

#### c) Genie Space MCP

Query Genie spaces to analyze structured data using natural language.

- **Endpoint:** `https://<workspace-hostname>/api/2.0/mcp/genie/{genie_space_id}`
- **Use for:** Read-only data retrieval with natural language queries
- **Note:** Best for external AI assistants (Claude, ChatGPT) connecting to your data
- **Example:** `https://workspace.cloud.databricks.com/api/2.0/mcp/genie/01234567-89ab-cdef-0123-456789abcdef`

**Configuration:**
```yaml
external:
  genie_billing:
    endpoint: "https://workspace.cloud.databricks.com/api/2.0/mcp/genie/${BILLING_GENIE_SPACE_ID}"
    timeout_seconds: 60  # Genie queries can be slower
    retry_attempts: 2
    auth:
      type: "bearer_token"
      token: "${DATABRICKS_TOKEN}"
```

#### d) DBSQL MCP

Run AI-generated SQL queries.

- **Endpoint:** `https://<workspace-hostname>/api/2.0/mcp/sql`
- **Use for:** Authoring data pipelines with AI coding tools (Cursor, Claude Code, Codex)
- **Note:** For read-only data retrieval in chatbots, use Genie instead
- **Example:** `https://workspace.cloud.databricks.com/api/2.0/mcp/sql`

**Configuration:**
```yaml
external:
  dbsql_mcp:
    endpoint: "https://workspace.cloud.databricks.com/api/2.0/mcp/sql"
    timeout_seconds: 60
    auth:
      type: "bearer_token"
      token: "${DATABRICKS_TOKEN}"
```

#### 📋 Real-World Multi-MCP Example: Customer Support Agent

```yaml
# config/mcp_deployment_config.yaml
deployment_mode: external

external:
  enabled: true

  # Search support tickets & docs (unstructured data)
  vector_search_support:
    endpoint: "https://workspace.cloud.databricks.com/api/2.0/mcp/vector-search/prod/customer_support"
    auth:
      type: "bearer_token"
      token: "${DATABRICKS_TOKEN}"

  # Query billing data (structured data)
  genie_billing:
    endpoint: "https://workspace.cloud.databricks.com/api/2.0/mcp/genie/${BILLING_SPACE_ID}"
    timeout_seconds: 60
    auth:
      type: "bearer_token"
      token: "${DATABRICKS_TOKEN}"

  # Account lookups & updates (custom business logic)
  uc_functions_billing:
    endpoint: "https://workspace.cloud.databricks.com/api/2.0/mcp/functions/prod/billing"
    auth:
      type: "bearer_token"
      token: "${DATABRICKS_TOKEN}"
```

**Agent code:**
```python
from mcp import McpClient

async with McpClient() as client:
    # Search support history
    tickets = await client.call_tool(
        server="vector_search_support",
        tool="search",
        args={"query": "payment issues", "top_k": 5}
    )

    # Get customer billing info
    billing = await client.call_tool(
        server="genie_billing",
        tool="query",
        args={"question": "Show billing for customer ID 12345"}
    )

    # Execute account update
    result = await client.call_tool(
        server="uc_functions_billing",
        tool="update_account_status",
        args={"customer_id": "12345", "status": "active"}
    )
```

---

### 2. Native MLflow MCP (MLflow 3.5.1+)

**MLflow Traces & Experiments MCP**
- Endpoint: `https://your-workspace.cloud.databricks.com/mlflow/mcp`
- Tools: Trace search, experiment tracking, model registry
- Auth: Use your Databricks token

**Configuration:**
```yaml
# config/mcp_deployment_config.yaml
deployment_mode: external

external:
  enabled: true
  mlflow_mcp:
    endpoint: "https://your-workspace.cloud.databricks.com/mlflow/mcp"
    auth:
      type: "bearer_token"
      token: "${DATABRICKS_TOKEN}"
```

### 3. Public MCP Servers

Examples (check availability):
- **GitHub MCP**: Repository operations, issue management
- **Slack MCP**: Channel management, messaging
- **Google Drive MCP**: Document operations
- **Notion MCP**: Database queries, page creation

**Configuration:**
```yaml
external:
  github_mcp:
    endpoint: "https://api.github.com/mcp"
    auth:
      type: "bearer_token"
      token: "${GITHUB_TOKEN}"

  slack_mcp:
    endpoint: "https://mcp.slack.com/v1"
    auth:
      type: "bearer_token"
      token: "${SLACK_BOT_TOKEN}"
```

### 4. Your Separately Deployed MCP Servers

If you deployed MCP servers from the `databricks-mcp-server` project:

```yaml
external:
  databricks_mcp:
    endpoint: "https://mcp.yourcompany.com/agent-tools"
    auth:
      type: "bearer_token"
      token: "${CUSTOM_MCP_TOKEN}"
```

### 5. Enterprise/Internal MCP Servers

Your company might have internal MCP servers:

```yaml
external:
  enterprise_tools:
    endpoint: "https://internal-mcp.company.com"
    auth:
      type: "api_key"
      api_key: "${INTERNAL_API_KEY}"
      header_name: "X-Company-API-Key"
```

---

## Configuration Modes

### External Mode (For Existing Servers)

```yaml
# config/mcp_deployment_config.yaml
deployment_mode: external

external:
  enabled: true

  # Add as many MCP servers as you need
  mlflow_mcp:
    endpoint: "..."
    auth: {...}

  custom_server_1:
    endpoint: "..."
    auth: {...}

  custom_server_2:
    endpoint: "..."
    auth: {...}
```

### Embedded Mode (For Local Development)

Only if you've copied MCP server implementations into your project:

```yaml
deployment_mode: embedded

embedded:
  enabled: true
  mlflow_mcp:
    enabled: true
    port: 5000
    command: ["mlflow", "server", "mcp", ...]
```

### Separate Mode (For Production Scale)

When you want to deploy MCP servers separately but manage them yourself:

```yaml
deployment_mode: separate

separate:
  enabled: true
  mlflow_mcp:
    endpoint: "http://mcp-servers:5000"  # Internal service name
  databricks_mcp:
    endpoint: "http://mcp-servers:6000"
```

---

## Using MCP Servers in Agent Code

Once configured, use the MCP client:

```python
from mcp import McpClient

async with McpClient() as client:
    # MLflow MCP (native Databricks)
    traces = await client.call_tool(
        server="mlflow_mcp",
        tool="search_traces",
        args={"filter_string": "tags.agent = 'my-agent'"}
    )

    # GitHub MCP (public)
    issues = await client.call_tool(
        server="github_mcp",
        tool="list_issues",
        args={"repo": "my-org/my-repo"}
    )

    # Your custom MCP
    result = await client.call_tool(
        server="databricks_mcp",
        tool="check_performance",
        args={"agent_id": "my-agent"}
    )
```

---

## Authentication

### Bearer Token (Most Common)

```yaml
auth:
  type: "bearer_token"
  token: "${YOUR_TOKEN_ENV_VAR}"
```

### API Key

```yaml
auth:
  type: "api_key"
  api_key: "${YOUR_API_KEY}"
  header_name: "X-API-Key"  # Optional, defaults to "Authorization"
```

### No Auth (Internal Networks)

```yaml
auth:
  type: "none"
```

---

## Best Practices

1. **Use Environment Variables** for all tokens/keys
2. **Start with external mode** - use existing/managed servers
3. **Only use embedded mode** for development or if you control the MCP implementations
4. **Monitor health checks** - enable healthcheck_enabled: true
5. **Set appropriate timeouts** based on expected tool execution time

---

## Example: Full Configuration

```yaml
# config/mcp_deployment_config.yaml
deployment_mode: external

external:
  enabled: true

  # Native Databricks MLflow
  mlflow_mcp:
    endpoint: "https://workspace.cloud.databricks.com/mlflow/mcp"
    timeout_seconds: 30
    auth:
      type: "bearer_token"
      token: "${DATABRICKS_TOKEN}"

  # Public GitHub MCP
  github_mcp:
    endpoint: "https://api.github.com/mcp"
    timeout_seconds: 60
    auth:
      type: "bearer_token"
      token: "${GITHUB_TOKEN}"

  # Your custom tools
  custom_tools:
    endpoint: "https://mcp.yourcompany.com"
    timeout_seconds: 45
    auth:
      type: "api_key"
      api_key: "${CUSTOM_API_KEY}"
      header_name: "X-API-Key"
```

---

## Troubleshooting

**MCP server not connecting?**
- Check endpoint URL
- Verify authentication token
- Ensure server is reachable (network/firewall)
- Check health_check logs

**Timeout errors?**
- Increase `timeout_seconds`
- Check server performance
- Verify tool execution time

**Auth errors?**
- Verify token is valid
- Check token has correct permissions
- Ensure auth type matches server requirements

---

## Resources

- MCP Protocol: https://modelcontextprotocol.io/
- MLflow MCP: https://mlflow.org/docs/latest/llms/tracing/index.html#mcp-server
- Client Code: `mcp/client.py`
- Manager Code: `mcp/manager.py`
