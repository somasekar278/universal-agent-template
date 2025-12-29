# Project Structure & Key Concepts

## Overview

This is a **domain-agnostic, plug-and-play agent framework** that integrates AI agents into existing data pipelines with minimal code changes. Built on **5 core architectural principles** and designed to work seamlessly with Databricks-native offerings.

**Originally designed for fraud detection, this pattern applies to ANY domain:** risk analysis, customer support, compliance monitoring, clinical decision support, content moderation, etc.

---

## 📖 Terminology & Glossary

Before diving in, let's clarify key terms used throughout this project:

### Execution Modes

| Term | Aliases | Meaning | Use Case |
|------|---------|---------|----------|
| **Inline** | `in_process`, synchronous | Agent runs in same process, waits for result | Fast agents, tight SLA (<50ms) |
| **Offline** | `async`, background, out-of-path | Agent runs asynchronously, doesn't block | Slow agents, relaxed SLA |
| **Ephemeral** | `ray_task`, stateless | Agent instance created, runs once, destroyed | True isolation, distributed |
| **Hot Pool** | `process_pool`, warm | Pre-initialized agents, reused across requests | Balance of speed and isolation |

### Agent Types

| Type | Purpose | Latency | Execution |
|------|---------|---------|-----------|
| **Critical Path** | Fast fraud decision | <50ms | Always inline |
| **Enrichment** | Narrative generation, context | 200ms+ | Inline or offline (customer choice) |

### Architecture Layers

| Layer | Description | Examples (Any Domain) |
|-------|-------------|----------|
| **Critical Path** | Fast ML scoring, required decision | Fraud scorer, health risk, ticket classifier |
| **Agentic Layer** | LLM-based enrichment, orchestration | Narrative generator, recommender, explainer |
| **Orchestration** | Customer's existing workflow | Databricks Workflows, streaming pipelines |

### Communication Patterns

| Pattern | Technology | Use Case |
|---------|-----------|----------|
| **ASGI** | FastAPI, WebSockets | HTTP endpoints, real-time streaming |
| **A2A (Agent-to-Agent)** | NATS/Redis | Agent communication, event-driven workflows |
| **Sync** | Direct function calls | Critical path, inline execution |

**Key Principle:** Agentic layer NEVER blocks critical path!

---

## 🎯 Core Architectural Principles

| # | Principle | Why | Implementation |
|---|-----------|-----|----------------|
| 1 | **Separation of Concerns** | Keep decision-critical logic separate from enrichment | `CriticalPathAgent` vs `EnrichmentAgent` |
| 2 | **Uniform Agent Interface** | All agents callable the same way | `async def process(request)` |
| 3 | **Pluggable Execution** | Switch execution mode without code changes | `AgentRunner` + backends |
| 4 | **Async-First** | Default to async, inline is opt-in | Primary interface is async |
| 5 | **Lightweight Metadata** | Config separate from execution | YAML config + registry |

---

## 🔄 Visual Architecture Flows

### 1. Critical Path vs Enrichment Flow (Generic Pattern)

```
┌─────────────────────────────────────────────────────────┐
│  Data Record Arrives (any domain)                       │
│  Examples: Transaction, Patient Record, Support Ticket  │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ▼
    ┌───────────────────────────────────────┐
    │  CRITICAL PATH (Always Inline)        │
    │  ┌─────────────────────────────────┐  │
    │  │ CriticalPathAgent               │  │
    │  │ - Fast ML scoring               │  │
    │  │ - <50ms SLA                     │  │
    │  │ - IN_PROCESS execution          │  │
    │  │ - Returns: decision/score/class │  │
    │  └─────────────────────────────────┘  │
    └───────────────┬───────────────────────┘
                    │
                    │ ✅ Decision Made! Processing can proceed
                    │
                    ├──────────────────────────────────────┐
                    │                                      │
                    ▼ (low priority)                      ▼ (high priority)
         Skip enrichment                    ┌──────────────────────────┐
         Continue pipeline                  │  ENRICHMENT (Modular)    │
                                           │  ┌────────────────────┐  │
                                           │  │ EnrichmentAgent    │  │
                                           │  │ - Explanation gen  │  │
                                           │  │ - 200ms+ allowed   │  │
                                           │  │ - Customer choice: │  │
                                           │  │   • Inline (wait)  │  │
                                           │  │   • Offline (async)│  │
                                           │  └────────────────────┘  │
                                           └────────┬─────────────────┘
                                                    │
                                                    ▼
                                           Output / Alerts / UI
```

