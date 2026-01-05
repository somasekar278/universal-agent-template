"""
Complete Databricks Apps deployment example.

This file demonstrates the production architecture:
- Agent Mesh (reasoning agents) in hot pool container
- A2A transport layer (FastAPI/Starlette)
- MCP servers (FastAPI/Starlette)
- Agent memory (Lakebase/Delta, async)
- LLM inference (always-on Model Serving)
- Monitoring (OTEL → ZeroBus → Delta)

All services run in a single Databricks Apps container.
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from starlette.routing import Mount
from databricks.sdk import WorkspaceClient
from typing import Dict, Any, Optional
import asyncio
import uvicorn
from multiprocessing import Process

# Framework imports
from agents import AgentRouter
from agents.base import CriticalPathAgent
from shared.schemas import AgentInput, AgentOutput
from services.model_serving_client import ModelServingClient
from services.prompt_manager import PromptManager
from memory.databricks_vector_store import DatabricksVectorStore
from telemetry.zerobus_exporter import setup_telemetry, setup_metrics
from config.uc_loader import UCConfigLoader

# ============================================================================
# 1. INITIALIZATION (runs once at container startup)
# ============================================================================

print("🚀 Initializing Databricks Agent App...")

# Databricks client
w = WorkspaceClient()

# Load configuration from Unity Catalog
config_loader = UCConfigLoader(workspace_client=w)
config = config_loader.load_config(
    uc_path="/Volumes/main/agents/configs/sota_config.yaml",
    environment="production"  # or from env var
)

# Set up telemetry (OTEL → ZeroBus → Delta)
setup_telemetry()
setup_metrics()

# Initialize shared services
model_client = ModelServingClient(
    workspace_client=w,
    default_endpoint=config["model_serving"]["default_endpoint"]
)

prompt_manager = PromptManager(workspace_client=w)

memory_store = DatabricksVectorStore(
    index_name=config["unity_catalog"]["vector_index"],
    delta_table=config["unity_catalog"]["memory_table"],
    embedding_endpoint=config["model_serving"]["embedding_endpoint"]
)

# Initialize agent router
router = AgentRouter(
    config=config,
    model_client=model_client,
    prompt_manager=prompt_manager,
    memory_store=memory_store
)

print("✅ Initialization complete")

# ============================================================================
# 2. MAIN AGENT API (Port 8000)
# ============================================================================

def create_agent_api() -> FastAPI:
    """
    Create main agent execution API.

    Endpoints:
    - POST /execute - Execute an agent
    - GET /health - Health check
    - GET /metrics - Prometheus metrics
    - GET /agents - List available agents
    """
    app = FastAPI(
        title="Agent Framework",
        description="Production agent deployment on Databricks",
        version="1.0.0"
    )

    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "agents": router.list_agents(),
            "model_serving": config["model_serving"]["default_endpoint"],
            "memory_index": config["unity_catalog"]["vector_index"]
        }

    @app.post("/execute")
    async def execute_agent(request: Dict[str, Any]):
        """
        Execute an agent.

        Request:
        {
            "agent_name": "fraud_detector",
            "data": {...},
            "metadata": {...}
        }
        """
        try:
            agent_name = request.get("agent_name")
            data = request.get("data", {})
            metadata = request.get("metadata", {})

            if not agent_name:
                raise HTTPException(status_code=400, detail="agent_name is required")

            # Create agent input
            agent_input = AgentInput(
                agent_id=agent_name,
                data=data,
                metadata=metadata
            )

            # Execute via router
            result = await router.execute(agent_name, agent_input)

            return {
                "success": True,
                "agent": agent_name,
                "result": result.result,
                "confidence": result.confidence,
                "metadata": result.metadata
            }

        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": str(e)
                }
            )

    @app.get("/agents")
    async def list_agents():
        """List all available agents."""
        return {
            "agents": router.list_agents(),
            "count": len(router.list_agents())
        }

    @app.get("/metrics")
    async def get_metrics():
        """Prometheus metrics endpoint."""
        # TODO: Export Prometheus metrics
        return {"status": "ok"}

    return app

# ============================================================================
# 3. A2A TRANSPORT LAYER (Port 8001 or /a2a/*)
# ============================================================================

def create_a2a_server() -> FastAPI:
    """
    Create A2A (Agent-to-Agent) communication server.

    Implements the official Agent2Agent Protocol:
    - JSON-RPC 2.0 endpoint
    - Agent discovery
    - Peer-to-peer communication

    Endpoints:
    - POST /a2a/rpc - JSON-RPC 2.0 endpoint
    - GET /a2a/discover - Agent discovery
    - GET /a2a/card/{agent_id} - Get agent card
    """
    from agents.a2a.server import A2AServer

    a2a_server = A2AServer(
        router=router,
        workspace_client=w
    )

    return a2a_server.create_app()

# ============================================================================
# 4. MCP SERVER (Port 8002 or /mcp/*)
# ============================================================================

def create_mcp_server() -> FastAPI:
    """
    Create MCP (Model Context Protocol) server.

    Provides standardized tool and resource interfaces.

    Endpoints:
    - GET /mcp/tools - List available tools
    - POST /mcp/tools/{tool_name} - Execute tool
    - GET /mcp/resources - List available resources
    - GET /mcp/resources/{resource_id} - Get resource
    """
    from agents.mcp_server import MCPServer

    mcp_server = MCPServer(
        router=router,
        workspace_client=w
    )

    return mcp_server.create_app()

# ============================================================================
# 5. COMBINED APP (Single Port with Path Routing)
# ============================================================================

def create_combined_app() -> FastAPI:
    """
    Create combined app with all services on a single port.

    Routes:
    - /api/* - Main agent API
    - /a2a/* - A2A transport layer
    - /mcp/* - MCP server
    """
    app = FastAPI(
        title="Agent Framework - Combined",
        description="All services in one app"
    )

    # Mount sub-applications
    app.mount("/api", create_agent_api())
    app.mount("/a2a", create_a2a_server())
    app.mount("/mcp", create_mcp_server())

    @app.get("/")
    async def root():
        return {
            "status": "running",
            "services": {
                "agent_api": "/api",
                "a2a_transport": "/a2a",
                "mcp_server": "/mcp"
            }
        }

    return app

# ============================================================================
# 6. STARTUP (Choose deployment mode)
# ============================================================================

if __name__ == "__main__":
    import os

    deployment_mode = os.getenv("DEPLOYMENT_MODE", "combined")

    if deployment_mode == "combined":
        # Single port deployment (recommended for Databricks Apps)
        print("🚀 Starting combined app on port 8000")
        app = create_combined_app()
        uvicorn.run(app, host="0.0.0.0", port=8000)

    elif deployment_mode == "multi-port":
        # Multi-port deployment (separate services)
        print("🚀 Starting multi-port deployment")

        processes = [
            Process(
                target=lambda: uvicorn.run(
                    create_agent_api(),
                    host="0.0.0.0",
                    port=8000
                )
            ),
            Process(
                target=lambda: uvicorn.run(
                    create_a2a_server(),
                    host="0.0.0.0",
                    port=8001
                )
            ),
            Process(
                target=lambda: uvicorn.run(
                    create_mcp_server(),
                    host="0.0.0.0",
                    port=8002
                )
            )
        ]

        for p in processes:
            p.start()

        for p in processes:
            p.join()

    else:
        print(f"❌ Unknown deployment mode: {deployment_mode}")
        print("Valid modes: 'combined', 'multi-port'")
