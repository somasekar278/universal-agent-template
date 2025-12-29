# Schema Adaptation Guide

**How to deploy to customers with different schemas in minutes, not weeks.**

## The Challenge

Every payment processor has different data structures:
- **Stripe**: `amount` in cents, nested `payment_method_details`
- **Adyen**: `pspReference` for ID, `additionalData` for card details
- **Custom Systems**: Completely unique field names and structures

**Problem:** Your core fraud detection logic shouldn't change for each customer.

**Solution:** Schema adapters that translate external schemas to your canonical format.

---

## Architecture

```
┌─────────────────────┐
│  Customer Event     │  ← Stripe/Adyen/Custom format
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Schema Adapter     │  ← Configured per customer
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Canonical Schema    │  ← Our NestedTransaction
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Core Logic         │  ← Fraud detection (unchanged)
│  - Agents           │
│  - MCP Tools        │
│  - Evaluation       │
└─────────────────────┘
```

**Key Principle:** Core logic always uses canonical schemas. Adapters handle translation.

---

## Quick Start: Onboard a New Customer

### Step 1: Create Adapter Config (5 minutes)

```yaml
# config/adapters/new_customer.yaml

customer_id: "new_customer"
adapter_class: "ConfigurableTransactionAdapter"

config:
  field_mappings:
    id: "their_field.transaction_id"
    timestamp: "their_field.created_at"
    amount: "their_field.amount_cents"
    # ... map all fields
  
  transformations:
    amount:
      divide: 100  # Convert cents to decimal
    currency:
      uppercase: true
  
  defaults:
    device.is_vpn: false
```

### Step 2: Load Adapter (30 seconds)

```python
from shared.adapters.loader import register_adapter_from_config

# Load customer's adapter
register_adapter_from_config("config/adapters/new_customer.yaml")
```

### Step 3: Use in Production (no code changes!)

```python
from shared.adapters.loader import get_adapter_for_customer
from shared.schemas import NestedTransaction

# Get customer's adapter
adapter = get_adapter_for_customer("new_customer")

# Convert their data to canonical format
canonical_txn = adapter.to_canonical(customer_event_data)

# Core logic uses canonical schema (unchanged!)
agent_output = fraud_agent.analyze(canonical_txn)

# Convert back to customer format (if needed)
customer_response = adapter.from_canonical(agent_output)
```

**Total Time:** ~10 minutes to onboard a new customer!

---

## Adapter Types

### 1. Pre-Built Adapters (Fastest)

Use for common payment processors:

```python
from shared.adapters import StripeTransactionAdapter, AdyenTransactionAdapter

# Stripe customer
adapter = StripeTransactionAdapter()
txn = adapter.to_canonical(stripe_event)

# Adyen customer
adapter = AdyenTransactionAdapter(config={"merchant_country": "NL"})
txn = adapter.to_canonical(adyen_notification)
```

**When to use:** Customer schema matches a known provider.

**Time to deploy:** < 1 minute (just specify adapter in config)

---

### 2. Configurable Adapter (Most Flexible)

Use for any custom schema:

```yaml
# config/adapters/custom_customer.yaml
customer_id: "custom_customer"
adapter_class: "ConfigurableTransactionAdapter"

config:
  field_mappings:
    # Map ANY customer field to canonical schema
    id: "transaction.ref_number"
    timestamp: "transaction.event_time"
    amount: "payment.total"
    currency: "payment.curr"
    
    # Nested fields use dot notation
    payment_method.bin: "card.bin_digits"
    payment_method.last4: "card.masked_pan"
    
    customer.id: "buyer.customer_ref"
    merchant.id: "seller.account_id"
    device.ip: "request.client_ip"
  
  transformations:
    # Transform values as needed
    amount:
      divide: 100  # cents → decimal
    timestamp:
      from_unix: true  # unix → datetime
    currency:
      uppercase: true  # usd → USD
  
  defaults:
    # Fill in missing fields
    device.is_vpn: false
    customer.prior_disputes: 0
```

**When to use:** Customer has unique schema.

**Time to deploy:** 5-10 minutes (create config, test)

---

### 3. Custom Adapter (Full Control)

For complex transformations:

```python
from shared.adapters import SchemaAdapter
from shared.schemas import NestedTransaction

class MyCustomAdapter(SchemaAdapter[NestedTransaction, dict]):
    def to_canonical(self, source: dict) -> NestedTransaction:
        # Custom transformation logic
        return NestedTransaction(
            id=self._transform_id(source),
            amount=self._calculate_amount(source),
            # ... custom logic
        )
    
    def from_canonical(self, target: NestedTransaction) -> dict:
        # Reverse transformation
        return {...}
```

