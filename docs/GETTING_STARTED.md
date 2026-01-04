# Getting Started Guide

Quick start guide for building agents with Databricks Agent Toolkit.

---

## Installation

```bash
# Basic installation
pip install databricks-agent-toolkit

# With Databricks integrations
pip install databricks-agent-toolkit[databricks]
```

---

## Choose Your Agent Type

### 🤔 Which Scaffold Should I Use?

| Use Case | Scaffold | Complexity | Time to Build |
|----------|----------|------------|---------------|
| **Simple chatbot** | `chatbot` | ⭐ | 15 min |
| **Context-aware assistant with memory** | `assistant` | ⭐⭐ | 30 min |
| **Production API with auth & monitoring** | `api` | ⭐⭐⭐ | 45 min |
| **Multi-step workflow with orchestration** | `workflow` | ⭐⭐⭐⭐ | 60 min |
| **Multi-agent system with A2A** | `system` | ⭐⭐⭐⭐⭐ | 90 min |

### Decision Tree

**Start here:** What's your main requirement?

1. **Just need basic LLM chat?** → `chatbot`
   - Single-turn or multi-turn conversations
   - No memory required
   - Quick proof-of-concept

2. **Need to remember past conversations?** → `assistant`
   - Uses Lakebase (PostgreSQL) for memory
   - Session management
   - Personalized responses

3. **Need to expose as API for other apps?** → `api`
   - FastAPI wrapper
   - Authentication & rate limiting
   - Health checks & monitoring
   - Production-ready

4. **Need complex multi-step workflows?** → `workflow`
   - LangGraph orchestration
   - Multiple tools/agents
   - Error handling & retries
   - State management

5. **Building autonomous multi-agent system?** → `system`
   - Agent-to-agent communication
   - Supervisory agent
   - Self-improvement
   - MCP integration

---

## Option 1: Generate a Scaffold (Recommended)

### Chatbot (Currently Available in v0.1.1)

```bash
# Generate chatbot
databricks-agent-toolkit generate chatbot my-chatbot

cd my-chatbot
pip install -r requirements.txt

# Run locally (CLI)
python chatbot.py

# Or run as web app (Databricks Apps ready)
python app.py  # Visit http://localhost:8000
```

### Other Scaffolds (Coming Soon)

```bash
# Assistant with memory (L2)
databricks-agent-toolkit generate assistant my-assistant

# Production API (L3)
databricks-agent-toolkit generate api my-api

# Complex workflow (L4)
databricks-agent-toolkit generate workflow my-workflow

# Multi-agent system (L5)
databricks-agent-toolkit generate system my-system
```

---

## Option 2: Use Integrations Directly

### Basic LLM Chat

```python
from databricks_agent_toolkit.integrations import DatabricksLLM

# Initialize (auto-auth via Databricks SDK)
llm = DatabricksLLM(endpoint="databricks-claude-sonnet-4-5")

# Chat (batch)
response = await llm.chat([
    {"role": "user", "content": "What is RAG?"}
])
print(response["content"])

# Chat (streaming)
async for chunk in llm.stream([
    {"role": "user", "content": "Explain quantum computing"}
]):
    print(chunk["content"], end="")
```

### Add Memory (Lakebase - PostgreSQL)

```python
from databricks_agent_toolkit.integrations import Lakebase

# Initialize
lakebase = Lakebase()

# Create conversations table (one-time)
lakebase.create_conversations_table()

# Store conversation
lakebase.store_message(
    session_id="user_123",
    role="user",
    content="Hello!"
)

# Get conversation history
history = lakebase.get_conversation_history(session_id="user_123")
```

### Add Vector Search (Delta Lake)

```python
from databricks_agent_toolkit.integrations import DatabricksVectorSearch

# Initialize
vector_search = DatabricksVectorSearch()

# Create index (one-time)
vector_search.create_index(
    name="main.docs.knowledge_base",
    source_table="main.docs.raw_documents",
    embedding_column="content",
    primary_key="id"
)

# Search
results = vector_search.search(
    index_name="main.docs.knowledge_base",
    query="How do I deploy to Databricks Apps?",
    num_results=5
)

for result in results:
    print(result["content"])
```

### Use with LangGraph

```python
from databricks_agent_toolkit.integrations import DatabricksLLM
from langgraph.graph import StateGraph, END
from typing import TypedDict

# Initialize LLM
llm = DatabricksLLM(endpoint="databricks-claude-sonnet-4-5")

# Define state
class State(TypedDict):
    messages: list
    result: str

# Define agent node
async def chat_node(state: State) -> State:
    response = await llm.chat(state["messages"])
    return {
        "messages": state["messages"] + [{"role": "assistant", "content": response["content"]}],
        "result": response["content"]
    }

# Build workflow
workflow = StateGraph(State)
workflow.add_node("chat", chat_node)
workflow.set_entry_point("chat")
workflow.add_edge("chat", END)

app = workflow.compile()

# Run
result = await app.ainvoke({
    "messages": [{"role": "user", "content": "Hello!"}]
})
print(result["result"])
```

---

## Deploy to Databricks Apps

### From Generated Scaffold

```bash
cd my-chatbot

# Set credentials
export DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
export DATABRICKS_CLIENT_ID="your-sp-client-id"
export DATABRICKS_CLIENT_SECRET="your-sp-client-secret"

# Deploy
databricks apps deploy my-chatbot \
    --source-code-path . \
    --app-config-file databricks-app.yml
```

### Custom Deployment

See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for detailed instructions.

---

## Authentication

### Local Development

The toolkit uses Databricks SDK for authentication. Set one of:

**Option 1: Databricks CLI**
```bash
databricks configure
```

**Option 2: Environment Variables**
```bash
export DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
export DATABRICKS_TOKEN="your-token"
```

**Option 3: .databrickscfg**
```ini
[DEFAULT]
host = https://your-workspace.cloud.databricks.com
token = your-token
```

### Databricks Apps (Production)

Set Service Principal credentials:
```bash
export DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
export DATABRICKS_CLIENT_ID="your-sp-client-id"
export DATABRICKS_CLIENT_SECRET="your-sp-client-secret"
```

The toolkit automatically uses OAuth M2M authentication.

---

## Next Steps

- **Explore Examples:** [config/examples/](../config/examples/)
- **Read Architecture:** [ARCHITECTURE.md](./ARCHITECTURE.md)
- **Deploy to Production:** [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)
- **Check PyPI:** https://pypi.org/project/databricks-agent-toolkit/

---

## Getting Help

- **GitHub:** https://github.com/databricks/databricks-agent-toolkit
- **Issues:** https://github.com/databricks/databricks-agent-toolkit/issues
- **PyPI:** https://pypi.org/project/databricks-agent-toolkit/
