# Schema Mapping - Your Data Structures to Our Schemas

**Created:** December 25, 2025  
**Status:** ✅ Complete - All structures mapped

This document maps your actual data structures to the comprehensive Pydantic schemas we've created.

---

## 1. Transaction Data ✅

**Your Structure:**
```json
{
  "id": "txn_0001",
  "timestamp": "2025-12-25T14:12:00Z",
  "amount": 123.45,
  "currency": "USD",
  "payment_method": { "type": "card", "bin": "559021", ... },
  "customer": { "id": "cust_001", "country": "US", ... },
  "merchant": { "id": "mch_001", "country": "US", ... },
  "device": { "ip": "192.0.2.1", "fingerprint_id": "fp_001", ... }
}
```

**Our Schema:** `NestedTransaction` in `shared/schemas/nested_transaction.py`

```python
from shared.schemas import NestedTransaction

transaction = NestedTransaction(
    id="txn_0001",
    timestamp=datetime.fromisoformat("2025-12-25T14:12:00Z"),
    amount=123.45,
    currency="USD",
    payment_method=PaymentMethodDetails(
        type="card",
        bin="559021",
        last4="4628",
        issuer_country="US"
    ),
    customer=CustomerDetails(...),
    merchant=MerchantDetails(...),
    device=DeviceDetails(...)
)
```

**Includes:**
- ✅ Nested `PaymentMethodDetails` (BIN, last4, issuer_country)
- ✅ Nested `CustomerDetails` (account_age_days, email_verified)
- ✅ Nested `MerchantDetails` (category, avg_txn_amount_30d, chargeback_rate_90d)
- ✅ Nested `DeviceDetails` (IP, fingerprint_id, is_vpn)

---

## 2. Merchant / Customer Context ✅

**Your Structures:**
```json
{
  "merchant_risk_tier": "medium",
  "weekly_velocity": 143,
  "usual_top_countries": ["US", "CA", "UK"],
  "recent_chargebacks_7d": 2,
  "embedding": [0.12, 0.34, ..., 0.56]
}
```

**Our Schemas:** `MerchantContextWithEmbedding` & `CustomerContextWithEmbedding`

```python
from shared.schemas import MerchantContextWithEmbedding, Embedding

merchant_context = MerchantContextWithEmbedding(
    merchant_id="mch_001",
    merchant_risk_tier="medium",
    weekly_velocity=143,
    usual_top_countries=["US", "CA", "UK"],
    recent_chargebacks_7d=2,
    avg_txn_amount_30d=210.50,
    chargeback_rate_90d=0.02,
    embedding=Embedding(
        vector=[0.12, 0.34, 0.56],  # Full vector
        dimension=768,
        model_name="text-embedding-ada-002"
    )
)
```

**Key Features:**
- ✅ **Embeddings support** for Lakebase similarity search
- ✅ Risk tier, velocity, countries, chargebacks
- ✅ Structured `Embedding` object with model name & dimension

---

## 3. MCP Tool Results (Enrichment) ✅

**Your Structure:**
```json
{
  "bin_lookup": { "issuer": "Example Bank", "country": "NG", "risk_level": 0.91 },
  "ip_geo_lookup": { "country": "US", "region": "CA", "risk_level": 0.1 },
  "sanctions_check": { "merchant_sanctioned": false },
  "velocity_anomaly": { "deviation_factor": 5.7, "flagged": true }
}
```

**Our Schema:** `MCPToolResults` in `shared/schemas/mcp_tools.py`

```python
from shared.schemas import (
    MCPToolResults,
    BINLookupResult,
    IPGeoLookupResult,
    SanctionsCheckResult,
    VelocityAnomalyResult
)

mcp_results = MCPToolResults(
    transaction_id="txn_0001",
    bin_lookup=BINLookupResult(
        bin="559021",
        issuer="Example Bank",
        country="NG",
        risk_level=0.91,
        card_type="credit"
    ),
    ip_geo_lookup=IPGeoLookupResult(
        ip_address="192.0.2.1",
        country="US",
        region="CA",
        risk_level=0.1,
        is_vpn=False
    ),
    sanctions_check=SanctionsCheckResult(
        merchant_sanctioned=False,
        country_watchlist_hit=False,
        ofac_hit=False
    ),
    velocity_anomaly=VelocityAnomalyResult(
        deviation_factor=5.7,
        flagged=True,
        typical_hourly_txns=2,
        current_hour_txns=13,
        anomaly_type="count_spike"
    )
)
```