**Key:** Critical path completes first, enrichment runs after (inline or offline based on customer SLA).

**Domain Examples:**
- **Fraud:** Decision → Narrative explanation
- **Healthcare:** Risk assessment → Treatment recommendations
- **Support:** Category → Draft response
- **Compliance:** AML score → SAR narrative

---

### 2. Agent Routing Flow

```
Customer's Pipeline
      │
      ▼
config/agents.yaml ──────┐
      │                  │
      ▼                  ▼
AgentRouter.from_yaml("config.yaml")
      │
      ├─ Loads: AgentRegistry
      │          ├─ Agent classes
      │          ├─ Execution modes
      │          └─ Timeouts, retries
      │
      ▼
router.route("narrative", request)
      │
      ├─ 1. Lookup agent metadata (registry)
      ├─ 2. Select execution backend (config)
      │      ├─ IN_PROCESS    (inline)
      │      ├─ PROCESS_POOL  (hot pool)
      │      └─ RAY_TASK      (ephemeral)
      │
      ├─ 3. Execute agent
      │      AgentRunner.execute(agent_class, request)
      │
      └─ 4. Return result
             AgentOutput (Pydantic validated)
```

**Key:** Config controls everything - no code changes to switch execution modes!

---

### 3. Data Flow (Customer Integration)

```
Customer's Schema          Our Framework              Customer's Pipeline
      │                          │                           │
      ▼                          │                           │
{ their_format }                 │                           │
      │                          │                           │
      ├─ Schema Adapter          │                           │
      │  (config/adapters/*.yaml)│                           │
      │                          │                           │
      ▼                          ▼                           │
AgentInput (Pydantic) ──────> Agent.process() ──────> AgentOutput
      ▲                          │                           │
      │                          │                           │
      │                          ▼                           │
      │                    Execution Backend                 │
      │                    (IN_PROCESS/RAY_TASK)            │
      │                          │                           │
      │                          ▼                           │
      └────────────────────── Result ─────────────────────> │
                                                              ▼
                                                    Continue pipeline
```

**Key:** Schema adapters handle any customer format → our format → back to customer.

---

### 4. Optimization Flow (DSPy + TextGrad)

```
Production Traffic
      │
      ├─────────────────────────────────────────────┐
      │                                             │
      ▼ (Critical Path)                            ▼ (Enrichment)
CriticalPathAgent                          EnrichmentAgent
      │                                             │
      ├─ Telemetry (Zerobus → Delta)              ├─ Telemetry
      │                                             │
      ▼                                             ▼
┌─────────────────────────────────────────────────────────┐
│  Evaluation (MLflow Scorers)                            │
│  - Score agent outputs                                  │
│  - Identify high-risk transactions                      │
│  - Log metrics to MLflow                                │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ├──────────────────┬──────────────────┐
                    │                  │                  │
                    ▼                  ▼                  ▼
            ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
            │    DSPy      │  │  TextGrad    │  │ Few-Shot     │
            │              │  │              │  │ Selection    │
            │ Optimize:    │  │ Optimize:    │  │              │
            │ - Task       │  │ - System     │  │ Select best  │
            │   prompts    │  │   prompts    │  │ examples     │
            │ - Pipelines  │  │ - Guardrails │  │ from high-   │
            │ - Few-shot   │  │ - Safety     │  │ risk cases   │
            │   examples   │  │              │  │              │
            └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
                   │                 │                  │
                   └─────────────────┼──────────────────┘
                                     │
                                     ▼
                        Unity Catalog (Prompt Registry)
                        - Version new prompts
                        - A/B test configs
                        - Deploy to production
                                     │
                                     ▼
                        Updated agents in production
```

**Key:** Continuous optimization loop improves agents over time.

---

### 5. ASGI + A2A Communication Flow

