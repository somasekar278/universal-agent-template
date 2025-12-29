# Schema Versioning Guide

**How to evolve Pydantic schemas over time without breaking production systems.**

---

## The Problem

When your schemas change:
- Old clients break if you make breaking changes
- You can't deploy new features without migrating all clients
- Data in different versions needs to coexist
- Backward compatibility is hard to maintain

**Solution:** Comprehensive schema versioning framework.

---

## Quick Start

### 1. Register Schema Versions

```python
from shared.schemas.versioning import schema_registry

# Register version 1.0.0
schema_registry.register(
    schema_name="Transaction",
    version="1.0.0",
    schema_class=TransactionV1,
)

# Register version 2.0.0 (with breaking changes)
schema_registry.register(
    schema_name="Transaction",
    version="2.0.0",
    schema_class=TransactionV2,
    breaking_changes=["Added required field: payment_method"]
)
```

### 2. Define Migrations

```python
from shared.schemas.versioning import migration_chain, FieldMigration

# Migration from v1 to v2
migration = FieldMigration(
    from_version="1.0.0",
    to_version="2.0.0",
    schema_name="Transaction",
    default_values={
        "payment_method": "card"  # Default for new required field
    }
)

migration_chain.register(migration)
```

### 3. Use Auto-Migration

```python
from shared.schemas.versioning import auto_migrator

# Old data in v1 format
old_data = {"id": "txn_123", "amount": "99.99", ...}

# Auto-upgrade to latest version
model, version = auto_migrator.auto_upgrade(
    schema_name="Transaction",
    data=old_data,
    data_version="1.0.0"
)

# model is now TransactionV2 instance!
```

---

## Core Concepts

### Semantic Versioning

We use **semantic versioning** (semver): `MAJOR.MINOR.PATCH`

- **MAJOR** (1.0.0 → 2.0.0): Breaking changes
  - Removed fields
  - Renamed fields
  - Changed field types
  - Made optional fields required

- **MINOR** (1.0.0 → 1.1.0): Backward-compatible additions
  - Added optional fields
  - New features that don't break existing code

- **PATCH** (1.0.0 → 1.0.1): Backward-compatible fixes
  - Bug fixes
  - Documentation updates
  - No API changes

### Schema Registry

Central registry for all schema versions:

```python
from shared.schemas.versioning import schema_registry

# Register a version
schema_registry.register(
    schema_name="Transaction",
    version="1.0.0",
    schema_class=TransactionV1
)

# Get specific version
schema = schema_registry.get("Transaction", "1.0.0")

# Get latest version
latest = schema_registry.get_latest("Transaction")

# List all versions
versions = schema_registry.list_versions("Transaction")
# ['3.0.0', '2.0.0', '1.0.0']  # Newest first
```

### Migration Chain

Automatically migrates data between versions:

```python
from shared.schemas.versioning import migration_chain

# Migrate data
migrated = migration_chain.migrate(
    schema_name="Transaction",
    data=old_data,
    from_version="1.0.0",
    to_version="3.0.0"  # Automatically chains through v2!
)
```

**Auto-chaining:** If you have migrations 1→2 and 2→3, you can migrate 1→3 directly.

---

## Evolution Example

### Version 1.0.0 (Initial)

```python
class TransactionV1(BaseModel):
    id: str
    amount: Decimal
    currency: str
    customer_id: str
    merchant_id: str
```

### Version 2.0.0 (Breaking: New Required Field)

```python
class TransactionV2(BaseModel):
    id: str
    amount: Decimal
    currency: str
    customer_id: str
    merchant_id: str
    payment_method: str  # NEW REQUIRED FIELD → BREAKING
    timestamp: Optional[datetime] = None  # NEW OPTIONAL FIELD
```

**Migration v1 → v2:**

```python
migration = FieldMigration(
    from_version="1.0.0",
    to_version="2.0.0",
    schema_name="Transaction",
    default_values={
        "payment_method": "card",  # Provide default for required field
        "timestamp": None
    }
)
```

