# Databricks Agent Toolkit

[![PyPI version](https://badge.fury.io/py/databricks-agent-toolkit.svg)](https://pypi.org/project/databricks-agent-toolkit/)

**Unified toolkit for building production agents on Databricks**

Pre-wired integrations + scaffolding generators for LangGraph, LangChain, and custom agents.

---

## What This Is

**A toolkit, not a framework.**

- Use with **LangGraph**, **LangChain**, or your own agent code
- Pre-wired integrations to **all Databricks services**
- Best practices for **Databricks-native agents**
- **Optional scaffolds** to generate working code

Think of it like **Create React App** but for Databricks agents.

---

## Quick Start

### Option 1: Use Integrations Directly

```bash
pip install databricks-agent-toolkit
```

```python
from databricks_agent_toolkit.integrations import DatabricksLLM

# Easy Databricks Model Serving (auto-auth, auto-trace)
llm = DatabricksLLM(endpoint="databricks-claude-sonnet-4-5")
response = await llm.chat([{"role": "user", "content": "Hello!"}])
print(response["content"])
```

### Option 2: Generate a Scaffold

```bash
pip install databricks-agent-toolkit

# Generate chatbot (L1) - Simple conversational AI
databricks-agent-toolkit generate chatbot my-bot

# Generate assistant (L2) - With memory + RAG
databricks-agent-toolkit generate assistant my-assistant

cd my-assistant
pip install -r requirements.txt

# Configure RAG in config.yaml (optional)
# rag:
#   enabled: true
#   source: /Volumes/main/default/docs
#   backend: pgvector  # or vector_search

python app.py  # Web UI on http://localhost:8000

# Deploy to Databricks Apps
databricks apps deploy my-assistant
```

---

## ✨ New in 0.1.3: RAG-Powered Assistants

The L2 Assistant scaffold now includes **production-ready RAG** with two backends:

### **pgvector** (Default, Cost-Effective)
- 🚀 Instant setup (< 1 second)
- 💰 Included in Lakebase, no extra cost
- 📊 IVFFlat (fast) or HNSW (accurate) indexing
- 📁 Auto-indexes from UC Volumes
- ✅ Perfect for small-medium knowledge bases (100s-10,000s docs)

### **Databricks Vector Search** (Enterprise-Scale)
- 🌐 Millions of documents
- 🔄 Auto-sync via Delta Change Data Feed
- 🤖 Managed embeddings (Databricks FMAPI)
- 🏢 Enterprise features (versioning, lineage, governance)
- ✅ Perfect for large-scale production RAG

**Both backends:**
- Auto-index documents from UC Volumes on startup
- Generate embeddings using Databricks Foundation Models
- Support incremental updates
- Configurable via `config.yaml`

```yaml
# Simple pgvector setup
rag:
  enabled: true
  source: /Volumes/main/default/docs
  backend: pgvector
  index_type: ivfflat  # or hnsw for better accuracy
```

---

## What's Included

### **Storage & Memory: Choose the Right Tool**

**Lakebase (PostgreSQL)** - Use for:
- Conversational memory (chat history, sessions)
- Structured agent data (user profiles, configurations)
- OLTP workloads (fast reads/writes)
- pgvector for small-scale embeddings

**DatabricksVectorSearch (Delta Lake)** - Use for:
- Large-scale RAG (millions of documents)
- Knowledge bases synced from Delta tables
- Semantic search across data lake
- Auto-embedding with Databricks models

**Both work together!** L2+ agents typically use Lakebase for conversations and Vector Search for knowledge retrieval.

### **Integrations** (Pre-wired Databricks Services)

```python
from databricks_agent_toolkit.integrations import (
    DatabricksLLM,           # Model Serving
    DatabricksMCPTools,      # Managed MCP Servers
    UnityAgentArtifacts,     # Unity Catalog
    Lakebase,                # Managed PostgreSQL (conversations, memory)
    DatabricksVectorSearch,  # Delta Lake vector search (RAG, knowledge bases)
    DatabricksAppDeployment  # Apps deployment
)
```

- **Model Serving** - Easy LLM client with OAuth M2M auth, MLflow auto-tracing
- **Unity Catalog** - Manage prompts, configs, functions
- **Lakebase** - Managed PostgreSQL for conversational memory + pgvector for RAG
- **DatabricksVectorSearch** - Delta Lake-based vector search for enterprise RAG
- **RAG Manager** - Auto-indexing from UC Volumes, dual-backend support (NEW in 0.1.3)
- **Scaffold Validator** - Auto-validates generated scaffolds (NEW in 0.1.3)
- **Managed MCP Servers** - Vector Search, Genie, UC Functions, DBSQL
- **Databricks Apps** - One-command deployment
- **Workflows** - Schedule optimization jobs
- **SQL Dashboards** - Pre-built monitoring

### **Evaluation** (MLflow 3 GenAI)

Located in `evaluation/`:
- Built-in scorers (Correctness, Groundedness, Safety)
- Custom scorers & judges
- Automatic evaluation logging

### **Optimization** (DSPy + TextGrad)

Located in `optimization/`:
- Automatic prompt optimization
- Store optimized prompts to Unity Catalog
- A/B testing support

### **Telemetry** (Zerobus + OpenTelemetry)

Located in `telemetry/`:
- Real-time event tracking
- Automatic Delta Lake writes
- Pre-built dashboards

### **CLI Tools**

```bash
databricks-agent-toolkit generate chatbot my-bot      # L1: Simple chatbot
databricks-agent-toolkit generate assistant my-agent  # L2: With memory + RAG
```

**Scaffold Types (v0.1.3):**

| Scaffold | Status | Features |
|----------|--------|----------|
| **chatbot** (L1) | ✅ Available | Simple conversational AI, MLflow tracing |
| **assistant** (L2) | ✅ Available | Memory (Lakebase), RAG (pgvector/Vector Search), UC Volumes |
| **api** (L3) | 🔜 Coming soon | FastAPI production endpoint |
| **workflow** (L4) | 🔜 Coming soon | LangGraph workflows |
| **system** (L5) | 🔜 Coming soon | Multi-agent with A2A |

---

## Example: LangGraph Agent with Databricks

```python
from langgraph.graph import StateGraph
from databricks_agent_toolkit.integrations import (
    DatabricksLLM,
    DatabricksMCPTools,
    UnityAgentArtifacts
)

# 1. Pre-wired Databricks services (easy!)
llm = DatabricksLLM(endpoint="databricks-claude-sonnet-4-5")
mcp = DatabricksMCPTools(servers={
    "vector_search": {"catalog": "prod", "schema": "docs"}
})
uc = UnityAgentArtifacts(catalog="main", schema="agents")

# 2. Your agent logic (standard LangGraph)
async def my_agent(state):
    tools = await mcp.get_tool_schemas()
    response = await llm.chat(
        messages=state["messages"],
        tools=tools
    )
    return {"response": response}

# 3. Build workflow (standard LangGraph)
workflow = StateGraph()
workflow.add_node("agent", my_agent)
app = workflow.compile()

# 4. Deploy (one line - coming soon)
# from databricks_agent_toolkit.integrations import DatabricksAppDeployment
# deployer = DatabricksAppDeployment()
# url = deployer.deploy_agent(agent_name="my-agent", app_code_path=".")
```

---

## vs. Other Frameworks

| | **Databricks Agent Toolkit** | **LangGraph** | **LangChain** |
|---|---|---|---|
| **Purpose** | Databricks integrations | Agent framework | LLM framework |
| **Use Together?** | YES | Primary framework | Alternative framework |
| **Model Serving** | Pre-wired | You integrate | You integrate |
| **Unity Catalog** | Pre-wired | You integrate | You integrate |
| **Lakebase** | Pre-wired | You integrate | You integrate |
| **Managed MCPs** | Pre-wired | You integrate | You integrate |
| **MLflow 3** | Pre-wired | You integrate | You integrate |
| **Databricks Apps** | One-command deploy | You figure out | You figure out |

**Use this toolkit WITH LangGraph or LangChain, not instead of.**

---

## Documentation

- **[Architecture Guide](docs/ARCHITECTURE.md)** - Deployment model, Apps vs Workflows, optimization strategy
- **[Quick Start](docs/GETTING_STARTED.md)** - Get started in 5 minutes
- **[Integrations Guide](docs/PLATFORM_INTEGRATION.md)** - All Databricks services
- **[Examples](examples/)** - LangGraph, LangChain, custom agents
- **[Evaluation Guide](docs/EVALUATION_GUIDE.md)** - MLflow 3 evaluation
- **[Optimization Guide](docs/EVALUATION_GUIDE.md#optimization)** - DSPy + TextGrad

---

## Learning Path

| Level | Complexity | Time | What You Build | Status |
|-------|-----------|------|----------------|--------|
| **L1 (chatbot)** | Simple | 2-4h | Simple chatbot (learn basics) | ✅ v0.1.0 |
| **L2 (assistant)** | Basic+ | 4-8h | Assistant with memory + RAG | ✅ v0.1.3 |
| **L3 (api)** | Intermediate | 8-16h | Production API (FastAPI + toolkit) | 🔜 Coming soon |
| **L4 (workflow)** | Advanced | 16-32h | Complex workflow (LangGraph + optimization) | 🔜 Coming soon |
| **L5 (system)** | Expert | 32-64h | Multi-agent system (LangGraph + A2A) | 🔜 Coming soon |

See `config/examples/` for configuration templates.

---

## Architecture

### **Deployment Model**

```
┌─────────────────────────────────────────────────────────┐
│  Databricks Apps (Real-time, Always-On)                 │
│  ┌────────────────────────────────────────────────────┐ │
│  │ L1-L2: Flask Web UI (chatbot, assistant)          │ │ ← User interaction
│  │ L3-L5: FastAPI REST API (workflows, systems)      │ │ ← API calls
│  └────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────┐ │
│  │ Supervisory Agent (optional)                      │ │ ← Self-improvement
│  │  - Monitors MLflow metrics in real-time          │ │
│  │  - Triggers on-demand optimization               │ │
│  │  - Auto-fixes performance issues                 │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
              ↕ (logs traces)        ↕ (reads/writes)
┌─────────────────────────────────────────────────────────┐
│  Unity Catalog + MLflow                                  │
│  - Prompts, configs, models                             │
│  - Evaluation metrics & traces                          │
│  - Training datasets                                     │
└─────────────────────────────────────────────────────────┘
              ↕ (scheduled jobs)
┌─────────────────────────────────────────────────────────┐
│  Databricks Workflows (Batch/Scheduled)                  │
│  - Nightly prompt optimization (DSPy/TextGrad)          │ ← Scheduled
│  - Batch evaluation runs                                │
│  - Dataset preparation                                   │
│  - Monitoring reports                                    │
└─────────────────────────────────────────────────────────┘
```

### **Optimization Strategy: Dual Approach**

**1. Scheduled Optimization** (Databricks Workflows)
- Runs nightly/weekly on a schedule
- Uses accumulated traces since last run
- Stable, predictable improvements
- Lower compute cost (batch processing)

**2. On-Demand Self-Improvement** (Supervisory Agent in Apps)
- Monitors agent performance in real-time
- Triggers optimization when needed:
  - Error rate spikes
  - User feedback drops below threshold
  - Performance degrades
  - Manual trigger via API
- Faster response to issues
- Slightly higher compute cost (always monitoring)

**Both work together:** Scheduled for maintenance, on-demand for reactive fixes.

### **Stack Layers**

```
Your Agent Code (LangGraph/LangChain/Custom)
    ↓
Databricks Agent Toolkit (Integrations Layer)
    ↓
Databricks Services (Model Serving, UC, Lakebase, MCP, etc.)
```

**You own:** Agent logic, workflows, business rules  
**Toolkit provides:** Easy access to all Databricks services  
**Databricks provides:** Infrastructure, services, deployment

---

## Philosophy

> **"Build ON TOP OF existing platforms, not INSTEAD OF"**

We don't replace LangGraph or LangChain.  
We make Databricks services easy to use with them.

---

## Installation

```bash
# Minimal (just integrations)
pip install databricks-agent-toolkit

# With Databricks services
pip install databricks-agent-toolkit[databricks]

# With agent frameworks (LangGraph, LangChain)
pip install databricks-agent-toolkit[agent-frameworks]

# With optimization (DSPy, TextGrad)
pip install databricks-agent-toolkit[optimization]

# Everything
pip install databricks-agent-toolkit[all]
```

---

## 🤝 Contributing

We welcome contributions! This toolkit is in active development (v0.1.3).

**Priority areas:**
- Complete scaffold generation (L1-L5)
- Enhance Unity Catalog integration
- Add more MCP examples
- Improve deployment automation

---

## 📄 License

Apache 2.0

---

## 🔗 Resources

- [Databricks Documentation](https://docs.databricks.com/)
- [Databricks Managed MCP Servers](https://docs.databricks.com/generative-ai/mcp/)
- [LangGraph](https://langchain-ai.github.io/langgraph/)
- [MLflow 3 GenAI](https://mlflow.org/docs/latest/llms/index.html)

---

## 🎉 What's Next?

**v0.1.3 (Current Release):**
- ✅ Core integrations (Model Serving, Unity Catalog, OAuth M2M auth)
- ✅ L1 Chatbot scaffold (simple conversational AI)
- ✅ L2 Assistant scaffold (memory + RAG)
- ✅ RAG with pgvector + Databricks Vector Search
- ✅ UC Volume auto-indexing
- ✅ IVFFlat/HNSW configurable indexing
- ✅ Scaffold validation system
- ✅ MLflow 3 tracing (@mlflow.trace)
- ✅ Databricks Apps deployment (OAuth M2M)

**v0.2.0 (Next Release):**
- L3-L5 scaffold generation (api, workflow, system)
- MCP server integration for L4/L5
- DSPy/TextGrad optimization workflows
- Advanced monitoring & observability
- Video tutorials

---

**Built with ❤️  for the Databricks agent community**
