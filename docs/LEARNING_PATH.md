# SOTA Agent Framework - Learning Path

**Learn by building: From simple chatbot to autonomous multi-agent system**

---

## 🎓 Your Learning Journey

This guide takes you from **theoretical understanding** to **practical implementation** by building 5 progressively complex examples.

**Philosophy**: Each level builds on the previous, introducing new concepts gradually.

---

## 📚 Level 1: Simple Chatbot (Week 1)

**Goal**: Understand the core agent architecture  
**Time**: 2-3 hours  
**Complexity**: ⭐ Basic

### What You'll Learn
- ✅ What is an agent?
- ✅ How to define agent behavior
- ✅ Input/Output schemas with Pydantic
- ✅ Agent registration and routing
- ✅ Basic YAML configuration

### What You'll Build
A simple Q&A chatbot that:
- Takes a question
- Processes it through an agent
- Returns an answer
- Uses configuration for settings

### Key Concepts

#### **1. Agent Base Class**
```python
from agents.base import Agent

class SimpleChatAgent(Agent):
    """
    Agents inherit from base Agent class
    They MUST implement the process() method
    """
    async def process(self, input_data):
        # Your logic here
        return output_data
```

**Why?** Standardized interface means all agents work the same way.

#### **2. Input/Output Schemas**
```python
from pydantic import BaseModel

class ChatInput(BaseModel):
    question: str
    user_id: str

class ChatOutput(BaseModel):
    answer: str
    confidence: float
```

**Why?** Type safety prevents bugs and makes your code self-documenting.

#### **3. Agent Registry**
```python
from agents.registry import AgentRegistry

registry = AgentRegistry()
registry.register("chat_agent", SimpleChatAgent())

# Later, route requests
result = await registry.route("chat_agent", input_data)
```

**Why?** Centralized routing makes it easy to add/remove agents without code changes.

### Step-by-Step Build

**Step 1**: Define your schema (`schemas.py`)
**Step 2**: Create your agent (`agent.py`)
**Step 3**: Register and route (`main.py`)
**Step 4**: Add configuration (`config.yaml`)
**Step 5**: Test it (`test.py`)

### Exercises
1. Add a `timestamp` to the output
2. Create a second agent for a different purpose
3. Route between agents based on input

---

## 📚 Level 2: Context-Aware Assistant (Week 2)

**Goal**: Add memory to remember past interactions  
**Time**: 3-4 hours  
**Complexity**: ⭐⭐ Intermediate

### What You'll Learn
- ✅ Why agents need memory
- ✅ Short-term vs long-term memory
- ✅ Storage backends (in-memory, disk, Delta Lake)
- ✅ Retrieval strategies (recency, semantic, importance)
- ✅ Context window management

### What You'll Build
A customer support agent that:
- Remembers previous questions from the same user
- Retrieves relevant past interactions
- Provides context-aware responses
- Manages memory storage intelligently

### Key Concepts

#### **1. Memory Manager**
```python
from memory import MemoryManager, MemoryType

memory = MemoryManager()

# Store a memory
await memory.store(
    content="User asked about pricing",
    memory_type=MemoryType.EPISODIC,
    metadata={"user_id": "123"}
)

# Retrieve related memories
memories = await memory.retrieve(
    query="pricing questions",
    top_k=5
)
```

**Why?** Agents without memory can't learn or maintain context across interactions.

#### **2. Storage Backends**
```python
from memory.stores import InMemoryStore, DeltaLakeStore

# Start simple
memory = MemoryManager(store=InMemoryStore())

# Scale to production
memory = MemoryManager(store=DeltaLakeStore(
    catalog="main",
    schema="agent_memory"
))
```

**Why?** Start with in-memory for dev, switch to persistent storage for prod.

#### **3. Retrieval Strategies**
```python
from memory.strategies import RecencyStrategy, SemanticStrategy

# Get most recent
recent = await memory.retrieve(
    query="user_123",
    strategy=RecencyStrategy(top_k=5)
)

# Get semantically similar
similar = await memory.retrieve(
    query="How do I cancel my subscription?",
    strategy=SemanticStrategy(top_k=5)
)
```

**Why?** Different use cases need different retrieval approaches.

### Step-by-Step Build

**Step 1**: Add memory to Level 1 agent
**Step 2**: Store each interaction in memory
**Step 3**: Retrieve relevant context before responding
**Step 4**: Show how context improves responses
**Step 5**: Add memory configuration to YAML

### Exercises
1. Add importance scoring to memories
2. Implement a forgetting policy (delete old memories)
3. Share memory between multiple agents

---

## 📚 Level 3: Production API (Week 3)

**Goal**: Deploy as a production REST API with monitoring  
**Time**: 4-6 hours  
**Complexity**: ⭐⭐⭐ Advanced