### Version 3.0.0 (Breaking: Renamed Fields)

```python
class TransactionV3(BaseModel):
    id: str
    amount: Decimal
    currency: str
    buyer_id: str  # RENAMED from customer_id
    seller_id: str  # RENAMED from merchant_id
    payment_method: str
    timestamp: Optional[datetime] = None
```

**Migration v2 → v3:**

```python
migration = FieldMigration(
    from_version="2.0.0",
    to_version="3.0.0",
    schema_name="Transaction",
    field_mappings={
        "customer_id": "buyer_id",
        "merchant_id": "seller_id"
    }
)
```

---

## Usage Patterns

### Pattern 1: API Version Negotiation

```python
from fastapi import FastAPI, Header
from shared.schemas.versioning import schema_registry

app = FastAPI()

@app.post("/transactions")
def create_transaction(
    data: dict,
    api_version: str = Header(default="1.0.0", alias="X-API-Version")
):
    # Get requested schema version
    schema = schema_registry.negotiate_version(
        schema_name="Transaction",
        requested_version=api_version,
        accept_newer=True  # Allow newer compatible versions
    )
    
    if not schema:
        return {"error": "Unsupported API version"}
    
    # Parse with versioned schema
    transaction = schema.parse(data)
    
    # Process (core logic version-agnostic)
    result = process_transaction(transaction)
    
    return result
```

### Pattern 2: Database Migrations

```python
from shared.schemas.versioning import auto_migrator

def upgrade_database_records():
    """Upgrade all transactions to latest schema."""
    
    for record in database.query("SELECT * FROM transactions"):
        # Each record has its schema version
        current_version = record["schema_version"]
        
        # Auto-upgrade to latest
        upgraded_model, new_version = auto_migrator.auto_upgrade(
            schema_name="Transaction",
            data=record,
            data_version=current_version
        )
        
        # Save back to database
        database.update(
            record_id=record["id"],
            data=upgraded_model.model_dump(),
            schema_version=new_version
        )
```

### Pattern 3: Multi-Version Support

```python
# Support multiple versions simultaneously
SUPPORTED_VERSIONS = ["1.0.0", "2.0.0", "3.0.0"]

def handle_request(data: dict, requested_version: str):
    if requested_version not in SUPPORTED_VERSIONS:
        raise ValueError(f"Unsupported version: {requested_version}")
    
    # Get schema for requested version
    schema = schema_registry.get("Transaction", requested_version)
    
    # Parse with that version
    model = schema.parse(data)
    
    # Process (works with all versions)
    return process(model)
```

### Pattern 4: Automatic Schema Detection

```python
def smart_parse(data: dict, schema_name: str):
    """Try to detect schema version from data."""
    
    # Try each version from newest to oldest
    versions = schema_registry.list_versions(schema_name)
    
    for version in versions:
        schema = schema_registry.get(schema_name, version)
        try:
            model = schema.parse(data)
            return model, version  # Success!
        except ValidationError:
            continue  # Try next version
    
    raise ValueError("Data doesn't match any known schema version")
```

---

## Compatibility Checking

### Detect Breaking Changes

```python
from shared.schemas.versioning import CompatibilityChecker

# Compare two schema versions
is_compatible, breaking_changes = CompatibilityChecker.is_backward_compatible(
    old_schema=TransactionV1,
    new_schema=TransactionV2
)

if not is_compatible:
    print("❌ Breaking changes detected:")
    for change in breaking_changes:
        print(f"  - {change.description}")
        # Output: "Added required field: payment_method"
```

### Suggest Version Bump

```python
# Automatically suggest next version based on changes
suggested_version = CompatibilityChecker.suggest_version_bump(
    old_schema=TransactionV2,
    new_schema=TransactionV3,
    current_version="2.0.0"
)

print(f"Suggested version: {suggested_version}")
# Output: "3.0.0" (major bump due to breaking changes)
```

### Types of Changes Detected

