"""
Databricks Authentication Utilities

Easy authentication and workspace client management.
"""

import logging
from typing import Any, Dict, Optional

from databricks.sdk import WorkspaceClient

logger = logging.getLogger(__name__)


def get_workspace_client(
    host: Optional[str] = None, token: Optional[str] = None, profile: Optional[str] = None
) -> WorkspaceClient:
    """
    Get authenticated WorkspaceClient.

    Authentication priority:
    1. Explicit host/token parameters
    2. DATABRICKS_HOST/DATABRICKS_TOKEN env vars
    3. Databricks CLI profile
    4. Default authentication (tries various methods)

    Args:
        host: Optional Databricks workspace URL
        token: Optional Databricks token
        profile: Optional Databricks CLI profile name

    Returns:
        Authenticated WorkspaceClient

    Example:
        # Auto-detect authentication
        w = get_workspace_client()

        # Use specific credentials
        w = get_workspace_client(
            host="https://workspace.cloud.databricks.com",
            token="dapi123..."
        )

        # Use CLI profile
        w = get_workspace_client(profile="my-profile")
    """
    try:
        if host and token:
            # Explicit credentials
            logger.info(f"Authenticating with explicit credentials: {host}")
            return WorkspaceClient(host=host, token=token)

        elif profile:
            # CLI profile
            logger.info(f"Authenticating with profile: {profile}")
            return WorkspaceClient(profile=profile)

        else:
            # Auto-detect (env vars, CLI, etc.)
            logger.info("Auto-detecting Databricks authentication")
            return WorkspaceClient()

    except Exception as e:
        logger.error(f"❌ Authentication failed: {e}")
        logger.info("\n" + get_auth_help())
        raise


def get_auth_help() -> str:
    """
    Get authentication troubleshooting help.

    Returns:
        Help text
    """
    return """
    Databricks Authentication Help
    =============================

    You can authenticate in several ways:

    1. Environment Variables (recommended for production):
       export DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
       export DATABRICKS_TOKEN="dapi123..."

    2. Databricks CLI (recommended for development):
       databricks auth login --host https://your-workspace.cloud.databricks.com

    3. Explicit credentials in code:
       from databricks_agent_toolkit.integrations import get_workspace_client
       w = get_workspace_client(
           host="https://your-workspace.cloud.databricks.com",
           token="dapi123..."
       )

    For more info: https://docs.databricks.com/en/dev-tools/auth.html
    """


def check_authentication() -> Dict[str, Any]:
    """
    Check current authentication status.

    Returns:
        Dict with authentication details

    Example:
        from databricks_agent_toolkit.integrations import check_authentication
        status = check_authentication()
        print(status)
    """
    try:
        w = WorkspaceClient()
        user = w.current_user.me()

        return {"authenticated": True, "host": w.config.host, "user": user.user_name, "user_id": user.id}

    except Exception as e:
        return {"authenticated": False, "error": str(e), "help": get_auth_help()}
