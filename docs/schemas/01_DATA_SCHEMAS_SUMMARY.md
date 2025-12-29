# Data Schemas - Implementation Summary

**Created:** December 25, 2025  
**Status:** ✅ Complete - Foundation Ready

## What We Built

We've created a comprehensive, type-safe foundation for the Realtime Insights & Alerts system using Pydantic data models. All schemas are MCP-compatible and designed for the Databricks stack.

## Schemas Created

### 1. **Transaction Data** (`shared/schemas/transactions.py`)

Core payment transaction records with fraud detection metadata.

**Key Models:**
- `Transaction` - Complete transaction record (19 fields)
- `PaymentMethod` - Card, bank transfer, wallet, crypto, BNPL
- `TransactionStatus` - Pending, approved, declined, review, refunded
- `FraudLabel` - Ground truth labels for evaluation

**Features:**
- ✅ ISO currency validation (3-letter codes)
- ✅ Decimal precision for amounts
- ✅ Device fingerprinting support
- ✅ Geolocation fields (lat/long/country)
- ✅ ML risk score integration
- ✅ Extensible metadata dict

---

### 2. **Fraud Signals** (`shared/schemas/fraud_signals.py`)

Multi-dimensional fraud detection signals.

**Key Models:**
- `FraudSignals` - Aggregated indicators
- `VelocitySignal` - Transaction velocity anomalies
- `AmountAnomalySignal` - Unusual transaction amounts
- `LocationSignal` - Geographic risk (impossible travel)
- `DeviceSignal` - Device fingerprinting patterns

**Signal Types:**
- **Velocity**: Hourly/daily/weekly transaction counts, amounts, unique merchants/countries
- **Amount**: Z-score, percentile vs customer/merchant averages
- **Location**: Distance from last txn, impossible travel detection, location mismatch
- **Device**: New device, shared device, device age, transaction count per device

**Composite Scoring:**
- Individual signal scores (0-1)
- Overall signal strength
- Rules triggered list

---

### 3. **Context Data** (`shared/schemas/contexts.py`)

Historical merchant and customer profiles.

**Key Models:**
- `MerchantContext` - Business profile, transaction history, risk metrics
- `CustomerContext` - Account history, behavioral patterns, risk indicators
- `MerchantRiskTier` - Low, Medium, High, Critical

**Merchant Context:**
- Business info (name, category, risk tier)
- Transaction history (total volume, avg amount)
- Risk metrics (chargeback rate, fraud incidents)
- Geographic focus (primary countries)
- Recent activity (30-day stats)

**Customer Context:**
- Account details (age, verification status)
- Transaction history (success rate, spend patterns)
- Behavioral patterns (preferred payment methods, countries)
- Device/IP diversity
- Risk indicators (fraud incidents, disputes, chargebacks)

---

### 4. **Agent I/O** (`shared/schemas/agent_io.py`)

Agent execution structures - **MCP-READY**.

**Key Models:**
- `AgentInput` - Complete fraud analysis input
- `AgentOutput` - Risk narrative + recommendation
- `ToolCall` - MCP tool invocation (includes tool_server, tool_name)
- `ToolResult` - Tool execution result with latency
- `ReasoningStep` - Chain-of-thought trace
- `AgentAction` - Approve, Decline, Review, Flag, Request Verification

**MCP Integration Points:**
- `ToolCall.tool_server` → MCP server identifier
- `ToolCall.tool_name` → MCP method/tool name
- `ToolCall.arguments` → Type-safe parameters
- Full traceability via `tool_id` → telemetry

**Agent Output:**
- Human-readable risk narrative
- Recommended action + confidence score
- Complete reasoning trace (for MLflow)
- Tool usage summary
- Token usage tracking
- Latency metrics

---

### 5. **Evaluation** (`shared/schemas/evaluation.py`)

MLflow evaluation and feedback loops.

**Key Models:**
- `EvaluationRecord` - Complete evaluation with ground truth
- `ScorerMetrics` - Classification + business + narrative quality metrics
- `FeedbackSignal` - Merchant appeal, manual review, chargeback, etc.

**Scorer Metrics:**
- **Classification**: Accuracy, precision, recall, F1
- **Fraud-specific**: FPR, FNR
- **Business**: Caught/missed/false decline value
- **Narrative Quality**: Clarity, completeness, accuracy (LLM-as-judge)

**Evaluation Flow:**
- Links agent output → ground truth → metrics → feedback
- MLflow run tracking
- Prompt version tracking (from UC)
- Timestamps for feedback loops

---

### 6. **Telemetry** (`shared/schemas/telemetry.py`)

OTEL traces for Zerobus → Delta Lake ingestion.

**Key Models:**
- `TelemetryEvent` - Generic event (maps to UC Delta table)
- `AgentTrace` - Complete agent execution trace
- `MCPToolTrace` - MCP tool call trace
- `LLMTrace` - LLM inference trace (Databricks Model Serving)
- `EventType` - Agent start/complete/error, tool calls, LLM requests

**Telemetry Features:**
- Full OTEL trace context (trace_id, span_id, parent_span_id)
- Latency tracking per component
- Token usage + cost tracking
- Environment tagging (dev/staging/prod)
- Flexible payload dict for event-specific data

**Zerobus Integration:**
- `TelemetryEvent` schema → UC table schema
- Protobuf generation from Pydantic model
- Ready for Zerobus SDK ingestion

---

## Supporting Files Created

### **Configuration**