**Individual Tool Result Schemas:**
- ✅ `BINLookupResult` - Issuer, country, risk, card type, brand
- ✅ `IPGeoLookupResult` - Country, region, VPN/proxy/Tor detection, ISP
- ✅ `SanctionsCheckResult` - OFAC, EU, UN sanctions, watchlist matches
- ✅ `VelocityAnomalyResult` - Deviation factor, baseline vs current metrics

**MCP Integration:** Each tool result maps to a specific MCP server endpoint.

---

## 4. Conversation / Agent Memory (Lakebase) ✅

**Your Structure:**
```json
{
  "agent_id": "narrative_agent_001",
  "transaction_id": "txn_0001",
  "conversation_history": [
    {
      "timestamp": "2025-12-25T14:12:10Z",
      "message": "IP and BIN mismatch detected, flagged for fraud.",
      "embedding": [0.21, 0.43, ..., 0.78]
    }
  ]
}
```

**Our Schema:** `ConversationHistory` in `shared/schemas/embeddings.py`

```python
from shared.schemas import ConversationHistory, ConversationMessage, Embedding

conversation = ConversationHistory(
    agent_id="narrative_agent_001",
    transaction_id="txn_0001",
    messages=[
        ConversationMessage(
            message_id="msg_001",
            timestamp=datetime.fromisoformat("2025-12-25T14:12:10Z"),
            role="agent",
            content="IP and BIN mismatch detected, flagged for fraud.",
            embedding=Embedding(
                vector=[0.21, 0.43, 0.78],
                dimension=1536,
                model_name="text-embedding-ada-002"
            )
        )
    ],
    conversation_embedding=Embedding(...)  # Entire conversation embedding
)
```

**Features:**
- ✅ Message-level embeddings for semantic search
- ✅ Conversation-level embedding for similarity matching
- ✅ Role tracking (system, agent, tool, user)
- ✅ Tool call linkage via `tool_call_id`
- ✅ **Lakebase-ready** for vector storage

---

## 5. DSPy Optimization Metadata ✅

**Your Structure:**
```json
{
  "transaction_id": "txn_0001",
  "task_prompt_version": "v1.3",
  "system_prompt_version": "v2.1",
  "scorer_results": { "accuracy": 0.92, "relevance": 0.87 },
  "drift_detected": false,
  "action_needed": true,
  "examples_selected": [ { "input": "...", "output": "..." } ]
}
```

**Our Schema:** `DSPyOptimizerMetadata` in `shared/schemas/optimization.py`

```python
from shared.schemas import DSPyOptimizerMetadata, FewShotExample

optimizer_metadata = DSPyOptimizerMetadata(
    run_id="opt_run_123",
    transaction_id="txn_0001",
    task_prompt_version="v1.3",
    system_prompt_version="v2.1",
    optimizer_type="MIPRO",  # or COPRO, BootstrapFewShot
    scorer_results={
        "accuracy": 0.92,
        "relevance": 0.87,
        "drift_detected": False
    },
    accuracy=0.92,
    relevance=0.87,
    drift_detected=False,
    action_needed=True,
    examples_selected=[
        FewShotExample(
            example_id="ex_001",
            input="Transaction context...",
            output="Risk narrative...",
            fraud_label="fraud",
            quality_score=0.95
        )
    ],
    mlflow_run_id="mlflow_run_xyz"
)
```

**Includes:**
- ✅ **Prompt version tracking** (task & system prompts from UC)
- ✅ **Scorer results** dictionary
- ✅ **Drift detection** flag
- ✅ **Few-shot examples** with quality scores
- ✅ **MLflow integration** for tracking

**Related Schemas:**
- `FewShotExample` - Individual training examples
- `PromptVersion` - Versioned prompts in Unity Catalog

---

## 6. Dashboard / Streaming Output ✅