### What You'll Learn
- ✅ FastAPI for REST endpoints
- ✅ Health checks and liveness probes
- ✅ Metrics collection (latency, throughput, errors)
- ✅ Telemetry and tracing (OpenTelemetry)
- ✅ Experiment tracking (feature flags, A/B tests)
- ✅ Background workers for async tasks

### What You'll Build
A production-ready agent API with:
- REST endpoints (`/chat`, `/health`, `/metrics`)
- WebSocket for real-time streaming
- Health monitoring dashboard
- Request tracing
- A/B testing for different prompts
- Background job processing

### Key Concepts

#### **1. FastAPI Service**
```python
from services.api import create_agent_api
from fastapi import FastAPI

app = create_agent_api(
    agents={"chat": chat_agent},
    enable_metrics=True,
    enable_health_checks=True
)

# Now you have:
# POST /agents/chat - Chat endpoint
# GET /health - Health check
# GET /metrics - Prometheus metrics
```

**Why?** Production systems need standard endpoints for orchestration (K8s, etc.)

#### **2. Monitoring**
```python
from monitoring import HealthCheckManager, MetricsCollector

health = HealthCheckManager()
health.register_check("agent", agent_health_check)
health.register_check("memory", memory_health_check)

metrics = MetricsCollector()
metrics.record_latency("agent.chat", 0.245)
metrics.record_success("agent.chat")
```

**Why?** You can't improve what you don't measure.

#### **3. Telemetry**
```python
from telemetry import AgentTracer

tracer = AgentTracer()

with tracer.trace_agent_execution(agent_name="chat"):
    result = await agent.process(input_data)
    
# Traces automatically exported to Delta Lake
```

**Why?** Debug production issues by replaying exact execution paths.

#### **4. Experiments**
```python
from experiments import FeatureFlagManager, ABTest

flags = FeatureFlagManager()
if flags.is_enabled("new_prompt_v2"):
    prompt = new_prompt
else:
    prompt = old_prompt

ab_test = ABTest(
    variants=["prompt_a", "prompt_b"],
    traffic_split=[0.5, 0.5]
)
variant = ab_test.assign(user_id)
```

**Why?** Safely test new features and optimize performance without risk.

### Step-by-Step Build

**Step 1**: Wrap Level 2 agent in FastAPI
**Step 2**: Add health checks
**Step 3**: Add metrics collection
**Step 4**: Add telemetry tracing
**Step 5**: Set up A/B test for prompts
**Step 6**: Deploy locally with Docker Compose

### Exercises
1. Add rate limiting to the API
2. Create a Grafana dashboard for metrics
3. Run an A/B test comparing two agent prompts

---

## 📚 Level 4: Complex Workflow (Week 4)

**Goal**: Build autonomous agents that plan, act, critique, and re-plan  
**Time**: 6-8 hours  
**Complexity**: ⭐⭐⭐⭐ Expert

### What You'll Learn
- ✅ LangGraph for multi-step workflows
- ✅ Plan-Act-Critique loops
- ✅ Reasoning optimization (trajectory tuning)
- ✅ Chain-of-thought distillation
- ✅ Prompt optimization (DSPy, TextGrad)
- ✅ Agent benchmarking and evaluation
- ✅ Execution visualization

### What You'll Build
An autonomous fraud detection system that:
- Creates a plan to investigate a transaction
- Executes the plan (calls tools, checks databases)
- Critiques its own work
- Re-plans if needed
- Learns from past executions
- Optimizes its prompts automatically
- Visualizes decision-making process

### Key Concepts

#### **1. LangGraph Workflows**
```python
from orchestration.langgraph import AgentWorkflowGraph
from orchestration.langgraph.nodes import PlannerNode, ExecutorNode, CriticNode

workflow = AgentWorkflowGraph(agent_router=router)

# Add nodes
workflow.add_node("planner", PlannerNode())
workflow.add_node("executor", ExecutorNode())
workflow.add_node("critic", CriticNode())

# Define flow
workflow.add_edge("planner", "executor")
workflow.add_conditional_edge(
    "executor", 
    "critic",
    should_replan  # Function that decides if we need to re-plan
)

# Run
result = await workflow.run(transaction_data)
```

**Why?** Complex tasks require breaking down into steps, executing, and self-correcting.

#### **2. Reasoning Optimization**
```python
from reasoning import TrajectoryOptimizer, FeedbackLoop

# Learn from execution paths
optimizer = TrajectoryOptimizer()
trajectory = optimizer.record(execution)
suggestions = optimizer.suggest_improvements(trajectory)

# Self-improvement loop
feedback = FeedbackLoop(agent)
improved = await feedback.improve_with_feedback(
    input_data=task,
    max_iterations=3
)
```

