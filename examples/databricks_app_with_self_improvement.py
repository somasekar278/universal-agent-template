"""
Databricks App with Embedded Self-Improvement Service

Complete production-ready FastAPI app that includes:
1. Agent endpoints for chat/queries
2. Embedded MCP servers (MLflow + Databricks)
3. Background self-improvement service
4. Health & monitoring endpoints
5. Admin endpoints for manual control

This demonstrates the complete Phase 2 integration.
"""

from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging
import yaml
from pathlib import Path

from mcp import MCPServerManager
from agent_cli.self_improvement_service import SelfImprovementService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global services
mcp_manager: Optional[MCPServerManager] = None
improvement_service: Optional[SelfImprovementService] = None


# ============================================================================
# Request/Response Models
# ============================================================================

class ChatRequest(BaseModel):
    """Chat request"""
    message: str
    context: Optional[str] = None


class ChatResponse(BaseModel):
    """Chat response"""
    agent: str
    response: str
    confidence: Optional[float] = None
    self_improvement_enabled: bool = True


class ManualImprovementRequest(BaseModel):
    """Manual improvement trigger"""
    reason: Optional[str] = "Manual trigger"


# ============================================================================
# Application Lifecycle
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Startup:
    1. Load configuration
    2. Start MCP servers (embedded mode)
    3. Start self-improvement service

    Shutdown:
    1. Stop self-improvement service
    2. Stop MCP servers
    """
    global mcp_manager, improvement_service

    logger.info("🚀 Starting Databricks App with Self-Improvement")

    # Load configuration
    config_path = Path("config/agent_config.yaml")
    if not config_path.exists():
        logger.error(f"Config file not found: {config_path}")
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path) as f:
        config = yaml.safe_load(f)

    try:
        # Step 1: Initialize and start MCP manager
        logger.info("Step 1/3: Starting MCP servers...")
        mcp_config_path = config.get("mcp_deployment_config", "config/mcp_deployment_config.yaml")
        mcp_manager = MCPServerManager(mcp_config_path)
        await mcp_manager.start()
        logger.info("✅ MCP servers started")

        # Step 2: Initialize self-improvement service
        logger.info("Step 2/3: Starting self-improvement service...")
        improvement_service = SelfImprovementService(config)
        # Start service in background (non-blocking)
        import asyncio
        asyncio.create_task(improvement_service.start())
        logger.info("✅ Self-improvement service started")

        logger.info("Step 3/3: Application ready!")
        logger.info("✅ All services operational\n")

        yield

        # Shutdown
        logger.info("\n🛑 Shutting down application...")

        if improvement_service:
            await improvement_service.stop()
            logger.info("✅ Self-improvement service stopped")

        if mcp_manager:
            await mcp_manager.stop()
            logger.info("✅ MCP servers stopped")

        logger.info("✅ Shutdown complete")

    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise


# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(
    title="Agent Framework with Self-Improvement",
    description="Production-ready agent application with continuous self-improvement",
    version="0.5.0",
    lifespan=lifespan
)


# ============================================================================
# Agent Endpoints
# ============================================================================

@app.post("/agent/{agent_name}/chat", response_model=ChatResponse)
async def agent_chat(agent_name: str, request: ChatRequest):
    """
    Chat with an agent.

    The agent automatically improves itself in the background.
    """
    # TODO: Implement actual agent logic here
    # For now, return a mock response

    return ChatResponse(
        agent=agent_name,
        response=f"Agent {agent_name} received: {request.message}",
        confidence=0.95,
        self_improvement_enabled=True
    )


@app.get("/agent/{agent_name}/status")
async def agent_status(agent_name: str):
    """
    Get agent status including recent performance.
    """
    if not improvement_service:
        raise HTTPException(status_code=503, detail="Service not ready")

    service_status = await improvement_service.get_service_status()
    agent_status = service_status.get("agents", {}).get(agent_name)

    if not agent_status:
        raise HTTPException(status_code=404, detail=f"Agent not found: {agent_name}")

    return {
        "agent_name": agent_name,
        "mcp_connected": agent_status.get("connected", False),
        "last_improvement_check": agent_status.get("last_check", "never"),
        "self_improvement_enabled": service_status.get("enabled", False)
    }


# ============================================================================
# Health & Monitoring Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint with service information"""
    if not mcp_manager:
        return {"status": "starting", "message": "Services initializing..."}

    endpoints = mcp_manager.get_endpoints()

    return {
        "status": "healthy",
        "service": "Agent Framework with Self-Improvement",
        "version": "0.5.0",
        "mcp_servers": {
            "mlflow": endpoints["mlflow"],
            "databricks": endpoints["databricks"]
        },
        "features": {
            "self_improvement": True,
            "mcp_integration": True,
            "continuous_monitoring": True
        }
    }


