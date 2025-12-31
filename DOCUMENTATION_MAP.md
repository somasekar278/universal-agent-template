# Documentation Map

**Your complete guide to navigating SOTA Agent Framework documentation.**

---

## 🚀 Start Here (3 Essential Files)

1. **[README.md](README.md)** - Feature overview and capabilities
2. **[GETTING_STARTED.md](GETTING_STARTED.md)** - 5-minute quick start guide
3. **[docs/USER_JOURNEY.md](docs/USER_JOURNEY.md)** - Choose your path (Beginner/Intermediate/Advanced)

---

## 📖 Core Documentation (6 Focused Guides)

### Learning & Getting Started
- **[docs/ARCHITECTURE_ADVISOR.md](docs/ARCHITECTURE_ADVISOR.md)** - 🤖 **NEW** AI-powered architecture recommendations from briefs
- **[docs/LEARNING_PATH.md](docs/LEARNING_PATH.md)** - 🎓 **NEW** Learn by building (5 progressively complex examples)
- **[examples/learning_agents_generic.py](examples/learning_agents_generic.py)** - 💻 **NEW** Example agents using generic schemas

### Choose Features
- **[docs/FEATURE_SELECTION.md](docs/FEATURE_SELECTION.md)** - Which features do YOU need? (8 use cases with recommendations)

### Add Integrations
- **[docs/INTEGRATIONS.md](docs/INTEGRATIONS.md)** - All integrations in one:
  - Model Context Protocol (MCP)
  - LangGraph Orchestration
  - Databricks Integration
  - **A2A Protocol** (Official Linux Foundation standard - Level 5)

### Enable Advanced Features
- **[docs/ADVANCED_FEATURES.md](docs/ADVANCED_FEATURES.md)** - **NEW** All advanced features in one:
  - Agent-Governed Memory
  - Reasoning Optimization
  - Prompt Optimization
  - Agent Benchmarking

### Deploy to Production
- **[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)** - 🚀 **NEW** Deploy your agent solutions:
  - Docker & Docker Compose
  - Kubernetes (with HPA)
  - Databricks (Jobs & Model Serving)
  - Serverless (AWS Lambda, GCP Functions)
  - CI/CD Pipelines (GitHub Actions)

---

## 🎯 Quick Decision Tree

```
1. Start → README.md (2 min)
           ↓
2. New to agents? → GETTING_STARTED.md (5 min)
                    ↓
3. What's my experience level? → USER_JOURNEY.md
                                  ↓
4. What features do I need? → FEATURE_SELECTION.md
                               ↓
5. Need MCP/LangGraph/Databricks? → INTEGRATIONS.md
                                     ↓
6. Need Memory/Reasoning/Optimization? → ADVANCED_FEATURES.md
```

---

## 📦 Documentation by Experience Level

### 🌱 Beginners (Just Starting)
**Goal**: Install and run your first agent

1. **[README.md](README.md)** - Understand what the framework does
2. **[GETTING_STARTED.md](GETTING_STARTED.md)** - Install and run
3. **[docs/USER_JOURNEY.md](docs/USER_JOURNEY.md)** - Follow "Beginner" path
4. Use `sota-setup` CLI for guided setup

**Time**: 15-30 minutes

### 🔧 Intermediate (Building Custom Agents)
**Goal**: Build a production-ready agent

1. **[docs/FEATURE_SELECTION.md](docs/FEATURE_SELECTION.md)** - Choose features for your use case
2. **[docs/INTEGRATIONS.md](docs/INTEGRATIONS.md)** - Add MCP or LangGraph if needed
3. Use `sota-advisor` CLI for recommendations

**Time**: 1-2 hours

### 🚀 Advanced (Production & Optimization)
**Goal**: Deploy, optimize, and scale

1. **[docs/ADVANCED_FEATURES.md](docs/ADVANCED_FEATURES.md)** - Enable Memory, Reasoning, etc.
2. **[docs/INTEGRATIONS.md](docs/INTEGRATIONS.md)#databricks-integration** - Deploy to Databricks
3. Use `sota-benchmark` CLI for evaluation

**Time**: 2-4 hours

---

## 🔍 Quick Answers

| I want to... | Read this... |
|--------------|--------------|
| **Get started in 5 minutes** | [GETTING_STARTED.md](GETTING_STARTED.md) |
| **Know what features I need** | [FEATURE_SELECTION.md](docs/FEATURE_SELECTION.md) |
| **Find my path (Beginner/Intermediate/Advanced)** | [USER_JOURNEY.md](docs/USER_JOURNEY.md) |
| **Get architecture recommendations** | [ARCHITECTURE_ADVISOR.md](docs/ARCHITECTURE_ADVISOR.md) |
| **Add MCP tool calling** | [INTEGRATIONS.md](docs/INTEGRATIONS.md)#mcp |
| **Use LangGraph workflows** | [INTEGRATIONS.md](docs/INTEGRATIONS.md)#langgraph |
| **Deploy to Databricks** | [INTEGRATIONS.md](docs/INTEGRATIONS.md)#databricks |
| **Add agent memory** | [ADVANCED_FEATURES.md](docs/ADVANCED_FEATURES.md)#memory |
| **Optimize reasoning** | [ADVANCED_FEATURES.md](docs/ADVANCED_FEATURES.md)#reasoning |
| **Optimize prompts with DSPy/TextGrad** | [ADVANCED_FEATURES.md](docs/ADVANCED_FEATURES.md)#optimization |
| **Benchmark & evaluate agents** | [ADVANCED_FEATURES.md](docs/ADVANCED_FEATURES.md)#benchmarking |
| **Learn with hands-on examples** | [LEARNING_PATH.md](docs/LEARNING_PATH.md) |

