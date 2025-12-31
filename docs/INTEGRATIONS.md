# External Integrations Guide

**All external integrations in one place**: A2A, MCP, LangGraph, Databricks

---

## 📋 Table of Contents

- [Agent2Agent Protocol (A2A) - Official](#agent2agent-protocol-a2a)
- [Model Context Protocol (MCP)](#model-context-protocol-mcp)
- [LangGraph Orchestration](#langgraph-orchestration)
- [Databricks Integration](#databricks-integration)

---

## 🌐 Agent2Agent Protocol (A2A)

**Purpose**: Official Linux Foundation standard for cross-framework agent communication

**Level**: ⭐⭐⭐⭐⭐ Advanced (Level 5)

### Overview

The [Agent2Agent (A2A) Protocol](https://github.com/a2aproject/A2A) is an open protocol enabling communication and interoperability between opaque agentic applications across different frameworks.

**Official Resources:**
- GitHub: https://github.com/a2aproject/A2A
- Website: https://a2a-protocol.org/
- Specification: https://a2a-protocol.org/docs/specification

**Key Features:**
- JSON-RPC 2.0 over HTTP(S)
- Agent Cards for discovery
- Task-based collaboration
- Streaming (SSE) and push notifications
- Enterprise security and authentication
- Multi-framework interoperability

### Quick Start

```bash
# Install with A2A support
pip install sota-agent-framework[a2a]
```

### Exposing Agents via A2A

```python
from agents.a2a import A2AServer

# Expose your agent via A2A protocol
server = A2AServer(
    agent=my_fraud_agent,
    name="fraud_detector",
    description="Advanced fraud detection agent",
    skills=["fraud_detection", "risk_analysis"],
    port=8080
)

# Start server
await server.start()

# Agent Card published at http://localhost:8080/card.json
# A2A endpoint at http://localhost:8080/a2a
# Other A2A-compliant agents can now discover and use it!
```

### Calling External A2A Agents

```python
from agents.a2a import A2AClient

# Discover external agent
client = A2AClient()
agent_card = await client.discover(
    "https://external-service.com/agent/card.json"
)

print(f"Found: {agent_card.name}")
print(f"Skills: {agent_card.skills}")

# Execute task on external agent
result = await client.execute_task(
    agent_url=agent_card.url,
    skill="risk_analysis",
    input_data={"transaction": transaction_data},
    timeout=60.0
)

print(f"Result: {result}")
```

### Agent Cards

Agent Cards are JSON documents describing agent capabilities:

```python
from agents.a2a import create_agent_card

# Create Agent Card
card = create_agent_card(
    name="fraud_detector",
    description="Advanced fraud detection agent",
    url="http://localhost:8080/a2a",
    skills=["fraud_detection", "risk_analysis"],
    author="SOTA Framework",
    supports_streaming=True
)

# Publish card
with open("agent_card.json", "w") as f:
    f.write(card.to_json())
```

### Integration with SOTA Agents

```python
from agents.a2a import A2AAgent

# Wrap existing agent
fraud_agent = MyFraudAgent()
a2a_agent = A2AAgent(
    agent=fraud_agent,
    name="fraud_detector",
    skills=["fraud_detection"]
)

# Call external A2A agents
external_result = await a2a_agent.call_external_agent(
    agent_url="http://external.com/a2a",
    skill="deep_analysis",
    input_data={"transaction": data}
)

# Discover agents by skill
agents = await a2a_agent.find_agents_with_skill(
    skill="risk_analysis",
    marketplace_url="https://marketplace.com/api/agents"
)
```

### Why Use A2A?

**✅ Use A2A When:**
- Building agent marketplaces
- Need cross-framework interoperability
- Enterprise agent ecosystems
- Agents built on different platforms need to collaborate
- Industry-standard compliance required

**❌ Don't Use A2A When:**
- Simple internal communication (use Router)
- Single-framework systems (use Router)
- Learning basics (start with Router, add A2A at Level 5)

### Official SDK

The official A2A SDK is maintained by the Linux Foundation:

```bash
pip install a2a-sdk
```

Our integration wraps the official SDK and integrates it seamlessly with SOTA Framework agents.

**Full Documentation**: See `agents/a2a/` directory and https://a2a-protocol.org/

---

## 🔌 Model Context Protocol (MCP)

**Purpose**: Standardized tool interfaces for external services

### Quick Start

```bash
# Install with MCP support
pip install sota-agent-framework[mcp]
```

### Usage

```python
from agents.mcp_client import AgentMCPClient

# Initialize MCP client
mcp_client = AgentMCPClient()

# Connect to MCP server (stdio-based)
await mcp_client.connect("python", "path/to/mcp_server.py")

# List available tools
tools = await mcp_client.list_tools()

# Call a tool
result = await mcp_client.call_tool("bin_lookup", {"bin": "123456"})

# Close when done
await mcp_client.close()
```

### Configuration

```yaml
# config/sota_config.yaml
mcp:
  enabled: true
  servers:
    - name: "fraud_tools"
      command: "python"
      args: ["mcp_servers/fraud_tools.py"]
    - name: "data_tools"
      command: "python"
      args: ["mcp_servers/data_tools.py"]
```

### Creating Custom MCP Servers

See `mcp-servers/` directory for examples.

**Full Documentation**: See `docs/MCP_INTEGRATION.md` (archived) for detailed guide

---

## 🔄 LangGraph Orchestration

**Purpose**: Plan → Act → Critique → Re-plan loops for complex workflows

### Quick Start

```bash
# Install with LangGraph support
pip install sota-agent-framework[agent-frameworks]
```

### Usage

```python
from orchestration.langgraph.workflow import AgentWorkflowGraph
from orchestration.langgraph.nodes import PlannerNode, ExecutorNode, CriticNode

# Create workflow
workflow = AgentWorkflowGraph(agent_router=router)

# Add nodes
workflow.add_node("planner", PlannerNode())
workflow.add_node("executor", ExecutorNode())
workflow.add_node("critic", CriticNode())

# Define edges
workflow.add_edge("planner", "executor")
workflow.add_conditional_edge("executor", "critic", should_replan)

# Run workflow
result = await workflow.run(input_data)
```

### Configuration

```yaml
# config/sota_config.yaml
langgraph:
  enabled: true
  max_iterations: 5
  planning:
    model: "gpt-4"
    temperature: 0.7
  critique:
    enabled: true
    threshold: 0.8
```

### When to Use

- ✅ Multi-step workflows
- ✅ Autonomous decision-making
- ✅ Self-correcting agents
- ✅ Complex task decomposition

**Full Documentation**: See `docs/LANGGRAPH_INTEGRATION.md` (archived) for detailed guide

---

## 🏢 Databricks Integration

**Purpose**: Native integration with Databricks for production deployments

### Quick Start

```bash
# Install with Databricks support
pip install sota-agent-framework[databricks]
```

### Features

#### 1. **Unity Catalog Integration**

```python
from uc_registry import PromptRegistry

# Store prompts in Unity Catalog
registry = PromptRegistry()
registry.register_prompt(
    name="fraud_detector_v2",
    content=prompt_text,
    metadata={"version": "2.0"}
)

# Retrieve later
prompt = registry.get_prompt("fraud_detector_v2")
```

#### 2. **Telemetry → Delta Lake**

```python
from telemetry import AgentTracer

# Traces automatically exported to Delta Lake
tracer = AgentTracer()

with tracer.trace_agent_execution():
    result = agent.execute(input_data)

# Query traces in Delta Lake
spark.read.table("main.sota_agents.traces")
```

#### 3. **Databricks-Native Visualization**

```python
from visualization import DatabricksVisualizer

# Works in Databricks notebooks
viz = DatabricksVisualizer()

# Execution graph (Mermaid)
viz.show_execution_graph(trace)

# Timeline (Plotly)
viz.show_timeline(trace)

# Log to MLflow
viz.log_to_mlflow(trace)
```

#### 4. **Infrastructure as Code (Terraform)**

```bash
cd infra/databricks
terraform init
terraform plan
terraform apply
```

**Provisions:**
- Unity Catalog (catalogs, schemas, volumes)
- Model Serving endpoints
- Compute clusters
- Databricks Jobs

### Configuration

```yaml
# config/sota_config.yaml
databricks:
  workspace_url: ${DATABRICKS_HOST}
  token: ${DATABRICKS_TOKEN}
  
  unity_catalog:
    catalog: "main"
    schema: "sota_agents"
    volume: "prompts"
  
  mlflow:
    experiment_name: "sota_agents"
    tracking_uri: "databricks"
  
  model_serving:
    endpoint_name: "agent-llm"
    workload_size: "Small"
```

### Databricks Notebook Example

```python
# Works seamlessly in Databricks notebooks
from sota_agent import AgentRouter
from visualization import DatabricksVisualizer

# Load agents
router = AgentRouter.from_yaml("config/agents.yaml")

# Execute
result = await router.route("fraud_detector", transaction_data)

# Visualize (renders natively in notebook)
viz = DatabricksVisualizer()
viz.show_execution_graph(result.trace)

# Data automatically in Delta Lake
display(spark.read.table("main.sota_agents.agent_executions"))
```

### Environment Detection

Framework auto-detects Databricks:

```python
import os

if "DATABRICKS_RUNTIME_VERSION" in os.environ:
    # Automatically uses Databricks-specific features
    # - Unity Catalog for storage
    # - MLflow for tracking
    # - displayHTML() for viz
    pass
```

**Full Documentation**: See `docs/archive/DATABRICKS_NATIVE_CHECKLIST.md` for deployment checklist

---

## 📦 Installation Matrix

| Integration | Install Command | Optional Features |
|-------------|----------------|-------------------|
| **MCP** | `pip install sota-agent-framework[mcp]` | Tool calling |
| **LangGraph** | `pip install sota-agent-framework[agent-frameworks]` | Orchestration |
| **Databricks** | `pip install sota-agent-framework[databricks]` | UC, MLflow, Viz |
| **All** | `pip install sota-agent-framework[all]` | Everything |

---

## 🎯 When to Use Each

| Integration | Use Case |
|-------------|----------|
| **MCP** | Need external tool APIs (BIN lookup, sanctions, etc.) |
| **LangGraph** | Complex multi-step workflows, autonomous agents |
| **Databricks** | Production deployment, data platform integration |

---

## 📚 Additional Resources

- **MCP Servers**: See `mcp-servers/` directory for examples
- **LangGraph Examples**: See `examples/langgraph_planning_workflow.py`
- **Terraform**: See `infra/databricks/main.tf`
- **Detailed Docs**: See `docs/archive/` for comprehensive guides

---

**All integrations are optional - use only what you need!** 🎯

