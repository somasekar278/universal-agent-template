"""
Schema versioning framework for Pydantic models.

Supports:
- Multiple schema versions running simultaneously
- Backward compatibility
- Schema migration between versions
- Breaking change management
- Version negotiation
"""

from .base import (
    SchemaVersion,
    VersionedSchema,
    SchemaRegistry,
    schema_registry,
)

from .migrations import (
    SchemaMigration,
    MigrationChain,
    AutoMigrator,
)

from .compatibility import (
    CompatibilityChecker,
    BreakingChange,
    ChangeType,
)

__all__ = [
    "SchemaVersion",
    "VersionedSchema",
    "SchemaRegistry",
    "schema_registry",
    "SchemaMigration",
    "MigrationChain",
    "AutoMigrator",
    "CompatibilityChecker",
    "BreakingChange",
    "ChangeType",
]

