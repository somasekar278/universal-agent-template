# Data Schemas

This directory contains Pydantic data models that define the core data structures for the Realtime Insights & Alerts system.

## Schema Categories

### 1. **transactions.py** - Transaction Data
Core transaction records with payment details, device info, and location data.

**Key Models:**
- `Transaction` - Primary transaction record
- `PaymentMethod` - Enum of payment types
- `TransactionStatus` - Transaction lifecycle states
- `FraudLabel` - Ground truth labels for evaluation

### 2. **fraud_signals.py** - Fraud Detection Signals
Computed fraud indicators from various detection systems.

**Key Models:**
- `FraudSignals` - Aggregated fraud indicators
- `VelocitySignal` - Transaction velocity anomalies
- `AmountAnomalySignal` - Unusual transaction amounts
- `LocationSignal` - Geographic risk indicators
- `DeviceSignal` - Device fingerprinting signals

### 3. **contexts.py** - Merchant & Customer Context
Historical context and profiles for risk assessment.

**Key Models:**
- `MerchantContext` - Merchant profile and history
- `CustomerContext` - Customer behavior patterns
- `MerchantRiskTier` - Merchant risk categorization

### 4. **agent_io.py** - Agent Input/Output
Structures for agent execution and reasoning.

**Key Models:**
- `AgentInput` - Complete input to fraud analysis agent
- `AgentOutput` - Agent's risk narrative and recommendation
- `ToolCall` - MCP tool invocation (MCP-ready)
- `ToolResult` - Tool execution result (MCP-ready)
- `ReasoningStep` - Chain-of-thought reasoning trace
- `AgentAction` - Possible agent actions

### 5. **evaluation.py** - Evaluation & Scoring
MLflow evaluation metrics and feedback loops.

**Key Models:**
- `EvaluationRecord` - Complete evaluation with ground truth
- `ScorerMetrics` - MLflow custom scorer metrics
- `FeedbackSignal` - Feedback signal types

### 6. **telemetry.py** - Observability & Tracing
OTEL traces for Zerobus → Delta Lake ingestion.

**Key Models:**
- `TelemetryEvent` - Generic event for Zerobus (maps to UC table)
- `AgentTrace` - Complete agent execution trace
- `MCPToolTrace` - MCP tool call trace
- `LLMTrace` - LLM inference trace
- `EventType` - Event type enum

## MCP Compatibility

The `ToolCall` and `ToolResult` models in `agent_io.py` are designed to be compatible with Model Context Protocol (MCP) tool calling patterns:

- `tool_server` field identifies the MCP server
- `tool_name` identifies the specific method/tool
- `arguments` carries typed parameters
- Fully traceable via `tool_id` → telemetry pipeline

## Usage Example

```python
from shared.schemas import (
    Transaction,
    FraudSignals,
    MerchantContext,
    CustomerContext,
    AgentInput,
    AgentOutput,
)

# Create transaction
transaction = Transaction(
    transaction_id="txn_123",
    merchant_id="mch_001",
    customer_id="cust_456",
    timestamp=datetime.utcnow(),
    amount=Decimal("499.99"),
    currency="GBP",
    payment_method="card",
)

# Create agent input
agent_input = AgentInput(
    request_id="req_abc",
    transaction=transaction,
    fraud_signals=fraud_signals,
    merchant_context=merchant_context,
    customer_context=customer_context,
)

# Agent processes and returns output
agent_output = AgentOutput(
    request_id="req_abc",
    agent_id="agent_narrative_1",
    risk_narrative="High velocity detected...",
    recommended_action="review",
    confidence_score=0.85,
    risk_score=0.78,
    started_at=start_time,
    latency_ms=245.5,
    model_name="meta-llama-3.1-70b-instruct",
)
```

## Validation

All schemas include:
- ✅ Type validation via Pydantic
- ✅ Field constraints (min/max, ranges)
- ✅ Default values where appropriate
- ✅ Example data in Config.json_schema_extra
- ✅ Comprehensive docstrings

## Integration Points

### Synthetic Data Generation → `data/synthetic/`
Use these schemas to generate realistic test data.

### Unity Catalog → `uc-registry/`
Schemas sync to UC for versioning and governance.

### Zerobus → Delta Lake → `telemetry/`
`TelemetryEvent` schema maps to UC Delta tables via Zerobus protobuf.

### MLflow → `evaluation/`
`EvaluationRecord` and `ScorerMetrics` track experiment results.

## Next Steps

1. Generate synthetic data using these schemas
2. Create Zerobus protobuf from `TelemetryEvent` schema
3. Register schema versions in Unity Catalog
4. Build MCP tool interfaces that return these types