```
┌─────────────────────────────────────────────────────────────┐
│  ASGI Layer (HTTP/WebSocket)                                │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  FastAPI / Databricks Apps                            │  │
│  │  - Async request handling                             │  │
│  │  - WebSocket streaming                                │  │
│  │  - SSE for real-time updates                          │  │
│  └─────────────────┬─────────────────────────────────────┘  │
└────────────────────┼────────────────────────────────────────┘
                     │
                     ▼ (HTTP request)
         ┌───────────────────────────┐
         │  Agent Router             │
         │  (async-first framework)  │
         └──────────┬────────────────┘
                    │
                    ├─────────────────────────┐
                    │                         │
                    ▼ (inline)                ▼ (publish to A2A)
         ┌──────────────────┐      ┌──────────────────────────┐
         │ Critical Path    │      │  Message Bus (A2A)       │
         │ - Fast response  │      │  ┌────────────────────┐  │
         │ - Return to HTTP │      │  │ NATS / Redis       │  │
         └──────────────────┘      │  │ - Topics/channels  │  │
                                   │  │ - Pub/Sub          │  │
                                   │  │ - Agent-to-Agent   │  │
                                   │  └─────┬──────────────┘  │
                                   └────────┼─────────────────┘
                                            │
                                            ▼ (subscribe)
                                   ┌────────────────────┐
                                   │ Enrichment Agent   │
                                   │ - Async processing │
                                   │ - Can publish to   │
                                   │   other agents     │
                                   └─────┬──────────────┘
                                         │
                                         ▼ (publish result)
                                   ┌────────────────────┐
                                   │ Message Bus (A2A)  │
                                   │ topic: "enriched"  │
                                   └─────┬──────────────┘
                                         │
                                         ▼ (multiple consumers)
                                   ┌────────────────────┐
                                   │ - Dashboard        │
                                   │ - Alerts           │
                                   │ - Analytics        │
                                   │ - Other agents     │
                                   └────────────────────┘
```

**Key Features:**
- ✅ **ASGI** - Fast async HTTP/WebSocket endpoints
- ✅ **A2A** - Agent-to-agent communication via message bus
- ✅ **Hybrid** - Inline critical path + offline A2A enrichment
- ✅ **Event-Driven** - Agents can chain via pub/sub

---

## 📁 Project Structure (High-Level)

<details>
<summary><b>Click to expand full structure</b></summary>

```
SOTA Agent/
│
├── 🤖 agents/                   AGENT FRAMEWORK (CORE)
│   ├── base.py                  Base interfaces
│   ├── config.py                Configuration loader
│   ├── registry.py              Registry + router
│   └── execution/               Pluggable backends
│
├── 📦 shared/                   SHARED LIBRARIES
│   ├── schemas/                 Pydantic data models
│   └── adapters/                Schema adaptation
│
├── ⚙️  config/                   CONFIGURATION
│   ├── agents/                  Agent configs (YAML)
│   └── adapters/                Customer schemas
│
├── 🚀 services/                 DEPLOYABLE SERVICES
├── 🔄 orchestration/            DATABRICKS WORKFLOWS
├── 🎓 optimization/             DSPY + TEXTGRAD
├── 🧠 memory/                   LAKEBASE
├── 🔧 mcp-servers/              MODEL CONTEXT PROTOCOL
├── 📊 evaluation/               MLFLOW SCORERS
├── 📈 telemetry/                OTEL → ZEROBUS → DELTA
├── 🗃️  uc-registry/              UNITY CATALOG
├── 🏗️  infrastructure/           DEPLOYMENT (DABS)
├── 📊 data/                     SYNTHETIC TESTBED
├── 🔬 experiments/              NOTEBOOKS + MLFLOW
├── 🧪 tests/                    TESTING
├── 📚 examples/                 INTEGRATION EXAMPLES
└── 📖 docs/                     DOCUMENTATION
```

</details>

---

## 🔑 Key Concepts (Simplified)

### 1. Agent Framework (`agents/`)

<details>
<summary><b>What it does</b></summary>

Provides base classes and execution infrastructure for all agents.

**Three main components:**

1. **Base Classes** (`agents/base.py`)
   - `Agent` - Uniform interface all agents implement
   - `CriticalPathAgent` - For fast decisions (<50ms)
   - `EnrichmentAgent` - For slow enrichment (200ms+)

2. **Execution Backends** (`agents/execution/`)
   - `IN_PROCESS` - Same process (inline, fast)
   - `PROCESS_POOL` - Process pool (bin-packing, hot pool)
   - `RAY_TASK` - Ray tasks (ephemeral, distributed)

3. **Registry & Router** (`agents/registry.py`, `agents/config.py`)
   - Load agents from YAML config
   - Route requests to appropriate agents
   - Handle retries, timeouts, telemetry

**Key principle:** Same agent code runs in any execution mode!

</details>

---

### 2. Pydantic Schemas (`shared/schemas/`)

<details>
<summary><b>What it does</b></summary>

Type-safe contracts between all components.

