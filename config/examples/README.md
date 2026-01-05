# Configuration Examples (L1-L5)

**Generic config templates for each learning level.**

---

## 📋 Overview

These configuration files correspond to the **5 learning levels** in the Agent Framework. Each level progressively adds more complexity and features.

| File | Level | Complexity | Time | Description |
|------|-------|-----------|------|-------------|
| `level_1_simple_chatbot.yaml` | L1 | Simple | 2-4 hrs | Stateless single agent |
| `level_2_context_aware.yaml` | L2 | Basic+ | 4-8 hrs | Memory & context tracking |
| `level_3_production_api.yaml` | L3 | Intermediate | 8-16 hrs | Production REST API |
| `level_4_complex_workflow.yaml` | L4 | Advanced | 16-32 hrs | Plan-Act-Critique loops |
| `level_5_multi_agent.yaml` | L5 | Expert | 32-64 hrs | Multi-agent coordination |

---

## 🎯 How to Use

### 1. Choose Your Level

```bash
# Start with L1 for learning
cp config/examples/level_1_simple_chatbot.yaml config/agent_config.yaml

# Or jump to production-ready L3
cp config/examples/level_3_production_api.yaml config/agent_config.yaml
```

### 2. Customize for Your Use Case

Edit `config/agent_config.yaml`:
- Update agent names
- Adjust thresholds
- Set environment variables
- Configure your domain

### 3. Deploy

```bash
# Generate monitoring (if enabled)
agent-monitoring

# Deploy to Databricks
databricks apps create -f databricks-app.yml
```

---

## 📖 Level Breakdowns

### Level 1: Simple Chatbot (2-4 hours)

**What's included:**
- ✅ Single stateless agent
- ✅ Basic LLM integration
- ❌ No memory
- ❌ No monitoring
- ❌ No optimization

**Use cases:**
- Learning the basics
- Simple Q&A
- Proof of concept

**Config features:**
```yaml
agents:
  chatbot:
    enabled: true
    model_endpoint: "databricks-dbrx-instruct"

monitoring:
  enabled: false  # Disabled for L1

optimization:
  enabled: false  # Disabled for L1
```

---

### Level 2: Context-Aware Assistant (4-8 hours)

**What's added:**
- ✅ Memory/context tracking
- ✅ Session management
- ✅ Basic MLflow logging
- ❌ No monitoring yet
- ❌ No optimization yet

**Use cases:**
- Learning tutor
- Customer support bot
- Personal assistant

**Config features:**
```yaml
agents:
  assistant:
    memory:
      enabled: true
      type: "short_term"
      max_history: 10

memory:
  enabled: true
  storage:
    type: "in_memory"

telemetry:
  mlflow:
    enabled: true  # Basic logging
```

---

### Level 3: Production-Ready API (8-16 hours)

**What's added:**
- ✅ RESTful API endpoints
- ✅ Async execution
- ✅ Error handling & retries
- ✅ Full observability (OTEL + MLflow)
- ✅ Delta Lake storage
- ✅ Basic monitoring
- ⚠️ MCP tools (optional - for document/knowledge retrieval)

**Use cases:**
- Production chatbot API
- Content generation service
- Document analyzer

**Config features:**
```yaml
agents:
  api_agent:
    execution:
      mode: "async"
      timeout: 30
      max_retries: 3
    rate_limit:
      requests_per_minute: 60

memory:
  storage:
    type: "delta"  # Persistent storage

# Optional: Add if your agent needs external knowledge
# mcp:
#   external:
#     vector_search_docs:
#       endpoint: "https://<host>/api/2.0/mcp/vector-search/prod/documents"

monitoring:
  deployment_mode: "embedded"
  enabled: true
  check_interval_seconds: 600

telemetry:
  otel:
    enabled: true
    export_to_delta: true
```

---

### Level 4: Complex Workflow (16-32 hours)

**What's added:**
- ✅ Plan → Act → Critique → Re-plan loops
- ✅ Multi-step reasoning
- ✅ LangGraph orchestration
- ✅ Prompt optimization (DSPy + TextGrad)
- ✅ Advanced monitoring
- ✅ Self-improvement
- ✅ MCP tools (recommended - multi-knowledge-base retrieval)

**Use cases:**
- Research assistant
- Code reviewer
- Complex decision-making

**Config features:**
```yaml
agents:
  workflow_agent:
    reasoning:
      enabled: true
      mode: "chain_of_thought"
      max_iterations: 5

orchestration:
  langgraph:
    enabled: true
    workflow:
      nodes:
        - name: "planner"
        - name: "executor"
        - name: "critic"
        - name: "refiner"

# Recommended: LLM chooses when to retrieve from multiple knowledge bases
mcp:
  external:
    vector_search_research:
      endpoint: "https://<host>/api/2.0/mcp/vector-search/research/papers"
    genie_research_data:
      endpoint: "https://<host>/api/2.0/mcp/genie/${GENIE_SPACE_ID}"

optimization:
  enabled: true  # Auto-optimization!
  dspy:
    enabled: true
  textgrad:
    enabled: true

monitoring:
  check_interval_seconds: 300  # More frequent
  agents:
    workflow_agent:
      thresholds:
        plan_success_rate: 0.80  # Custom metrics
```