**When to use:** Complex business logic in transformation.

**Time to deploy:** 30-60 minutes (write custom code, test)

---

## Real-World Examples

### Example 1: Stripe Integration

```python
# Stripe event (their format)
stripe_event = {
    "id": "ch_abc123",
    "amount": 12345,  # cents
    "currency": "usd",
    "payment_method_details": {
        "card": {
            "brand": "visa",
            "last4": "4242",
            "country": "US"
        }
    },
    "customer": "cus_xyz",
    "created": 1609459200
}

# Convert to canonical (one line!)
adapter = StripeTransactionAdapter()
canonical_txn = adapter.to_canonical(stripe_event)

# Now canonical_txn is NestedTransaction
print(canonical_txn.amount)  # Decimal('123.45')
print(canonical_txn.currency)  # 'USD'
print(canonical_txn.payment_method.last4)  # '4242'
```

---

### Example 2: Completely Custom Schema

**Customer's Format:**
```json
{
  "txn": {
    "ref": "TXN-2025-001",
    "total_cents": 9999,
    "curr": "gbp"
  },
  "card": {
    "bin": "411111",
    "suffix": "1111",
    "issuer_nation": "GB"
  },
  "buyer": {
    "uid": "USER-123",
    "nation": "GB"
  }
}
```

**Adapter Config:**
```yaml
# config/adapters/custom.yaml
customer_id: "custom"
adapter_class: "ConfigurableTransactionAdapter"

config:
  field_mappings:
    id: "txn.ref"
    amount: "txn.total_cents"
    currency: "txn.curr"
    payment_method.bin: "card.bin"
    payment_method.last4: "card.suffix"
    payment_method.issuer_country: "card.issuer_nation"
    customer.id: "buyer.uid"
    customer.country: "buyer.nation"
  
  transformations:
    amount:
      divide: 100
    currency:
      uppercase: true
  
  defaults:
    payment_method.type: "card"
    merchant.id: "default_merchant"
    device.ip: "0.0.0.0"
    device.fingerprint_id: "unknown"
```

**Usage:**
```python
# Load once at startup
from shared.adapters.loader import register_adapter_from_config
register_adapter_from_config("config/adapters/custom.yaml")

# Use everywhere
from shared.adapters.loader import get_adapter_for_customer

adapter = get_adapter_for_customer("custom")
canonical_txn = adapter.to_canonical(customer_data)

# Core logic unchanged!
fraud_signals = compute_fraud_signals(canonical_txn)
agent_output = narrative_agent.analyze(canonical_txn, fraud_signals)
```

---

## Multi-Tenant Deployment Pattern

### Scenario: Deploy to 10 different customers

```python
# startup.py

from shared.adapters.loader import load_all_adapters

# Load all customer adapters from config directory
load_all_adapters("config/adapters/")

# ✓ Registered adapter for customer 'stripe_customer_1'
# ✓ Registered adapter for customer 'adyen_customer_2'
# ✓ Registered adapter for customer 'custom_customer_3'
# ... etc
```

```python
# ingestion.py

from shared.adapters.loader import get_adapter_for_customer

def process_transaction(customer_id: str, event_data: dict):
    # Get customer-specific adapter
    adapter = get_adapter_for_customer(customer_id)
    
    # Convert to canonical
    canonical_txn = adapter.to_canonical(event_data)
    
    # Core logic (same for all customers!)
    result = fraud_detection_pipeline(canonical_txn)
    
    return result
```

**Benefits:**
- ✅ Add new customer = add config file (no code changes)
- ✅ Core logic is customer-agnostic
- ✅ Easy to test (mock adapters)
- ✅ Centralized schema management

---

## Configuration Reference

### Field Mappings

Use dot notation for nested fields:

```yaml
field_mappings:
  # Flat fields
  id: "transaction_id"
  amount: "total"
  
  # Nested source
  id: "data.transaction.id"
  
  # Nested target (automatically creates nested structure)
  payment_method.bin: "card_bin"
  payment_method.last4: "card_last_four"
  customer.id: "user.customer_id"
```

### Transformations

```yaml
transformations:
  # Math operations
  amount:
    divide: 100     # cents → decimal
    multiply: 100   # decimal → cents
  
  # String operations
  currency:
    uppercase: true   # usd → USD
    lowercase: true   # USD → usd
  
  # Date/time
  timestamp:
    from_unix: true   # Unix timestamp → datetime
    to_unix: true     # datetime → Unix timestamp
```

