# Schemas Quick Reference

Quick lookup guide for all available schemas and their usage.

## Import Patterns

```python
# All schemas available from root
from shared.schemas import (
    # Your data structures
    NestedTransaction,
    MCPToolResults,
    MerchantContextWithEmbedding,
    ConversationHistory,
    DSPyOptimizerMetadata,
    StreamingOutput,
    
    # Core schemas
    Transaction, AgentInput, AgentOutput,
    FraudSignals, EvaluationRecord, TelemetryEvent,
)
```

## Schema Categories

### 📥 **Input Data (What Comes In)**

| Schema | File | Use For |
|--------|------|---------|
| `NestedTransaction` | `nested_transaction.py` | Raw transaction events from payment system |
| `PaymentMethodDetails` | `nested_transaction.py` | Card BIN, last4, issuer details |
| `CustomerDetails` | `nested_transaction.py` | Customer account info in event |
| `MerchantDetails` | `nested_transaction.py` | Merchant info in event |
| `DeviceDetails` | `nested_transaction.py` | Device fingerprint, IP, VPN detection |

**Example:**
```python
event = NestedTransaction.model_validate_json(kafka_message)
```

---

### 🔧 **MCP Tool Results (External Enrichment)**

| Schema | File | Tool Server |
|--------|------|-------------|
| `BINLookupResult` | `mcp_tools.py` | `enrichment-server` |
| `IPGeoLookupResult` | `mcp_tools.py` | `enrichment-server` |
| `SanctionsCheckResult` | `mcp_tools.py` | `enrichment-server` |
| `VelocityAnomalyResult` | `mcp_tools.py` | `risk-calculation-server` |
| `MCPToolResults` | `mcp_tools.py` | Aggregated results |

**Example:**
```python
bin_result = BINLookupResult(
    bin="559021", issuer="Bank", country="NG", risk_level=0.91
)
```

---

### 🧠 **Memory & Embeddings (Lakebase)**

| Schema | File | Use For |
|--------|------|---------|
| `Embedding` | `embeddings.py` | Vector representations (768/1536 dim) |
| `ConversationMessage` | `embeddings.py` | Individual message with embedding |
| `ConversationHistory` | `embeddings.py` | Complete agent conversation |
| `MerchantContextWithEmbedding` | `embeddings.py` | Merchant profile + vector |
| `CustomerContextWithEmbedding` | `embeddings.py` | Customer profile + vector |
| `SimilarCaseResult` | `embeddings.py` | Retrieved similar fraud cases |

**Example:**
```python
# Store in Lakebase
conversation = ConversationHistory(
    agent_id="agent_001",
    messages=[
        ConversationMessage(
            content="BIN mismatch detected",
            embedding=Embedding(vector=[...], dimension=1536)
        )
    ]
)
```

---

### 🤖 **Agent Execution (Runtime)**

| Schema | File | Use For |
|--------|------|---------|
| `AgentInput` | `agent_io.py` | Complete input to agent |
| `AgentOutput` | `agent_io.py` | Agent's decision + narrative |
| `ToolCall` | `agent_io.py` | MCP tool invocation |
| `ToolResult` | `agent_io.py` | Tool execution result |
| `ReasoningStep` | `agent_io.py` | Chain-of-thought trace |
| `AgentAction` | `agent_io.py` | Enum: approve/decline/review |

**Example:**
```python
output = AgentOutput(
    request_id="req_001",
    agent_id="agent_narrative_1",
    risk_narrative="High velocity detected...",
    recommended_action=AgentAction.REVIEW,
    confidence_score=0.92,
    risk_score=0.87
)
```

---

### 📊 **Evaluation & Scoring (MLflow)**

| Schema | File | Use For |
|--------|------|---------|
| `EvaluationRecord` | `evaluation.py` | Prediction vs ground truth |
| `ScorerMetrics` | `evaluation.py` | Accuracy, precision, F1, business metrics |
| `FeedbackSignal` | `evaluation.py` | Merchant appeals, chargebacks |

**Example:**
```python
eval_record = EvaluationRecord(
    evaluation_id="eval_001",
    predicted_action="decline",
    ground_truth_label="fraud",
    is_correct=True,
    scorer_metrics=ScorerMetrics(accuracy=0.92, precision=0.88)
)
```

---

### 🔬 **Prompt Optimization (DSPy/TextGrad)**

| Schema | File | Use For |
|--------|------|---------|
| `FewShotExample` | `optimization.py` | Training examples for DSPy |
| `PromptVersion` | `optimization.py` | Versioned prompts in UC |
| `DSPyOptimizerMetadata` | `optimization.py` | Optimization run results |
| `HighRiskSelectionMetadata` | `optimization.py` | MLflow scorer selection |

**Example:**
```python
example = FewShotExample(
    example_id="ex_001",
    input="Transaction context...",
    output="Risk narrative...",
    quality_score=0.95
)

optimizer = DSPyOptimizerMetadata(
    task_prompt_version="v1.3",
    scorer_results={"accuracy": 0.92},
    examples_selected=[example]
)
```

---

### 📤 **Output & Streaming (Dashboard)**

| Schema | File | Use For |
|--------|------|---------|
| `StreamingOutput` | `optimization.py` | Real-time dashboard display |

**Example:**
```python
output = StreamingOutput(
    transaction_id="txn_001",
    narrative="BIN mismatch detected...",
    risk_score=0.91,
    recommended_action="decline"
)
```

---

### 📡 **Telemetry (Zerobus → Delta)**

| Schema | File | Use For |
|--------|------|---------|
| `TelemetryEvent` | `telemetry.py` | Generic event for Zerobus |
| `AgentTrace` | `telemetry.py` | Complete agent execution trace |
| `MCPToolTrace` | `telemetry.py` | MCP tool call trace |
| `LLMTrace` | `telemetry.py` | LLM inference trace |

