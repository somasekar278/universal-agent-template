"""
MCP client wrapper for agents.

Provides clean interface for agents to call MCP servers.
Abstracts connection details - works locally or remotely!

IMPORTANT: Agents should ONLY use this wrapper, never import from mcp-servers/ directly!

Compatible with MCP v1.25.0+
"""

import os
from typing import Any, Dict, Optional, List
try:
    from mcp.client.session import ClientSession
    from mcp.client.stdio import stdio_client
    from mcp import StdioServerParameters
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    ClientSession = None


class AgentMCPClient:
    """
    MCP client wrapper for agents.
    
    Benefits:
    - Abstracts connection (local vs remote)
    - No direct imports from mcp-servers/
    - Easy to switch environments
    - Works before and after MCP extraction
    - Compatible with MCP v1.25.0+
    
    Usage:
        client = AgentMCPClient.from_config()
        result = await client.call_tool("server_name", "tool_name", {...})
        
    Note:
        MCP v1.25.0+ uses ClientSession API.
        Install with: pip install sota-agent-framework[mcp]
    """
    
    def __init__(self, config: Dict[str, Dict[str, Any]]):
        """
        Initialize MCP client.
        
        Args:
            config: MCP server configurations
                {
                    "databricks-sql": {
                        "command": "python",
                        "args": ["server.py"],
                        "env": {...}
                    },
                    ...
                }
        """
        if not MCP_AVAILABLE:
            raise ImportError(
                "MCP package not installed. Install with: pip install sota-agent-framework[mcp]"
            )
        
        self.config = config
        self._sessions: Dict[str, ClientSession] = {}
        self._contexts: Dict[str, Any] = {}
    
    @classmethod
    def from_config(cls, config_path: Optional[str] = None) -> "AgentMCPClient":
        """
        Create client from config file.
        
        Args:
            config_path: Path to config file (uses default if None)
        
        Returns:
            AgentMCPClient instance
            
        Example config.yaml:
            mcp_servers:
              databricks-sql:
                command: python
                args: ["mcp-servers/databricks_sql_server.py"]
                env:
                  DATABRICKS_HOST: "..."
        """
        if config_path is None:
            # Use environment-specific config
            env = os.getenv("ENVIRONMENT", "development")
            config_path = f"config/mcp-servers-{env}.yaml"
        
        # Load config (implement based on your config format)
        import yaml
        try:
            with open(config_path) as f:
                config_data = yaml.safe_load(f)
            return cls(config_data.get("mcp_servers", {}))
        except FileNotFoundError:
            # Return empty config if file not found
            return cls({})
    
    @classmethod
    def from_env(cls) -> "AgentMCPClient":
        """
        Create client from environment variables.
        
        Useful for simple deployments where MCP servers are stdio-based.
        
        Environment variables:
            MCP_SERVER_COMMAND: Command to run server (default: python)
            MCP_SERVER_SCRIPT: Path to server script
        """
        config = {}
        
        # Check if a simple server is configured via env
        if os.getenv("MCP_SERVER_SCRIPT"):
            config["default"] = {
                "command": os.getenv("MCP_SERVER_COMMAND", "python"),
                "args": [os.getenv("MCP_SERVER_SCRIPT")],
                "env": {k: v for k, v in os.environ.items() if k.startswith("MCP_")}
            }
        
        return cls(config)
    
    async def _get_session(self, server: str) -> ClientSession:
        """Get or create MCP session for server."""
        if server not in self._sessions:
            if server not in self.config:
                raise ValueError(f"MCP server '{server}' not configured")
            
            server_config = self.config[server]
            
            # Create stdio server parameters
            server_params = StdioServerParameters(
                command=server_config.get("command", "python"),
                args=server_config.get("args", []),
                env=server_config.get("env")
            )
            
            # Create and store the session context
            stdio = stdio_client(server_params)
            self._contexts[server] = stdio
            
            # Enter the context and initialize session
            read, write = await stdio.__aenter__()
            session = ClientSession(read, write)
            await session.initialize()
            
            self._sessions[server] = session
        
        return self._sessions[server]
    
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
            
        Example:
            result = await client.call_tool(
                "databricks-sql",
                "query_table",
                {"query": "SELECT * FROM table"}
            )
        """
        session = await self._get_session(server)
        
        # Call the tool using the session
        result = await session.call_tool(tool, arguments)
        
        # Extract content from the result
        if hasattr(result, 'content'):
            # Return the first content item if available
            if result.content and len(result.content) > 0:
                content = result.content[0]
                if hasattr(content, 'text'):
                    return content.text
                return content
        
        return result
    
    async def list_tools(self, server: str) -> List[Dict[str, Any]]:
        """
        List available tools for a server.
        
        Args:
            server: MCP server name
            
        Returns:
            List of available tools
        """
        session = await self._get_session(server)
        result = await session.list_tools()
        
        tools = []
        if hasattr(result, 'tools'):
            for tool in result.tools:
                tools.append({
                    "name": tool.name,
                    "description": tool.description if hasattr(tool, 'description') else None,
                    "inputSchema": tool.inputSchema if hasattr(tool, 'inputSchema') else None
                })
        
        return tools
    
    async def close(self):
        """Close all MCP sessions."""
        for server, context in list(self._contexts.items()):
            try:
                await context.__aexit__(None, None, None)
            except Exception as e:
                print(f"Warning: Error closing MCP context for {server}: {e}")
        
        self._sessions.clear()
        self._contexts.clear()
    
    # Convenience methods for specific servers
    
    async def call_databricks_sql(
        self,
        tool: str,
        arguments: Dict[str, Any]
    ) -> Any:
        """
        Call Databricks SQL tool.
        
        Args:
            tool: Tool name (e.g., "query_table")
            arguments: Tool arguments
            
        Returns:
            Tool result
        """
        return await self.call_tool("databricks-sql", tool, arguments)
    
    async def call_unity_catalog(
        self,
        tool: str,
        arguments: Dict[str, Any]
    ) -> Any:
        """
        Call Unity Catalog tool.
        
        Args:
            tool: Tool name
            arguments: Tool arguments
            
        Returns:
            Tool result
        """
        return await self.call_tool("unity-catalog", tool, arguments)
    
    async def call_lakebase(
        self,
        tool: str,
        arguments: Dict[str, Any]
    ) -> Any:
        """
        Call Lakebase tool.
        
        Args:
            tool: Tool name
            arguments: Tool arguments
            
        Returns:
            Tool result
        """
        return await self.call_tool("lakebase", tool, arguments)
    
    async def call_enrichment(
        self,
        tool: str,
        arguments: Dict[str, Any]
    ) -> Any:
        """
        Call enrichment service tool.
        
        Args:
            tool: Tool name (e.g., "lookup_bin")
            arguments: Tool arguments
            
        Returns:
            Tool result
        """
        return await self.call_tool("enrichment", tool, arguments)
    
    # High-level helper methods
    
    async def query_table(self, query: str, server: str = "databricks-sql") -> Any:
        """
        Query table using SQL.
        
        Convenience method for common operation.
        
        Args:
            query: SQL query string
            server: MCP server to use (default: "databricks-sql")
            
        Returns:
            Query results
        """
        return await self.call_tool(
            server,
            "query_table",
            {"query": query}
        )
    
    async def get_context(
        self,
        context_type: str,
        entity_id: str,
        server: str = "lakebase"
    ) -> Any:
        """
        Get context for an entity.
        
        Args:
            context_type: Type of context (e.g., "merchant", "customer")
            entity_id: Entity identifier
            server: MCP server to use (default: "lakebase")
            
        Returns:
            Context data
        """
        return await self.call_tool(
            server,
            "get_context",
            {
                "context_type": context_type,
                "id": entity_id
            }
        )

