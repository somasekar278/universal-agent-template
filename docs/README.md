# SOTA Agent Framework - Documentation

**Complete guide to using SOTA Agent Framework as a universal template for AI agent workflows.**

## 🚀 Quick Start (Choose Your Path)

### For First-Time Users
1. **[Quick Start Guide](../GETTING_STARTED.md)** ⭐ - Start here! 5-minute guide
2. **[Template Guide](TEMPLATE_GUIDE.md)** - Comprehensive usage guide
3. **[Examples](CROSS_DOMAIN_EXAMPLES.md)** - 8 real-world domain examples

### For Developers
- **[Project Structure](PROJECT_STRUCTURE.md)** - Code organization
- **[Configuration System](CONFIGURATION_SYSTEM.md)** - YAML configuration guide
- **[Implementation Roadmap](IMPLEMENTATION_ROADMAP.md)** - Development phases

### For Advanced Users
- **[Schema Documentation](schemas/)** - Data schemas and adaptation
- **[Use Cases](USE_CASES.md)** - Advanced usage patterns
- **[Databricks Deployment](DATABRICKS_NATIVE_CHECKLIST.md)** - Databricks-specific guide

## 📚 Documentation Structure

```
docs/
├── README.md (this file)           # Documentation index
├── TEMPLATE_GUIDE.md               # Complete template guide
├── CROSS_DOMAIN_EXAMPLES.md        # 8 domain examples
├── PROJECT_STRUCTURE.md            # Code organization
├── CONFIGURATION_SYSTEM.md         # Configuration guide
├── IMPLEMENTATION_ROADMAP.md       # Development phases
├── USE_CASES.md                    # Advanced patterns
├── DATABRICKS_NATIVE_CHECKLIST.md  # Databricks deployment
└── schemas/                        # Schema documentation
    ├── 01_DATA_SCHEMAS_SUMMARY.md
    ├── 02_SCHEMA_MAPPING.md
    ├── 03_SCHEMA_ADAPTATION_GUIDE.md
    ├── 04_SCHEMA_VERSIONING_GUIDE.md
    ├── SCHEMAS_QUICK_REFERENCE.md
    └── SCHEMA_VERSIONING_QUICK_START.md
```

## 🎯 Common Use Cases

### I want to create a new agent workflow
→ Read [Getting Started](../GETTING_STARTED.md), then use the template generator:
```bash
python template_generator.py --domain "your_domain"
```

### I want to integrate agents into existing pipeline
→ Read [Configuration System](CONFIGURATION_SYSTEM.md), then:
```python
from agents import AgentRouter
router = AgentRouter.from_yaml("config/agents.yaml")
result = await router.route("agent", input)
```

### I want to see examples in my domain
→ Check [Cross-Domain Examples](CROSS_DOMAIN_EXAMPLES.md) for 8 different domains

### I want to understand the architecture
→ Read [Template Guide](TEMPLATE_GUIDE.md) and [Project Structure](PROJECT_STRUCTURE.md)

### I want to customize schemas for my data
→ See [Schema Adaptation Guide](schemas/03_SCHEMA_ADAPTATION_GUIDE.md)

### I want to deploy to Databricks
→ Follow [Databricks Native Checklist](DATABRICKS_NATIVE_CHECKLIST.md)

## 📖 Learning Path

### Beginner Path
1. [Getting Started](../GETTING_STARTED.md) - 5 minutes
2. [Template Guide](TEMPLATE_GUIDE.md) - 15 minutes
3. Generate your first project - 5 minutes
4. [Examples](CROSS_DOMAIN_EXAMPLES.md) - Browse for your domain

### Intermediate Path
1. [Project Structure](PROJECT_STRUCTURE.md)
2. [Configuration System](CONFIGURATION_SYSTEM.md)
3. [Schema Documentation](schemas/01_DATA_SCHEMAS_SUMMARY.md)
4. Build and deploy your agents

### Advanced Path
1. [Use Cases](USE_CASES.md)
2. [Schema Adaptation](schemas/03_SCHEMA_ADAPTATION_GUIDE.md)
3. [Schema Versioning](schemas/04_SCHEMA_VERSIONING_GUIDE.md)
4. Extend the framework for your needs

## 🛠️ Template Generator

Quick reference for the template generator:

```bash
# Basic usage
python template_generator.py --domain "customer_support"

# Advanced usage
python template_generator.py \
  --domain "content_moderation" \
  --output ./my-agents \
  --agent-type "CRITICAL_PATH" \
  --execution-mode "in_process"
```

See [Template Guide](TEMPLATE_GUIDE.md) for full details.

## 📦 What's Included

| Component | Description | Documentation |
|-----------|-------------|---------------|
| **Base Framework** | Agent classes, registry, execution | [Project Structure](PROJECT_STRUCTURE.md) |
| **Template Generator** | Scaffold new projects | [Template Guide](TEMPLATE_GUIDE.md) |
| **Configuration System** | YAML-driven behavior | [Configuration System](CONFIGURATION_SYSTEM.md) |
| **Type-Safe Schemas** | Pydantic data models | [Schema Docs](schemas/) |
| **Execution Backends** | In-process, Ray, serverless | [Template Guide](TEMPLATE_GUIDE.md) |
| **Examples** | 8 domain examples | [Examples](CROSS_DOMAIN_EXAMPLES.md) |

## 🔍 Find What You Need

| I need to... | Go to... |
|--------------|----------|
| Get started quickly | [Getting Started](../GETTING_STARTED.md) |
| Generate a project | [Template Guide](TEMPLATE_GUIDE.md) |
| See examples | [Cross-Domain Examples](CROSS_DOMAIN_EXAMPLES.md) |
| Understand architecture | [Project Structure](PROJECT_STRUCTURE.md) |
| Configure agents | [Configuration System](CONFIGURATION_SYSTEM.md) |
| Adapt data schemas | [Schema Adaptation](schemas/03_SCHEMA_ADAPTATION_GUIDE.md) |
| Deploy to production | [Databricks Checklist](DATABRICKS_NATIVE_CHECKLIST.md) |
| Explore use cases | [Use Cases](USE_CASES.md) |

## 📞 Support

- **Questions**: Check documentation above
- **Issues**: File a GitHub issue
- **Examples**: See [Cross-Domain Examples](CROSS_DOMAIN_EXAMPLES.md)

## 🎓 Additional Resources

- **Code Examples**: `examples/` directory
- **Configuration Examples**: `config/agents/` directory
- **Test Examples**: `tests/` directory
- **MCP Servers**: `mcp-servers/README.md`

---

**Ready to build? Start with [Getting Started](../GETTING_STARTED.md)!** 🚀

