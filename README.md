[![PyPI](https://img.shields.io/pypi/v/sota-agent-framework)](https://pypi.org/project/sota-agent-framework/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

# SOTA Agent Framework

**Production-ready template for building AI agent workflows in any domain.**

Build intelligent agents with memory, reasoning, optimization, and seamless Databricks integration. Start simple, scale to autonomous systems.

---

## 🚀 Quick Start

### Installation

```bash
# Basic (core features only)
pip install sota-agent-framework

# With features you need
pip install sota-agent-framework[all]  # Everything
pip install sota-agent-framework[databricks]  # Databricks integration
pip install sota-agent-framework[optimization]  # DSPy + TextGrad
```

### Choose Your Path

**🤖 Have a Use Case? (NEW! - AI-Powered)**
```bash
sota-architect "Build a fraud detection system with memory and self-improvement"
# → Instant architecture recommendation: Level, schemas, features, integrations!
```
Describe your use case in natural language, get instant architecture recommendations.

**🎓 Want to Learn? (NEW!)**
```bash
sota-learn  # Interactive learning mode - build 5 progressively complex examples
```
Learn by building: chatbot → context-aware → production API → complex workflow → autonomous multi-agent

**🚀 New to Agents?**
```bash
sota-setup  # Interactive wizard guides you through
```

**🔧 Building an Agent?**
```bash
sota-generate --domain "fraud_detection" --output ./my-agent
cd my-agent && sota-advisor .  # Get recommendations
```

**⚡ Expert?**
```bash
# Use the framework as a library
from agents import Agent, AgentRouter
from memory import MemoryManager
from orchestration import AgentWorkflowGraph
```

**📖 [See complete getting started guide →](GETTING_STARTED.md)**  
**🎓 [See learning path →](docs/LEARNING_PATH.md)**

---

## ✨ Key Features

### Core Framework
- ⚡ **Multiple Execution Modes** - In-process, parallel, Ray, serverless
- 🔌 **Pluggable Architecture** - Use only what you need
- 📝 **Type-Safe Schemas** - Pydantic models throughout
- ⚙️ **YAML Configuration** - Infrastructure as code

### Agent Intelligence
- 🧠 **Agent-Governed Memory** - Smart storage, retrieval, reflection, forgetting
- 🎯 **Reasoning Optimization** - Trajectory tuning, CoT distillation, self-improvement
- 🔄 **Plan-Act-Critique Loops** - LangGraph-powered orchestration
- 🤝 **A2A Protocol (Official)** - Linux Foundation standard for cross-framework agent communication
- 📊 **Comprehensive Benchmarking** - 6+ metrics, regression testing

### Production Ready
- 🏢 **Databricks Native** - Unity Catalog, Delta Lake, MLflow integration
- 📈 **Complete Observability** - OpenTelemetry, execution graphs, trace replay
- 🔧 **Prompt Optimization** - DSPy & TextGrad for auto-tuning
- 🌐 **REST & WebSocket APIs** - Production services included
- 🎛️ **Experiment Tracking** - Feature flags, A/B testing, MLflow

### Developer Experience
- 🎯 **Progressive Disclosure** - Strong defaults for beginners, full control for experts
- 🤖 **AI-Powered Tools** - `sota-architect` (AI recommendations), `sota-setup`, `sota-generate`, `sota-advisor`, `sota-benchmark`, `sota-learn`
- 📚 **8 Core Docs** - Clear, concise, use-case driven
- 🔍 **Use-Case Guidance** - Know exactly which features you need

---

## 📦 Use Cases

**Works for any agent workflow:**
- 🔒 Fraud Detection & Risk Analysis
- 💬 Customer Support & Chatbots
- 📝 Content Moderation
- 🏥 Healthcare & Diagnostics
- 🔍 Data Quality & Anomaly Detection
- 📊 Analytics & Report Generation
- 🤖 **Your Use Case Here**

---

## 📖 Documentation

**Start Here:**
1. **[Getting Started](GETTING_STARTED.md)** - 5-minute setup
2. **[User Journey](docs/USER_JOURNEY.md)** - Choose your path (Beginner/Intermediate/Advanced)
3. **[Feature Selection](docs/FEATURE_SELECTION.md)** - Which features do YOU need?

**Core Guides:**
- **[Configuration](docs/CONFIGURATION.md)** - Complete YAML configuration
- **[Integrations](docs/INTEGRATIONS.md)** - MCP, LangGraph, Databricks
- **[Advanced Features](docs/ADVANCED_FEATURES.md)** - Memory, Reasoning, Optimization, Benchmarking

**Quick Links:**
- [Documentation Map](DOCUMENTATION_MAP.md) - Complete navigation guide
- [Examples](examples/) - Working code examples
- [Benchmarks](benchmarks/) - Evaluation suites

---

## 🛠️ CLI Tools

```bash
# 🎓 Interactive learning mode (NEW!)
sota-learn              # Learn by building 5 progressively complex examples
sota-learn start 1      # Start Level 1: Simple Chatbot
sota-learn start 2      # Start Level 2: Context-Aware Assistant

# Interactive setup wizard (use-case based)
sota-setup

# Generate new project
sota-generate --domain "your_domain" --output ./project

# Analyze project & get recommendations
sota-advisor ./project

# Run benchmarks & evaluations
sota-benchmark run --suite fraud_detection --report md
```

---

## 🎯 Feature Selection Guide

| Use Case | Memory | Reasoning | Optimization | Monitoring | LangGraph |
|----------|--------|-----------|--------------|------------|-----------|
| **Simple Chatbot** | ⚪ Optional | ❌ No | ❌ No | ⚪ Optional | ❌ No |
| **Context-Aware Agent** | ✅ Yes | ⚪ Optional | ⚪ Optional | ✅ Yes | ⚪ Optional |
| **Production API** | ⚪ Optional | ❌ No | ⚪ Optional | ✅ Yes | ❌ No |
| **Complex Workflows** | ✅ Yes | ✅ Yes | ⚪ Optional | ✅ Yes | ✅ Yes |
| **Autonomous Agent** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |

**📖 [See detailed feature guide →](docs/FEATURE_SELECTION.md)**

---

## 🏗️ Architecture

```
SOTA Agent Framework
├── agents/           # Core agent classes & registry
├── memory/           # Agent-governed memory system
├── reasoning/        # Trajectory optimization & feedback
├── optimization/     # DSPy & TextGrad prompt optimization
├── orchestration/    # LangGraph workflows
├── evaluation/       # Benchmarking & metrics
├── visualization/    # Databricks-native observability
├── telemetry/        # OpenTelemetry → Delta Lake
├── uc_registry/      # Unity Catalog integration
├── experiments/      # Feature flags & A/B testing
├── monitoring/       # Health checks & metrics
├── services/         # REST API & WebSocket
└── infra/            # Terraform for Databricks
```

**📖 [See detailed architecture →](docs/USER_JOURNEY.md)**

---

## 🚀 Example: Fraud Detection Agent

```python
from agents import Agent, CriticalPathAgent
from memory import MemoryManager
from orchestration import AgentWorkflowGraph

# Define agent
class FraudDetectorAgent(CriticalPathAgent):
    async def process(self, input_data):
        # Check memory for similar cases
        similar = await self.memory.retrieve(
            query=f"transaction {input_data.transaction_id}",
            top_k=5
        )
        
        # Run detection
        result = await self.detect_fraud(input_data)
        
        # Store in memory
        await self.memory.store(result, importance="HIGH")
        
        return result

# Use with LangGraph for complex workflows
workflow = AgentWorkflowGraph(agent_router=router)
workflow.add_node("planner", PlannerNode())
workflow.add_node("detector", FraudDetectorAgent())
workflow.add_node("critic", CriticNode())

result = await workflow.run(transaction_data)
```

**📖 [See more examples →](examples/)**

---

## 🤝 Contributing

We welcome contributions! See our contribution guidelines (coming soon) or file an issue.

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🔗 Links

- **PyPI**: https://pypi.org/project/sota-agent-framework/
- **GitHub**: https://github.com/somasekar278/universal-agent-template
- **Documentation**: [DOCUMENTATION_MAP.md](DOCUMENTATION_MAP.md)

---

## ⭐ What Makes This SOTA?

Unlike orchestration-only or research-only agent frameworks, SOTA Agent ships a complete agentic development stack including autonomous planning loops, agent-governed memory, reasoning trajectory optimization, prompt auto-tuning, benchmark harnesses, and governed deployment — built for real data pipelines and production SLAs

✅ **Agent-Governed Memory** - Not just storage, intelligent decisions  
✅ **Plan-Act-Critique Loops** - True autonomous workflows  
✅ **Reasoning Optimization** - Learn from execution trajectories  
✅ **Comprehensive Benchmarking** - Track performance over time  
✅ **Databricks Native** - Production-ready from day one  
✅ **Progressive Disclosure** - Works for beginners AND experts  
✅ **Modular Design** - Use only what you need  

**🚀 [Get started now →](GETTING_STARTED.md)**