**Your Structure:**
```json
{
  "transaction_id": "txn_0001",
  "narrative": "BIN issued in Nigeria, merchant in US, IP from CA...",
  "risk_score": 0.91,
  "timestamp": "2025-12-25T14:12:15Z"
}
```

**Our Schema:** `StreamingOutput` in `shared/schemas/optimization.py`

```python
from shared.schemas import StreamingOutput

output = StreamingOutput(
    transaction_id="txn_0001",
    narrative="BIN issued in Nigeria, merchant in US, IP from CA, 3 prior chargebacks. Strong fraud signal. Decline.",
    risk_score=0.91,
    recommended_action="decline",
    timestamp=datetime.fromisoformat("2025-12-25T14:12:15Z"),
    key_risk_factors=["BIN_MISMATCH", "CHARGEBACKS", "GEO_ANOMALY"],
    confidence=0.94
)
```

**Features:**
- ✅ Lightweight for real-time streaming
- ✅ Concise narrative
- ✅ Risk score + recommended action
- ✅ Optional risk factors & confidence

---

## Additional Schemas You Mentioned ✅

### A. High-Risk Selection Metadata

**Schema:** `HighRiskSelectionMetadata` in `shared/schemas/optimization.py`

```python
from shared.schemas import HighRiskSelectionMetadata

selection = HighRiskSelectionMetadata(
    transaction_id="txn_0001",
    is_high_risk=True,
    risk_score=0.91,
    selection_threshold=0.7,
    selection_reasons=[
        "risk_score_above_threshold",
        "velocity_anomaly_detected",
        "bin_ip_mismatch"
    ],
    should_run_mlflow_scorers=True,
    should_log_detailed_trace=True,
    use_cached_embeddings=True,
    embedding_cache_key="emb:merchant:mch_001"
)
```

**Purpose:**
- Determines which transactions get detailed MLflow evaluation
- Controls which get cached embedding prefetch from Redis
- Triggers for manual review

---

### B. Embedding Index Vectors (Prefetch Caching)

**Schema:** `Embedding` in `shared/schemas/embeddings.py`

```python
from shared.schemas import Embedding

# Merchant embedding for Redis cache
merchant_embedding = Embedding(
    vector=[0.12, 0.34, ..., 0.56],  # 768 or 1536 dimensions
    dimension=768,
    model_name="text-embedding-ada-002"
)

# Redis cache key pattern
cache_key = f"emb:merchant:{merchant_id}"
cache_key = f"emb:customer:{customer_id}"
cache_key = f"emb:case:{case_id}"
```

**Redis Caching Strategy:**
- Pre-fetch common merchant/customer embeddings
- Cache in Redis with TTL (e.g., 1 hour)
- Lakebase as source of truth
- Redis as hot cache layer

---

### C. Few-Shot Examples for Task Prompt Bootstrapping

**Schema:** `FewShotExample` in `shared/schemas/optimization.py`

```python
from shared.schemas import FewShotExample

example = FewShotExample(
    example_id="ex_fraud_001",
    input="""
Transaction: $1500, new device, BIN from Nigeria, IP from US California.
Customer: 2 days old, unverified email.
Merchant: Medium risk, digital goods.
Velocity: 13 txns in 1 hour (typical: 2).
""",
    output="""
HIGH RISK - DECLINE. Multiple critical fraud indicators:
1. New account (2 days) with unverified credentials
2. Severe velocity anomaly (6.5x normal rate)
3. BIN/IP country mismatch (Nigeria/US)
4. High-risk merchant category (digital goods)
Strong likelihood of account takeover or card testing.
""",
    fraud_label="fraud",
    quality_score=0.98,
    times_used=42,
    success_rate=0.94
)
```

**DSPy BootstrapFewShot Usage:**
- Curated high-quality examples
- Tracked success rate per example
- Quality scoring for selection
- Automatically selected by DSPy optimizers

---

## Complete Schema Overview

### **New Schemas Added (4 files):**

1. **`mcp_tools.py`** - MCP tool result structures
   - `BINLookupResult`
   - `IPGeoLookupResult`
   - `SanctionsCheckResult`
   - `VelocityAnomalyResult`
   - `MCPToolResults` (aggregator)

