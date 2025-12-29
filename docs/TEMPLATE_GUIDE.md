# SOTA Agent Framework - Universal Template Guide

## Overview

This framework is designed as a **universal template** for integrating AI agents into any data pipeline or application. Originally built for fraud detection, the architecture is domain-agnostic and works for:

- 🔒 **Fraud Detection** - Transaction monitoring, risk scoring
- 🎯 **Risk Analysis** - Credit risk, compliance monitoring
- 💬 **Customer Support** - Automated responses, ticket routing
- 📝 **Content Moderation** - Text/image review, policy enforcement
- 🏥 **Healthcare** - Diagnosis support, claims processing
- 🔍 **Data Quality** - Anomaly detection, data validation
- 📊 **Analytics** - Report generation, insight extraction
- 🤖 **Any Agent Workflow** - Generic agent orchestration pattern

## Why This Makes a Great Template

### 1. Domain-Agnostic Architecture

```
┌─────────────────────────────────────────────────┐
│            Your Domain-Specific Code            │
│  (fraud agents, support agents, risk agents)    │
├─────────────────────────────────────────────────┤
│           Generic Agent Framework               │
│  • Base classes (Agent, CriticalPath, Enrich)   │
│  • Registry & Router (discovery, execution)     │
│  • Execution backends (in-process, Ray, etc)    │
│  • Configuration system (YAML-driven)           │
│  • Type-safe schemas (Pydantic)                 │
└─────────────────────────────────────────────────┘
```

### 2. Minimal Integration (3 Lines of Code)

```python
# Add to ANY existing pipeline:
from agents import AgentRouter

router = AgentRouter.from_yaml("config/agents.yaml")  # 1. Load
result = await router.route("your_agent", input_data)  # 2. Execute
```

### 3. Configuration-Driven Behavior

```yaml
# No code changes to enable/disable or change execution modes
agents:
  your_agent:
    enabled: true                # Toggle on/off
    execution_mode: "async"      # inline, async, distributed
    timeout: 30                  # SLA control
```

## Template Usage Patterns

### Pattern 1: Critical Path + Enrichment

**Use Case:** Fast decision + detailed explanation

```python
# Critical path agent (<50ms, no LLMs)
class FastRiskScorer(CriticalPathAgent):
    async def score(self, request: AgentInput) -> float:
        # Fast ML model inference
        return calculate_risk_score(request.data)

# Enrichment agent (slower, can use LLMs)
class DetailedNarrative(EnrichmentAgent):
    async def enrich(self, request: AgentInput, risk_score: float) -> str:
        # Generate detailed explanation
        return await llm.generate_narrative(request, risk_score)
```

**Configuration:**
```yaml
agents:
  fast_scorer:
    class: "your_module.FastRiskScorer"
    execution_mode: "inline"  # Critical path
  
  narrative:
    class: "your_module.DetailedNarrative"
    execution_mode: "async"   # Enrichment
```

### Pattern 2: Pipeline Integration

**Use Case:** Add agents to existing Databricks/Spark pipeline

```python
# Existing pipeline
def your_existing_pipeline(spark: SparkSession):
    # Your existing code
    data = spark.table("your_table")
    features = engineer_features(data)
    predictions = ml_model.predict(features)
    
    # Add agents (3 lines!)
    router = AgentRouter.from_yaml("config/agents.yaml")
    enriched = await enrich_with_agents(predictions, router)
    
    # Continue existing code
    enriched.write.saveAsTable("enriched_results")
```

### Pattern 3: Real-Time API

**Use Case:** Agent-powered API endpoints

```python
from fastapi import FastAPI
from agents import AgentRouter

app = FastAPI()
router = AgentRouter.from_yaml("config/agents.yaml")

@app.post("/analyze")
async def analyze(request: YourRequest):
    # Convert to AgentInput
    agent_input = AgentInput(
        request_id=request.id,
        data=request.data
    )
    
    # Route to agent
    result = await router.route("analyzer", agent_input)
    
    return result.dict()
```

### Pattern 4: Event-Driven Processing

**Use Case:** Process messages from queue/stream

```python
import asyncio
from agents import AgentRouter

async def process_events():
    router = AgentRouter.from_yaml("config/agents.yaml")
    
    async for event in event_stream:
        # Convert event to AgentInput
        agent_input = convert_event(event)
        
        # Process with agent
        result = await router.route("processor", agent_input)
        
        # Handle result
        await handle_result(result)
```

## Creating Agents for Your Domain

### Step 1: Define Your Data Schemas

```python
# shared/schemas/your_domain.py
from pydantic import BaseModel
from datetime import datetime

class YourDomainData(BaseModel):
    """Your domain-specific data structure."""
    id: str
    timestamp: datetime
    # ... your fields ...

class YourContext(BaseModel):
    """Additional context for your domain."""
    # ... your context fields ...
```

### Step 2: Create Agent Input/Output