1. **`requirements.txt`** - Complete dependency list
   - Pydantic 2.x for schemas
   - LangGraph for orchestration
   - MLflow for evaluation
   - DSPy + TextGrad for optimization
   - OpenTelemetry for observability
   - FastAPI for services

2. **`pyproject.toml`** - Project metadata + tool configs
   - Black, Ruff, MyPy configurations
   - Test settings (pytest, coverage)
   - Python 3.9+ compatibility

3. **`.gitignore`** - Comprehensive ignore rules
   - Python artifacts
   - Virtual environments
   - Data files (synthetic should be regenerated)
   - MLflow/Databricks state

### **Documentation**

4. **`README.md`** - Project overview and getting started
5. **`shared/schemas/README.md`** - Schema documentation
6. **`shared/schemas/examples.py`** - Complete working example

---

## Example Usage

Run the included example to see the full flow:

```bash
python shared/schemas/examples.py
```

**Output:**
- Creates example high-risk transaction
- Computes fraud signals
- Fetches merchant/customer context
- Agent performs reasoning with MCP tool calls
- Generates risk narrative
- Shows complete reasoning trace

---

## Schema Validation

✅ **All schemas validated**
- No linter errors
- Type-safe with Pydantic
- Field constraints enforced
- Example data in all models
- Comprehensive docstrings

---

## MCP Compatibility

The `ToolCall` and `ToolResult` schemas are designed for seamless MCP integration:

```python
# MCP tool call
tool_call = ToolCall(
    tool_id="call_001",
    tool_name="merchant_context",        # MCP method
    tool_server="uc-query-server",       # MCP server
    arguments={"merchant_id": "mch_001"}  # Typed args
)

# MCP result
tool_result = ToolResult(
    tool_call_id="call_001",
    success=True,
    result=merchant_data,
    latency_ms=45.2
)
```

**MCP Servers Anticipated:**
- `uc-query-server` - Unity Catalog queries (merchant/customer/fraud history)
- `risk-calculation-server` - Real-time risk calculations (velocity, anomaly)
- `lakebase-retrieval-server` - Vector similarity, conversation memory
- `enrichment-server` - Device intel, IP reputation, geo validation
- `action-server` - Create alerts, update cases, request reviews

---

## Databricks Integration Points

| Schema | Databricks Integration |
|--------|------------------------|
| `Transaction` | → UC Delta table (source data) |
| `FraudSignals` | → Computed by Databricks SQL/Workflows |
| `MerchantContext` | → Retrieved from UC via MCP |
| `CustomerContext` | → Retrieved from UC via MCP |
| `AgentOutput` | → Logged to MLflow traces |
| `EvaluationRecord` | → MLflow experiments + UC Delta |
| `TelemetryEvent` | → Zerobus → UC Delta table |

---

## Next Steps

Now that schemas are complete, we can proceed with:

### **Phase 1: Synthetic Data (Immediate Next)**
1. ✅ **Create seed configurations** (`data/seeds/`)
   - Fraud pattern definitions
   - Merchant/customer archetypes
   - Generation parameters

2. ✅ **Build idempotent generator** (`data/synthetic/`)
   - Generate 1000-5000 transactions
   - Varied fraud scenarios (velocity, ATO, card testing)
   - Realistic merchant/customer distributions

3. ✅ **Create few-shot examples** (`data/examples/`)
   - Hand-curated high-quality examples
   - For DSPy BootstrapFewShot

### **Phase 2: Infrastructure**
4. ⏭️ Zerobus protobuf generation from `TelemetryEvent`
5. ⏭️ Unity Catalog schema registration
6. ⏭️ MCP server interface definitions

### **Phase 3: Agent Implementation**
7. ⏭️ Baseline prompt templates (system + task)
8. ⏭️ Ephemeral agent implementation
9. ⏭️ LangGraph workflow

### **Phase 4: Optimization & Evaluation**
10. ⏭️ MLflow custom scorers
11. ⏭️ DSPy optimization pipeline
12. ⏭️ TextGrad system prompt optimization

---

## Design Principles Achieved

✅ **Type Safety** - Full Pydantic validation  
✅ **MCP Compatibility** - Tool calling structures ready  
✅ **Databricks-Native** - Designed for UC, MLflow, Model Serving, Zerobus  
✅ **Observability** - Complete telemetry schemas with OTEL support  
✅ **Extensibility** - Metadata dicts for future fields  
✅ **Documentation** - Examples, docstrings, README  
✅ **Idempotency** - Ready for deterministic synthetic data generation  

---

## Files Summary

**Created 11 files:**

```
shared/schemas/
├── __init__.py              (Central imports)
├── transactions.py          (Transaction data)
├── fraud_signals.py         (Fraud detection signals)
├── contexts.py              (Merchant & customer profiles)
├── agent_io.py              (Agent I/O + MCP tool calling)
├── evaluation.py            (MLflow evaluation)
├── telemetry.py             (OTEL → Zerobus → Delta)
├── examples.py              (Working example code)
└── README.md                (Schema documentation)

Root:
├── requirements.txt         (Dependencies)
├── pyproject.toml           (Project config)
├── .gitignore               (Ignore rules)
└── README.md                (Project README)

docs/
└── 01_DATA_SCHEMAS_SUMMARY.md  (This file)
```

---

## Validation Results

```bash
✅ No linter errors
✅ All imports valid
✅ Type hints complete
✅ Field constraints working
✅ Examples run successfully
```

---

**Status:** Foundation complete. Ready to build synthetic data generator.

**Next Command:** Would you like to proceed with Phase 1 (Synthetic Data Generation)?

