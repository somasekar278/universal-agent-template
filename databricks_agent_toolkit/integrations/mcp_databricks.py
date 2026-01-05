"""
Databricks Managed MCP Servers Integration

Easy integration with Databricks-native MCP servers:
- Vector Search MCP
- Genie Space MCP
- UC Functions MCP
- DBSQL MCP

Automatically constructs endpoints and handles authentication.
"""

import logging
from typing import Any, Dict, List, Optional

import httpx
from databricks.sdk import WorkspaceClient

logger = logging.getLogger(__name__)


class DatabricksMCPTools:
    """
    Easy access to Databricks Managed MCP Servers.

    Features:
    - Automatic endpoint construction from catalog/schema
    - Automatic authentication via Databricks SDK
    - Tool schema discovery
    - OpenAI tool format conversion

    Example:
        from databricks_agent_toolkit.integrations import DatabricksMCPTools

        mcp = DatabricksMCPTools(
            servers={
                "vector_search": {
                    "catalog": "prod",
                    "schema": "documents"
                },
                "genie": {
                    "space_id": "01234567-89ab-cdef-0123-456789abcde"
                },
                "uc_functions": {
                    "catalog": "prod",
                    "schema": "utils"
                }
            }
        )

        # Get tool schemas for LLM
        tools = await mcp.get_tool_schemas()

        # Execute a tool
        result = await mcp.execute_tool(
            server="vector_search",
            tool="search",
            args={
                "query": "diabetes treatment options",
                "filters": {"publication_year": ">2020"}
            }
        )
    """

    def __init__(self, servers: Dict[str, Dict[str, Any]], workspace_client: Optional[WorkspaceClient] = None):
        """
        Initialize MCP tools client.

        Args:
            servers: Dict of server configs
                {
                    "vector_search": {"catalog": "prod", "schema": "docs"},
                    "genie": {"space_id": "12345..."},
                    "uc_functions": {"catalog": "prod", "schema": "utils"},
                    "dbsql": {}  # No config needed
                }
            workspace_client: Optional WorkspaceClient (auto-created if None)
        """
        self.workspace_client = workspace_client or WorkspaceClient()
        self.host = self.workspace_client.config.host
        self.token = self.workspace_client.config.token

        # Construct endpoint URLs
        self.endpoints = self._construct_endpoints(servers)
        self.servers = servers

        # HTTP client for MCP calls
        self.http_client = httpx.AsyncClient(headers={"Authorization": f"Bearer {self.token}"}, timeout=30.0)

        logger.info(f"✅ Initialized Databricks MCP Tools: {list(self.endpoints.keys())}")

    def _construct_endpoints(self, servers: Dict[str, Dict[str, Any]]) -> Dict[str, str]:
        """Construct full MCP endpoint URLs from server configs."""
        endpoints = {}

        for name, config in servers.items():
            if name == "vector_search":
                catalog = config.get("catalog")
                schema = config.get("schema")
                if not catalog or not schema:
                    raise ValueError("vector_search requires 'catalog' and 'schema'")
                endpoints[name] = f"{self.host}/api/2.0/mcp/vector-search/{catalog}/{schema}"

            elif name == "genie":
                space_id = config.get("space_id")
                if not space_id:
                    raise ValueError("genie requires 'space_id'")
                endpoints[name] = f"{self.host}/api/2.0/mcp/genie/{space_id}"

            elif name == "uc_functions":
                catalog = config.get("catalog")
                schema = config.get("schema")
                if not catalog or not schema:
                    raise ValueError("uc_functions requires 'catalog' and 'schema'")
                endpoints[name] = f"{self.host}/api/2.0/mcp/functions/{catalog}/{schema}"

            elif name == "dbsql":
                endpoints[name] = f"{self.host}/api/2.0/mcp/sql"

            else:
                # Custom endpoint (user provides full URL)
                if "endpoint" in config:
                    endpoints[name] = config["endpoint"]
                else:
                    raise ValueError(f"Unknown server type '{name}' and no 'endpoint' provided")

        return endpoints

    async def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """
        Get all tool schemas in OpenAI format.

        Discovers tools from all configured MCP servers and returns
        them in a format ready to pass to LLM chat completion.

        Returns:
            List of tool schemas (OpenAI function calling format)

        Example:
            tools = await mcp.get_tool_schemas()
            response = await llm.chat(messages=[...], tools=tools)
        """
        all_tools = []

        for server_name, endpoint in self.endpoints.items():
            try:
                # Call MCP server to discover tools
                response = await self.http_client.get(f"{endpoint}/tools")
                response.raise_for_status()

                tools_data = response.json()

                # Convert MCP tool schemas to OpenAI format
                for tool in tools_data.get("tools", []):
                    all_tools.append(
                        {
                            "type": "function",
                            "function": {
                                "name": f"{server_name}__{tool['name']}",  # Prefix with server name
                                "description": tool.get("description", ""),
                                "parameters": tool.get("inputSchema", {"type": "object", "properties": {}}),
                            },
                        }
                    )

                logger.info(f"✅ Discovered {len(tools_data.get('tools', []))} tools from {server_name}")

            except Exception as e:
                logger.warning(f"⚠️  Failed to discover tools from {server_name}: {e}")

        return all_tools

    async def execute_tool(self, server: str, tool: str, args: Dict[str, Any]) -> Any:
        """
        Execute a tool via MCP.

        Args:
            server: Server name (e.g., "vector_search")
            tool: Tool name (e.g., "search")
            args: Tool arguments

        Returns:
            Tool execution result

        Example:
            result = await mcp.execute_tool(
                server="vector_search",
                tool="search",
                args={"query": "machine learning", "top_k": 10}
            )
        """
        if server not in self.endpoints:
            raise ValueError(f"Unknown server: {server}")

        endpoint = self.endpoints[server]

        try:
            # Call MCP server to execute tool
            response = await self.http_client.post(f"{endpoint}/tools/{tool}", json={"arguments": args})
            response.raise_for_status()

            result = response.json()
            logger.info(f"✅ Executed {server}/{tool}")

            return result.get("result")

        except Exception as e:
            logger.error(f"❌ Tool execution failed ({server}/{tool}): {e}")
            raise

    def get_server_info(self, server: str) -> Dict[str, Any]:
        """
        Get information about a specific server.

        Args:
            server: Server name

        Returns:
            Dict with server details
        """
        if server not in self.endpoints:
            return {"error": f"Unknown server: {server}"}

        return {"name": server, "endpoint": self.endpoints[server], "config": self.servers.get(server, {})}

    async def close(self):
        """Close HTTP client."""
        await self.http_client.aclose()
