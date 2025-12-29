"""
MCP client wrapper for agents.

Provides clean interface for agents to call MCP servers.
Abstracts connection details - works locally or remotely!

IMPORTANT: Agents should ONLY use this wrapper, never import from mcp-servers/ directly!
"""

import os
from typing import Any, Dict, Optional
from mcp import MCPClient


class AgentMCPClient:
    """
    MCP client wrapper for agents.
    
    Benefits:
    - Abstracts connection (local vs remote)
    - No direct imports from mcp-servers/
    - Easy to switch environments
    - Works before and after MCP extraction
    
    Usage:
        client = AgentMCPClient.from_config()
        result = await client.call_databricks_sql("query_table", {...})
    """
    
    def __init__(self, config: Dict[str, Dict[str, str]]):
        """
        Initialize MCP client.
        
        Args:
            config: MCP server configurations
                {
                    "databricks-sql": {"url": "http://localhost:3001"},
                    "unity-catalog": {"url": "http://localhost:3002"},
                    ...
                }
        """
        self.config = config
        self._clients: Dict[str, MCPClient] = {}
    
    @classmethod
    def from_config(cls, config_path: Optional[str] = None) -> "AgentMCPClient":
        """
        Create client from config file.
        
        Args:
            config_path: Path to config file (uses default if None)
        
        Returns:
            AgentMCPClient instance
        """
        if config_path is None:
            # Use environment-specific config
            env = os.getenv("ENVIRONMENT", "development")
            config_path = f"config/mcp-servers-{env}.yaml"
        
        # Load config (implement based on your config format)
        import yaml
        with open(config_path) as f:
            config_data = yaml.safe_load(f)
        
        return cls(config_data.get("mcp_servers", {}))
    
    @classmethod
    def from_env(cls) -> "AgentMCPClient":
        """
        Create client from environment variables.
        
        Useful for simple deployments.
        """
        config = {
            "databricks-sql": {
                "url": os.getenv("MCP_DATABRICKS_SQL_URL", "http://localhost:3001")
            },
            "unity-catalog": {
                "url": os.getenv("MCP_UNITY_CATALOG_URL", "http://localhost:3002")
            },
            "lakebase": {
                "url": os.getenv("MCP_LAKEBASE_URL", "http://localhost:3003")
            }
        }
        return cls(config)
    
    def _get_client(self, server: str) -> MCPClient:
        """Get or create MCP client for server."""
        if server not in self._clients:
            if server not in self.config:
                raise ValueError(f"MCP server '{server}' not configured")
            
            server_config = self.config[server]
            self._clients[server] = MCPClient(url=server_config["url"])
        
        return self._clients[server]
    
    async def call_tool(
        self,
        server: str,
        tool: str,
        arguments: Dict[str, Any]
    ) -> Any:
        """
        Call MCP tool.
        
        Generic method - use specific methods below for convenience.
        
        Args:
            server: MCP server name
            tool: Tool name
            arguments: Tool arguments
        
        Returns:
            Tool result
        """
        client = self._get_client(server)
        return await client.call_tool(tool, arguments)
    
    # Convenience methods for specific servers
    
    async def call_databricks_sql(
        self,
        tool: str,
        arguments: Dict[str, Any]
    ) -> Any:
        """Call Databricks SQL tool."""
        return await self.call_tool("databricks-sql", tool, arguments)
    
    async def call_unity_catalog(
        self,
        tool: str,
        arguments: Dict[str, Any]
    ) -> Any:
        """Call Unity Catalog tool."""
        return await self.call_tool("unity-catalog", tool, arguments)
    
    async def call_lakebase(
        self,
        tool: str,
        arguments: Dict[str, Any]
    ) -> Any:
        """Call Lakebase tool."""
        return await self.call_tool("lakebase", tool, arguments)
    
    # High-level helper methods
    
    async def query_table(self, query: str) -> Dict[str, Any]:
        """
        Query Delta table.
        
        Convenience method for common operation.
        """
        return await self.call_databricks_sql(
            "query_table",
            {"query": query}
        )
    
    async def get_merchant_context(self, merchant_id: str) -> Dict[str, Any]:
        """Get merchant context from Lakebase."""
        return await self.call_lakebase(
            "get_context",
            {
                "context_type": "merchant",
                "id": merchant_id
            }
        )
    
    async def get_customer_context(self, customer_id: str) -> Dict[str, Any]:
        """Get customer context from Lakebase."""
        return await self.call_lakebase(
            "get_context",
            {
                "context_type": "customer",
                "id": customer_id
            }
        )
    
    async def store_prompt(
        self,
        name: str,
        prompt: str,
        version: str
    ) -> Dict[str, Any]:
        """Store prompt in Unity Catalog."""
        return await self.call_unity_catalog(
            "register_prompt",
            {
                "name": name,
                "prompt": prompt,
                "version": version
            }
        )

