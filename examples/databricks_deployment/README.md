# Databricks Deployment Example

**Complete production deployment example for Agent Framework on Databricks.**

This example demonstrates the production architecture:

| Component | Location | Details |
|-----------|----------|---------|
| **Agent Mesh** | Databricks Apps hot pool | Your custom reasoning agents |
| **A2A Transport** | Inside container (FastAPI) | Agent-to-agent communication |
| **MCP Servers** | Inside container (FastAPI) | Tool/resource servers |
| **Agent Memory** | Lakebase + Delta Lake | Async vector + metadata queries |
| **LLM Inference** | Model Serving (always-on) | No scale-to-zero for production |
| **Prompt Optimization** | Databricks Jobs (offline) | DSPy/TextGrad, scheduled |
| **Monitoring** | OTEL → ZeroBus → Delta | Batch telemetry pipeline |

## 📁 Files

```
examples/databricks_deployment/
├── README.md                          # This file
├── app.py                             # Main entry point (all services)
├── databricks-app.yml                 # Production app configuration
├── requirements.txt                   # Python dependencies
│
├── agents/
│   └── fraud_detector.py              # Example agent
│
├── deployment/
│   ├── setup_unity_catalog.py         # UC setup script
│   ├── create_model_serving.py        # Model Serving setup
│   └── sync_to_uc.py                  # Sync configs/prompts to UC
│
└── jobs/
    └── optimize_prompts_dspy.py       # Offline DSPy optimization job
```

## 🚀 Quick Start

### 1. Prerequisites

```bash
# Install Databricks CLI
pip install databricks-cli databricks-sdk

# Configure authentication
databricks configure --token

# Install framework
pip install sota-agent-framework[databricks]
```

### 2. Set Up Infrastructure

```bash
# Create Unity Catalog structure
python deployment/setup_unity_catalog.py

# Create Model Serving endpoints (always-on)
python deployment/create_model_serving.py

# Upload configs and prompts to UC Volumes
python deployment/sync_to_uc.py
```

### 3. Deploy to Databricks Apps

```bash
# Deploy app (hot pool with min 2 instances)
databricks apps create \
  --name fraud-detection-agent \
  --config databricks-app.yml

# Get app URL
APP_URL=$(databricks apps get fraud-detection-agent --json | jq -r '.url')
echo "✅ App deployed: $APP_URL"
```

### 4. Schedule Offline Optimization

```bash
# Create nightly DSPy optimization job
databricks jobs create --json @jobs/optimize_prompts_job.json
```

### 5. Verify Deployment

```bash
# Health check
curl $APP_URL/health

# Test agent execution
curl -X POST $APP_URL/api/execute \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $DATABRICKS_TOKEN" \
  -d '{
    "agent_name": "fraud_detector",
    "data": {
      "transaction_id": "txn_12345",
      "amount": 5000,
      "merchant": "Electronics Store"
    }
  }'

# Check telemetry
databricks sql execute \
  --statement "SELECT * FROM main.agents.traces ORDER BY timestamp DESC LIMIT 10"
```

## 🏗️ Architecture Details

### Single Container, Multiple Services

All services run in one Databricks Apps container:

```
┌────────────────────────────────────────────────┐
│  Databricks Apps Container (Port 8000)        │
│                                                │
│  Routes:                                       │
│  ├─ /api/*    → Agent execution API           │
│  ├─ /a2a/*    → A2A transport layer           │
│  └─ /mcp/*    → MCP tool server               │
│                                                │
│  Background:                                   │
│  ├─ OTEL batch exporter (every 10s)          │
│  └─ Prompt refresh (every 5m)                │
└────────────────────────────────────────────────┘
```

### Hot Pool Configuration

**Production settings (in `databricks-app.yml`):**

```yaml
compute:
  min_instances: 2          # Always keep 2 warm
  max_instances: 20         # Scale up to 20
  scale_to_zero: false      # Never cold start
```

**Benefits:**
- ✅ < 50ms response times (no cold start)
- ✅ Persistent in-memory caches
- ✅ Stable WebSocket/A2A connections

### Always-On Model Serving

**LLM endpoint configuration:**

```python
ServedEntityInput(
    entity_name="databricks-dbrx-instruct",
    workload_size="Medium",
    scale_to_zero_enabled=False,  # Always-on
    min_provisioned_throughput=100
)
```

