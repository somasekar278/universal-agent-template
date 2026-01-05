# Platform Integration Guide

Complete guide to integrating with native platforms: LangGraph, DSPy, MLflow 3, Databricks, and MCP.

---

## Table of Contents

1. [Philosophy](#philosophy)
2. [LangGraph - Orchestration](#langgraph---orchestration)
3. [DSPy - Reasoning](#dspy---reasoning)
4. [Lakebase - Vector Search](#lakebase---vector-search)
5. [Databricks SDK - Unity Catalog](#databricks-sdk---unity-catalog)
6. [MLflow UI & SQL - Visualization](#mlflow-ui--sql---visualization)
7. [Databricks Workflows - Scheduling](#databricks-workflows---scheduling)
8. [Databricks Deployment](#databricks-deployment)
9. [MCP Integration](#mcp-integration)

---

## Philosophy

**We integrate, we don't reinvent.**

This framework builds ON TOP OF existing platforms, not INSTEAD OF them. Use native APIs directly for full power, or use our thin wrappers for convenience.

---

## LangGraph - Orchestration

Use LangGraph StateGraph for all agent orchestration.

### Basic Agent Workflow

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict

class State(TypedDict):
    messages: list
    current_agent: str
    result: dict

# Define workflow
workflow = StateGraph(State)
workflow.add_node("research", research_agent)
workflow.add_node("analyze", analyze_agent)
workflow.add_node("summarize", summarize_agent)
workflow.add_edge("research", "analyze")
workflow.add_edge("analyze", "summarize")
workflow.add_edge("summarize", END)
workflow.set_entry_point("research")

# Compile and run
app = workflow.compile()
result = app.invoke({"messages": ["Query"], "current_agent": "research"})
```

### Multi-Agent with Conditional Routing

```python
def should_continue(state: State) -> str:
    if state["confidence"] > 0.9:
        return "end"
    return "expert_review"

workflow = StateGraph(State)
workflow.add_node("analyze", analyze_agent)
workflow.add_node("expert_review", expert_agent)
workflow.add_conditional_edges(
    "analyze",
    should_continue,
    {"end": END, "expert_review": "expert_review"}
)
workflow.add_edge("expert_review", END)
workflow.set_entry_point("analyze")
```

**Resources:**
- LangGraph Docs: https://langchain-ai.github.io/langgraph/
- Examples: https://github.com/langchain-ai/langgraph/tree/main/examples

---

## DSPy - Reasoning

Use DSPy for reasoning patterns and prompt optimization.

### Chain of Thought

```python
import dspy

lm = dspy.Databricks(model="databricks-dbrx-instruct")
dspy.settings.configure(lm=lm)

class Analyze(dspy.Signature):
    """Analyze input with reasoning"""
    input = dspy.InputField()
    analysis = dspy.OutputField()
    reasoning_steps = dspy.OutputField()

class ReasoningAgent(dspy.Module):
    def __init__(self):
        super().__init__()
        self.analyze = dspy.ChainOfThought(Analyze)

    def forward(self, input):
        return self.analyze(input=input)

agent = ReasoningAgent()
result = agent(input="Analyze this transaction...")
print(f"Analysis: {result.analysis}")
print(f"Reasoning: {result.reasoning_steps}")
```

### Optimization (Already Integrated)

Our `agent-optimize` command uses DSPy's optimization:

```bash
agent-optimize --config config/optimization/my_agent.yaml
```

**Resources:**
- DSPy Docs: https://dspy-docs.vercel.app/
- Databricks DSPy: https://docs.databricks.com/en/generative-ai/dspy.html
- Our Integration: `optimization/dspy_optimizer.py`

---

## Lakebase - Vector Search

Use Databricks Lakebase for vector/memory storage.

### Using Our Thin Wrapper

```python
from memory import LakebaseClient

client = LakebaseClient()

# Create index (one-time)
client.create_index(
    name="main.agents.knowledge",
    source_table="main.agents.documents",
    embedding_column="content"
)

# Search
results = client.search(
    index_name="main.agents.knowledge",
    query="What is machine learning?",
    num_results=5
)
```

### Using Databricks SDK Directly

```python
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.catalog import VectorIndexType

w = WorkspaceClient()

# Create index
w.vector_search_indexes.create_index(
    name="main.agents.my_vectors",
    endpoint_name="my_endpoint",
    primary_key="id",
    index_type=VectorIndexType.DELTA_SYNC,
    delta_sync_index_spec={
        "source_table": "main.agents.documents",
        "embedding_source_columns": [
            {
                "name": "content",
                "embedding_model_endpoint_name": "databricks-bge-large-en"
            }
        ]
    }
)

# Search
results = w.vector_search_indexes.query_index(
    index_name="main.agents.my_vectors",
    query_text="Your query",
    num_results=10
)
```

**Resources:**
- Lakebase Docs: https://docs.databricks.com/en/generative-ai/vector-search.html
- Our Wrapper: `memory/lakebase_client.py`

---

## Databricks SDK - Unity Catalog

Use Databricks SDK for all UC operations.

### Tables

```python
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

# List tables
tables = w.tables.list(catalog_name="main", schema_name="default")
for table in tables:
    print(f"{table.name}: {table.table_type}")

# Get table details
table = w.tables.get(full_name="main.default.my_table")
print(f"Columns: {table.columns}")

# Create table
w.tables.create(
    name="main.default.new_table",
    catalog_name="main",
    schema_name="default",
    table_type="MANAGED",
    columns=[
        {"name": "id", "type_name": "INT"},
        {"name": "content", "type_name": "STRING"}
    ]
)
```

### Delta Tables with Spark

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder.getOrCreate()

# Read
df = spark.table("main.default.my_table")

# Write
df.write.format("delta").mode("append").saveAsTable("main.default.my_table")
```

**Resources:**
- Databricks SDK: https://databricks-sdk-py.readthedocs.io/
- Unity Catalog: https://docs.databricks.com/en/data-governance/unity-catalog/

---

## MLflow UI & SQL - Visualization

### MLflow UI (Automatic)

All evaluations, experiments, and optimizations automatically appear in MLflow UI:

**Access:** Your Databricks workspace → MLflow → Experiments

**Features:**
- Metrics charts (automatic)
- Parameter comparison
- Artifact viewing
- Run comparison
- Model registry

### Databricks SQL Dashboards

Create custom business dashboards:

```sql
-- Agent performance over time
SELECT
    agent_name,
    DATE(timestamp) as date,
    AVG(correctness_score) as avg_correctness,
    AVG(latency_ms) as avg_latency,
    COUNT(*) as num_requests
FROM main.agents.telemetry
WHERE timestamp > CURRENT_DATE - INTERVAL 7 DAYS
GROUP BY agent_name, DATE(timestamp)
ORDER BY date DESC
```

**Create Dashboard:**
1. Databricks SQL → Queries
2. Write your SQL
3. Add visualization (chart type)
4. Add to dashboard
5. Schedule refresh

**Resources:**
- Databricks SQL: https://docs.databricks.com/en/sql/
- Dashboards: https://docs.databricks.com/en/dashboards/

---

## Databricks Workflows - Scheduling

Use Databricks Workflows for scheduled tasks.

### Example: Scheduled Monitoring

```yaml
# databricks-workflow.yml
name: agent_monitoring
schedule:
  quartz_cron_expression: "0 0 * * * ?"  # Every hour
  timezone_id: "UTC"

tasks:
  - task_key: monitor_agents
    python_wheel_task:
      package_name: "sota_agent_framework"
      entry_point: "monitor_agents"
    libraries:
      - pypi:
          package: "sota-agent-framework>=0.5.0"
    cluster:
      num_workers: 2
      spark_version: "13.3.x-scala2.12"
      node_type_id: "i3.xlarge"
```

**Deploy:**
```bash
databricks workflows create --json @databricks-workflow.yml
```

**Resources:**
- Workflows: https://docs.databricks.com/en/workflows/
- Job API: https://docs.databricks.com/api/workspace/jobs

---

## Databricks Deployment

### Architecture

**Component Placement:**

| Component | Technology | Deployment |
|-----------|-----------|------------|
| Agent Application | Python/FastAPI | **Databricks Apps** (hot pools) |
| LLM Inference | Foundation Models | **Databricks Model Serving** (always-on) |
| Vector Search | Lakebase | **Databricks Vector Search** |
| Prompts & Configs | Unity Catalog | **UC Volumes** |
| Telemetry Sink | Delta Lake | **UC Tables** |
| Dashboards | SQL | **Databricks SQL** |
| Orchestration | Workflows | **Databricks Jobs** |

### Databricks Apps Deployment

#### 1. Create Deployment Config

```yaml
# deployment/databricks-app.yml
resources:
  - name: my-agent-app
    description: "Agent application"
    runtime:
      kind: container
      image: "your-registry/agent-app:latest"
      command: ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
      env:
        - name: DATABRICKS_HOST
          valueFrom:
            secretRef: databricks-host
        - name: DATABRICKS_TOKEN
          valueFrom:
            secretRef: databricks-token
      ports:
        - name: app
          containerPort: 8000
          protocol: TCP
      resources:
        requests:
          cpu: "2"
          memory: "8Gi"
        limits:
          cpu: "4"
          memory: "16Gi"
    health:
      httpPath: /health
      port: 8000
      intervalSeconds: 30
    autoscaling:
      enabled: true
      minReplicas: 1
      maxReplicas: 5
      metrics:
        - type: Resource
          resource:
            name: cpu
            target:
              type: Utilization
              averageUtilization: 70
```

#### 2. Deploy

```bash
databricks apps deploy -f deployment/databricks-app.yml
```

#### 3. Access

```bash
# Get app URL
databricks apps list
# → https://your-workspace.cloud.databricks.com/apps/my-agent-app
```

**Resources:**
- Databricks Apps: https://docs.databricks.com/en/dev-tools/databricks-apps/

---

## MCP Integration

Model Context Protocol enables agents to call tools (including self-improvement).

### Architecture

**Two MCP Servers:**

1. **MLflow MCP** (Native, MLflow 3.5.1+)
   - Traces, experiments, models
   - Native Databricks offering

2. **Databricks Agent MCP** (Custom, this framework)
   - Optimization triggers
   - Dataset curation
   - Performance monitoring

### Deployment Modes

Configure in `config/mcp_deployment_config.yaml`:

**Embedded (Dev/Simple):**
```yaml
deployment_mode: embedded  # Both MCP servers run as subprocesses
```

**Separate (Production):**
```yaml
deployment_mode: separate  # MCP servers in separate container
```

**External (Enterprise):**
```yaml
deployment_mode: external  # MCP servers managed externally
mlflow_mcp:
  endpoint: "https://mcp-prod.company.com:5000"
databricks_agent_mcp:
  endpoint: "https://mcp-prod.company.com:6000"
```

### Using MCP in Agents

```python
from mcp import McpClient

async with McpClient() as client:
    # Check agent performance
    perf = await client.call_databricks_tool(
        "check_performance",
        {"agent_id": "fraud_detector"}
    )

    if perf["status"] == "degraded":
        # Trigger optimization
        result = await client.call_databricks_tool(
            "trigger_optimization",
            {"agent_id": "fraud_detector"}
        )

    # Query MLflow traces
    traces = await client.call_mlflow_tool(
        "search_traces",
        {"filter_string": "tags.agent_id = 'fraud_detector'"}
    )
```

### MCP Configuration Files

- **Deployment:** `config/mcp_deployment_config.yaml`
- **Agent Settings:** `config/agent_config.yaml` (mcp_client section)
- **Full Guide:** See `MIGRATION_GUIDE_V0.5.md`

**Resources:**
- MCP Protocol: https://modelcontextprotocol.io/
- MLflow MCP: https://mlflow.org/docs/latest/llms/tracing/index.html#mcp-server
- Our Integration: `sota_agent/mcp_client.py`, `sota_agent/mcp_manager.py`

---

## Quick Reference

### When to Use What

| Need | Use | Not |
|------|-----|-----|
| Orchestrate agents | LangGraph | Custom `orchestration/` |
| Reasoning patterns | DSPy | Custom `reasoning/` |
| Vector search | Lakebase | Custom `memory/` |
| UC operations | Databricks SDK | Custom `uc_registry/` |
| Dashboards | MLflow UI + SQL | Custom `visualization/` |
| Scheduling | Workflows | Custom schedulers |
| Evaluation | MLflow 3 | Custom benchmark system |

### Configuration

All configuration in two files:
- `config/agent_config.yaml` - Agent settings
- `config/mcp_deployment_config.yaml` - MCP deployment

### CLI Commands

All commands still work:
- `agent-generate` - Generate agent code
- `agent-optimize` - Optimize prompts (uses DSPy)
- `agent-benchmark` - Run benchmarks (uses MLflow 3)
- `agent-deploy` - Deploy to Databricks
- `agent-telemetry` - Setup telemetry

**See:** `agent --help` for full list

---

## Getting Help

- **Platform Integration:** This guide
- **Evaluation:** `EVALUATION_GUIDE.md`
- **Monitoring:** `OBSERVABILITY_GUIDE.md`
- **Migration:** `MIGRATION_GUIDE_V0.5.md` (from v0.4.x)

---

**Remember: We build ON TOP OF platforms, not INSTEAD OF them.**
