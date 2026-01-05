"""
Databricks Agent Toolkit - Integrations Module

Pre-wired integrations to all Databricks services for agentic development.
"""

try:
    from .apps import DatabricksAppDeployment  # noqa: F401
    from .auth import check_authentication, get_workspace_client  # noqa: F401
    from .lakebase import Lakebase, get_lakebase_connection_string  # noqa: F401
    from .mcp_databricks import DatabricksMCPTools  # noqa: F401
    from .model_serving import DatabricksLLM  # noqa: F401
    from .unity_catalog import UnityAgentArtifacts  # noqa: F401
    from .vector_search import DatabricksVectorSearch, get_native_vector_search_client  # noqa: F401

    __all__ = [
        "DatabricksLLM",
        "DatabricksMCPTools",
        "UnityAgentArtifacts",
        "Lakebase",
        "get_lakebase_connection_string",
        "DatabricksVectorSearch",
        "get_native_vector_search_client",
        "DatabricksAppDeployment",
        "get_workspace_client",
        "check_authentication",
    ]
except ImportError as e:
    import warnings

    warnings.warn(
        f"Databricks integrations not available: {e}\n" "Install with: pip install databricks-agent-toolkit[databricks]"
    )
    __all__ = []