**Why always-on?**
- Sub-second inference latency
- No cold start delays (5-30s)
- Predictable costs

### Async Memory Access

**All memory queries are async:**

```python
# Non-blocking memory retrieval
similar_cases = await memory_store.retrieve(
    query="transaction 12345",
    agent_id="fraud_detector",
    top_k=5
)
```

**Benefits:**
- Agent execution never blocks on memory I/O
- Parallel queries to Lakebase + Delta
- Better throughput

### Offline Prompt Optimization

**Optimization runs as scheduled Databricks Jobs:**

```
Nightly at 2am:
1. Load training data from Delta Lake
2. Run DSPy/TextGrad optimization (30-60 min)
3. Evaluate on holdout set
4. Save optimized prompt to UC Volume
5. Agents auto-refresh prompts (every 5 min)
```

**Benefits:**
- No optimization overhead in agent execution path
- More iterations = better prompts
- Cost-effective batch processing

### ZeroBus Telemetry Pipeline

**OTEL → ZeroBus → Delta:**

```
Agent execution
    ↓ (instrumented)
OpenTelemetry spans
    ↓ (batched)
ZeroBus (in-memory buffer)
    ↓ (every 10s or 1000 events)
Delta Lake (COPY INTO)
    ↓ (query)
Databricks SQL dashboards
```

**Benefits:**
- Zero latency impact on agents
- Efficient batched writes
- Comprehensive observability

## 📊 Monitoring

### View Telemetry

```bash
# Recent agent executions
databricks sql execute \
  --statement "
    SELECT
      timestamp,
      agent_id,
      duration_ms,
      status
    FROM main.agents.traces
    ORDER BY timestamp DESC
    LIMIT 20
  "

# Error rate by agent
databricks sql execute \
  --statement "
    SELECT
      agent_id,
      COUNT(*) as total,
      SUM(CASE WHEN status = 'ERROR' THEN 1 ELSE 0 END) as errors,
      (errors * 100.0 / total) as error_rate_pct
    FROM main.agents.traces
    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL 1 DAY
    GROUP BY agent_id
  "
```

### Databricks SQL Dashboards

1. Navigate to Databricks SQL
2. Create new dashboard
3. Add queries from `main.agents.traces`, `main.agents.metrics`
4. Share with team

## 🔧 Customization

### Add Your Custom Agent

```python
# agents/your_agent.py
from agents.base import CriticalPathAgent
from shared.schemas import AgentInput, AgentOutput

class YourCustomAgent(CriticalPathAgent):
    async def process(self, request: AgentInput) -> AgentOutput:
        # Your agent logic
        pass
```

### Update Configuration

```bash
# Edit config locally
vim config/sota_config.yaml

# Sync to Unity Catalog
python deployment/sync_to_uc.py

# Agents will auto-refresh within 5 minutes
# (or restart app for immediate refresh)
```

### Scale Up/Down

```bash
# Update databricks-app.yml
# Change min_instances, max_instances

# Re-deploy
databricks apps update fraud-detection-agent \
  --config databricks-app.yml
```

## 📚 Documentation

- **[Complete Databricks Deployment Guide](../../docs/DATABRICKS_DEPLOYMENT.md)**
- **[Model Serving API](https://docs.databricks.com/machine-learning/model-serving/)**
- **[Unity Catalog](https://docs.databricks.com/data-governance/unity-catalog/)**
- **[Databricks Apps](https://docs.databricks.com/apps/)**

## 🆘 Troubleshooting

### App not starting

```bash
# Check logs
databricks apps logs fraud-detection-agent --tail

# Check health
curl $APP_URL/health
```

### Slow response times

- Check if Model Serving is always-on (`scale_to_zero_enabled: false`)
- Verify hot pool min_instances ≥ 2
- Check memory query latency in telemetry

### High costs

- Reduce min_instances (but keep ≥ 1 for production)
- Enable telemetry sampling (`TELEMETRY_SAMPLE_RATE: 0.1`)
- Review Model Serving workload size

## 🎯 Next Steps

1. ✅ Deploy to Databricks
2. ✅ Set up monitoring dashboards
3. ✅ Schedule prompt optimization jobs
4. ⬜ Set up A/B testing for prompt versions
5. ⬜ Fine-tune custom models in MLflow
6. ⬜ Add more agents to the mesh

---

**🎉 Your agent solution is production-ready on Databricks!**
