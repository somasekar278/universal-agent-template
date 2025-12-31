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
- **[docs/LEARNING_SCHEMAS.md](docs/LEARNING_SCHEMAS.md)** - 📋 **NEW** Generic schemas for all learning levels (domain-agnostic)
- **[examples/learning_agents_generic.py](examples/learning_agents_generic.py)** - 💻 **NEW** Example agents using generic schemas

### Choose Features
- **[docs/FEATURE_SELECTION.md](docs/FEATURE_SELECTION.md)** - Which features do YOU need? (8 use cases with recommendations)

### Configure Framework
- **[docs/CONFIGURATION.md](docs/CONFIGURATION.md)** - Complete YAML configuration guide

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
5. How do I configure? → CONFIGURATION.md
                         ↓
6. Need MCP/LangGraph/Databricks? → INTEGRATIONS.md
                                     ↓
7. Need Memory/Reasoning/Optimization? → ADVANCED_FEATURES.md
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
2. **[docs/CONFIGURATION.md](docs/CONFIGURATION.md)** - Configure agents
3. **[docs/INTEGRATIONS.md](docs/INTEGRATIONS.md)** - Add MCP or LangGraph if needed
4. Use `sota-advisor` CLI for recommendations

**Time**: 1-2 hours

### 🚀 Advanced (Production & Optimization)
**Goal**: Deploy, optimize, and scale

1. **[docs/ADVANCED_FEATURES.md](docs/ADVANCED_FEATURES.md)** - Enable Memory, Reasoning, etc.
2. **[docs/INTEGRATIONS.md](docs/INTEGRATIONS.md)#databricks-integration** - Deploy to Databricks
3. **[docs/CONFIGURATION.md](docs/CONFIGURATION.md)** - Advanced configuration
4. Use `sota-benchmark` CLI for evaluation

**Time**: 2-4 hours

---

## 🔍 Quick Answers

| I want to... | Read this... |
|--------------|--------------|
| **Get started in 5 minutes** | [GETTING_STARTED.md](GETTING_STARTED.md) |
| **Know what features I need** | [FEATURE_SELECTION.md](docs/FEATURE_SELECTION.md) |
| **Find my path (Beginner/Intermediate/Advanced)** | [USER_JOURNEY.md](docs/USER_JOURNEY.md) |
| **Configure agents with YAML** | [CONFIGURATION.md](docs/CONFIGURATION.md) |
| **Add MCP tool calling** | [INTEGRATIONS.md](docs/INTEGRATIONS.md)#mcp |
| **Use LangGraph workflows** | [INTEGRATIONS.md](docs/INTEGRATIONS.md)#langgraph |
| **Deploy to Databricks** | [INTEGRATIONS.md](docs/INTEGRATIONS.md)#databricks |
| **Add agent memory** | [ADVANCED_FEATURES.md](docs/ADVANCED_FEATURES.md)#memory |
| **Optimize reasoning** | [ADVANCED_FEATURES.md](docs/ADVANCED_FEATURES.md)#reasoning |
| **Optimize prompts with DSPy/TextGrad** | [ADVANCED_FEATURES.md](docs/ADVANCED_FEATURES.md)#optimization |
| **Benchmark & evaluate agents** | [ADVANCED_FEATURES.md](docs/ADVANCED_FEATURES.md)#benchmarking |
| **Adapt data schemas** | [docs/schemas/](docs/schemas/) |

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
  - `langgraph_planning_workflow.py` - LangGraph example
  - `mcp_basic_usage.py` - MCP integration
  - `dynamic_tool_registry.py` - Tool registration
- **`tests/`** - Usage patterns and test examples
- **`benchmarks/`** - Evaluation suites
- **`benchmark_agents/`** - Example agents for benchmarking

### Schema Documentation
- **[docs/schemas/](docs/schemas/)** - Complete data model docs
  - `01_DATA_SCHEMAS_SUMMARY.md` - Overview
  - `02_SCHEMA_MAPPING.md` - Mapping guide
  - `03_SCHEMA_ADAPTATION_GUIDE.md` - Multi-tenant adaptation
  - `04_SCHEMA_VERSIONING_GUIDE.md` - Version management

---

## 🗂️ Documentation Structure

```
SOTA Agent Framework/
├── README.md                    # ⭐ Start here
├── GETTING_STARTED.md           # ⭐ Quick start
├── DOCUMENTATION_MAP.md         # ⭐ This file
│
└── docs/
    ├── USER_JOURNEY.md          # 🎯 Your path (Beginner/Intermediate/Advanced)
    ├── FEATURE_SELECTION.md     # 🎯 What features do YOU need?
    ├── CONFIGURATION.md         # 🎯 Complete YAML config guide
    ├── INTEGRATIONS.md          # 🎯 MCP + LangGraph + Databricks (all in one)
    ├── ADVANCED_FEATURES.md     # 🎯 Memory + Reasoning + Optimization + Benchmarking (all in one)
    │
    ├── schemas/                 # Schema documentation
    │   ├── 01_DATA_SCHEMAS_SUMMARY.md
    │   ├── 02_SCHEMA_MAPPING.md
    │   ├── 03_SCHEMA_ADAPTATION_GUIDE.md
    │   ├── 04_SCHEMA_VERSIONING_GUIDE.md
    │   ├── SCHEMAS_QUICK_REFERENCE.md
    │   └── SCHEMA_VERSIONING_QUICK_START.md
    │
    └── archive/                 # 📚 Reference material (9 files)
        ├── FRAMEWORK_GUIDANCE.md
        ├── NOT_EVERYTHING_FOR_EVERYONE.md
        ├── TEMPLATE_GUIDE.md
        ├── CROSS_DOMAIN_EXAMPLES.md
        ├── USE_CASES.md
        ├── QUICK_REFERENCE.md
        ├── DATABRICKS_NATIVE_CHECKLIST.md
        ├── IMPLEMENTATION_ROADMAP.md
        └── PROJECT_STRUCTURE.md
```

**Total**: 8 core docs + schemas + archived reference

---

## 📊 Before vs After Consolidation

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Top-level docs** | 5 | 3 | 40% fewer |
| **docs/ directory** | 23 | 5 | 78% fewer |
| **User-facing docs** | 16 | 8 | **50% reduction** |
| **Archived (reference)** | 0 | 9 | Available if needed |

**Result**: **Clearer navigation, less overwhelm, same comprehensive coverage** ✅

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
  → CONFIGURATION.md
    → INTEGRATIONS.md (if needed)
      → ADVANCED_FEATURES.md (if needed)
        → Deploy! 🚀
```

### Optimization & Scaling (ongoing)
```
ADVANCED_FEATURES.md
  → INTEGRATIONS.md#databricks
    → CONFIGURATION.md (advanced settings)
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

✅ **8 core docs** - Down from 16 (50% reduction)  
✅ **Clear decision tree** - Know exactly where to go  
✅ **Experience-level based** - Beginner/Intermediate/Advanced paths  
✅ **Consolidated guides** - INTEGRATIONS.md and ADVANCED_FEATURES.md combine related content  
✅ **Archive available** - Reference material preserved in docs/archive/  

**The framework is easier to navigate while maintaining comprehensive documentation!** 🎯

---

**Ready to start?** → [GETTING_STARTED.md](GETTING_STARTED.md)
