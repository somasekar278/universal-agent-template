# Learning Path Schemas Guide

**Domain-agnostic schemas for building agents across any use case**

---

## Overview

The learning path schemas (`shared/schemas/learning.py`) provide **generic, reusable data models** that work across different domains and use cases. Unlike the fraud-specific schemas, these are designed for flexibility and broad applicability.

**Key Benefits:**
- ✅ **Domain-agnostic** - Work for chatbots, APIs, workflows, multi-agent systems
- ✅ **Type-safe** - Full Pydantic validation
- ✅ **Level-matched** - Designed specifically for each learning level
- ✅ **Production-ready** - Not just for learning, use in real applications!

---

## Schema by Learning Level

### 📚 Level 1: Simple Chatbot

**Input Schema: `ChatInput`**

```python
from shared.schemas.learning import ChatInput, ChatOutput

# Input
request = ChatInput(
    question="How do I reset my password?",
    user_id="user_123",
    session_id="session_456",  # Optional
    context={"channel": "web"}  # Optional
)
```

**Output Schema: `ChatOutput`**

```python
# Output
response = ChatOutput(
    answer="To reset your password, click 'Forgot Password' on the login page.",
    confidence=0.95,
    sources=["knowledge_base", "faq"],
    metadata={"response_time_ms": 150}
)
```

**Use Cases:**
- FAQ bots
- Customer support chatbots
- Technical assistants
- General Q&A systems

---

### 📚 Level 2: Context-Aware Agent

**Input Schema: `ContextAwareInput`**

```python
from shared.schemas.learning import ContextAwareInput, ContextAwareOutput

# Input with conversation history
request = ContextAwareInput(
    message="What about the other option?",
    user_id="user_123",
    session_id="session_456",
    conversation_history=[
        {"role": "user", "content": "Should I upgrade?"},
        {"role": "assistant", "content": "There are two options..."}
    ],
    retrieve_context=True,
    max_context_items=5
)
```

**Output Schema: `ContextAwareOutput`**

```python
# Output
response = ContextAwareOutput(
    response="The other option includes...",
    confidence=0.88,
    context_used=["previous_discussion_about_upgrade"],
    stored_to_memory=True,
    memory_summary="Stored preference for upgrade discussion"
)
```

**Use Cases:**
- Conversational AI with memory
- Multi-turn dialogues
- Personalized assistants
- Context-aware support systems

---

### 📚 Level 3: Production API

**Input Schema: `APIRequest`**

```python
from shared.schemas.learning import APIRequest, APIResponse, HealthCheckResponse

# Generic API request
request = APIRequest(
    endpoint="analyze",
    data={"text": "Sample text to analyze"},
    user_id="user_123",
    request_id="req_abc123",
    metadata={"priority": "high"}
)
```

**Output Schema: `APIResponse`**

```python
# API response
response = APIResponse(
    success=True,
    data={"sentiment": "positive", "score": 0.85},
    request_id="req_abc123",
    processing_time_ms=45.3,
    metadata={"model_version": "v1.2"}
)
```

**Health Check Schema: `HealthCheckResponse`**

```python
# Health check
health = HealthCheckResponse(
    status="healthy",
    version="1.0.0",
    checks={
        "database": True,
        "cache": True,
        "model": True
    }
)
```

**Use Cases:**
- Production REST APIs
- Microservices
- Data processing APIs
- ML model serving

---

### 📚 Level 4: Complex Workflow

**Input Schema: `WorkflowInput`**

```python
from shared.schemas.learning import (
    WorkflowInput,
    WorkflowOutput,
    TaskStep,
    TaskStatus
)

# Complex workflow with Plan-Act-Critique
request = WorkflowInput(
    objective="Analyze customer feedback and generate insights",
    context={
        "data_source": "feedback_db",
        "time_range": "last_30_days"
    },
    constraints={"max_time_seconds": 300, "min_quality": 0.8},
    max_iterations=5,
    require_critique=True
)
```

**Output Schema: `WorkflowOutput`**