```python
# Extend or use existing AgentInput/AgentOutput
from shared.schemas import AgentInput, AgentOutput

# Option A: Use generic AgentInput
agent_input = AgentInput(
    request_id="req_123",
    data=YourDomainData(**your_data),
    context={"key": "value"}
)

# Option B: Create domain-specific wrapper
class YourAgentInput(AgentInput):
    domain_data: YourDomainData
```

### Step 3: Implement Your Agent

```python
# your_agents/your_agent.py
from agents import Agent, AgentType, ExecutionPriority
from shared.schemas import AgentInput, AgentOutput

class YourAgent(Agent):
    """Your domain-specific agent."""
    
    # Set agent metadata
    agent_type = AgentType.ENRICHMENT
    execution_priority = ExecutionPriority.NORMAL
    timeout_seconds = 30
    
    def __init__(self, config: dict):
        super().__init__(config)
        # Initialize your agent-specific resources
        self.model = load_model(config.get("model_name"))
    
    async def process(self, request: AgentInput) -> AgentOutput:
        """Process request with your logic."""
        
        # Extract your domain data
        domain_data = request.data
        
        # Your processing logic
        result = await self.your_processing_logic(domain_data)
        
        # Return standardized output
        return AgentOutput(
            request_id=request.request_id,
            agent_id=self.agent_id,
            # ... populate fields ...
        )
    
    async def your_processing_logic(self, data):
        """Your domain-specific logic."""
        # Implement your agent's core functionality
        pass
```

### Step 4: Configure Your Agent

```yaml
# config/agents/your_agents.yaml
agents:
  your_agent:
    class: "your_agents.YourAgent"
    enabled: true
    execution_mode: "async"
    timeout: 30
    
    # Your agent-specific config
    model_name: "your-model"
    custom_param: "value"
```

### Step 5: Use in Your Pipeline

```python
from agents import AgentRouter
from shared.schemas import AgentInput

# Load your agents
router = AgentRouter.from_yaml("config/agents/your_agents.yaml")

# Convert your data
agent_input = AgentInput(
    request_id=your_record.id,
    data=your_record.to_dict()
)

# Execute
result = await router.route("your_agent", agent_input)
```

## Template Customization Guide

### Execution Modes

Choose based on your requirements:

| Mode | Use When | SLA | Scalability | Isolation |
|------|----------|-----|-------------|-----------|
| `in_process` | Testing, simple apps | Fastest | Single machine | Low |
| `process_pool` | Multiple agent types | Fast | Multi-core | Medium |
| `ray_task` | Production, scale | Normal | Distributed | High |

### Agent Types

Extend the base classes:

```python
# For fast, critical decisions
class YourCriticalAgent(CriticalPathAgent):
    async def score(self, request: AgentInput) -> float:
        # Must be <50ms!
        return fast_score(request)

# For slower, detailed processing
class YourEnrichmentAgent(EnrichmentAgent):
    async def enrich(self, request: AgentInput, score: float) -> str:
        # Can take longer, use LLMs, etc.
        return await detailed_analysis(request)

# Custom agent type
class YourCustomAgent(Agent):
    async def process(self, request: AgentInput) -> AgentOutput:
        # Your custom processing
        pass
```

### Custom Execution Backends

Add your own execution backend:

```python
# agents/execution/backends.py
from .runner import ExecutionBackend

class YourCustomBackend(ExecutionBackend):
    """Execute agents on your custom infrastructure."""
    
    async def execute(self, agent_class, request, config):
        # Your execution logic
        pass
    
    async def initialize(self):
        # Setup your backend
        pass
    
    async def cleanup(self):
        # Cleanup your backend
        pass
```

## Domain-Specific Examples

### Example 1: Customer Support

```python
# support_agents/ticket_classifier.py
class TicketClassifier(CriticalPathAgent):
    """Fast ticket classification."""
    
    async def score(self, request: AgentInput) -> float:
        ticket = request.data
        # Fast classification model
        category = self.model.predict(ticket.text)
        return category.confidence

class ResponseGenerator(EnrichmentAgent):
    """Generate support response."""
    
    async def enrich(self, request: AgentInput, urgency: float) -> str:
        ticket = request.data
        # LLM-generated response
        return await self.llm.generate_response(ticket, urgency)
```

### Example 2: Content Moderation

```python
# moderation_agents/content_scorer.py
class ContentScorer(CriticalPathAgent):
    """Fast content risk scoring."""
    
    async def score(self, request: AgentInput) -> float:
        content = request.data
        # Fast toxicity/policy check
        return self.toxicity_model.score(content.text)

class DetailedAnalysis(EnrichmentAgent):
    """Detailed policy analysis."""
    
    async def enrich(self, request: AgentInput, risk: float) -> str:
        if risk > 0.8:
            # Only for high-risk content
            return await self.llm.explain_policy_violations(request)
        return "No issues found"
```