**Why?** Agents should get better over time, not stay static.

#### **3. Prompt Optimization**
```python
from optimization import PromptOptimizer

optimizer = PromptOptimizer()

# Automatically improve prompts
result = await optimizer.optimize(
    prompt="Analyze this transaction for fraud",
    prompt_type="task",
    training_data=examples
)

# DSPy finds optimal few-shot examples
# TextGrad refines wording for better results
```

**Why?** Manual prompt engineering is slow; let the framework optimize for you.

#### **4. Benchmarking**
```python
from evaluation import EvaluationHarness
from evaluation.metrics import (
    ToolCallSuccessRate, 
    PlanCorrectnessMetric,
    HallucinationMetric
)

harness = EvaluationHarness()
harness.add_metric(ToolCallSuccessRate())
harness.add_metric(PlanCorrectnessMetric())

results = await harness.evaluate(
    agent=fraud_detector,
    test_suite=test_cases
)

# Get detailed report
print(results.to_markdown())
```

**Why?** Track agent performance over time, prevent regressions.

### Step-by-Step Build

**Step 1**: Define a multi-step workflow (plan → execute → critique)
**Step 2**: Implement planner, executor, critic nodes
**Step 3**: Add trajectory recording
**Step 4**: Run prompt optimization on key prompts
**Step 5**: Create benchmark suite
**Step 6**: Visualize execution graphs

### Exercises
1. Add a "tool selection" node that picks optimal tools
2. Implement confidence-based re-planning
3. Compare optimized vs non-optimized prompts

---

## 📚 Level 5: Autonomous Multi-Agent System (Week 5)

**Goal**: Full production system with ALL features  
**Time**: 8-12 hours  
**Complexity**: ⭐⭐⭐⭐⭐ SOTA

### What You'll Learn
- ✅ **A2A Protocol** - Official Linux Foundation standard for cross-framework agent communication
- ✅ Agent Cards for discovery and interoperability
- ✅ MCP for standardized tool interfaces
- ✅ Semantic embeddings for memory
- ✅ Memory graphs for relationship tracking
- ✅ Unity Catalog for prompt/model versioning
- ✅ RL-style agent tuning
- ✅ Databricks deployment with Terraform
- ✅ Complete observability stack

### What You'll Build
A production-grade fraud detection system with:
- **A2A-enabled agents** that can communicate with external agent frameworks
- Multiple specialized agents (fraud detector, risk analyzer, investigator)
- MCP servers for external tools (BIN lookup, sanctions check)
- Semantic memory with relationship graphs
- Prompt versioning in Unity Catalog
- Deployed to Databricks with full observability
- Continuous learning and improvement

### Key Concepts

#### **1. A2A Protocol (Official Linux Foundation Standard)**

```python
from agents.a2a import A2AServer, A2AClient, create_agent_card

# Expose your agent via A2A protocol
server = A2AServer(
    agent=my_fraud_agent,
    name="fraud_detector",
    description="Advanced fraud detection agent",
    skills=["fraud_detection", "risk_analysis"],
    port=8080
)
await server.start()

# Agent Card published at http://localhost:8080/card.json
# Other A2A-compliant agents can now discover and use it!

# Call external A2A agents
client = A2AClient()
external_card = await client.discover(
    "https://external-service.com/agent/card.json"
)

result = await client.execute_task(
    agent_url=external_card.url,
    skill="deep_analysis",
    input_data={"transaction": transaction_data}
)
```

**Why?** A2A enables cross-framework interoperability. Your SOTA agents can collaborate with agents built on LangChain, AutoGPT, CrewAI, or any A2A-compliant framework. It's the industry standard backed by Google and the Linux Foundation.

**Key Features:**
- JSON-RPC 2.0 over HTTP(S)
- Agent Cards for discovery
- Streaming support (SSE)
- Push notifications
- Enterprise security and authentication

**Official Resources:**
- GitHub: https://github.com/a2aproject/A2A
- Website: https://a2a-protocol.org/
- Spec: https://a2a-protocol.org/docs/specification

#### **2. MCP Integration**
```python
from agents.mcp_client import AgentMCPClient

mcp = AgentMCPClient()
await mcp.connect("python", "mcp_servers/fraud_tools.py")

# Call external tools via standardized interface
result = await mcp.call_tool("sanctions_check", {
    "entity_name": "John Doe"
})
```

**Why?** MCP standardizes how agents call external APIs and tools.

