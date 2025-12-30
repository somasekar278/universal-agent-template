# SOTA Agent - Universal Agent Workflow Template

**A generic, production-ready template for integrating AI agents into any application or data pipeline.**

🎯 **This is a TEMPLATE** - Use it to build agent workflows for any domain!

Originally designed for fraud detection, this architecture template applies to **any domain** requiring AI agent integration:
- 🔒 Fraud Detection & Risk Analysis
- 💬 Customer Support & Chatbots
- 📝 Content Moderation & Policy Enforcement
- 🏥 Healthcare & Diagnosis Support
- 🔍 Data Quality & Anomaly Detection
- 📊 Analytics & Report Generation
- 🤖 **Any Agent-Powered Workflow**

## 🚀 Quick Start

### One-Time Setup (30 seconds)

```bash
# Run setup script (Mac/Linux)
./setup.sh

# Or on Windows
setup.bat

# Or manually
pip install -r requirements.txt && pip install -e .
```

### Generate Projects (Anytime)

```bash
# Generate a complete project for your domain
python template_generator.py --domain "your_domain" --output ./your-project

cd your-project
python examples/example_usage.py  # Works immediately! ✅
```

### Path 2: Integrate Into Existing Code (3 lines)

```python
from agents import AgentRouter

router = AgentRouter.from_yaml("config/agents.yaml")  # 1. Load
result = await router.route("your_agent", input_data)  # 2. Execute
# That's it! 🎉
```

**📖 See [Getting Started Guide](GETTING_STARTED.md) for detailed 5-minute guide**

## Why Use This Template?

✨ **Universal Design** - Works for any domain, not just fraud detection  
🔌 **Plug-and-Play** - 3 lines to integrate into existing pipelines  
⚙️ **Configuration-Driven** - Enable/disable agents via YAML, zero code changes  
🎯 **SLA-Aware** - Control inline vs async execution based on your requirements  
🏗️ **Production-Ready** - Battle-tested patterns, not toy examples  
📦 **Complete Stack** - Includes telemetry, evaluation, optimization, deployment  
🚀 **Template Generator** - Scaffold new projects in seconds  

## Architecture Overview

This project implements a **domain-agnostic, plug-and-play agent framework** that integrates into existing data pipelines with minimal code changes. The architecture leverages:

- **Ephemeral Agents**: Task-specific narrative agents that spin up on-demand
- **Hot LLM Pools**: Always-on GPU endpoints via Databricks Model Serving
- **Prompt Optimization**: DSPy for task prompts, TextGrad for system prompts
- **Memory & Context**: Lakebase for conversation history and embeddings
- **MCP Tool Calling**: Standardized tool interfaces via Model Context Protocol
- **Observability**: OTEL → Zerobus → Delta Lake telemetry pipeline
- **Evaluation**: MLflow custom scorers and continuous feedback loops

## Key Features

🔌 **Plug-and-Play Integration** - Add to existing pipelines with 3 lines of code  
⚙️ **Configuration-Driven** - Enable/disable agents via YAML, no code changes  
🎯 **SLA-Aware Execution** - Control inline vs offline based on requirements  
🔒 **Type-Safe** - Pydantic schemas validate all data at runtime  
🌐 **ASGI Support** - FastAPI endpoints, SSE streaming, async HTTP  
🔄 **Agent-to-Agent (A2A)** - Event-driven agent communication via NATS/Redis (optional)  
✨ **Domain-Agnostic** - Works for fraud, risk, support, compliance, or any use case  
📈 **Prompt Optimization** - DSPy for task prompts, TextGrad for system prompts  
📊 **Comprehensive Telemetry** - All events streamed to Delta Lake via Zerobus  
🧠 **Memory Management** - Lakebase for vector embeddings and conversation history  
🔧 **MCP Tool Integration** - Standardized external tool calling  
📉 **MLflow Tracking** - Experiment tracking, evaluation, and model registry  
🏛️ **Unity Catalog** - Centralized prompt and model versioning  
🏢 **Multi-Tenant Ready** - Schema adapters handle any customer format  