### Example 3: Healthcare Diagnosis

```python
# healthcare_agents/diagnosis_support.py
class SymptomAnalyzer(CriticalPathAgent):
    """Fast symptom analysis."""
    
    async def score(self, request: AgentInput) -> float:
        symptoms = request.data
        # Fast triage model
        return self.triage_model.urgency_score(symptoms)

class DiagnosisSuggester(EnrichmentAgent):
    """Detailed diagnosis suggestions."""
    
    async def enrich(self, request: AgentInput, urgency: float) -> str:
        patient_data = request.data
        # Medical LLM for suggestions
        return await self.medical_llm.suggest_diagnosis(patient_data)
```

## Migration Guide

### From Existing System to SOTA Agent Framework

#### Step 1: Audit Current System
```
Current system:
- [ ] Identify agent types (fast vs slow)
- [ ] Document data schemas
- [ ] List execution requirements (SLA, scale)
- [ ] Map existing workflows
```

#### Step 2: Map to Framework
```
Framework mapping:
- [ ] Critical path → CriticalPathAgent
- [ ] Enrichment → EnrichmentAgent
- [ ] Custom logic → Agent subclass
```

#### Step 3: Implement Incrementally
```
Migration approach:
1. Keep existing system running
2. Implement one agent in framework
3. Run in parallel (A/B test)
4. Validate results match
5. Migrate next agent
```

#### Step 4: Configuration Setup
```yaml
# Start with simple config
agents:
  first_agent:
    class: "your_module.FirstAgent"
    execution_mode: "in_process"  # Start simple
    enabled: true
```

#### Step 5: Gradual Rollout
```
Rollout plan:
1. Development environment (in_process)
2. Staging environment (process_pool)
3. Production canary (ray_task, 5% traffic)
4. Full production (ray_task, 100%)
```

## Best Practices

### 1. Separation of Concerns
```
✅ DO: Separate fast scoring from slow enrichment
❌ DON'T: Mix LLM calls in critical path agents
```

### 2. Configuration Over Code
```
✅ DO: Control behavior via YAML config
❌ DON'T: Hard-code execution modes in agent
```

### 3. Type Safety
```
✅ DO: Use Pydantic models for all data
❌ DON'T: Pass unvalidated dictionaries
```

### 4. Error Handling
```python
# Agents should handle errors gracefully
try:
    result = await agent.process(request)
except AgentExecutionError as e:
    logger.error(f"Agent failed: {e}")
    # Fallback logic
```

### 5. Testing
```python
# Test agents independently
@pytest.mark.asyncio
async def test_your_agent():
    agent = YourAgent(config=test_config)
    result = await agent.process(test_input)
    assert result.is_valid()
```

## Template Checklist

Use this checklist when creating a new agent workflow:

### Domain Definition
- [ ] Define data schemas (Pydantic models)
- [ ] Identify agent types (critical vs enrichment)
- [ ] Document SLA requirements
- [ ] Map existing workflows

### Agent Implementation
- [ ] Create agent classes extending base classes
- [ ] Implement process() method
- [ ] Add error handling
- [ ] Write unit tests

### Configuration
- [ ] Create YAML config file
- [ ] Set execution modes based on SLA
- [ ] Configure timeouts and retries
- [ ] Add agent-specific parameters

### Integration
- [ ] Add AgentRouter to pipeline (3 lines!)
- [ ] Convert data to AgentInput
- [ ] Handle AgentOutput
- [ ] Test end-to-end

### Deployment
- [ ] Test in development (in_process)
- [ ] Stage with process_pool
- [ ] Production with Ray (ray_task)
- [ ] Monitor and optimize

## Support & Resources

### Documentation
- [Project Structure](PROJECT_STRUCTURE.md) - Framework overview
- [Configuration System](CONFIGURATION_SYSTEM.md) - Config details
- [Schema Guide](../shared/schemas/README.md) - Data schemas

### Examples
- [Plug and Play Integration](../examples/plug_and_play_integration.py)
- [Example Configs](../config/agents/)
- [Base Agent Classes](../agents/base.py)

### Key Concepts
- **Agent**: Base class for all agents
- **Registry**: Agent discovery and routing
- **Router**: Execute agents based on config
- **Backend**: Pluggable execution engine
- **AgentInput/Output**: Type-safe data contracts

## Contributing Template Improvements

To improve this template:
1. Add domain-specific examples
2. Create scaffolding tools
3. Document edge cases
4. Share integration patterns

## Conclusion

This framework is designed as a **universal template** for agent workflows. The architecture is proven, flexible, and production-ready. Whether you're building fraud detection, customer support, content moderation, or any other agent-powered system, this template provides:

✅ Minimal integration (3 lines)  
✅ Configuration-driven behavior  
✅ SLA-aware execution  
✅ Type-safe data handling  
✅ Production-ready patterns  
✅ Domain-agnostic design  

**Start building your agent workflow today!**