@app.get("/health")
async def health():
    """
    Comprehensive health check.

    Checks:
    - MCP servers health
    - Self-improvement service status
    - Resource usage (embedded mode)
    """
    if not mcp_manager or not improvement_service:
        return {
            "status": "starting",
            "mcp_servers": "initializing",
            "self_improvement": "initializing"
        }

    # Get MCP health
    mcp_health = await mcp_manager.get_health()

    # Get self-improvement status
    si_status = await improvement_service.get_service_status()

    # Overall health
    mcp_healthy = (
        mcp_health.get("mlflow_mcp", {}).get("healthy", False) and
        mcp_health.get("databricks_mcp", {}).get("healthy", False)
    )
    si_healthy = si_status.get("running", False)

    overall_status = "healthy" if (mcp_healthy and si_healthy) else "degraded"

    return {
        "status": overall_status,
        "mcp_servers": mcp_health,
        "self_improvement": {
            "running": si_status.get("running", False),
            "agents_monitored": len(si_status.get("agents", {})),
            "check_interval_hours": si_status.get("config", {}).get("check_interval_hours", 24)
        }
    }


@app.get("/health/resources")
async def resource_health():
    """
    Resource usage (embedded mode only).
    """
    if not mcp_manager:
        raise HTTPException(status_code=503, detail="Service not ready")

    usage = await mcp_manager.get_resource_usage()

    return {
        "status": "ok",
        "deployment_mode": mcp_manager.mode.value,
        "resources": usage
    }


# ============================================================================
# Admin Endpoints
# ============================================================================

@app.post("/admin/agents/{agent_name}/improve")
async def trigger_manual_improvement(agent_name: str, request: ManualImprovementRequest):
    """
    Manually trigger self-improvement for an agent.

    Useful for:
    - Testing
    - Emergency optimization
    - After major changes
    """
    if not improvement_service:
        raise HTTPException(status_code=503, detail="Self-improvement service not ready")

    result = await improvement_service.trigger_manual_cycle(agent_name)

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Unknown error"))

    return {
        "status": "triggered",
        "agent_name": agent_name,
        "reason": request.reason,
        "result": result
    }


@app.get("/admin/self-improvement/status")
async def self_improvement_status():
    """
    Get detailed self-improvement service status.
    """
    if not improvement_service:
        raise HTTPException(status_code=503, detail="Service not ready")

    return await improvement_service.get_service_status()


@app.get("/admin/mcp/config")
async def mcp_config():
    """
    Get current MCP configuration.
    """
    if not mcp_manager:
        raise HTTPException(status_code=503, detail="Service not ready")

    return {
        "deployment_mode": mcp_manager.mode.value,
        "endpoints": mcp_manager.get_endpoints(),
        "config": mcp_manager.config
    }


@app.post("/admin/mcp/restart")
async def restart_mcp():
    """
    Restart MCP servers (embedded mode only).
    """
    if not mcp_manager:
        raise HTTPException(status_code=503, detail="Service not ready")

    if mcp_manager.mode.value != "embedded":
        raise HTTPException(
            status_code=400,
            detail=f"Restart only supported in embedded mode (current: {mcp_manager.mode.value})"
        )

    await mcp_manager.stop()
    await mcp_manager.start()

    return {
        "status": "restarted",
        "message": "MCP servers restarted successfully"
    }


# ============================================================================
# Run Application
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