### Defaults

```yaml
defaults:
  # Provide defaults for missing fields
  device.is_vpn: false
  device.is_proxy: false
  customer.prior_disputes: 0
  merchant.is_verified: false
  fraud_label: "unknown"
```

---

## Testing Adapters

### Unit Test Pattern

```python
import pytest
from shared.adapters import StripeTransactionAdapter
from shared.schemas import NestedTransaction

def test_stripe_adapter():
    adapter = StripeTransactionAdapter()
    
    # Test data in Stripe format
    stripe_event = {
        "id": "ch_test123",
        "amount": 10000,  # $100.00
        "currency": "usd",
        "payment_method_details": {
            "card": {"last4": "4242", "country": "US"}
        }
    }
    
    # Convert to canonical
    result = adapter.to_canonical(stripe_event)
    
    # Assertions on canonical schema
    assert isinstance(result, NestedTransaction)
    assert result.id == "ch_test123"
    assert result.amount == Decimal("100.00")
    assert result.currency == "USD"
    assert result.payment_method.last4 == "4242"
```

### Integration Test

```python
def test_end_to_end_with_adapter():
    # Customer event
    customer_event = {...}
    
    # Get adapter
    adapter = get_adapter_for_customer("customer_a")
    
    # Convert
    canonical_txn = adapter.to_canonical(customer_event)
    
    # Run through core logic
    agent_output = fraud_detection_pipeline(canonical_txn)
    
    # Verify output
    assert agent_output.risk_score > 0
    assert agent_output.recommended_action in ["approve", "decline", "review"]
```

---

## Performance Considerations

### Caching Adapters

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_cached_adapter(customer_id: str):
    """Cache adapter instances per customer."""
    return get_adapter_for_customer(customer_id)
```

### Batch Processing

```python
def process_batch(customer_id: str, events: list[dict]):
    adapter = get_cached_adapter(customer_id)
    
    # Process all events with same adapter
    canonical_txns = [
        adapter.to_canonical(event)
        for event in events
    ]
    
    return canonical_txns
```

---

## Migration Strategy

### Phase 1: Add Adapter Layer (No Changes to Core)

```python
# Before (directly using customer schema)
def process_event(event: dict):
    amount = event["their_amount_field"] / 100
    currency = event["their_currency_field"]
    # ... lots of customer-specific code

# After (with adapter)
def process_event(customer_id: str, event: dict):
    adapter = get_adapter_for_customer(customer_id)
    canonical_txn = adapter.to_canonical(event)
    # Core logic now uses canonical_txn (type-safe!)
```

### Phase 2: Move All Customers to Adapters

```python
# Old customers → create adapters from existing logic
# New customers → just add config file
```

### Phase 3: Enjoy Multi-Tenant Deployment

```python
# One codebase, unlimited customers!
```

---

## Benefits Summary

| Without Adapters | With Adapters |
|------------------|---------------|
| Custom code per customer | Config file per customer |
| Core logic intertwined with schema | Core logic schema-agnostic |
| Hard to test | Easy to test |
| Weeks to onboard | Minutes to onboard |
| Code changes for new customer | No code changes |
| 10 customers = 10 codebases | 10 customers = 1 codebase |

---

## FAQ

**Q: What if customer has fields we don't support?**

A: Use `metadata` or `additional_data` dicts in schemas, or extend canonical schema if truly needed.

**Q: How do we handle breaking changes in customer schema?**

A: Version adapters (e.g., `StripeTransactionAdapter_v1`, `StripeTransactionAdapter_v2`) or use config versioning.

**Q: Can we transform data going back to customer?**

A: Yes! Use `from_canonical()` method to convert responses back to customer format.

**Q: Performance overhead?**

A: Minimal (<1ms). Pydantic validation is very fast. Cache adapter instances for best performance.

**Q: What about backward compatibility?**

A: Canonical schema changes are versioned. Old adapters can target old canonical versions if needed.

---

## Next Steps

1. ✅ **Start with pre-built adapters** for known providers
2. ✅ **Use ConfigurableAdapter** for custom schemas
3. ✅ **Test adapters** with customer sample data
4. ✅ **Deploy multi-tenant** using adapter registry

**Status:** Schema adaptation framework complete and production-ready!

**Time to onboard new customer:** 5-10 minutes ⚡

