# Architecture Guide

## Overview

The Databricks Agent Toolkit provides a **dual-deployment architecture** for building production agents:

1. **Real-time serving** via Databricks Apps
2. **Batch/scheduled operations** via Databricks Workflows

This separation ensures optimal performance, cost efficiency, and maintainability.

---

## Deployment Architecture

### **Databricks Apps** (Real-Time Layer)

**Purpose:** Serve real-time agent requests

**What Runs Here:**
- **L1-L2 Agents** (Flask-based web UI)
  - Simple chatbot (L1)
  - Context-aware assistant (L2)
  - Interactive web interface for users

- **L3-L5 Agents** (FastAPI-based REST API)
  - Production API (L3)
  - Complex workflows (L4)
  - Multi-agent systems (L5)
  - Programmatic access for systems

- **Supervisory Agent** (Optional)
  - Monitors MLflow metrics continuously
  - Detects performance degradation
  - Triggers on-demand optimization
  - Self-healing capabilities

**Characteristics:**
- Always-on (hot pools)
- Sub-second latency
- Scales with traffic
- Pay for uptime

**Use When:**
- Serving user requests
- Interactive applications
- Real-time APIs
- Agent-to-agent communication

---

### **Databricks Workflows** (Batch Layer)

**Purpose:** Run scheduled and batch operations

**What Runs Here:**
- **Prompt Optimization**
  - DSPy optimization (task prompts)
  - TextGrad optimization (system prompts)
  - Runs nightly/weekly on schedule

- **Batch Evaluation**
  - MLflow GenAI Evaluation
  - Process 100s-1000s of test cases
  - Generate evaluation reports

- **Dataset Curation**
  - Prepare training datasets
  - Clean and label traces
  - Sample representative data

- **Monitoring & Reporting**
  - Aggregate performance metrics
  - Generate dashboards
  - Send alerts

**Characteristics:**
- Scheduled execution
- Batch processing
- Cost-efficient (compute only when running)
- Can process large datasets

**Use When:**
- Regular maintenance tasks
- Processing large datasets
- Compute-intensive operations
- Non-time-sensitive work

---

## Optimization Strategy

### **1. Scheduled Optimization** (Workflows)

**Trigger:** Cron schedule (e.g., nightly at 2 AM)

**Process:**
```
1. Fetch traces from MLflow since last run
2. Filter for successful/failed examples
3. Run DSPy/TextGrad optimization
4. Evaluate new prompts
5. Update Unity Catalog if improved
6. Log metrics to MLflow
```

**Pros:**
- Predictable compute costs
- Large-batch optimization (better statistical power)
- Can use cheaper compute (no latency requirement)
- Thorough evaluation before deployment

**Cons:**
- Slower to react to issues
- Fixed schedule may miss critical problems

**Configuration:**
```yaml
# config/optimization_config.yaml
scheduled_optimization:
  enabled: true
  schedule: "0 2 * * *"  # Daily at 2 AM
  min_traces: 100  # Minimum traces needed
  framework: "dspy"  # or "textgrad"
  evaluation_threshold: 0.7
```

---

### **2. On-Demand Self-Improvement** (Apps)

**Trigger:** Performance degradation detected

**Process:**
```
1. Supervisory agent monitors MLflow metrics
2. Detects trigger condition:
   - Error rate > 5%
   - Avg rating < 3.0
   - Response time > 5s
   - Volume >= min_samples
3. Calls Optimization MCP Server
4. Runs fast optimization (smaller dataset)
5. Updates prompts immediately
6. Logs intervention to MLflow
```

**Pros:**
- Fast reaction to issues (minutes)
- Self-healing capabilities
- Continuous monitoring
- Can be manually triggered

**Cons:**
- Slightly higher compute cost (always monitoring)
- Smaller datasets (less statistical power)
- May overcorrect to outliers

**Configuration:**
```yaml
# config/agent_config.yaml
ondemand_optimization:
  enabled: true
  supervisory_agent:
    check_interval: 300  # seconds
    min_traces_for_trigger: 50
  triggers:
    error_rate_threshold: 0.05
    rating_threshold: 3.0
    response_time_threshold: 5.0
  mcp_server:
    endpoint: "http://localhost:9000"
```

---

## Technology Mapping

| Component | L1 (Chatbot) | L2 (Assistant) | L3 (API) | L4 (Workflow) | L5 (System) |
|-----------|--------------|----------------|----------|---------------|-------------|
| **Runtime** | Databricks Apps | Databricks Apps | Databricks Apps | Databricks Apps | Databricks Apps |
| **Web Framework** | Flask | Flask | FastAPI | FastAPI | FastAPI |
| **UI** | Web Chat | Web Chat | None (API) | None (API) | None (API) |
| **Memory** | None | Lakebase | Lakebase | Lakebase | Lakebase |
| **Orchestration** | None | None | None | LangGraph | LangGraph |
| **MCP** | None | Optional | Yes | Yes | Yes |
| **A2A** | None | None | None | No | Yes |
| **Optimization** | Optional | Optional | Recommended | Required | Required |

---

## Data Flow

### **Real-Time Inference**

```
User Request
  ↓
Flask/FastAPI App (Databricks Apps)
  ↓
DatabricksLLM (toolkit integration)
  ↓ (REST API call)
Databricks Model Serving
  ↓
Response
  ↓ (auto-traced)
MLflow (Unity Catalog)
```

### **Scheduled Optimization**

