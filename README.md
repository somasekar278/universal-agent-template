# Databricks Agent Toolkit

[![PyPI version](https://badge.fury.io/py/databricks-agent-toolkit.svg)](https://pypi.org/project/databricks-agent-toolkit/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

**Build production agents on Databricks in minutes, not days.**

Generate production-ready agent scaffolds that follow official Databricks patterns and work with any of the 6 official UI templates.

```bash
pip install databricks-agent-toolkit

# Generate a chatbot (use the short alias!)
dbat generate chatbot my-bot
cd my-bot
python start_server.py

# 🎉 Done! Agent running at http://localhost:8000
```

---

## Why This Toolkit?

**Philosophy: "On Top Of, Not Instead Of"**

We don't create custom frameworks. We generate **production-ready agent backends** that follow:
- ✅ **OpenAI API standard** (industry-wide compatibility)
- ✅ **Official Databricks patterns** (FastAPI + OpenAPI)
- ✅ **MLflow best practices** (auto-tracing, experiments)
- ✅ **Databricks integrations** (Model Serving, Lakebase, Unity Catalog)

**Your agents work with:**
- All 6 official [Databricks UI templates](https://github.com/databricks/app-templates)
- Any OpenAI-compatible UI framework
- Custom frontends (React, Streamlit, Gradio, etc.)

---

## Quick Start

### 1. Install

```bash
pip install databricks-agent-toolkit
```

### 2. Generate an Agent

```bash
# Use the short alias (much easier to type!)
dbat generate chatbot my-bot

# Or the full command:
# databricks-agent-toolkit generate chatbot my-bot
```

**Available aliases:**
- `dbat` → Databricks Agent Toolkit ✨ **(recommended)**
- `dat` → Even shorter!
- `databricks-agent-toolkit` → Full command

### 3. What You Get

```
my-bot/
├── agent.py              # Your agent logic (OpenAI API compatible)
├── start_server.py       # FastAPI server with auto-docs
├── chatbot.py           # CLI interface for testing
├── config.yaml          # Easy configuration
├── requirements.txt     # All dependencies
├── databricks.yml       # Deploy to Databricks Apps
├── app.yaml            # App configuration
└── README.md           # Setup instructions
```

### 4. Run Locally

```bash
cd my-bot
pip install -r requirements.txt

# Start the server
python start_server.py
# 🚀 Backend: http://localhost:8000
# 📚 API Docs: http://localhost:8000/docs
# 💚 Health: http://localhost:8000/health

# Or test in CLI
python chatbot.py
```

### 5. Deploy to Databricks

```bash
# One command deployment
databricks bundle deploy

# Your app is live at: https://<workspace>/apps/my-bot
```

---

## What's Included

### **L1: Chatbot (Simple Conversational AI)**

```bash
dbat generate chatbot my-bot
```

**Features:**
- 💬 OpenAI API compatible via MLflow AgentServer (`/invocations`)
- 🔄 Streaming with Server-Sent Events (SSE)
- 📊 MLflow auto-tracing (requires mlflow>=3.6.0)
- 🎛️ Configuration-driven (no code changes to switch models)
- 🚀 One-command deploy to Databricks Apps
- 📝 Built-in web UI (or use official templates)
- 📖 Auto-generated OpenAPI docs

**Perfect for:**
- Quick prototypes and demos
- Simple Q&A bots
- Customer support assistants
- Internal tools

---

### **Coming Soon:**

- **L2: RAG Chatbot** - Add Vector Search (Databricks or Lakebase pgvector) for knowledge base Q&A
- **L3: Agent with Memory & Tools** - LangGraph-based agents with persistent memory and tool calling
- **L4: Multi-Agent System** - Orchestrated agent workflows with specialized agents

---

## Configuration

Edit `config.yaml` to customize your agent:

```yaml
# config.yaml
model:
  endpoint: databricks-meta-llama-3-1-70b-instruct  # Any Databricks Model Serving endpoint
  temperature: 0.7
  max_tokens: 500
  streaming: true
  token_delay_ms: 50  # Streaming speed (lower = faster)
  system_prompt: "You are a helpful AI assistant."

mlflow:
  experiment: /Shared/my-bot
  auto_trace: true  # Automatic tracing of all LLM calls
  embedding_model: databricks-bge-large-en
```

**No code changes needed!** Just edit config and redeploy.

---

## Official UI Templates

Your agent backend is **100% compatible** with all official Databricks UI templates:

| **Framework** | **Best For** | **Streaming** | **L2 Memory** | **Template** |
|---------------|--------------|---------------|---------------|--------------|
| **Streamlit** | Quick prototypes, data apps | ✅ | ✅ | [e2e-chatbot-app](https://github.com/databricks/app-templates/tree/main/e2e-chatbot-app) |
| **Gradio** | ML demos, simple interfaces | ❌ | ❌ | [gradio-chatbot-app](https://github.com/databricks/app-templates/tree/main/gradio-chatbot-app) |
| **Plotly Dash** | Data dashboards with chat | ❌ | ❌ | [dash-chatbot-app](https://github.com/databricks/app-templates/tree/main/dash-chatbot-app) |
| **Shiny** | Statistical apps, R users | - | - | [shiny-chatbot-app](https://github.com/databricks/app-templates/tree/main/shiny-chatbot-app) |
| **React** | Production, enterprise | - | - | [e2e-chatbot-app](https://github.com/databricks/app-templates/tree/main/e2e-chatbot-app) |
| **Next.js** | Modern production, SSR | - | - | [e2e-chatbot-app-next](https://github.com/databricks/app-templates/tree/main/e2e-chatbot-app-next) |

**Integrated Frameworks (v0.3.0):**
- ✅ **Streamlit**: Full support (L1 + L2, streaming, memory)
- ✅ **Gradio**: L1 only (batch mode)
- ✅ **Dash**: L1 only (batch mode)

**Why compatible?**
We follow the **OpenAI API standard** via MLflow AgentServer (`/invocations` endpoint).

**Using official UIs:**
```bash
# 1. Generate our backend
dbat generate chatbot my-bot

# 2. Clone official UI
git clone https://github.com/databricks/app-templates.git
cp -r app-templates/streamlit-chatbot-app my-bot/frontend

# 3. Point UI to backend (http://localhost:8000)
# 4. Deploy together!
```

**✨ NEW in v0.3.0:** One-command UI integration!
```bash
# L1 Chatbot - Choose any framework
dat generate chatbot my-bot --ui streamlit   # ✅ Streaming support
dat generate chatbot my-bot --ui gradio      # Batch only
dat generate chatbot my-bot --ui dash        # Batch only
```

**Framework Support:**
- **L1 (Chatbot)**: Streamlit, Gradio, Dash - all supported
- **L2+ (Coming Soon)**: RAG and Agent features

See [UI Integration Guide](docs/UI_FRAMEWORK_INTEGRATION.md) for details.

---

## API Documentation

Your agent comes with **auto-generated OpenAPI documentation**:

- **Swagger UI**: http://localhost:8000/docs
- **OpenAPI JSON**: http://localhost:8000/openapi.json
- **Health Check**: http://localhost:8000/health

### Example API Call

```python
import requests

response = requests.post(
    "http://localhost:8000/invocations",
    json={
        "input": [{"role": "user", "content": "Hello!"}],
        "stream": False
    }
)
# ResponsesAgent format: data.output[0].content[0].text
print(response.json()["output"][0]["content"][0]["text"])
```

### Streaming Example

```python
import requests
import json

response = requests.post(
    "http://localhost:8000/invocations",
    json={
        "input": [{"role": "user", "content": "Tell me a story"}],
        "stream": True
    },
    stream=True
)

for line in response.iter_lines():
    if line.startswith(b"data: "):
        data = line[6:].decode('utf-8')
        if data != "[DONE]":
            chunk = json.loads(data)
            # ResponsesAgent streaming format: chunk.content
            print(chunk.get("content", ""), end="", flush=True)
```

---

## Features

### **Production-Ready**
- ✅ FastAPI for performance and reliability
- ✅ OpenAPI schema for API documentation
- ✅ Health endpoints for monitoring
- ✅ Error handling and logging
- ✅ CORS configured for web UIs

### **Databricks-Native**
- ✅ Auto-authentication with Databricks
- ✅ MLflow auto-tracing (track all LLM calls)
- ✅ Unity Catalog for data governance
- ✅ Model Serving integration
- ✅ Lakebase (PostgreSQL) for memory
- ✅ Vector Search for RAG

### **Developer Experience**
- ✅ Configuration-driven (YAML, no code changes)
- ✅ CLI for quick testing
- ✅ Local development with hot-reload
- ✅ One-command deployment
- ✅ Comprehensive documentation

### **Standards-Based**
- ✅ OpenAI API format (universal compatibility)
- ✅ Server-Sent Events (SSE) for streaming
- ✅ OpenAPI 3.0 schema
- ✅ REST best practices

---

## Architecture

```
Your Application
┌─────────────────────────────────────────────────┐
│                                                 │
│  ┌─────────────┐        ┌──────────────────┐  │
│  │  Your UI    │◄──────►│  Agent Backend   │  │
│  │             │        │  (our toolkit)   │  │
│  │ - Streamlit │        │                  │  │
│  │ - React     │        │ - agent.py       │  │
│  │ - Gradio    │        │ - FastAPI server │  │
│  │ - Custom    │        │ - OpenAI API     │  │
│  └─────────────┘        └────────┬─────────┘  │
│                                  │             │
└──────────────────────────────────┼─────────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    │   Databricks Platform       │
                    │                             │
                    │ - Model Serving (LLMs)      │
                    │ - MLflow (tracing)          │
                    │ - Lakebase (memory)         │
                    │ - Vector Search (RAG)       │
                    │ - Unity Catalog (data)      │
                    └─────────────────────────────┘
```

**We provide the agent backend. You choose the UI.**

---

## Examples

### **Basic Chatbot**
```bash
dbat generate chatbot hello-bot
cd hello-bot
python start_server.py
```

### **Assistant with Memory**
```bash
dbat generate assistant support-bot
cd support-bot
# Configure Lakebase in databricks.yml
databricks bundle deploy
```

### **RAG-Powered Assistant**
```bash
dbat generate assistant doc-bot --enable-rag
cd doc-bot

# Edit config.yaml:
# rag:
#   enabled: true
#   source: /Volumes/main/default/docs
#   backend: pgvector

databricks bundle deploy
```

### **Custom Model**
```bash
dbat generate chatbot custom-bot
cd custom-bot

# Edit config.yaml:
# model:
#   endpoint: my-custom-endpoint
#   temperature: 0.9
#   max_tokens: 1000

python start_server.py
```

---

## Requirements

- **Python**: 3.9+
- **Databricks**: Workspace access (for deployment)
- **Model Serving**: At least one LLM endpoint
- **Optional**:
  - Lakebase (for L2 memory)
  - Vector Search (for L2 RAG)
  - Unity Catalog Volumes (for RAG documents)

---

## Documentation

- **[UI Integration Guide](docs/UI_FRAMEWORK_INTEGRATION.md)** - Using official Databricks UI templates
- **[App Templates Compliance](docs/APP_TEMPLATES_COMPLIANCE.md)** - Compatibility verification
- **[Upstream Sync Strategy](docs/UPSTREAM_SYNC_STRATEGY.md)** - How we stay compatible

---

## FAQ

**Q: Do I need to use Databricks?**
A: For deployment, yes. For local development, you just need access to Databricks Model Serving endpoints.

**Q: Can I use my own UI?**
A: Absolutely! Your agent backend follows the OpenAI API standard, so any OpenAI-compatible UI works.

**Q: What about LangChain/LangGraph?**
A: Coming in v0.3.0+. For now, our agents use a simple, lightweight pattern. You can integrate LangChain yourself if needed.

**Q: Is this production-ready?**
A: Yes! L1 (chatbot) is production-ready in v0.2.0. L2 (assistant) is in active testing.

**Q: How do I switch models?**
A: Just edit `config.yaml` → `model.endpoint`. No code changes needed!

**Q: Can I customize the agent logic?**
A: Yes! Edit `agent.py` - it's your code, do whatever you want.

**Q: How do I add custom tools/functions?**
A: Modify the `predict()` method in `agent.py` to call your functions before/after the LLM.

---

## Roadmap

### **v0.3.0** (Coming Soon)
- [ ] `--ui=streamlit|gradio|react` flag for one-command UI integration
- [ ] L3: API agents with custom tools
- [ ] L4: Multi-step workflows
- [ ] Template upgrade commands

### **v0.4.0+** (Future)
- [ ] L5: Multi-agent systems
- [ ] LangGraph integration
- [ ] Custom tool marketplace
- [ ] Performance benchmarking

---

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Areas we'd love help with:**
- Additional UI framework integrations
- More example agents
- Documentation improvements
- Bug reports and feature requests

---

## Philosophy

**"On Top Of, Not Instead Of"**

We don't reinvent wheels. We integrate official Databricks patterns:
- ✅ Official app-templates for UI
- ✅ OpenAI API standard
- ✅ MLflow for tracing
- ✅ FastAPI for servers
- ✅ Databricks services for infrastructure

**We add:**
- 🛠️ Scaffold generation (save time)
- ⚙️ Configuration management (no code changes)
- 📦 Pre-wired integrations (batteries included)
- 📚 Best practices (production-ready)

---

## License

Apache 2.0

---

## Support

- **GitHub Issues**: https://github.com/databricks/agent-toolkit/issues
- **Documentation**: See `docs/` folder
- **Examples**: See `examples/` folder

---

**Built with ❤️ for the Databricks community**

Start building agents today:
```bash
pip install databricks-agent-toolkit
dbat generate chatbot my-bot
```