---

## 📂 Additional Resources

### CLI Tools
```bash
sota-setup      # Interactive wizard (use-case based)
sota-generate   # Quick project generation
sota-advisor    # Project analysis & recommendations
sota-benchmark  # Agent evaluation & benchmarking
```

**Learn more**: Run any command with `--help`

### Code Examples
- **`examples/`** - Working code examples
  - `learning_agents_generic.py` - Generic agents for all levels
  - `langgraph_planning_workflow.py` - LangGraph example
  - `mcp_basic_usage.py` - MCP integration
  - `a2a_official_example.py` - A2A protocol example
  - `dynamic_tool_registry.py` - Tool registration
- **`tests/`** - Usage patterns and test examples
- **`benchmarks/`** - Evaluation suites
- **`benchmark_agents/`** - Example agents for benchmarking

---

## 🗂️ Documentation Structure

```
SOTA Agent Framework/
├── README.md                    # ⭐ Start here
├── GETTING_STARTED.md           # ⭐ Quick start
├── DOCUMENTATION_MAP.md         # ⭐ This file
├── TESTING_GUIDE.md             # 🧪 Testing framework
│
└── docs/
    ├── USER_JOURNEY.md          # 🎯 Your path (Beginner/Intermediate/Advanced)
    ├── FEATURE_SELECTION.md     # 🎯 What features do YOU need?
    ├── ARCHITECTURE_ADVISOR.md  # 🤖 AI-powered architecture recommendations
    ├── LEARNING_PATH.md         # 🎓 Learn by building (5 levels)
    ├── INTEGRATIONS.md          # 🎯 MCP + LangGraph + Databricks + A2A
    ├── ADVANCED_FEATURES.md     # 🎯 Memory + Reasoning + Optimization + Benchmarking
    │
    └── archive/                 # 📚 Reference material
        ├── BENCHMARKING.md
        ├── LANGGRAPH_INTEGRATION.md
        ├── MCP_INTEGRATION.md
        ├── MEMORY_SYSTEM.md
        ├── OPTIMIZATION.md
        └── REASONING_OPTIMIZATION.md
```

**Total**: 7 core docs + testing guide + archived reference

---

## 📊 Before vs After Consolidation

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Top-level docs** | 5 | 4 | 20% fewer |
| **docs/ directory** | 23 | 6 | 74% fewer |
| **User-facing docs** | 16 | 7 | **56% reduction** |
| **Archived (reference)** | 0 | 6 | Available if needed |

**Result**: **Clearer navigation, less overwhelm, comprehensive coverage maintained** ✅

---

## 🎓 Recommended Reading Order

### New User (30 minutes)
```
README.md (2 min)
  → GETTING_STARTED.md (5 min)
    → USER_JOURNEY.md (10 min)
      → FEATURE_SELECTION.md (10 min)
        → Start building! 🚀
```

### Building Production Agent (2-3 hours)
```
FEATURE_SELECTION.md
  → INTEGRATIONS.md (if needed)
    → ADVANCED_FEATURES.md (if needed)
      → Deploy! 🚀
```

### Optimization & Scaling (ongoing)
```
ADVANCED_FEATURES.md
  → INTEGRATIONS.md#databricks
    → Benchmark with sota-benchmark
      → Iterate! 🔄
```

---

## 📞 Need Help?

1. **Quick Start**: [GETTING_STARTED.md](GETTING_STARTED.md)
2. **Find Your Path**: [USER_JOURNEY.md](docs/USER_JOURNEY.md)
3. **Choose Features**: [FEATURE_SELECTION.md](docs/FEATURE_SELECTION.md)
4. **Use CLI**: Run `sota-setup` for interactive guidance
5. **Browse Examples**: Check `examples/` directory
6. **File an Issue**: GitHub Issues

---

## ⭐ Key Takeaways

✅ **7 core docs** - Down from 16 (56% reduction)  
✅ **Clear decision tree** - Know exactly where to go  
✅ **Experience-level based** - Beginner/Intermediate/Advanced paths  
✅ **Consolidated guides** - INTEGRATIONS.md and ADVANCED_FEATURES.md combine related content  
✅ **Testing guide** - Comprehensive testing without building agents
✅ **Archive available** - Reference material preserved in docs/archive/  

**The framework is easier to navigate while maintaining comprehensive documentation!** 🎯

---

**Ready to start?** → [GETTING_STARTED.md](GETTING_STARTED.md)