**Core schemas:**
- `AgentInput` / `AgentOutput` - Uniform agent interface
- `Transaction`, `MerchantContext`, `CustomerContext` - Domain models
- `MCPToolResults` - External tool integration
- `TelemetryEvent`, `AgentTrace` - Observability

**Schema Adaptation** (`shared/adapters/`)
- Map customer schemas to our schemas via YAML config
- Zero code changes for new customers
- 2-hour onboarding (vs 2 days)

**Schema Versioning** (`shared/schemas/versioning/`)
- Evolve schemas safely over time
- Auto-migration between versions
- Breaking change detection

</details>

---

### 3. Configuration System (`config/`)

<details>
<summary><b>What it does</b></summary>

Everything is configurable - customers control behavior without code changes.

**Agent Configuration** (`config/agents/*.yaml`)
```yaml
agents:
  narrative:
    class: "agents.NarrativeAgent"
    execution_mode: "offline"  # or "inline"
    enabled: true
    timeout: 30
```

**Customer controls:**
- Which agents to enable/disable
- Inline vs offline execution
- Timeout values
- Custom configuration

**No code changes needed!**

</details>

---

### 4. Databricks Integration

<details>
<summary><b>What it does</b></summary>

Leverages Databricks-native offerings wherever possible.

| Component | Databricks Offering | Purpose |
|-----------|-------------------|---------|
| LLM Inference | Model Serving (FMAPI) | Hot pools, guardrails |
| Evaluation | MLflow | Scorers, tracing, tracking |
| Memory | Lakebase | Vector embeddings, <10ms |
| Telemetry | Zerobus → Delta | OTEL logs to Delta Lake |
| Prompts | Unity Catalog | Version control, registry |
| Orchestration | Workflows | Batch jobs, scheduling |

</details>

---

### 5. Optimization Frameworks

<details>
<summary><b>What it does</b></summary>

Two complementary approaches for prompt optimization:

**DSPy** (`optimization/dspy/`)
- **For:** Task prompts, reasoning pipelines, few-shot examples
- **Method:** Program synthesis, bootstrap sampling
- **Optimizers:** MIPRO, COPRO, BootstrapFewShot

**TextGrad** (`optimization/textgrad/`)
- **For:** System prompts, guardrails, safety constraints
- **Method:** Gradient-based optimization
- **Features:** Feedback-driven, constraint-aware

**Both feed optimized prompts back to Unity Catalog for deployment.**

</details>

---

### 6. ASGI Support (`services/api/`)

<details>
<summary><b>What it does</b></summary>

Full ASGI support for async HTTP and WebSocket endpoints.

**FastAPI Integration:**
```python
from fastapi import FastAPI, WebSocket
from agents import AgentRouter

app = FastAPI()  # ASGI application
router = AgentRouter.from_yaml("config/agents.yaml")

@app.post("/fraud/score")
async def score(request: TransactionRequest):
    # Agent framework is async-first!
    result = await router.route("risk_scorer", agent_input)
    return result

@app.websocket("/fraud/stream")
async def stream(websocket: WebSocket):
    # Real-time streaming
    async for transaction in transaction_stream:
        result = await router.route("narrative", transaction)
        await websocket.send_json(result.dict())
```

**Databricks Apps** (ASGI-native)
- Deploy FastAPI apps directly
- Auto-scaling, load balancing
- Native ASGI support

</details>

---

### 7. Agent-to-Agent (A2A) Communication (`services/message-bus/`)

<details>
<summary><b>What it does</b></summary>

Event-driven agent communication via message bus.

**Supported Message Buses:**
- **NATS JetStream** - High throughput, distributed
- **Redis Streams** - Simpler, good for moderate load

**A2A Pattern:**
```python
# Agent A publishes
async def critical_path_agent(transaction):
    risk_score = score(transaction)
    
    if risk_score > 0.7:
        # Publish to message bus (A2A)
        await message_bus.publish(
            topic="fraud.high_risk",
            data={"transaction": transaction, "risk_score": risk_score}
        )

# Agent B subscribes
async def enrichment_agent():
    async for msg in message_bus.subscribe("fraud.high_risk"):
        result = await router.route("narrative", msg.data)
        
        # Publish enriched result (A2A chain)
        await message_bus.publish("fraud.enriched", result)
```

**Benefits:**
- ✅ Loose coupling between agents
- ✅ Event-driven workflows
- ✅ Scalable pub/sub
- ✅ Agent chains and orchestration

</details>

---

## 🚀 Quick Start (3 Lines!)

### For Customers Integrating Agents

