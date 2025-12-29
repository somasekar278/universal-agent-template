"""
Databricks MCP Servers

Standalone package providing MCP servers for Databricks operations.

This package is designed to be:
- Used within the SOTA Agent project (monorepo)
- Extracted to a separate repository when needed
- Shared across multiple agent projects

Servers:
- databricks-sql: SQL Warehouse and Delta table operations
- unity-catalog: Unity Catalog model/prompt registry
- lakebase: Vector store for agent memory

Usage:
    # Option 1: Run as subprocess (development)
    python -m mcp_servers.databricks_sql.server
    
    # Option 2: Run as HTTP service (production)
    docker-compose up
    
    # Option 3: Import programmatically (advanced)
    from mcp_servers import DatabricksSQLServer
    server = DatabricksSQLServer()
    await server.start()
"""

__version__ = "0.1.0"

__all__ = [
    "__version__",
]

