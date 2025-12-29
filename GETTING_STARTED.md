# Getting Started with SOTA Agent Framework

**Build AI agent workflows for any domain in 5 minutes.**

## What Is This?

A universal template for integrating AI agents into applications and data pipelines.

**Works for:** Fraud detection • Customer support • Content moderation • Healthcare • Data quality • Security • **Any domain**

## Quick Start (Choose One)

### Option 1: Generate New Project (Fastest)

```bash
# 1. Generate project for your domain
python template_generator.py --domain "your_domain" --output ./my-agents

# 2. Navigate and install
cd my-agents
pip install -r requirements.txt

# 3. Implement your logic
# Edit your_domain/agents.py (replace TODOs with your code)

# 4. Run
python examples/example_usage.py
```

**Time: 5-10 minutes**

### Option 2: Integrate Into Existing Code

```python
# Add to your existing pipeline (3 lines!)
from agents import AgentRouter

router = AgentRouter.from_yaml("config/agents.yaml")
result = await router.route("your_agent", input_data)
```

**Time: 5 minutes**

## Template Generator

### Basic Usage

```bash
python template_generator.py --domain "customer_support"
```

This creates:
- ✅ Agent implementation template
- ✅ Configuration file
- ✅ Unit tests
- ✅ Usage examples
- ✅ Documentation

### Advanced Options

```bash
python template_generator.py \
  --domain "content_moderation" \
  --output ./moderation-agents \
  --agent-type "CRITICAL_PATH" \
  --priority "HIGH" \
  --timeout 5 \
  --execution-mode "in_process"
```

| Parameter | Options | Default |
|-----------|---------|---------|
| `--domain` | any_string | **required** |
| `--output` | path | `./generated_agent_project` |
| `--agent-type` | CRITICAL_PATH, ENRICHMENT, ORCHESTRATION | ENRICHMENT |
| `--priority` | CRITICAL, HIGH, NORMAL, LOW | NORMAL |
| `--timeout` | seconds | 30 |
| `--execution-mode` | in_process, process_pool, ray_task | ray_task |

## Next Steps

### 1. Learn the Patterns

Read the [Template Guide](docs/TEMPLATE_GUIDE.md) to understand:
- Agent types (Critical vs Enrichment)
- Execution modes (inline vs distributed)
- Configuration patterns
- Integration approaches

### 2. See Examples

Check [Cross-Domain Examples](docs/CROSS_DOMAIN_EXAMPLES.md) for complete examples in:
- Fraud detection
- Customer support
- Content moderation
- Healthcare diagnosis
- Data quality monitoring
- E-commerce recommendations
- Legal document review
- Security threat detection

### 3. Build Your Agent

After generating your project, focus on:

#### Edit Agent Logic
```python
# your_domain/agents.py
async def process(self, request: AgentInput) -> AgentOutput:
    # Replace TODOs with your logic
    data = request.data
    result = await your_processing_logic(data)
    return AgentOutput(...)
```

#### Configure Behavior
```yaml
# config/your_domain_config.yaml
agents:
  your_agent:
    enabled: true
    execution_mode: "in_process"  # or ray_task for distributed
    timeout: 30
```

#### Test
```bash
pytest tests/
python examples/example_usage.py
```

## Key Concepts

### Agent Types

**CriticalPathAgent** - Fast (< 50ms), no LLMs, quick decisions
```python
class FastScorer(CriticalPathAgent):
    async def score(self, request: AgentInput) -> float:
        return fast_ml_model.predict(request.data)
```

**EnrichmentAgent** - Slower, can use LLMs, detailed analysis
```python
class Narrator(EnrichmentAgent):
    async def enrich(self, request: AgentInput, score: float) -> str:
        return await llm.generate_narrative(request, score)
```

### Execution Modes

| Mode | Use When | Speed | Scale |
|------|----------|-------|-------|
| `in_process` | Development, testing | Fastest | Single machine |
| `process_pool` | Multiple agents, bin-packing | Fast | Multi-core |
| `ray_task` | Production, distributed | Normal | Auto-scaling cluster |

### Configuration Pattern

```yaml
# Control everything via config - zero code changes!
agents:
  your_agent:
    class: "your_module.YourAgent"
    enabled: true              # Toggle on/off
    execution_mode: "async"    # Change execution
    timeout: 30                # Set SLA
```

## Common Patterns

### Pattern 1: Fast Decision + Detailed Explanation

```python
# Critical path: Quick risk score
result = await router.route("fast_scorer", input)

if result.risk_score > 0.7:
    # Enrichment: Detailed narrative (async)
    narrative = await router.route("narrator", input)
```

### Pattern 2: Pipeline Integration

```python
# Your existing Databricks/Spark pipeline
def your_pipeline(data):
    features = engineer_features(data)
    predictions = ml_model.predict(features)
    
    # Add agents (3 lines!)
    router = AgentRouter.from_yaml("config/agents.yaml")
    enriched = await enrich_with_agents(predictions, router)
    
    return enriched
```

### Pattern 3: Real-Time API

```python
from fastapi import FastAPI

app = FastAPI()
router = AgentRouter.from_yaml("config/agents.yaml")

@app.post("/analyze")
async def analyze(request: YourRequest):
    result = await router.route("analyzer", to_agent_input(request))
    return result.dict()
```

## Troubleshooting

### Generator Issues
```bash
# Check syntax
python template_generator.py --help

# Use absolute paths
python template_generator.py --domain "test" --output /tmp/test
```

### Import Errors
```bash
# Install dependencies
pip install -r requirements.txt

# Make sure you're in the right directory
cd your-project-root
```

### Configuration Issues
```bash
# Validate YAML
python -c "import yaml; print(yaml.safe_load(open('config/your_config.yaml')))"
```

## Examples by Domain

```bash
# Customer support
python template_generator.py --domain "customer_support"

# Content moderation  
python template_generator.py --domain "content_moderation" --agent-type "CRITICAL_PATH"

# Healthcare
python template_generator.py --domain "healthcare_triage"

# Fraud detection
python template_generator.py --domain "fraud_detection"
```

## Documentation

| Document | Purpose |
|----------|---------|
| **[docs/README.md](docs/README.md)** | Documentation index |
| **[docs/TEMPLATE_GUIDE.md](docs/TEMPLATE_GUIDE.md)** | Comprehensive guide |
| **[docs/CROSS_DOMAIN_EXAMPLES.md](docs/CROSS_DOMAIN_EXAMPLES.md)** | 8 domain examples |
| **[docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md)** | Code organization |
| **[docs/CONFIGURATION_SYSTEM.md](docs/CONFIGURATION_SYSTEM.md)** | Configuration details |

## Resources

- **Core Framework**: `agents/` - Base classes and execution
- **Config Examples**: `config/agents/` - Sample configurations
- **Integration Example**: `examples/plug_and_play_integration.py`
- **Schemas**: `shared/schemas/` - Data models

## Summary

**To get started:**

1. Generate project: `python template_generator.py --domain "your_domain"`
2. Implement logic: Edit `your_domain/agents.py`
3. Configure: Edit `config/your_domain_config.yaml`
4. Run: `python examples/example_usage.py`

**That's it!** You now have a production-ready agent workflow.

**Need help?** Check [docs/README.md](docs/README.md) for detailed guides.

---

**Ready to build?** Run the generator now:

```bash
python template_generator.py --domain "your_domain"
```

🚀 **Start building agent workflows in 5 minutes!**