```python
from agents import AgentRouter

# 1. Load agents from config (one line!)
router = AgentRouter.from_yaml("config/agents.yaml")

# 2. Use in your pipeline
result = await router.route("narrative", agent_input)

# 3. Done! Config controls inline vs offline, enable/disable, etc.
```

### For Developers Building Agents

```python
from agents import EnrichmentAgent

# 1. Extend base class
class MyAgent(EnrichmentAgent):
    async def enrich(self, request, risk_score):
        # Your logic here
        return narrative

# 2. Register in config
# config/agents.yaml:
#   agents:
#     my_agent:
#       class: "my_package.MyAgent"
#       execution_mode: "offline"

# 3. Done! Framework handles execution, routing, retries.
```

---

## 🔄 How It Fits with Customer Orchestration

```
Customer's Databricks Workflow (Unchanged)
│
├── Step 1: Feature Engineering (their code)
│   transactions = spark.table("transactions")
│   features = engineer_features(transactions)
│
├── Step 2: ML Scoring (their code)
│   scores = ml_model.predict(features)
│
├── Step 3: ADD OUR AGENTS (3 lines!)
│   router = AgentRouter.from_yaml("config.yaml")
│   enriched = enrich_with_agents(scores, router)
│
├── Step 4: Business Rules (their code, unchanged)
│   decisions = apply_business_rules(enriched)
│
└── Step 5: Write Results (their code, unchanged)
    decisions.write.saveAsTable("fraud.decisions")
```

**Key:** We plug into their existing orchestration, not replace it!

---

## 📊 Key Metrics & Benefits

| Metric | Without Framework | With Framework | Improvement |
|--------|------------------|----------------|-------------|
| **Integration** | 50+ lines | 3 lines | 95% reduction |
| **Deployment** | 2 days | 2 hours | 90% faster |
| **Onboarding** | Custom code | YAML config | Zero code |
| **SLA Control** | Hardcoded | Config-driven | Flexible |
| **Multi-tenant** | Separate codebases | One + adapters | 10x efficiency |

---

## 🎯 What Makes This Different

### Not a Full Orchestration System
- ❌ We don't replace Databricks Workflows
- ✅ We plug into existing orchestration
- ✅ Customers keep their pipelines, just add our agents

### Not Framework Lock-In
- ❌ No vendor lock-in
- ✅ Config-driven everything
- ✅ Easy to switch execution modes (dev → prod)

### Not Just "Another Agent Library"
- ❌ Not another LangChain/CrewAI clone
- ✅ Built specifically for plug-and-play deployment
- ✅ Architected around 5 core principles
- ✅ Type-safe with Pydantic
- ✅ Databricks-native

---

## 📚 Documentation Index

### Getting Started
- **[WHATS_BUILT.md](WHATS_BUILT.md)** - Current state summary, what's complete
- **[CONFIGURATION_SYSTEM.md](CONFIGURATION_SYSTEM.md)** - How to use config system
- **[../examples/plug_and_play_integration.py](../examples/plug_and_play_integration.py)** - Working integration example

### Architecture & Design
- **[EXECUTIVE_SUMMARY.md](EXECUTIVE_SUMMARY.md)** - Architecture assessment
- **[ARCHITECTURE_CORRECTION_LAKEBASE.md](ARCHITECTURE_CORRECTION_LAKEBASE.md)** - Lakebase integration details

### Multi-Tenancy & Evolution
- **[03_SCHEMA_ADAPTATION_GUIDE.md](03_SCHEMA_ADAPTATION_GUIDE.md)** - Schema adapters for different customers
- **[04_SCHEMA_VERSIONING_GUIDE.md](04_SCHEMA_VERSIONING_GUIDE.md)** - Schema evolution and migration

### Reference
- **[01_DATA_SCHEMAS_SUMMARY.md](01_DATA_SCHEMAS_SUMMARY.md)** - Schema overview
- **[02_SCHEMA_MAPPING.md](02_SCHEMA_MAPPING.md)** - Schema mappings
- **[SCHEMAS_QUICK_REFERENCE.md](SCHEMAS_QUICK_REFERENCE.md)** - Quick reference

---

## 🎓 Key Takeaways

1. **Plug-and-Play** - 3-line integration with existing pipelines
2. **Configuration-Driven** - No code changes to enable/disable features
3. **Type-Safe** - Pydantic validates everything
4. **Flexible Execution** - Same code, different backends (inline/offline/ephemeral)
5. **Databricks-Native** - Leverages existing infrastructure
6. **Multi-Tenant Ready** - Schema adapters handle any format
7. **Principled** - 5 core architectural principles enforced