2. **`embeddings.py`** - Lakebase memory & vectors
   - `Embedding`
   - `ConversationMessage`
   - `ConversationHistory`
   - `MerchantContextWithEmbedding`
   - `CustomerContextWithEmbedding`
   - `SimilarCaseResult`

3. **`optimization.py`** - DSPy/TextGrad metadata
   - `FewShotExample`
   - `PromptVersion`
   - `DSPyOptimizerMetadata`
   - `HighRiskSelectionMetadata`
   - `StreamingOutput`

4. **`nested_transaction.py`** - Event structure
   - `NestedTransaction`
   - `PaymentMethodDetails`
   - `CustomerDetails`
   - `MerchantDetails`
   - `DeviceDetails`

### **Total Schema Files: 11**
- `transactions.py` (normalized)
- `nested_transaction.py` (event structure) ✨ NEW
- `fraud_signals.py`
- `contexts.py`
- `agent_io.py`
- `evaluation.py`
- `telemetry.py`
- `mcp_tools.py` ✨ NEW
- `embeddings.py` ✨ NEW
- `optimization.py` ✨ NEW
- `examples.py`

---

## Usage Examples

### Full Agent Flow with Your Data Structures

```python
from shared.schemas import (
    NestedTransaction,
    MCPToolResults,
    BINLookupResult,
    VelocityAnomalyResult,
    MerchantContextWithEmbedding,
    ConversationHistory,
    DSPyOptimizerMetadata,
    StreamingOutput,
    Embedding,
)

# 1. Ingest nested transaction event
transaction = NestedTransaction.model_validate_json(event_json)

# 2. Fetch MCP tool results
mcp_results = MCPToolResults(
    transaction_id=transaction.id,
    bin_lookup=BINLookupResult(...),
    velocity_anomaly=VelocityAnomalyResult(...),
)

# 3. Retrieve merchant context with embedding from Lakebase
merchant_context = MerchantContextWithEmbedding(
    merchant_id=transaction.merchant.id,
    embedding=cached_embedding  # Pre-fetched from Redis
)

# 4. Agent reasoning + conversation history
conversation = ConversationHistory(
    agent_id="narrative_agent_001",
    transaction_id=transaction.id,
    messages=[...]
)

# 5. Generate streaming output
output = StreamingOutput(
    transaction_id=transaction.id,
    narrative="BIN issued in Nigeria...",
    risk_score=0.91,
    recommended_action="decline"
)

# 6. Log DSPy optimization metadata
optimizer_metadata = DSPyOptimizerMetadata(
    run_id="opt_run_123",
    task_prompt_version="v1.3",
    scorer_results={"accuracy": 0.92}
)
```

---

## Validation Results

✅ **All schemas created**  
✅ **No linter errors**  
✅ **Full Pydantic validation**  
✅ **MCP-compatible tool calling**  
✅ **Lakebase embedding support**  
✅ **DSPy/TextGrad optimization tracking**  
✅ **Unity Catalog prompt versioning**  
✅ **MLflow evaluation integration**  
✅ **Zerobus telemetry ready**

---

## Architecture Alignment

| Your Data Structure | Our Schema | Integration Point |
|---------------------|------------|-------------------|
| Transaction event | `NestedTransaction` | Event ingestion, streaming |
| MCP tool results | `MCPToolResults`, `BINLookupResult`, etc. | MCP server responses |
| Merchant/Customer context | `MerchantContextWithEmbedding` | Lakebase + Redis cache |
| Conversation history | `ConversationHistory` | Lakebase vector store |
| DSPy metadata | `DSPyOptimizerMetadata` | MLflow experiments |
| Dashboard output | `StreamingOutput` | Real-time dashboard |
| High-risk selection | `HighRiskSelectionMetadata` | MLflow scorer selection |
| Embeddings | `Embedding` | Lakebase + Redis prefetch |
| Few-shot examples | `FewShotExample` | DSPy BootstrapFewShot |

---

## Next Steps

✅ **Schemas complete** - All your data structures mapped  
⏭️ **Synthetic data generation** - Generate realistic test transactions  
⏭️ **MCP server interfaces** - Define tool APIs  
⏭️ **Lakebase integration** - Set up vector store  
⏭️ **Unity Catalog setup** - Register prompt versions  

**Status:** Foundation ready for synthetic data generation and agent implementation!