**Breaking Changes:**
- `FIELD_REMOVED` - Field was removed
- `FIELD_RENAMED` - Field was renamed (detected as remove + add)
- `FIELD_TYPE_CHANGED` - Field type changed
- `FIELD_MADE_REQUIRED` - Optional field became required
- `DEFAULT_VALUE_REMOVED` - Default value was removed
- `VALIDATION_STRICTER` - Validation became more restrictive

**Non-Breaking Changes:**
- `FIELD_ADDED_OPTIONAL` - Optional field added
- `DEFAULT_VALUE_ADDED` - Default value added
- `FIELD_DESCRIPTION_CHANGED` - Documentation changed

---

## Deprecation & Sunset

### Mark Version as Deprecated

```python
from datetime import datetime, timedelta

# Deprecate old version with 90-day sunset
sunset_date = datetime.utcnow() + timedelta(days=90)

schema_registry.deprecate_version(
    schema_name="Transaction",
    version="1.0.0",
    sunset_date=sunset_date
)
```

### Check Deprecation Status

```python
schema = schema_registry.get("Transaction", "1.0.0")

if schema.is_deprecated():
    print(f"⚠️ Version {schema.version} is deprecated")
    print(f"Sunset date: {schema.version_info.sunset_date}")
    print(f"Breaking changes in v2: {schema.version_info.breaking_changes}")
```

### Enforce Sunset

```python
def validate_version(schema_name: str, version: str):
    schema = schema_registry.get(schema_name, version)
    
    if schema.is_sunset():
        raise ValueError(
            f"Version {version} has been sunset. "
            f"Please upgrade to {schema_registry.get_latest(schema_name).version}"
        )
```

---

## Migration Types

### 1. Field Migration (Built-in)

For common transformations:

```python
from shared.schemas.versioning import FieldMigration

migration = FieldMigration(
    from_version="1.0.0",
    to_version="2.0.0",
    schema_name="Transaction",
    
    # Rename fields
    field_mappings={
        "old_name": "new_name"
    },
    
    # Transform values
    field_transforms={
        "amount": lambda x: Decimal(x) / 100  # cents to dollars
    },
    
    # Add defaults
    default_values={
        "new_field": "default_value"
    },
    
    # Remove deprecated fields
    removed_fields=["deprecated_field"]
)
```

### 2. Custom Migration

For complex transformations:

```python
from shared.schemas.versioning import SchemaMigration

class CustomMigration(SchemaMigration):
    def __init__(self):
        super().__init__(
            from_version="2.0.0",
            to_version="3.0.0",
            schema_name="Transaction"
        )
    
    def migrate(self, data: dict) -> dict:
        # Custom transformation logic
        migrated = data.copy()
        
        # Complex business logic
        if "customer_type" in data:
            if data["customer_type"] == "premium":
                migrated["discount_rate"] = 0.10
            else:
                migrated["discount_rate"] = 0.05
        
        return migrated

# Register custom migration
migration_chain.register(CustomMigration())
```

---

## Testing

### Test Migrations

```python
import pytest
from shared.schemas.versioning import migration_chain

def test_migration_v1_to_v2():
    # V1 data
    v1_data = {
        "id": "txn_123",
        "amount": "99.99",
        "currency": "USD",
        "customer_id": "cust_456",
        "merchant_id": "mch_789"
    }
    
    # Migrate
    v2_data = migration_chain.migrate(
        schema_name="Transaction",
        data=v1_data,
        from_version="1.0.0",
        to_version="2.0.0"
    )
    
    # Assertions
    assert v2_data["id"] == "txn_123"
    assert v2_data["payment_method"] == "card"  # Default added
    assert "timestamp" in v2_data  # New field added
```

### Test Compatibility

```python
def test_backward_compatibility():
    is_compatible, breaking_changes = CompatibilityChecker.is_backward_compatible(
        old_schema=TransactionV1,
        new_schema=TransactionV2
    )
    
    # Expect breaking changes due to required field
    assert not is_compatible
    assert len(breaking_changes) > 0
    assert any("payment_method" in c.description for c in breaking_changes)
```

