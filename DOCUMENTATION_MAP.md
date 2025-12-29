# Documentation Map

**Quick reference to all documentation in the SOTA Agent Framework.**

## 🚀 Getting Started (Read These First)

1. **[README.md](README.md)** - Project overview and features
2. **[GETTING_STARTED.md](GETTING_STARTED.md)** - 5-minute quick start guide
3. **[docs/TEMPLATE_GUIDE.md](docs/TEMPLATE_GUIDE.md)** - Comprehensive template usage guide

## 📖 User Documentation

### Essential Guides
- **[Getting Started](GETTING_STARTED.md)** - Quick start in 5 minutes
- **[Template Guide](docs/TEMPLATE_GUIDE.md)** - Complete guide for any domain
- **[Cross-Domain Examples](docs/CROSS_DOMAIN_EXAMPLES.md)** - 8 real-world domain examples
- **[Documentation Index](docs/README.md)** - Main documentation hub

### Core Framework
- **[Project Structure](docs/PROJECT_STRUCTURE.md)** - Code organization
- **[Configuration System](docs/CONFIGURATION_SYSTEM.md)** - YAML configuration
- **[Use Cases](docs/USE_CASES.md)** - Advanced patterns

### Deployment
- **[Databricks Native Checklist](docs/DATABRICKS_NATIVE_CHECKLIST.md)** - Databricks deployment
- **[Implementation Roadmap](docs/IMPLEMENTATION_ROADMAP.md)** - Development phases

### Schema Documentation
- **[Schema Summary](docs/schemas/01_DATA_SCHEMAS_SUMMARY.md)** - Overview of schemas
- **[Schema Mapping](docs/schemas/02_SCHEMA_MAPPING.md)** - Mapping guide
- **[Schema Adaptation](docs/schemas/03_SCHEMA_ADAPTATION_GUIDE.md)** - Multi-tenant adaptation
- **[Schema Versioning](docs/schemas/04_SCHEMA_VERSIONING_GUIDE.md)** - Version management
- **[Schemas Quick Reference](docs/schemas/SCHEMAS_QUICK_REFERENCE.md)** - Quick lookup
- **[Schema Versioning Quick Start](docs/schemas/SCHEMA_VERSIONING_QUICK_START.md)** - Quick guide

### Component READMEs
- **[MCP Servers](mcp-servers/README.md)** - Model Context Protocol servers
- **[Shared Schemas](shared/schemas/README.md)** - Core data schemas

## 🗂️ Documentation Structure

```
.
├── README.md                     # Main project overview
├── GETTING_STARTED.md            # Quick start guide
├── DOCUMENTATION_MAP.md          # This file
│
└── docs/
    ├── README.md                 # Documentation hub
    ├── TEMPLATE_GUIDE.md         # Complete template guide
    ├── CROSS_DOMAIN_EXAMPLES.md  # 8 domain examples
    ├── PROJECT_STRUCTURE.md      # Code organization
    ├── CONFIGURATION_SYSTEM.md   # Configuration guide
    ├── USE_CASES.md              # Advanced patterns
    ├── DATABRICKS_NATIVE_CHECKLIST.md
    ├── IMPLEMENTATION_ROADMAP.md
    │
    ├── schemas/                  # Schema documentation
    │   ├── 01_DATA_SCHEMAS_SUMMARY.md
    │   ├── 02_SCHEMA_MAPPING.md
    │   ├── 03_SCHEMA_ADAPTATION_GUIDE.md
    │   ├── 04_SCHEMA_VERSIONING_GUIDE.md
    │   ├── SCHEMAS_QUICK_REFERENCE.md
    │   └── SCHEMA_VERSIONING_QUICK_START.md
    │
    └── archive/                  # Historical/internal docs
```

## 🎯 Find What You Need

| I want to... | Read this... |
|--------------|--------------|
| **Get started quickly** | [GETTING_STARTED.md](GETTING_STARTED.md) |
| **Generate a project** | [TEMPLATE_GUIDE.md](docs/TEMPLATE_GUIDE.md) |
| **See examples in my domain** | [CROSS_DOMAIN_EXAMPLES.md](docs/CROSS_DOMAIN_EXAMPLES.md) |
| **Understand the code structure** | [PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md) |
| **Configure agents** | [CONFIGURATION_SYSTEM.md](docs/CONFIGURATION_SYSTEM.md) |
| **Adapt data schemas** | [Schema Adaptation](docs/schemas/03_SCHEMA_ADAPTATION_GUIDE.md) |
| **Deploy to Databricks** | [DATABRICKS_NATIVE_CHECKLIST.md](docs/DATABRICKS_NATIVE_CHECKLIST.md) |
| **See advanced patterns** | [USE_CASES.md](docs/USE_CASES.md) |
| **Browse all docs** | [docs/README.md](docs/README.md) |

## 📚 Reading Order

### For Beginners
1. [README.md](README.md) - 2 minutes
2. [GETTING_STARTED.md](GETTING_STARTED.md) - 5 minutes
3. [TEMPLATE_GUIDE.md](docs/TEMPLATE_GUIDE.md) - 15 minutes
4. [CROSS_DOMAIN_EXAMPLES.md](docs/CROSS_DOMAIN_EXAMPLES.md) - Browse for your domain

### For Developers
1. [PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md)
2. [CONFIGURATION_SYSTEM.md](docs/CONFIGURATION_SYSTEM.md)
3. [Schema Documentation](docs/schemas/01_DATA_SCHEMAS_SUMMARY.md)

### For DevOps/Deployment
1. [IMPLEMENTATION_ROADMAP.md](docs/IMPLEMENTATION_ROADMAP.md)
2. [DATABRICKS_NATIVE_CHECKLIST.md](docs/DATABRICKS_NATIVE_CHECKLIST.md)
3. [CONFIGURATION_SYSTEM.md](docs/CONFIGURATION_SYSTEM.md)

## 🛠️ Code Examples

- **Integration Examples**: `examples/plug_and_play_integration.py`
- **Config Examples**: `config/agents/*.yaml`
- **Test Examples**: `tests/`
- **Agent Base Classes**: `agents/base.py`

## 📞 Need Help?

1. Check [GETTING_STARTED.md](GETTING_STARTED.md)
2. Browse [docs/README.md](docs/README.md)
3. See [CROSS_DOMAIN_EXAMPLES.md](docs/CROSS_DOMAIN_EXAMPLES.md) for examples
4. File a GitHub issue

---

**Ready to start?** → [GETTING_STARTED.md](GETTING_STARTED.md)