---

### Level 5: Multi-Agent System (32-64 hours)

**What's added:**
- ✅ Multiple specialized agents
- ✅ Agent coordination
- ✅ Agent-to-Agent (A2A) communication
- ✅ Shared memory across agents
- ✅ Distributed workflows
- ✅ Cross-agent optimization
- ✅ MCP tools (highly recommended - domain-specific per agent)

**Use cases:**
- Healthcare network
- Software development team
- E-commerce platform

**Config features:**
```yaml
agents:
  coordinator:
    role: "coordinator"
    peers: ["specialist_a", "specialist_b", "specialist_c"]

  specialist_a:
    role: "specialist"
    domain: "analysis"
    peers: ["coordinator", "specialist_b"]

  specialist_b:
    role: "specialist"
    domain: "generation"

  specialist_c:
    role: "validator"
    domain: "validation"

# Required: Domain-specific tools for each agent
mcp:
  external:
    # Specialist A tools
    vector_search_domain_a:
      endpoint: "https://<host>/api/2.0/mcp/vector-search/domains/analysis"

    # Specialist B tools
    vector_search_domain_b:
      endpoint: "https://<host>/api/2.0/mcp/vector-search/domains/generation"

  # Agent-specific access control
  access_control:
    specialist_a:
      allowed_servers: ["vector_search_domain_a"]
    specialist_b:
      allowed_servers: ["vector_search_domain_b"]

a2a:
  enabled: true  # Agent-to-Agent communication
  protocol_version: "1.0"
  transport:
    type: "http"

orchestration:
  langgraph:
    workflow:
      # Multi-agent collaboration
      parallel:
        enabled: true
        max_workers: 3

memory:
  shared:
    enabled: true  # Shared across agents
  private:
    enabled: true  # Private per agent

optimization:
  agents:  # Optimize all agents
    - "coordinator"
    - "specialist_a"
    - "specialist_b"
    - "specialist_c"

  training_data:
    include_a2a_messages: true  # Multi-agent specific
```

---

## 🚀 Progression Path

**Recommended learning path:**

```
L1 (2-4 hrs)
  ↓
Learn: Agent basics, LLM integration
  ↓
L2 (4-8 hrs)
  ↓
Learn: Memory, context, sessions
  ↓
L3 (8-16 hrs)
  ↓
Learn: Production APIs, observability, error handling
  ↓
L4 (16-32 hrs)
  ↓
Learn: Complex workflows, reasoning, optimization
  ↓
L5 (32-64 hrs)
  ↓
Master: Multi-agent systems, coordination, A2A
```

**Total learning time: 62-124 hours (progressive)**

---

## 💡 Tips

### Starting from Scratch?
**Start with L1.** Don't skip levels - each builds on the previous.

### Have Experience?
**Jump to L3** for production-ready setup, then explore L4/L5.

### Building Something Specific?

Use the decision matrix in [GETTING_STARTED.md](../../docs/GETTING_STARTED.md):
- **Simple chat?** → L1 (chatbot)
- **Need memory?** → L2 (assistant)
- **Production API?** → L3 (api)
- **Multi-step workflows?** → L4 (workflow)
- **Multi-agent system?** → L5 (system)

Or generate a scaffold:
```bash
databricks-agent-toolkit generate chatbot my-bot
```

### Want Examples?
See `examples/learning_agents_generic.py` for working code using these configs.

---

## 📚 Related Documentation

- **[Learning Path](../../docs/LEARNING_PATH.md)** - Complete learning guide
- **[Configuration Guide](../../docs/CONFIGURATION_GUIDE.md)** - All config options explained
- **[Architecture Advisor](../../docs/ARCHITECTURE_ADVISOR.md)** - Get AI-powered recommendations

---

## 🔍 Compare Levels

| Feature | L1 | L2 | L3 | L4 | L5 |
|---------|----|----|----|----|-----|
| **Single Agent** | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Memory** | ❌ | ✅ | ✅ | ✅ | ✅ |
| **MCP Tools** | ❌ | ❌ | ⚠️ Optional | ✅ | ✅ |
| **Monitoring** | ❌ | ❌ | ✅ | ✅ | ✅ |
| **Optimization** | ❌ | ❌ | ❌ | ✅ | ✅ |
| **Reasoning** | ❌ | ❌ | ❌ | ✅ | ✅ |
| **Multi-Agent** | ❌ | ❌ | ❌ | ❌ | ✅ |
| **A2A Protocol** | ❌ | ❌ | ❌ | ❌ | ✅ |
| **Production Ready** | ❌ | ❌ | ✅ | ✅ | ✅ |
| **Learning Time** | 2-4h | 4-8h | 8-16h | 16-32h | 32-64h |

---

**Choose your level and start building!** 🚀