## Project Structure

```
.
├── agents/                     # 🤖 Agent framework (CORE)
│   ├── base.py                #    - Base agent interfaces
│   ├── config.py              #    - Configuration loader
│   ├── registry.py            #    - Agent registry + router
│   └── execution/             #    - Pluggable execution backends
├── shared/                    # 📦 Shared libraries
│   ├── schemas/               #    - Pydantic data models (type-safe)
│   └── adapters/              #    - Schema adaptation framework
├── config/                    # ⚙️  Configuration (plug-and-play)
│   ├── agents/                #    - Agent configurations (YAML)
│   └── adapters/              #    - Customer schema adapters
├── services/                  # 🚀 Deployable services
├── optimization/              # 🎓 Prompt optimization (DSPy/TextGrad)
├── memory/                    # 🧠 Lakebase integration
├── orchestration/             # 🔄 Databricks Workflows + LangGraph
├── mcp-servers/               # 🔧 Model Context Protocol tools
├── evaluation/                # 📊 MLflow scorers and metrics
├── telemetry/                 # 📈 OTEL → Zerobus → Delta
├── uc-registry/               # 🗃️  Unity Catalog integration
├── data/                      # 📊 Synthetic testbed
├── infrastructure/            # 🏗️  Deployment configs (DABS)
├── experiments/               # 🔬 Notebooks + MLflow tracking
├── tests/                     # 🧪 Unit, integration, load tests
└── docs/                      # 📖 Documentation
```

**See [Project Structure](docs/PROJECT_STRUCTURE.md) for detailed breakdown with key concepts.**

## Data Schemas

All data structures are defined using Pydantic models in `shared/schemas/`:

- **transactions.py** - Transaction records and payment data
- **fraud_signals.py** - Velocity, amount, location, device signals
- **contexts.py** - Merchant and customer profiles
- **agent_io.py** - Agent inputs, outputs, tool calls (MCP-ready)
- **evaluation.py** - Evaluation records and scorer metrics
- **telemetry.py** - OTEL traces for Zerobus ingestion

See `shared/schemas/README.md` for detailed documentation.

## Quick Start (Plug-and-Play)

Add agents to your existing pipeline in 3 lines:

```python
from agents import AgentRouter
from shared.schemas import AgentInput

# 1. Load agents from config (one line!)
router = AgentRouter.from_yaml("config/agents.yaml")

# 2. Convert your data to AgentInput (Pydantic validates!)
agent_input = AgentInput(
    request_id=record.id,
    data=YourDomainData(**record.dict()),  # Your domain-specific data
    # ... your contexts
)

# 3. Route to agent (inline or offline based on config!)
result = await router.route("your_agent", agent_input)

# That's it! Agent runs according to your config.
# No code changes to enable/disable or switch execution modes.
```

**Configuration controls everything:**

```yaml
# config/agents.yaml
agents:
  your_agent:
    class: "your_package.YourAgent"
    execution_mode: "offline"  # or "inline" if SLA allows
    enabled: true              # Change to false to disable
    timeout: 30
```

**Works for any domain:** Fraud detection, risk analysis, customer support, compliance, content moderation, etc.

See [Configuration System](docs/CONFIGURATION_SYSTEM.md) for details.

---

## Getting Started

### Prerequisites

- Python 3.9+
- Databricks workspace with:
  - Model Serving endpoint
  - Unity Catalog
  - Lakebase access
- Zerobus server endpoint (for telemetry)

### Installation

```bash
# Clone the repository
git clone <repo-url>
cd "SOTA Agent"

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Or install in development mode
pip install -e ".[dev]"
```

### Configuration

```bash
# Copy example config
cp .env.example .env

# Edit .env with your Databricks credentials
# - DATABRICKS_HOST
# - DATABRICKS_TOKEN
# - MODEL_SERVING_ENDPOINT
# - UNITY_CATALOG_NAME
# - ZEROBUS_ENDPOINT
```

