# Observability & Monitoring Guide

Complete guide to monitoring, telemetry, and observability for production agents.

---

## Table of Contents

1. [Philosophy](#philosophy)
2. [MLflow Tracing](#mlflow-tracing)
3. [Zerobus Telemetry](#zerobus-telemetry)
4. [Performance Monitoring](#performance-monitoring)
5. [Self-Improvement Service](#self-improvement-service)
6. [Databricks SQL Dashboards](#databricks-sql-dashboards)
7. [Alerts & Notifications](#alerts--notifications)

---

## Philosophy

**Use native Databricks observability tools.**

- **MLflow:** Automatic trace logging, experiment tracking
- **Zerobus:** Real-time telemetry to Delta Lake
- **Databricks SQL:** Custom business dashboards
- **Unity Catalog:** Centralized telemetry storage

---

## MLflow Tracing

MLflow 3 provides **automatic tracing** for all agent interactions.

### Automatic Tracing

```python
import mlflow

# Enable autolog
mlflow.langchain.autolog()  # For LangChain/LangGraph
mlflow.dspy.autolog()       # For DSPy

# All agent calls are automatically traced
```

### Manual Tracing

```python
import mlflow

with mlflow.start_span(name="fraud_detection") as span:
    span.set_inputs({"transaction_id": "TX123"})

    # Your agent logic
    result = fraud_detector.process(transaction)

    span.set_outputs({"risk_score": result.risk_score})
    span.set_attribute("model", "databricks-dbrx-instruct")
```

### Querying Traces

```python
from mlflow import MlflowClient

client = MlflowClient()

# Search traces
traces = client.search_traces(
    experiment_ids=["123"],
    filter_string="attributes.agent_id = 'fraud_detector'"
)

for trace in traces:
    print(f"Trace: {trace.request_id}")
    print(f"Latency: {trace.execution_time_ms}ms")
    print(f"Status: {trace.status}")
```

### Using MCP for Traces

```python
from mcp import McpClient

async with McpClient() as client:
    # Search traces via MCP
    traces = await client.call_mlflow_tool(
        "search_traces",
        {
            "filter_string": "tags.agent_id = 'fraud_detector'",
            "max_results": 10
        }
    )
```

**Resources:**
- MLflow Tracing: https://mlflow.org/docs/latest/llms/tracing/
- MCP Server: https://mlflow.org/docs/latest/llms/tracing/index.html#mcp-server

---

## Zerobus Telemetry

Real-time telemetry sink to Delta Lake for custom business metrics.

### Setup

```bash
# Interactive setup
agent-telemetry setup

# Follow prompts:
# - Databricks workspace URL
# - Token
# - Target Delta table (e.g., main.agents.telemetry)
# - Batch settings
```

### Configuration

Edit `config/agent_config.yaml`:

```yaml
telemetry:
  enabled: true
  service_name: agent-framework

  otel:
    traces:
      enabled: true
      sample_rate: 1.0
      batch_size: 100
      flush_interval_seconds: 30
    metrics:
      enabled: true
      export_interval_seconds: 60

  zerobus:
    enabled: true
    uc_endpoint: "${DATABRICKS_HOST}"
    table: "main.agents.telemetry"
    client_id: "${DATABRICKS_CLIENT_ID}"
    client_secret: "${DATABRICKS_CLIENT_SECRET}"
    batch_size: 1000
    batch_interval_seconds: 10
    max_retries: 3

    track:
      requests: true
      responses: true
      errors: true
      feedback: true
      model_calls: true
      tool_calls: true
      memory_ops: true
```

### Using Zerobus

**Automatic (Decorator):**
```python
from telemetry.zerobus_integration import track_agent_call

@track_agent_call(agent_id="fraud_detector")
async def detect_fraud(transaction):
    # Your logic
    return result

# Automatically logs:
# - Request/response
# - Latency
# - Model calls
# - Errors
# - Custom metadata
```

**Manual:**
```python
from telemetry.zerobus_integration import ZerobusClient

client = ZerobusClient()

client.log_event(
    event_type="agent_request",
    agent_id="fraud_detector",
    transaction_id="TX123",
    risk_score=0.85,
    model="databricks-dbrx-instruct",
    latency_ms=250
)
```

### Querying Telemetry

```sql
-- In Databricks SQL
SELECT
    agent_id,
    DATE(timestamp) as date,
    AVG(latency_ms) as avg_latency,
    AVG(risk_score) as avg_risk,
    COUNT(*) as num_requests,
    SUM(CASE WHEN error IS NOT NULL THEN 1 ELSE 0 END) as num_errors
FROM main.agents.telemetry
WHERE timestamp > CURRENT_DATE - INTERVAL 7 DAYS
GROUP BY agent_id, DATE(timestamp)
ORDER BY date DESC
```

**Resources:**
- Zerobus Integration: `telemetry/zerobus_integration.py`
- CLI Setup: `agent-telemetry --help`

---

## Performance Monitoring

Monitor agent performance and trigger optimization when degraded.

### Configuration

In `config/agent_config.yaml`:

```yaml
self_improvement_service:
  enabled: true
  check_interval_seconds: 300  # Check every 5 minutes
  max_concurrent_optimizations: 2

  agents:
    fraud_detector:
      enabled: true
      priority: "critical"

      # Performance thresholds
      thresholds:
        accuracy: 0.90        # Trigger if < 90%
        error_rate: 0.03      # Trigger if > 3%
        latency: 1.0          # Trigger if > 1s

      # Cooldown to prevent over-optimization
      cooldown_hours: 24

      # Notifications
      notifications:
        on_degradation:
          - type: "slack"
            channel: "#fraud-alerts"
        on_optimization_complete:
          - type: "slack"
            channel: "#fraud-ops"

      # Optimization settings
      optimization:
        config_path: "config/optimization/fraud_detector_optimize.yaml"
        dspy_only: false
        textgrad_only: false
```

### Manual Performance Checks

**Using MCP:**
```python
from mcp import McpClient

async with McpClient() as client:
    # Check current performance
    perf = await client.call_databricks_tool(
        "check_performance",
        {"agent_id": "fraud_detector"}
    )

    print(f"Status: {perf['status']}")
    for metric in perf['metric_results']:
        print(f"{metric['metric_name']}: {metric['value']} (threshold: {metric['threshold']})")

    # Analyze trend
    trend = await client.call_databricks_tool(
        "analyze_performance_trend",
        {"agent_id": "fraud_detector", "time_period_days": 7}
    )

    print(f"Trend: {trend['trend_analysis']}")
```

**Using CLI:**
```bash
# Generate monitoring setup
agent-monitoring --config config/agent_config.yaml --mode embedded
```

---

## Self-Improvement Service

Background service that continuously monitors agents and triggers optimization.

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Agent Application                         │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Main FastAPI App                                       │ │
│  │  - Agent endpoints                                      │ │
│  │  - Health checks                                        │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Self-Improvement Service (Background Task)            │ │
│  │                                                         │ │
│  │  Every 5 minutes:                                       │ │
│  │  1. Check MLflow metrics for each agent                │ │
│  │  2. Compare vs thresholds                              │ │
│  │  3. If degraded:                                        │ │
│  │     - Trigger optimization (via MCP)                   │ │
│  │     - Send notifications                                │ │
│  │  4. Monitor optimization status                         │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                          │
                          │ MCP Calls
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                 Databricks Agent MCP Server                  │
│  - trigger_optimization()                                    │
│  - check_optimization_status()                               │
│  - check_performance()                                       │
└─────────────────────────────────────────────────────────────┘
```

### Enabling the Service

**In Databricks App:**
```python
from fastapi import FastAPI
from contextlib import asynccontextmanager
from agent_cli.self_improvement_service import (
    SelfImprovementService,
    SelfImprovementServiceConfig
)
from mcp import McpClient

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize MCP client
    mcp_client = McpClient()

    # Initialize self-improvement service
    config = SelfImprovementServiceConfig.load("config/agent_config.yaml")
    service = SelfImprovementService(config, mcp_client)

    # Start background monitoring
    service_task = asyncio.create_task(service.start())

    yield

    # Cleanup
    await service.stop()
    await mcp_client.close()

app = FastAPI(lifespan=lifespan)
```

### Monitoring the Service

```python
@app.get("/admin/self-improvement/status")
async def get_service_status():
    return {
        "enabled": service.config.enabled,
        "running": service.running,
        "check_interval_seconds": service.config.check_interval_seconds,
        "active_optimizations": list(service.active_optimizations.keys()),
        "cooldowns": service.optimization_cooldowns
    }
```

**Resources:**
- Service Implementation: `sota_agent/self_improvement_service.py`
- Example App: `examples/databricks_app_with_self_improvement.py`

---

## Databricks SQL Dashboards

Create custom business dashboards in Databricks SQL.

### Example Queries

**Agent Performance Overview:**
```sql
SELECT
    agent_id,
    DATE(timestamp) as date,
    AVG(correctness_score) as avg_correctness,
    AVG(latency_ms) as avg_latency,
    COUNT(*) as total_requests,
    SUM(CASE WHEN error IS NOT NULL THEN 1 ELSE 0 END) as error_count,
    CAST(SUM(CASE WHEN error IS NOT NULL THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100 as error_rate_pct
FROM main.agents.telemetry
WHERE timestamp > CURRENT_DATE - INTERVAL 30 DAYS
GROUP BY agent_id, DATE(timestamp)
ORDER BY date DESC, agent_id
```

**Real-Time Metrics (Last Hour):**
```sql
SELECT
    agent_id,
    COUNT(*) as requests_last_hour,
    AVG(latency_ms) as avg_latency,
    MAX(latency_ms) as max_latency,
    PERCENTILE(latency_ms, 0.95) as p95_latency,
    SUM(CASE WHEN error IS NOT NULL THEN 1 ELSE 0 END) as errors
FROM main.agents.telemetry
WHERE timestamp > CURRENT_TIMESTAMP - INTERVAL 1 HOUR
GROUP BY agent_id
```

**Optimization History:**
```sql
SELECT
    agent_id,
    optimization_id,
    timestamp,
    CASE
        WHEN status = 'completed' THEN 'Success'
        WHEN status = 'failed' THEN 'Failed'
        ELSE 'In Progress'
    END as status,
    accuracy_before,
    accuracy_after,
    accuracy_after - accuracy_before as improvement
FROM main.agents.optimization_history
ORDER BY timestamp DESC
LIMIT 100
```

### Creating Dashboards

1. **Databricks SQL** → **Queries** → **Create Query**
2. Write your SQL query
3. **Add Visualization**
   - Chart type (line, bar, pie, etc.)
   - X/Y axes
   - Grouping
4. **Add to Dashboard**
5. **Schedule Refresh** (e.g., every 5 minutes)

**Resources:**
- Databricks SQL: https://docs.databricks.com/en/sql/
- Dashboards: https://docs.databricks.com/en/dashboards/

---

## Alerts & Notifications

### Slack Notifications

Configure in `config/agent_config.yaml`:

```yaml
self_improvement_service:
  agents:
    fraud_detector:
      notifications:
        on_degradation:
          - type: "slack"
            channel: "#fraud-alerts"
            webhook_url: "${SLACK_WEBHOOK_URL}"
        on_optimization_complete:
          - type: "slack"
            channel: "#fraud-ops"
            webhook_url: "${SLACK_WEBHOOK_URL}"
```

### Email Notifications

```yaml
notifications:
  on_degradation:
    - type: "email"
      recipients: ["team@company.com"]
      smtp_host: "${SMTP_HOST}"
      smtp_port: 587
```

### Databricks Alerts

Create alerts in Databricks SQL:

1. **Databricks SQL** → **Alerts** → **Create Alert**
2. Select query (e.g., "Error Rate > 5%")
3. Set threshold
4. Configure destinations (email, Slack, PagerDuty)
5. Set schedule

**Example Alert Query:**
```sql
SELECT
    agent_id,
    CAST(SUM(CASE WHEN error IS NOT NULL THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100 as error_rate
FROM main.agents.telemetry
WHERE timestamp > CURRENT_TIMESTAMP - INTERVAL 1 HOUR
GROUP BY agent_id
HAVING error_rate > 5.0
```

---

## Quick Reference

### Monitoring Stack

| Component | Purpose | Tool |
|-----------|---------|------|
| Agent traces | Detailed execution logs | MLflow Tracing |
| Business metrics | Custom KPIs | Zerobus → Delta Lake |
| Dashboards | Visual monitoring | Databricks SQL |
| Performance checks | Degradation detection | Self-Improvement Service |
| Alerts | Real-time notifications | Databricks SQL Alerts |
| Optimization | Auto-remediation | MCP + DSPy |

### Configuration Files

- **Main Config:** `config/agent_config.yaml`
  - Telemetry settings
  - Self-improvement service
  - Agent thresholds
  - Notifications

- **MCP Config:** `config/mcp_deployment_config.yaml`
  - MCP server endpoints
  - Deployment mode

### CLI Commands

```bash
# Setup telemetry
agent-telemetry setup

# Test telemetry
agent-telemetry test

# Generate monitoring setup
agent-monitoring --config config/agent_config.yaml --mode embedded

# Check telemetry status
agent-telemetry status
```

### Key Metrics to Monitor

1. **Accuracy/Correctness** - Core evaluation metrics
2. **Latency** - Response time
3. **Error Rate** - Failed requests
4. **Throughput** - Requests per minute
5. **Token Usage** - LLM costs
6. **User Feedback** - Satisfaction scores
7. **Tool Call Success Rate** - For agentic workflows

---

## Getting Help

- **Platform Integration:** `PLATFORM_INTEGRATION.md`
- **Evaluation:** `EVALUATION_GUIDE.md`
- **Migration:** `MIGRATION_GUIDE_V0.5.md`

---

**Remember: Use native Databricks observability, don't build custom dashboards.**
