# Deployment Templates

This folder contains **template** deployment configurations for Databricks Apps.

## Philosophy

These are **starting point templates** - adapt them to your needs:
- Small apps: Use embedded mode (everything in one container)
- Production: Use separate mode (agents and MCP servers in separate containers)

## What's Included

### Basic Agent App
- `databricks-apps/basic-agent-app.yml` - Deploy just your agent application
- No MCP servers, just the agent code

### With MCP Servers (Optional)
If you want to include MCP servers:
- `databricks-apps/embedded-mode.yml` - Agent app + MCP servers in one container
- `databricks-apps/separate-mode.yml` - Agent app and MCP servers in separate containers

## Usage

### Option 1: Basic Agent Only

```bash
# Deploy just your agent application
databricks apps deploy -f deployment/databricks-apps/basic-agent-app.yml
```

### Option 2: With MCP Servers (Embedded)

For small apps, include MCP servers in the same container:

1. Add MCP server implementations to your project (from `databricks-mcp-server`)
2. Update `embedded-mode.yml` with your image
3. Deploy:

```bash
databricks apps deploy -f deployment/databricks-apps/embedded-mode.yml
```

### Option 3: Separate MCP Servers

For production, deploy MCP servers separately:

1. Deploy MCP servers first (separate project)
2. Update `separate-mode.yml` with MCP server endpoints
3. Deploy agent app:

```bash
databricks apps deploy -f deployment/databricks-apps/separate-mode.yml
```

## Customization

These templates are **starting points**. You'll need to customize:
- Docker image registry and tags
- Environment variables
- Resource limits (CPU, memory)
- Health check paths
- Auto-scaling settings
- Secrets references

## MCP Server Deployment

MCP servers should be deployed from the **separate** `databricks-mcp-server` project:
- https://github.com/your-org/databricks-mcp-server

This agent framework only contains the **MCP client** code (`mcp/` module).

## Resources

- Databricks Apps: https://docs.databricks.com/en/dev-tools/databricks-apps/
- Deployment Guide: `../docs/PLATFORM_INTEGRATION.md#databricks-deployment`