---

## Best Practices

### 1. Always Version Your Schemas

```python
# Good: Explicit versioning
from shared.schemas.versions.v1 import TransactionV1
from shared.schemas.versions.v2 import TransactionV2

# Bad: No versioning
from shared.schemas import Transaction  # Which version?
```

### 2. Store Version with Data

```json
{
  "schema_version": "2.0.0",
  "data": {
    "id": "txn_123",
    ...
  }
}
```

### 3. Provide Migration Guides

```python
schema_registry.register(
    schema_name="Transaction",
    version="2.0.0",
    schema_class=TransactionV2,
    breaking_changes=[
        "Added required field: payment_method",
        "Clients must provide payment_method or use default"
    ],
    migration_guide_url="https://docs.example.com/migrate-v1-to-v2"
)
```

### 4. Test All Migration Paths

```python
# Test each migration
test_migration_v1_to_v2()
test_migration_v2_to_v3()

# Test chained migrations
test_migration_v1_to_v3_via_v2()
```

### 5. Communicate Deprecations Early

```python
# Deprecate with plenty of notice
sunset_date = datetime.utcnow() + timedelta(days=180)  # 6 months

schema_registry.deprecate_version(
    schema_name="Transaction",
    version="1.0.0",
    sunset_date=sunset_date
)

# Send deprecation warnings in API responses
if schema.is_deprecated():
    response.headers["X-API-Deprecation"] = (
        f"Version {schema.version} deprecated. "
        f"Sunset: {schema.version_info.sunset_date.date()}"
    )
```

---

## Production Deployment

### Zero-Downtime Deployment

**Phase 1: Deploy New Version (Both Versions Active)**
```python
# Old clients use v1.0.0
# New clients use v2.0.0
# Server supports both simultaneously
```

**Phase 2: Migrate Clients**
```
# Gradually migrate clients to v2.0.0
# Monitor metrics
```

**Phase 3: Deprecate Old Version**
```python
# Mark v1.0.0 as deprecated with sunset date
schema_registry.deprecate_version("Transaction", "1.0.0")
```

**Phase 4: Remove Old Version**
```
# After sunset date, remove v1.0.0 support
```

### Rollback Strategy

```python
# If new version has issues, rollback
def rollback_to_v1():
    # Re-enable v1 as "latest"
    schema_registry._latest["Transaction"] = "1.0.0"
    
    # Undeprecate v1
    schema = schema_registry.get("Transaction", "1.0.0")
    schema.version_info.deprecated = False
```

---

## Summary

### Time to Evolve Schema

| Without Versioning | With Versioning |
|--------------------|-----------------|
| 2-4 weeks (coordinate all clients) | 1 day (deploy new version) |
| All-at-once deployment | Gradual rollout |
| High risk of breaking changes | Zero downtime |
| Hard to rollback | Easy rollback |

### Key Benefits

✅ **Backward Compatibility** - Old clients keep working  
✅ **Gradual Migration** - Migrate clients at their own pace  
✅ **Zero Downtime** - Deploy without service interruption  
✅ **Safety** - Detect breaking changes automatically  
✅ **Flexibility** - Support multiple versions simultaneously  
✅ **Auditability** - Track what changed and when  

---

## Quick Reference

```python
# Register version
schema_registry.register("Transaction", "1.0.0", TransactionV1)

# Define migration
migration = FieldMigration(from_version="1.0.0", to_version="2.0.0", ...)
migration_chain.register(migration)

# Auto-upgrade data
model, version = auto_migrator.auto_upgrade("Transaction", old_data, "1.0.0")

# Check compatibility
is_compatible, changes = CompatibilityChecker.is_backward_compatible(V1, V2)

# Deprecate version
schema_registry.deprecate_version("Transaction", "1.0.0", sunset_date)
```

---

**Status:** ✅ Production-ready schema versioning framework complete!

**Your schemas can now evolve safely without breaking production!** 🎉