#### **3. Advanced Memory**
```python
from memory import MemoryManager
from memory.embeddings import SentenceTransformerEmbeddings
from memory.graphs import MemoryGraph

# Semantic embeddings
memory = MemoryManager(
    embeddings=SentenceTransformerEmbeddings()
)

# Find similar cases by meaning, not keywords
similar = await memory.retrieve(
    query="wire transfer to high-risk country",
    strategy=SemanticStrategy()
)

# Track relationships
graph = MemoryGraph()
graph.add_relationship(
    "transaction_123",
    "merchant_456",
    relationship="processed_by"
)
patterns = graph.detect_patterns()
```

**Why?** Advanced memory enables agents to find insights humans would miss.

#### **4. Unity Catalog**
```python
from uc_registry import PromptRegistry, ModelRegistry

# Version prompts like code
prompts = PromptRegistry(
    catalog="main",
    schema="agent_prompts",
    volume="versions"
)

prompts.register_prompt(
    name="fraud_detector_v3",
    content=prompt_text,
    metadata={"accuracy": 0.94}
)

# Track in Unity Catalog, query via SQL later
```

**Why?** Treat prompts and models as versioned artifacts for governance.

#### **5. Databricks Deployment**
```hcl
# infra/databricks/main.tf

# Provision everything via Terraform
resource "databricks_catalog" "agent_catalog" {
  name = "agent_system"
}

resource "databricks_model_serving" "agent_endpoint" {
  name = "fraud-detector"
  config {
    served_models {
      model_name = "fraud_detector"
      model_version = "3"
      workload_size = "Small"
    }
  }
}
```

**Why?** Infrastructure as code makes deployment repeatable and auditable.

### Step-by-Step Build

**Step 1**: Create multiple specialized agents
**Step 2**: Build MCP servers for external tools
**Step 3**: Add semantic embeddings to memory
**Step 4**: Implement memory graph tracking
**Step 5**: Set up Unity Catalog integration
**Step 6**: Write Terraform for Databricks deployment
**Step 7**: Deploy and validate full system
**Step 8**: Run complete benchmark suite

### Exercises
1. Add a new specialized agent to the system
2. Create a custom MCP server for a new tool
3. Deploy to Databricks and run production traffic

---

## 🎯 Weekly Milestones

| Week | Level | What You'll Have Working | Skills Gained |
|------|-------|-------------------------|---------------|
| 1 | Simple Chatbot | Basic agent responding to questions | Core architecture |
| 2 | Context-Aware | Agent remembering past conversations | Memory systems |
| 3 | Production API | API with monitoring deployed locally | Production practices |
| 4 | Complex Workflow | Agent that plans, acts, and learns | Advanced orchestration |
| 5 | Multi-Agent System | Full production system on Databricks | Complete SOTA stack |

---

## 📚 Resources for Each Level

### Level 1 Resources
- `agents/base.py` - Read the Agent class
- `agents/registry.py` - Understand routing
- `shared/schemas/` - See schema examples
- `examples/` - Reference implementations

### Level 2 Resources
- `memory/manager.py` - Memory orchestration
- `memory/stores.py` - Storage backends
- `memory/strategies.py` - Retrieval strategies
- `docs/MEMORY_SYSTEM.md` - Full memory guide

### Level 3 Resources
- `services/api.py` - FastAPI implementation
- `monitoring/` - All monitoring modules
- `telemetry/` - OpenTelemetry integration
- `experiments/` - Feature flags & A/B testing

### Level 4 Resources
- `orchestration/langgraph/` - LangGraph workflows
- `reasoning/` - All reasoning modules
- `optimization/` - DSPy & TextGrad
- `evaluation/` - Benchmarking suite

### Level 5 Resources
- `agents/a2a/` - Official A2A protocol integration
- https://github.com/a2aproject/A2A - Official A2A GitHub
- https://a2a-protocol.org/ - A2A Protocol documentation
- `agents/mcp_client.py` - MCP integration
- `memory/embeddings.py` - Semantic embeddings
- `uc_registry/` - Unity Catalog
- `infra/databricks/` - Terraform configs

---

## 🤝 How We'll Work Together

**For each level:**

1. **I'll provide**: 
   - Starter code template
   - Explanation of key concepts
   - Step-by-step instructions

2. **You'll build**:
   - Complete the implementation
   - Test it works
   - Experiment with variations

3. **We'll review**:
   - What worked
   - What was confusing
   - How to improve

4. **You'll learn**:
   - By doing, not just reading
   - Practical implementation skills
   - Real-world patterns

---

## ✅ Next Steps

**Ready to start Level 1?** Say the word and I'll:
1. Create the directory structure
2. Provide starter code with TODOs
3. Explain each concept as we go
4. Help you debug issues
5. Celebrate when it works! 🎉

**You'll go from theoretical understanding to practical mastery, one level at a time.**

---

**Ready to begin Level 1: Simple Chatbot?** 🚀