## Databricks Stack

| Component | Technology |
|-----------|-----------|
| LLM Inference | Databricks Model Serving |
| Orchestration | LangGraph + Databricks Workflows |
| Tracing & Evaluation | Databricks MLflow |
| Memory/Vector Store | Lakebase |
| Telemetry Sink | Zerobus → Delta Lake |
| Prompt Registry | Unity Catalog |
| Dashboards | Databricks SQL |
| Compute | Databricks Clusters / Serverless |

## Development

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test suite
pytest tests/unit/
pytest tests/integration/
```

### Code Quality

```bash
# Format code
black .

# Lint
ruff check .

# Type check
mypy .
```

## Architecture Flows

### Realtime Path (Low-latency)
Transaction → Event Collector → Ephemeral Narrative Agent → MCP Tool Calls → LLM Pool → Risk Narrative → Dashboard/Alerts

### Async Path (Optimization)
MLflow Scorers → Evaluate High-Risk Txns → Log Metrics → DSPy/TextGrad Optimization → Update Prompts in UC → Deploy to Agents

## MCP Integration

All tool calls use Model Context Protocol for standardization:

```python
# Tool call schema (MCP-ready)
tool_call = ToolCall(
    tool_id="call_123",
    tool_name="merchant_context",
    tool_server="uc-query-server",
    arguments={"merchant_id": "mch_001"}
)

# Tool result
tool_result = ToolResult(
    tool_call_id="call_123",
    success=True,
    result=merchant_data,
    latency_ms=45.2
)
```

See `mcp-servers/` for tool implementations.

## Telemetry

All events flow through OTEL → Zerobus → Delta Lake:

- Agent start/complete/error
- MCP tool calls
- LLM requests/responses
- Stream chunks
- Evaluation results

Query telemetry in Unity Catalog:

```sql
SELECT * FROM main.telemetry.agent_traces
WHERE transaction_id = 'txn_123'
ORDER BY timestamp DESC;
```

## Prompt Optimization

### DSPy (Task Prompts)
```python
# Optimize reasoning pipeline
from optimization.dspy import MIPROOptimizer

optimizer = MIPROOptimizer(training_data)
optimized_prompt = optimizer.optimize(baseline_prompt)
```

### TextGrad (System Prompts)
```python
# Optimize system prompt with guardrails
from optimization.textgrad import SystemPromptOptimizer

optimizer = SystemPromptOptimizer(feedback_data)
optimized_system = optimizer.optimize(system_prompt)
```

## Synthetic Data

Generate idempotent test data:

```bash
# Generate synthetic transactions
python -m data.synthetic.generate --seed 42 --count 5000

# Output: data/synthetic/raw/transactions.parquet
```

## Contributing

1. Create a feature branch
2. Make changes with tests
3. Run linters and tests
4. Submit pull request

## License

MIT

## Documentation

### 🎯 Start Here
- **[Getting Started](GETTING_STARTED.md)** ⭐ - 5-minute quick start guide
- **[Template Guide](docs/TEMPLATE_GUIDE.md)** ⭐ - Comprehensive guide for any domain
- **[Cross-Domain Examples](docs/CROSS_DOMAIN_EXAMPLES.md)** ⭐ - 8 real-world examples
- **[Documentation Index](docs/README.md)** - Complete documentation map

### 📚 Core Documentation
- **[Project Structure](docs/PROJECT_STRUCTURE.md)** - Code organization and key concepts
- **[Configuration System](docs/CONFIGURATION_SYSTEM.md)** - YAML-based configuration
- **[Schema Documentation](docs/schemas/)** - Data schemas and adaptation
- **[Use Cases](docs/USE_CASES.md)** - Advanced usage patterns

### 🛠️ Tools
- **Template Generator** - `python template_generator.py --help`
- **Example Integrations** - `examples/plug_and_play_integration.py`

## Contact

For questions, see `docs/` or contact the team.

