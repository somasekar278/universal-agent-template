# Schema Documentation

**Complete guide to data schemas, adaptation, and versioning in SOTA Agent Framework.**

## Quick Links

| Document | Purpose | Read Time |
|----------|---------|-----------|
| **[Schema Summary](01_DATA_SCHEMAS_SUMMARY.md)** | Overview of all schemas | 5 min |
| **[Schema Mapping](02_SCHEMA_MAPPING.md)** | How schemas relate | 5 min |
| **[Schema Adaptation](03_SCHEMA_ADAPTATION_GUIDE.md)** | Multi-tenant adaptation | 10 min |
| **[Schema Versioning](04_SCHEMA_VERSIONING_GUIDE.md)** | Version management | 10 min |
| **[Quick Reference](SCHEMAS_QUICK_REFERENCE.md)** | Schema cheat sheet | 2 min |
| **[Versioning Quick Start](SCHEMA_VERSIONING_QUICK_START.md)** | Quick versioning guide | 3 min |

## Reading Order

### For New Users
1. Start with [Schema Summary](01_DATA_SCHEMAS_SUMMARY.md)
2. Check [Quick Reference](SCHEMAS_QUICK_REFERENCE.md)
3. Browse schemas in `../../shared/schemas/`

### For Multi-Tenant Scenarios
1. Read [Schema Mapping](02_SCHEMA_MAPPING.md)
2. Study [Schema Adaptation](03_SCHEMA_ADAPTATION_GUIDE.md)
3. Implement adapters for your customers

### For Version Management
1. Quick start: [Versioning Quick Start](SCHEMA_VERSIONING_QUICK_START.md)
2. Comprehensive: [Schema Versioning](04_SCHEMA_VERSIONING_GUIDE.md)
3. Implement migrations

## Schema Overview

### Core Schemas

Located in `../../shared/schemas/`:

- **agent_io.py** - Agent inputs and outputs (AgentInput, AgentOutput)
- **transactions.py** - Transaction data models
- **fraud_signals.py** - Velocity, amount, location signals
- **contexts.py** - Merchant and customer profiles
- **evaluation.py** - Evaluation records and metrics
- **telemetry.py** - OTEL traces
- **mcp_tools.py** - MCP tool interfaces

### Versioning System

Located in `../../shared/schemas/versioning/`:

- **base.py** - Version management base classes
- **compatibility.py** - Version compatibility checks
- **migrations.py** - Schema migration framework

## Common Use Cases

### Create Custom Schema

```python
from pydantic import BaseModel

class YourDomainData(BaseModel):
    id: str
    # Your fields here
```

### Adapt External Data

```python
from shared.adapters import SchemaAdapter

class YourAdapter(SchemaAdapter):
    def adapt(self, external_data: dict) -> YourSchema:
        # Map external format to your schema
        return YourSchema(...)
```

### Handle Schema Versions

```python
from shared.schemas.versioning import SchemaVersion

# Define version
v1 = SchemaVersion(major=1, minor=0, patch=0)

# Check compatibility
if v1.is_compatible_with(v2):
    # Safe to use
    pass
```

## Documentation Details

### 01_DATA_SCHEMAS_SUMMARY.md

- Overview of all schemas
- Schema relationships
- When to use each schema

### 02_SCHEMA_MAPPING.md

- How schemas relate to each other
- Data flow between schemas
- Integration points

### 03_SCHEMA_ADAPTATION_GUIDE.md

- Multi-tenant schema adaptation
- Custom schema adapters
- Handling different formats

### 04_SCHEMA_VERSIONING_GUIDE.md

- Version management strategy
- Breaking vs non-breaking changes
- Migration patterns

### SCHEMAS_QUICK_REFERENCE.md

- Quick lookup of all schemas
- Field descriptions
- Usage examples

### SCHEMA_VERSIONING_QUICK_START.md

- Quick start for versioning
- Common version operations
- Best practices

## Best Practices

1. **Type Safety** - Always use Pydantic models
2. **Validation** - Let Pydantic validate at runtime
3. **Versioning** - Version schemas when making changes
4. **Adaptation** - Use adapters for external formats
5. **Documentation** - Document all custom schemas

## Examples

### Basic Schema Usage

```python
from shared.schemas import AgentInput, Transaction

# Create input
input_data = AgentInput(
    request_id="req_123",
    transaction=Transaction(
        id="txn_456",
        amount=100.0,
        currency="USD"
    )
)
```

### Schema Adaptation

```python
from shared.adapters import TransactionAdapter

adapter = TransactionAdapter()
our_format = adapter.adapt(external_transaction)
```

### Schema Versioning

```python
from shared.schemas.versioning import migrate_schema

# Migrate from v1 to v2
v2_data = migrate_schema(v1_data, from_version="1.0", to_version="2.0")
```

## Related Documentation

- **[Configuration System](../CONFIGURATION_SYSTEM.md)** - How to configure schema usage
- **[Template Guide](../TEMPLATE_GUIDE.md)** - Using schemas in templates
- **[Project Structure](../PROJECT_STRUCTURE.md)** - Where schemas fit

---

**Start here:** [Schema Summary](01_DATA_SCHEMAS_SUMMARY.md)