**Example:**
```python
event = TelemetryEvent(
    event_id="evt_001",
    event_type=EventType.AGENT_COMPLETE,
    request_id="req_001",
    transaction_id="txn_001",
    trace_id="otel_trace_123",
    payload={"risk_score": 0.91}
)
```

---

## Common Patterns

### Pattern 1: Transaction Ingestion

```python
# Parse incoming event
event = NestedTransaction.model_validate_json(kafka_message)

# Extract IDs
transaction_id = event.id
merchant_id = event.merchant.id
customer_id = event.customer.id
```

### Pattern 2: MCP Tool Calling

```python
# Agent makes tool call
tool_call = ToolCall(
    tool_id="call_001",
    tool_name="bin_lookup",
    tool_server="enrichment-server",
    arguments={"bin": event.payment_method.bin}
)

# Tool returns result
tool_result = ToolResult(
    tool_call_id="call_001",
    success=True,
    result=BINLookupResult(...),
    latency_ms=42.5
)
```

### Pattern 3: Lakebase Retrieval

```python
# Retrieve merchant context with embedding
merchant_ctx = MerchantContextWithEmbedding(
    merchant_id="mch_001",
    merchant_risk_tier="medium",
    embedding=Embedding(vector=cached_vector, dimension=768)
)

# Search for similar cases
similar_cases = lakebase.vector_search(
    query_embedding=transaction_embedding,
    top_k=5
)
```

### Pattern 4: Agent Execution

```python
# Create agent input
agent_input = AgentInput(
    request_id="req_001",
    transaction=transaction,
    fraud_signals=signals,
    merchant_context=merchant_ctx,
    customer_context=customer_ctx
)

# Agent processes
agent_output = agent.run(agent_input)

# Log to MLflow
mlflow.log_trace(agent_output.reasoning_steps)
```

### Pattern 5: Streaming to Dashboard

```python
# Convert to streaming output
stream_output = StreamingOutput(
    transaction_id=event.id,
    narrative=agent_output.risk_narrative,
    risk_score=agent_output.risk_score,
    recommended_action=agent_output.recommended_action.value
)

# Stream to dashboard
websocket.send_json(stream_output.model_dump())
```

### Pattern 6: MLflow Evaluation

```python
# Create evaluation record
eval_record = EvaluationRecord(
    evaluation_id=f"eval_{txn_id}",
    request_id=request_id,
    predicted_action=agent_output.recommended_action.value,
    ground_truth_label=transaction.fraud_label,
    is_correct=(predicted == ground_truth),
    scorer_metrics=ScorerMetrics(...),
    mlflow_run_id=mlflow.active_run().info.run_id
)
```

### Pattern 7: DSPy Optimization

```python
# Track optimization run
optimizer_metadata = DSPyOptimizerMetadata(
    run_id="opt_run_123",
    task_prompt_version="v1.3",
    system_prompt_version="v2.1",
    optimizer_type="MIPRO",
    scorer_results={"accuracy": 0.92},
    examples_selected=[example1, example2]
)

# Log to MLflow
mlflow.log_dict(optimizer_metadata.model_dump(), "optimization_metadata.json")
```

### Pattern 8: Telemetry to Zerobus

```python
# Create telemetry event
telemetry = TelemetryEvent(
    event_id=f"evt_{uuid4()}",
    event_type=EventType.AGENT_COMPLETE,
    request_id=request_id,
    transaction_id=transaction_id,
    trace_id=otel_trace_id,
    payload={
        "risk_score": agent_output.risk_score,
        "action": agent_output.recommended_action.value,
        "latency_ms": agent_output.latency_ms
    }
)

# Send to Zerobus → Delta
zerobus_client.ingest(telemetry.model_dump())
```

---

## Validation & Serialization

### Pydantic Model Operations

```python
# Parse from JSON
obj = NestedTransaction.model_validate_json(json_string)

# Parse from dict
obj = NestedTransaction.model_validate(dict_data)

# Serialize to dict
dict_data = obj.model_dump()

# Serialize to JSON
json_string = obj.model_dump_json()

# Serialize to JSON (exclude None)
json_string = obj.model_dump_json(exclude_none=True)
```

---

## File Locations

```
shared/schemas/
├── __init__.py              ← Import all from here
├── transactions.py          ← Normalized transaction
├── nested_transaction.py    ← Event structure (your format)
├── fraud_signals.py         ← Velocity, amount, location, device
├── contexts.py              ← Merchant/customer profiles
├── agent_io.py              ← Agent I/O + tool calling
├── evaluation.py            ← MLflow scoring
├── telemetry.py             ← Zerobus events
├── mcp_tools.py             ← MCP tool results (NEW)
├── embeddings.py            ← Lakebase memory (NEW)
├── optimization.py          ← DSPy/TextGrad (NEW)
└── examples.py              ← Working examples
```

---

## Cheat Sheet

| I need to... | Use this schema |
|-------------|-----------------|
| Parse incoming transaction | `NestedTransaction` |
| Call MCP tool | `ToolCall` + specific result schema |
| Store conversation | `ConversationHistory` |
| Cache embeddings | `Embedding` |
| Generate agent output | `AgentOutput` |
| Stream to dashboard | `StreamingOutput` |
| Log to MLflow | `EvaluationRecord` |
| Track prompt version | `PromptVersion` |
| Run DSPy optimization | `DSPyOptimizerMetadata` |
| Send to Zerobus | `TelemetryEvent` |

---

**Status:** ✅ All schemas complete and validated  
**Next:** Synthetic data generation using these schemas

