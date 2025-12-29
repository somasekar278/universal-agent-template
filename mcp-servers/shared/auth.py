"""
Databricks authentication for MCP servers.

Handles authentication to Databricks services.
"""

import os
from typing import Optional
from databricks.sdk import WorkspaceClient
from databricks.sql import connect


class DatabricksAuth:
    """
    Databricks authentication helper.
    
    Reads from environment variables (populated from Terraform outputs).
    """
    
    def __init__(
        self,
        host: Optional[str] = None,
        token: Optional[str] = None,
        warehouse_id: Optional[str] = None,
        catalog: Optional[str] = None
    ):
        """
        Initialize Databricks auth.
        
        Args:
            host: Databricks workspace host
            token: Databricks personal access token
            warehouse_id: SQL Warehouse ID
            catalog: Default catalog name
        """
        self.host = host or os.getenv("DATABRICKS_HOST")
        self.token = token or os.getenv("DATABRICKS_TOKEN")
        self.warehouse_id = warehouse_id or os.getenv("DATABRICKS_WAREHOUSE_ID")
        self.catalog = catalog or os.getenv("DATABRICKS_CATALOG", "main")
        
        if not self.host or not self.token:
            raise ValueError(
                "DATABRICKS_HOST and DATABRICKS_TOKEN must be set "
                "(either via args or environment variables)"
            )
    
    def get_workspace_client(self) -> WorkspaceClient:
        """Get Databricks Workspace client."""
        return WorkspaceClient(
            host=self.host,
            token=self.token
        )
    
    def get_sql_connection(self):
        """Get SQL Warehouse connection."""
        if not self.warehouse_id:
            raise ValueError("DATABRICKS_WAREHOUSE_ID must be set")
        
        return connect(
            server_hostname=self.host,
            http_path=f"/sql/1.0/warehouses/{self.warehouse_id}",
            access_token=self.token
        )


def get_databricks_client() -> WorkspaceClient:
    """
    Convenience function to get Databricks client.
    
    Returns:
        Databricks Workspace client
    """
    auth = DatabricksAuth()
    return auth.get_workspace_client()

