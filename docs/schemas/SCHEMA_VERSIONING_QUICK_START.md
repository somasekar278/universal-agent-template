# Schema Versioning - Quick Start

**Get started with schema versioning in 5 minutes.**

---

## Installation

Versioning framework is already included. Just ensure you have:

```bash
pip install packaging>=23.0
```

(Already in `requirements.txt`)

---

## 3-Step Setup

### Step 1: Register Your Schema Versions (30 seconds)

```python
from shared.schemas.versioning import schema_registry
from shared.schemas import NestedTransaction

# Register current version as v1.0.0
schema_registry.register(
    schema_name="Transaction",
    version="1.0.0",
    schema_class=NestedTransaction
)
```

### Step 2: Use Versioned Schemas (30 seconds)

```python
from shared.schemas.versioning import schema_registry

# Get specific version
schema_v1 = schema_registry.get("Transaction", "1.0.0")
transaction = schema_v1.parse(data)

# Or get latest version
latest_schema = schema_registry.get_latest("Transaction")
transaction = latest_schema.parse(data)
```

### Step 3: Add New Version When Schema Changes (2 minutes)

```python
# Define v2 schema with changes
class NestedTransactionV2(NestedTransaction):
    risk_score: float  # NEW FIELD

# Register new version
schema_registry.register(
    schema_name="Transaction",
    version="2.0.0",  # Major bump for breaking change
    schema_class=NestedTransactionV2,
    breaking_changes=["Added required field: risk_score"]
)

# Define migration
from shared.schemas.versioning import migration_chain, FieldMigration

migration = FieldMigration(
    from_version="1.0.0",
    to_version="2.0.0",
    schema_name="Transaction",
    default_values={"risk_score": 0.5}  # Default for new field
)
migration_chain.register(migration)
```

---

## Common Use Cases

### Use Case 1: API Versioning

```python
from fastapi import FastAPI, Header

app = FastAPI()

@app.post("/transactions")
def create_transaction(
    data: dict,
    api_version: str = Header(default="1.0.0")
):
    # Get schema for requested version
    schema = schema_registry.get("Transaction", api_version)
    
    # Parse with that version
    transaction = schema.parse(data)
    
    # Process
    return process(transaction)
```

### Use Case 2: Auto-Upgrade Old Data

```python
from shared.schemas.versioning import auto_migrator

# Old data (v1.0.0)
old_data = {"id": "txn_123", ...}

# Auto-upgrade to latest
model, version = auto_migrator.auto_upgrade(
    schema_name="Transaction",
    data=old_data,
    data_version="1.0.0"
)

# model is now v2.0.0!
```

### Use Case 3: Check for Breaking Changes

```python
from shared.schemas.versioning import CompatibilityChecker

is_compatible, breaking_changes = CompatibilityChecker.is_backward_compatible(
    old_schema=NestedTransaction,
    new_schema=NestedTransactionV2
)

if not is_compatible:
    for change in breaking_changes:
        print(f"⚠️ {change.description}")
```

---

## Run Examples

```bash
# See versioning in action
python shared/schemas/versioning/examples.py
```

Output:
```
✅ Registered Transaction v1.0.0
✅ Registered Transaction v2.0.0 (breaking changes)
✅ Registered Transaction v3.0.0 (breaking changes)

📥 Original data (v1.0.0):
  id: txn_123
  amount: 99.99
  ...

✅ Migrated to v3.0.0 (automatic chaining):
  id: txn_123
  buyer_id: cust_456  (renamed from customer_id)
  seller_id: mch_789  (renamed from merchant_id)
  payment_method: card  (added with default)
  ...
```

---

## When to Bump Versions

### Patch (1.0.0 → 1.0.1)
- Bug fixes
- Documentation changes
- No API changes

### Minor (1.0.0 → 1.1.0)
- Added **optional** fields
- New features (backward compatible)
- Old clients still work

### Major (1.0.0 → 2.0.0)
- Added **required** fields
- Removed fields
- Renamed fields
- Changed field types
- **Breaking changes**

---

## Best Practices

1. **Always store schema version with data**
   ```json
   {
     "schema_version": "1.0.0",
     "data": {...}
   }
   ```

2. **Provide defaults for new required fields**
   ```python
   default_values={"new_field": "sensible_default"}
   ```

3. **Deprecate before removing**
   ```python
   schema_registry.deprecate_version(
       "Transaction",
       "1.0.0",
       sunset_date=datetime.now() + timedelta(days=90)
   )
   ```

4. **Test migrations**
   ```python
   def test_migration():
       migrated = migration_chain.migrate(
           "Transaction", old_data, "1.0.0", "2.0.0"
       )
       assert "new_field" in migrated
   ```

---

## Key Files

```
shared/schemas/versioning/
├── base.py              # SchemaRegistry, VersionedSchema
├── migrations.py        # Migration framework
├── compatibility.py     # Breaking change detection
└── examples.py          # Working examples

shared/schemas/versions/
├── v1/                  # Version 1.x.x schemas
│   └── __init__.py
└── __init__.py          # Current version exports

docs/
└── 04_SCHEMA_VERSIONING_GUIDE.md  # Complete guide
```

---

## Quick Reference

```python
# Import versioning tools
from shared.schemas.versioning import (
    schema_registry,
    migration_chain,
    auto_migrator,
    FieldMigration,
    CompatibilityChecker,
)

# Register version
schema_registry.register("Transaction", "1.0.0", TransactionV1)

# Get version
schema = schema_registry.get("Transaction", "1.0.0")
latest = schema_registry.get_latest("Transaction")

# Define migration
migration = FieldMigration(
    from_version="1.0.0",
    to_version="2.0.0",
    schema_name="Transaction",
    field_mappings={"old": "new"},
    default_values={"new_field": "default"}
)
migration_chain.register(migration)

# Auto-upgrade
model, ver = auto_migrator.auto_upgrade("Transaction", data, "1.0.0")

# Check compatibility
compatible, changes = CompatibilityChecker.is_backward_compatible(V1, V2)

# Deprecate
schema_registry.deprecate_version("Transaction", "1.0.0", sunset_date)
```

---

## Support

- 📖 **Full Guide:** `docs/04_SCHEMA_VERSIONING_GUIDE.md`
- 💻 **Examples:** `shared/schemas/versioning/examples.py`
- 🧪 **Tests:** `tests/unit/test_schema_versioning.py`

---

**Status:** ✅ Ready to use!

**Time to add versioning to existing schemas:** ~5 minutes

