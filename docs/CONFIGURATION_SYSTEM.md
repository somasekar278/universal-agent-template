# Configuration System (Option A)

## Overview

The configuration system enables **plug-and-play agent deployment** - customers can integrate agents into their existing fraud pipelines with minimal code changes.

## Key Benefits

### 1. **Zero Code Changes to Add/Remove Agents**
```yaml
# Enable agent - just set enabled: true
agents:
  narrative:
    enabled: true
    
# Disable for A/B test - just set enabled: false
  narrative:
    enabled: false
```

### 2. **Customer Controls Execution Based on SLA**
```yaml
# Tight SLA (50ms) - inline execution
agents:
  fast_scorer:
    execution_mode: "inline"  # Waits for result
    
# Relaxed SLA - async execution
  narrative:
    execution_mode: "async"  # Doesn't block pipeline
```

### 3. **Pydantic = Type Safety**
- Validates configuration at load time
- Validates data at runtime
- Clear error messages
- Auto-generated documentation

## What We Built

### 1. Configuration Loader (`agents/config.py`)

**Loads agents from YAML/dict:**
```python
from agents import AgentRouter

# From YAML file
router = AgentRouter.from_yaml("config/agents.yaml")

# From dictionary
config = {"agents": {...}}
router = AgentRouter.from_config(config)
```

**Features:**
- ✅ YAML parsing with validation
- ✅ Dynamic class loading
- ✅ Execution mode mapping
- ✅ Error handling with clear messages
- ✅ Supports custom agent config

### 2. Factory Methods (`agents/registry.py`)

**Extended AgentRouter with:**
```python
@classmethod
def from_config(cls, config: Dict) -> "AgentRouter":
    """Create from config dictionary"""

@classmethod
def from_yaml(cls, path: str) -> "AgentRouter":
    """Create from YAML file"""
```

**Benefits:**
- One-line initialization
- No manual registration needed
- Configuration-driven

### 3. Example Configurations

Created three example config files:

#### **Basic Example** (`config/agents/example_basic.yaml`)
- Minimal configuration
- Two agents (inline + async)
- Good starting point

#### **Advanced Example** (`config/agents/example_advanced.yaml`)
- All configuration options
- Multiple execution modes
- Custom agent config
- Enable/disable agents

#### **SLA-Driven Example** (`config/agents/example_customer_sla.yaml`)
- Shows tight vs relaxed SLA configs
- Comments explaining tradeoffs
- Easy to copy/modify

### 4. Integration Example (`examples/plug_and_play_integration.py`)

**Shows:**
- Before/after comparison
- How to add agents to existing pipeline (3 lines!)
- Configuration-driven behavior
- No code changes for different scenarios

## Configuration Format

### Full Configuration Options

```yaml
agents:
  agent_name:
    # REQUIRED
    class: "path.to.AgentClass"  # Python class path
    
    # OPTIONAL
    enabled: true                # Enable/disable (default: true)
    execution_mode: "async"      # How to run (default: ray_task)
    timeout: 30                  # Seconds (default: from agent class)
    retry_policy: "exponential"  # Retry strategy (default: exponential)
    max_retries: 3               # Max attempts (default: 3)
    threshold: 0.7               # When to apply (custom)
    
    # Custom config (passed to agent)
    custom_key: "custom_value"
    another_key: 123
```

### Execution Mode Options

| Mode | Alias | Use Case | Ephemeral? | Bin-Packing? |
|------|-------|----------|------------|--------------|
| `in_process` | `inline` | Fast, inline execution | No | No |
| `process_pool` | `hot_pool` | Multiple agents, bin-packing | Partial | Yes |
| `ray_task` | `async`, `ephemeral` | Distributed, true ephemeral | Yes | Yes |

### Example: Customer Integration

**Step 1: Create config file**
```yaml
# config/my_agents.yaml
agents:
  narrative:
    class: "fraud_agents.NarrativeAgent"
    execution_mode: "async"
    enabled: true
    timeout: 30
```

**Step 2: Add to existing pipeline (3 lines!)**
```python
# In existing Databricks Workflow job
from agents import AgentRouter

# Add this line
router = AgentRouter.from_yaml("config/my_agents.yaml")

# Use in pipeline
result = await router.route("narrative", agent_input)
```

**Step 3: Done!**
- No code changes to enable/disable agents
- No code changes to switch execution modes
- Just edit YAML config

## Integration with Existing Pipelines

### Databricks Workflows

```python
# Job task in Databricks Workflow
def fraud_enrichment_task():
    # Customer's existing code
    df = spark.table("transactions")
    scores = ml_model.predict(df)
    
    # Add agents (3 lines)
    router = AgentRouter.from_yaml("config/agents.yaml")
    enriched = enrich_with_agents(scores, router)
    enriched.write.saveAsTable("enriched_transactions")
```

### Streaming Pipelines

```python
# Real-time processing
async def process_stream():
    # Load agents once
    router = AgentRouter.from_yaml("config/agents.yaml")
    
    # Process stream
    async for transaction in stream:
        agent_input = convert_to_agent_input(transaction)
        
        # Router handles inline vs async based on config!
        result = await router.route("narrative", agent_input)
```

## How Customers Control Behavior

### Scenario 1: Tight SLA (50ms)

**Config:**
```yaml
agents:
  fast_scorer:
    execution_mode: "inline"
    timeout: 0.05  # 50ms strict
```

**Behavior:** Agent runs inline, blocks if needed

### Scenario 2: Relaxed SLA (can wait)

**Config:**
```yaml
agents:
  narrative:
    execution_mode: "async"
    timeout: 30
```

**Behavior:** Agent runs in background, doesn't block

### Scenario 3: A/B Testing

**Config:**
```yaml
agents:
  new_agent:
    enabled: false  # Disable for control group
```

**Behavior:** Agent won't run, no code changes needed

### Scenario 4: Development vs Production

**Development config:**
```yaml
agents:
  narrative:
    execution_mode: "in_process"  # Easy debugging
```

**Production config:**
```yaml
agents:
  narrative:
    execution_mode: "ray_task"  # Distributed, scalable
```

**Same code - different behavior!**

## Architecture Principles Satisfied

| Principle | How We Satisfy It |
|-----------|-------------------|
| **Separation of concerns** | Config separates agent definition from execution |
| **Uniform interface** | All agents loaded via same config format |
| **Pluggable execution** | `execution_mode` in config, no code changes |
| **Async-first** | Default to async, inline is opt-in via config |
| **Lightweight metadata** | Config is metadata, separate from agent code |

## Next Steps

### For Customers:
1. Copy example config (`example_basic.yaml`)
2. Update agent classes to their own agents
3. Set execution modes based on SLA
4. Add one line to existing pipeline: `AgentRouter.from_yaml(...)`

### For Development:
- **Option B**: Integration helpers (`AgentInput.from_spark_row()`)
- **Option C**: Customer examples (before/after templates)
- **Deployment**: Model Serving / Job / App templates

## Summary

✅ **Built:**
- Configuration loader with validation
- Factory methods for one-line initialization
- Three example config files
- Integration example showing plug-and-play

✅ **Enables:**
- Zero code changes to add/remove agents
- Customer controls inline vs async via config
- Type-safe with Pydantic
- Works with existing Databricks Workflows

✅ **Ready for:**
- Customer integration
- A/B testing
- SLA-driven execution
- Development → Production transition

**The foundation for plug-and-play deployment is complete!**

