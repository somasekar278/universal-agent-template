"""
Databricks Agent Toolkit

Unified toolkit for building production agents on Databricks.

Pre-wired integrations for:
- Databricks Model Serving (LLM inference)
- Unity Catalog (prompts, configs, functions)
- Lakebase (vector search & memory)
- Managed MCP Servers (Vector Search, Genie, UC Functions, DBSQL)
- Databricks Apps (deployment)
- MLflow 3 GenAI (evaluation)
- DSPy + TextGrad (optimization)
- Zerobus (telemetry)

Works with any agent framework (LangGraph, LangChain, custom).

Example:
    from databricks_agent_toolkit.integrations import (
        DatabricksLLM,
        DatabricksMCPTools,
        UnityAgentArtifacts
    )

    # Initialize (auto-auth)
    llm = DatabricksLLM(endpoint="databricks-claude-sonnet-4-5")
    mcp = DatabricksMCPTools(servers={
        "vector_search": {"catalog": "prod", "schema": "docs"}
    })

    # Use with LangGraph, LangChain, or custom code
    response = await llm.chat(messages=[...])
"""

__version__ = "0.2.1"
__author__ = "Databricks Agent Toolkit Team"

# Core integrations (lazy-loaded to avoid requiring optional dependencies)
__all__ = [
    "DatabricksLLM",
    "DatabricksMCPTools",
    "UnityAgentArtifacts",
    "Lakebase",
    "DatabricksAppDeployment",
    "get_workspace_client",
    "check_authentication",
]

# Only import integrations if databricks-sdk is available
try:
    from databricks_agent_toolkit.integrations import (
        DatabricksAppDeployment,
        DatabricksLLM,
        DatabricksMCPTools,
        Lakebase,
        UnityAgentArtifacts,
        check_authentication,
        get_workspace_client,
    )
except ImportError:
    # Integrations require databricks-sdk
    # Install with: pip install databricks-agent-toolkit[databricks]
    pass