```
Cron Schedule
  ↓
Databricks Workflow Job
  ↓
Fetch traces from MLflow
  ↓
DSPy/TextGrad Optimization
  ↓
Evaluate new prompts
  ↓
Update Unity Catalog (if better)
  ↓
Log metrics to MLflow
```

### **On-Demand Optimization**

```
Agent logs trace to MLflow
  ↓
Supervisory Agent monitors metrics
  ↓
Detects trigger condition (error spike)
  ↓
Calls Optimization MCP Server
  ↓
Runs fast optimization
  ↓
Updates prompts in Unity Catalog
  ↓
Agents pick up new prompts immediately
```

---

## Storage & Artifacts

### **Unity Catalog**

**Stores:**
- Optimized prompts (latest version)
- Configuration files
- Agent metadata
- UC Functions (callable tools)

**Accessed By:**
- Agents (read prompts at runtime)
- Optimization workflows (write new prompts)
- Supervisory agent (read/write)

### **MLflow**

**Stores:**
- Traces (all agent interactions)
- Evaluation metrics
- Optimization runs
- Model versions (if fine-tuning)

**Accessed By:**
- Agents (auto-trace via toolkit)
- Workflows (read traces, write evals)
- Supervisory agent (read metrics)
- Dashboards (visualization)

### **Lakebase (Delta Lake + Vector Search)**

**Stores:**
- Agent memory (conversation history)
- Document embeddings (RAG)
- Vector indexes

**Accessed By:**
- L2-L5 agents (read/write memory)
- MCP servers (vector search tools)

---

## Compute Resources

### **Databricks Apps Sizing**

| Agent Type | Recommended Size | Reasoning |
|------------|------------------|-----------|
| L1-L2 | Small (2-4 cores, 8-16 GB) | Simple logic, minimal compute |
| L3 | Medium (4-8 cores, 16-32 GB) | API serving, moderate traffic |
| L4 | Large (8-16 cores, 32-64 GB) | Complex workflows, parallel execution |
| L5 | X-Large (16+ cores, 64+ GB) | Multi-agent, high concurrency |

**Supervisory Agent:** Small (always-on, lightweight monitoring)

### **Databricks Workflows Sizing**

| Job Type | Recommended Size | Reasoning |
|----------|------------------|-----------|
| Prompt Optimization | Large (16+ cores) | Compute-intensive (DSPy/TextGrad) |
| Batch Evaluation | Medium (8 cores) | Parallel eval, moderate compute |
| Dataset Prep | Medium (8 cores) | Data processing |
| Monitoring | Small (2-4 cores) | Aggregation only |

**Tip:** Use cheaper compute tiers (spot instances) for workflows since latency isn't critical.

---

## Cost Optimization

### **Apps (Always-On)**
- Right-size based on traffic patterns
- Use smaller instances for L1-L2
- Scale up only for L3-L5 with heavy traffic
- Consider serverless if traffic is sporadic (future feature)

### **Workflows (Scheduled)**
- Run during off-peak hours (lower compute costs)
- Use spot instances (30-80% cheaper)
- Batch operations together
- Set min_traces thresholds to avoid unnecessary runs

### **Optimization Strategy**
- **Start with scheduled only** (cheaper)
- **Add on-demand** when you have:
  - High-stakes applications (cost of downtime > cost of monitoring)
  - Unpredictable traffic patterns
  - Strict SLAs

---

## Security & Permissions

### **Service Principal Setup**

Each Databricks App gets its own Service Principal:

```
App Service Principal needs access to:
✅ Model Serving endpoint (CAN_QUERY)
✅ Unity Catalog schema (READ/WRITE for prompts)
✅ MLflow experiments (READ/WRITE for traces)
✅ Delta tables (READ for Lakebase memory)
```

**How to Add:**
1. Go to Databricks Apps UI
2. Find your app → Resources tab
3. Add model endpoint with `CAN_QUERY` permission
4. Add UC catalog/schema with appropriate permissions

---

## Monitoring

### **App Health**
- `/health` endpoint (built into scaffolds)
- Databricks Apps dashboard
- MLflow trace logging (auto-enabled)

### **Optimization Health**
- MLflow experiment for optimization runs
- Metrics: prompt improvement %, eval scores
- Alerts on optimization failures

### **Agent Performance**
- MLflow traces dashboard
- Custom dashboards via Databricks SQL
- Supervisory agent monitoring (if enabled)

---

## Best Practices

1. **Start Simple**
   - Deploy L1 first to test infrastructure
   - Add scheduled optimization when you have data
   - Add on-demand only if needed

2. **Separate Concerns**
   - Real-time logic in Apps
   - Heavy compute in Workflows
   - Never run optimization in the serving path

3. **Version Control**
   - All prompts in Unity Catalog
   - Tag optimization runs in MLflow
   - Track prompt versions

4. **Cost Management**
   - Monitor Apps uptime costs
   - Use spot instances for Workflows
   - Set min_traces thresholds

5. **Security**
   - Use Service Principals (not personal tokens)
   - Limit permissions to minimum needed
   - Rotate credentials regularly

---

## Next Steps

- **Deploy Your First Agent:** See [Deployment Guide](DEPLOYMENT_GUIDE.md)
- **Set Up Optimization:** See [Evaluation Guide](EVALUATION_GUIDE.md)
- **Configure Monitoring:** See [Observability Guide](OBSERVABILITY_GUIDE.md)
