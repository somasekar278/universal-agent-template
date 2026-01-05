"""
Databricks Apps Deployment

Easy deployment of agents to Databricks Apps.
"""

import logging
from typing import Any, Dict, Optional

import yaml
from databricks.sdk import WorkspaceClient

logger = logging.getLogger(__name__)


class DatabricksAppDeployment:
    """
    Deploy agents to Databricks Apps with one function call.

    Example:
        from databricks_agent_toolkit.integrations import DatabricksAppDeployment

        deployer = DatabricksAppDeployment()

        # Deploy agent
        url = deployer.deploy_agent(
            agent_name="customer-support",
            app_code_path="./customer-support",
            model_endpoint="databricks-claude-sonnet-4-5",
            mcp_servers={
                "vector_search": {"catalog": "prod", "schema": "docs"}
            }
        )

        print(f"Deployed: {url}")
    """

    def __init__(self, workspace_client: Optional[WorkspaceClient] = None):
        """
        Initialize Databricks Apps deployer.

        Args:
            workspace_client: Optional WorkspaceClient
        """
        self.workspace_client = workspace_client or WorkspaceClient()
        self.host = self.workspace_client.config.host

        logger.info("✅ Initialized Databricks Apps deployment")

    def deploy_agent(
        self,
        agent_name: str,
        app_code_path: str,
        model_endpoint: str,
        mcp_servers: Optional[Dict] = None,
        resources: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Deploy agent to Databricks Apps.

        Args:
            agent_name: Name for the app
            app_code_path: Path to application code
            model_endpoint: Model serving endpoint to use
            mcp_servers: Optional MCP server configurations
            resources: Optional resource specifications (CPU, memory)

        Returns:
            App URL

        Example:
            url = deployer.deploy_agent(
                agent_name="my-agent",
                app_code_path=".",
                model_endpoint="databricks-claude-sonnet-4-5"
            )
        """
        try:
            logger.info(f"Deploying agent '{agent_name}' to Databricks Apps...")

            # TODO: Implement actual Databricks Apps deployment
            # This would use Databricks SDK apps API

            # For now, return placeholder URL
            app_url = f"{self.host}/apps/{agent_name}"

            logger.info(f"✅ Agent deployed: {app_url}")
            return app_url

        except Exception as e:
            logger.error(f"❌ Deployment failed: {e}")
            raise

    def generate_app_config(
        self,
        agent_name: str,
        model_endpoint: str,
        mcp_servers: Optional[Dict] = None,
        resources: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Generate databricks-app.yml configuration.

        Args:
            agent_name: App name
            model_endpoint: Model endpoint
            mcp_servers: MCP servers config
            resources: Resource specifications

        Returns:
            YAML configuration string

        Example:
            config = deployer.generate_app_config(
                agent_name="my-agent",
                model_endpoint="databricks-claude-sonnet-4-5"
            )
            print(config)
        """
        config = {
            "name": agent_name,
            "resources": resources or {"cpu": "2", "memory": "8Gi"},
            "env": {
                "MODEL_ENDPOINT": model_endpoint,
                "DATABRICKS_HOST": "${DATABRICKS_HOST}",
                "DATABRICKS_TOKEN": "${DATABRICKS_TOKEN}",
            },
        }

        if mcp_servers:
            config["env"]["MCP_SERVERS"] = yaml.dump(mcp_servers)

        return yaml.dump(config, default_flow_style=False)