```python
# Workflow results
response = WorkflowOutput(
    objective="Analyze customer feedback and generate insights",
    plan=[
        TaskStep(
            step_id="step_1",
            action="fetch_data",
            status=TaskStatus.COMPLETED,
            result={"records": 1250}
        ),
        TaskStep(
            step_id="step_2",
            action="analyze_sentiment",
            dependencies=["step_1"],
            status=TaskStatus.COMPLETED,
            result={"positive": 0.65}
        )
    ],
    execution_results={"overall": "success"},
    critiques=["Consider expanding time range"],
    final_status=TaskStatus.COMPLETED,
    iterations=2,
    total_time_seconds=45.2,
    optimizations_applied=["prompt_optimization", "batch_processing"]
)
```

**Task Status Enum:**

```python
class TaskStatus(str, Enum):
    PENDING = "pending"
    PLANNING = "planning"
    EXECUTING = "executing"
    CRITIQUING = "critiquing"
    REPLANNING = "replanning"
    COMPLETED = "completed"
    FAILED = "failed"
```

**Use Cases:**
- Multi-step workflows
- Plan-Act-Critique loops
- Complex analysis pipelines
- Autonomous task execution

---

### 📚 Level 5: Multi-Agent Collaboration

**Input Schema: `CollaborationRequest`**

```python
from shared.schemas.learning import (
    CollaborationRequest,
    CollaborationResponse,
    AgentCapabilityInfo
)

# Multi-agent collaboration
request = CollaborationRequest(
    task_id="task_789",
    initiating_agent="coordinator",
    required_capabilities=["data_analysis", "visualization", "reporting"],
    task_data={"dataset": "sales_2024", "format": "quarterly"},
    collaboration_mode="parallel",  # or "sequential", "consensus"
    timeout_seconds=120.0,
    use_a2a=True  # Use A2A protocol for external agents
)
```

**Output Schema: `CollaborationResponse`**

```python
# Collaboration results
response = CollaborationResponse(
    task_id="task_789",
    participating_agents=["analyzer", "visualizer", "reporter"],
    individual_results={
        "analyzer": {"insights": 15, "trends": 3},
        "visualizer": {"charts": 5},
        "reporter": {"report_url": "..."}
    },
    aggregated_result={
        "report": "Quarterly Sales Analysis",
        "key_insights": ["..."],
        "visualizations": ["..."]
    },
    consensus_reached=True,
    collaboration_time_seconds=67.5,
    a2a_agents_used=["external_forecaster"]
)
```

**Agent Capability Schema: `AgentCapabilityInfo`**

```python
# Describe agent capabilities
capability = AgentCapabilityInfo(
    agent_id="agent_001",
    agent_name="DataAnalyzer",
    capabilities=["data_analysis", "statistics", "ml_prediction"],
    availability=0.95,
    performance_score=0.87
)
```

**Use Cases:**
- Multi-agent systems
- Agent marketplaces
- Cross-framework collaboration (A2A)
- Distributed agent orchestration

---

## Universal Schemas

For maximum flexibility when you don't know the specific level or want to support multiple levels:

### `UniversalInput`

```python
from shared.schemas.learning import UniversalInput, UniversalOutput

# Flexible input for any level
request = UniversalInput(
    data={
        "type": "analysis",
        "payload": {"text": "..."}
    },
    user_id="user_123",
    request_id="req_456",
    agent_level=3,  # Optional: hint which level
    metadata={"source": "api"}
)
```

### `UniversalOutput`

```python
# Flexible output for any level
response = UniversalOutput(
    result={
        "type": "analysis_complete",
        "data": {"sentiment": "positive"}
    },
    success=True,
    confidence=0.85,
    metadata={"processed_by": "agent_v1"}
)
```

---

## Helper Functions

### Get Schema for Level

```python
from shared.schemas.learning import (
    get_input_schema_for_level,
    get_output_schema_for_level
)

# Dynamically get schema for a level
InputSchema = get_input_schema_for_level(3)  # Returns APIRequest
OutputSchema = get_output_schema_for_level(3)  # Returns APIResponse

# Use in agent
request = InputSchema(
    endpoint="classify",
    data={"text": "..."},
    request_id="req_123"
)
```