**This is not a framework that replaces orchestration - it's a library that plugs into existing orchestration!**

---

## 🔍 Detailed Structure Reference

<details>
<summary><b>Click for detailed folder breakdown</b></summary>

### `agents/` - Agent Framework

```
agents/
├── base.py                      # Base agent interfaces
│   ├── Agent (ABC)              # Uniform interface
│   ├── CriticalPathAgent        # Fast path (<50ms)
│   ├── EnrichmentAgent          # Slow path (200ms+)
│   └── AgentExecutionError      # Error handling
│
├── config.py                    # Configuration loader
│   ├── AgentConfig              # Load from YAML/dict
│   ├── AgentConfigError         # Config validation
│   └── Dynamic class loading    # Import agents at runtime
│
├── registry.py                  # Registry + router
│   ├── AgentRegistry            # Central agent catalog
│   ├── AgentRouter              # Route requests
│   ├── .from_yaml()             # Load from config
│   └── .from_config()           # Load from dict
│
└── execution/                   # Pluggable backends
    ├── runner.py                # AgentRunner (abstraction)
    └── backends.py              # Backend implementations
        ├── InProcessBackend     # Same process (inline)
        ├── ProcessPoolBackend   # Process pool (hot pool)
        └── RayBackend           # Ray tasks (ephemeral)
```

### `shared/schemas/` - Pydantic Schemas

```
shared/schemas/
├── agent_io.py                  # AgentInput, AgentOutput (uniform!)
├── transactions.py              # Transaction data
├── contexts.py                  # Merchant, Customer contexts
├── fraud_signals.py             # Fraud indicators
├── mcp_tools.py                 # MCP tool results
├── embeddings.py                # Lakebase integration
├── optimization.py              # DSPy/TextGrad metadata
├── telemetry.py                 # OTEL events
├── evaluation.py                # MLflow scorers
│
└── versioning/                  # Schema evolution
    ├── base.py                  # SchemaRegistry, VersionedSchema
    ├── migrations.py            # Auto-migration
    └── compatibility.py         # Breaking change detection
```

### `shared/adapters/` - Schema Adaptation

```
shared/adapters/
├── base.py                      # BaseAdapter, AdapterRegistry
├── transaction_adapters.py      # Pre-built adapters
├── loader.py                    # Config-driven loading
└── examples.py                  # Usage examples
```

### `config/` - Configuration

```
config/
├── agents/                      # Agent configurations
│   ├── example_basic.yaml       # Simple starter
│   ├── example_advanced.yaml    # All options
│   └── example_customer_sla.yaml # SLA-driven
│
└── adapters/                    # Customer schema adapters
    ├── customer_a.yaml          # Stripe-like
    └── customer_b.yaml          # Custom
```

</details>

---

## 💡 Common Questions

<details>
<summary><b>Q: When should I use inline vs offline execution?</b></summary>

**Inline** (wait for result):
- Agent is fast (<100ms)
- Result needed immediately for decision
- SLA allows waiting
- Example: Velocity checker

**Offline** (async, don't wait):
- Agent is slow (>100ms)
- Result not needed for decision
- Tight SLA requirements
- Example: Narrative generation

**Change via config only - no code changes!**

</details>

<details>
<summary><b>Q: How do I add a new agent?</b></summary>

1. Extend base class:
```python
class MyAgent(EnrichmentAgent):
    async def enrich(self, request, risk_score):
        return result
```

2. Add to config:
```yaml
agents:
  my_agent:
    class: "my_package.MyAgent"
    execution_mode: "offline"
```

3. Done! Framework handles everything else.

</details>

<details>
<summary><b>Q: How do I onboard a new customer with a different schema?</b></summary>

1. Create adapter config:
```yaml
# config/adapters/new_customer.yaml
field_mappings:
  id: "payment.id"
  amount: "payment.amount / 100"  # Convert cents
```

2. Load adapter:
```python
adapter = AdapterLoader.from_yaml("config/adapters/new_customer.yaml")
our_schema = adapter.adapt(their_data)
```

3. Done! Takes ~2 hours (vs 2 days of custom code).

</details>

---

**For more details, see [WHATS_BUILT.md](WHATS_BUILT.md) and [CONFIGURATION_SYSTEM.md](CONFIGURATION_SYSTEM.md).**