**Supported Levels:**
- Level 1 → `ChatInput`, `ChatOutput`
- Level 2 → `ContextAwareInput`, `ContextAwareOutput`
- Level 3 → `APIRequest`, `APIResponse`
- Level 4 → `WorkflowInput`, `WorkflowOutput`
- Level 5 → `CollaborationRequest`, `CollaborationResponse`
- Default → `UniversalInput`, `UniversalOutput`

---

## Migration from Domain-Specific Schemas

### Before (Fraud-Specific)

```python
from shared.schemas import Transaction, FraudSignals

# Tightly coupled to fraud domain
transaction = Transaction(
    amount=1000.0,
    merchant_id="merchant_123",
    # ... fraud-specific fields
)
```

### After (Generic)

```python
from shared.schemas.learning import APIRequest

# Works for ANY domain
request = APIRequest(
    endpoint="analyze",
    data={
        "amount": 1000.0,
        "merchant_id": "merchant_123",
        # ... any fields you need
    },
    request_id="req_123"
)
```

**Benefits:**
- ✅ Reusable across domains (fraud, support, analytics, etc.)
- ✅ Easier to learn and understand
- ✅ More flexible for different use cases

---

## Best Practices

### 1. **Match Schema to Level**

Use the appropriate schema for your learning level:

```python
# Level 1: Keep it simple
from shared.schemas.learning import ChatInput, ChatOutput

# Level 5: Use collaboration schemas
from shared.schemas.learning import CollaborationRequest, CollaborationResponse
```

### 2. **Extend with Domain Logic**

Inherit from generic schemas to add domain-specific fields:

```python
from shared.schemas.learning import APIRequest

class CustomerSupportRequest(APIRequest):
    """Extend generic schema with domain fields."""
    ticket_id: str
    priority: str
    category: str
```

### 3. **Use Universal for Unknown Levels**

When building flexible agents:

```python
from shared.schemas.learning import UniversalInput

def flexible_agent(request: UniversalInput):
    # Handle any level
    level = request.agent_level or 1
    # ... process based on level
```

### 4. **Validate Data**

Pydantic handles validation automatically:

```python
from shared.schemas.learning import ChatInput

try:
    request = ChatInput(
        question="Hello",
        user_id="user_123"
    )
except ValidationError as e:
    print(f"Invalid input: {e}")
```

---

## Examples

### Complete Example: Level 1 Agent

```python
from agents.base import Agent
from shared.schemas.learning import ChatInput, ChatOutput

class SimpleChatbot(Agent):
    async def process(self, request: ChatInput) -> ChatOutput:
        # Use generic schemas!
        answer = f"You asked: {request.question}"
        
        return ChatOutput(
            answer=answer,
            confidence=0.9,
            sources=["rule_engine"]
        )
```

### Complete Example: Level 4 Workflow

```python
from agents.base import Agent
from shared.schemas.learning import WorkflowInput, WorkflowOutput, TaskStep, TaskStatus

class WorkflowAgent(Agent):
    async def process(self, request: WorkflowInput) -> WorkflowOutput:
        # Create plan
        plan = [
            TaskStep(step_id="1", action="analyze", status=TaskStatus.PENDING),
            TaskStep(step_id="2", action="report", status=TaskStatus.PENDING)
        ]
        
        # Execute...
        
        return WorkflowOutput(
            objective=request.objective,
            plan=plan,
            execution_results={},
            final_status=TaskStatus.COMPLETED,
            iterations=1,
            total_time_seconds=10.5
        )
```

---

## Reference

**Schema File:** `shared/schemas/learning.py`  
**Example Agents:** `examples/learning_agents_generic.py`  
**Learning Path:** `docs/LEARNING_PATH.md`

**All Schemas:**
- `ChatInput`, `ChatOutput` (Level 1)
- `ContextAwareInput`, `ContextAwareOutput` (Level 2)
- `APIRequest`, `APIResponse`, `HealthCheckResponse` (Level 3)
- `WorkflowInput`, `WorkflowOutput`, `TaskStep`, `TaskStatus` (Level 4)
- `CollaborationRequest`, `CollaborationResponse`, `AgentCapabilityInfo` (Level 5)
- `UniversalInput`, `UniversalOutput` (All Levels)
- `get_input_schema_for_level()`, `get_output_schema_for_level()` (Helpers)

---

**🎯 These schemas enable you to build agents for ANY domain, not just fraud detection!**

