"""
Examples of schema versioning usage.

Demonstrates:
- Registering schema versions
- Migrating between versions
- Backward compatibility checking
- Multi-version API support
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field

from .base import schema_registry, SchemaVersion
from .migrations import migration_chain, FieldMigration, auto_migrator
from .compatibility import CompatibilityChecker


# Example: Transaction schema evolution
class TransactionV1(BaseModel):
    """Transaction schema version 1.0.0."""
    
    id: str
    amount: Decimal
    currency: str
    customer_id: str
    merchant_id: str


class TransactionV2(BaseModel):
    """
    Transaction schema version 2.0.0.
    
    Changes from v1:
    - Added: payment_method field (required) - BREAKING CHANGE
    - Added: timestamp field (optional)
    """
    
    id: str
    amount: Decimal
    currency: str
    customer_id: str
    merchant_id: str
    payment_method: str  # NEW REQUIRED FIELD - breaking change
    timestamp: Optional[datetime] = None  # NEW OPTIONAL FIELD


class TransactionV3(BaseModel):
    """
    Transaction schema version 3.0.0.
    
    Changes from v2:
    - Renamed: customer_id -> buyer_id - BREAKING CHANGE
    - Renamed: merchant_id -> seller_id - BREAKING CHANGE
    """
    
    id: str
    amount: Decimal
    currency: str
    buyer_id: str  # RENAMED from customer_id
    seller_id: str  # RENAMED from merchant_id
    payment_method: str
    timestamp: Optional[datetime] = None


def example_1_register_versions():
    """Example: Register multiple schema versions."""
    
    print("\n" + "="*80)
    print("EXAMPLE 1: Register Schema Versions")
    print("="*80)
    
    # Register version 1.0.0
    schema_registry.register(
        schema_name="Transaction",
        version="1.0.0",
        schema_class=TransactionV1,
        breaking_changes=[],
    )
    print("\n✅ Registered Transaction v1.0.0")
    
    # Register version 2.0.0 (breaking changes!)
    schema_registry.register(
        schema_name="Transaction",
        version="2.0.0",
        schema_class=TransactionV2,
        breaking_changes=[
            "Added required field: payment_method"
        ],
    )
    print("✅ Registered Transaction v2.0.0 (breaking changes)")
    
    # Register version 3.0.0 (more breaking changes!)
    schema_registry.register(
        schema_name="Transaction",
        version="3.0.0",
        schema_class=TransactionV3,
        breaking_changes=[
            "Renamed: customer_id -> buyer_id",
            "Renamed: merchant_id -> seller_id"
        ],
    )
    print("✅ Registered Transaction v3.0.0 (breaking changes)")
    
    # List all versions
    print("\n📋 All registered versions:")
    versions = schema_registry.list_versions("Transaction")
    for ver in versions:
        schema = schema_registry.get("Transaction", ver)
        breaking = schema.version_info.breaking_changes
        breaking_str = f" (Breaking: {', '.join(breaking)})" if breaking else ""
        print(f"  - v{ver}{breaking_str}")
    
    # Get latest
    latest = schema_registry.get_latest("Transaction")
    print(f"\n🆕 Latest version: v{latest.version}")


def example_2_define_migrations():
    """Example: Define migrations between versions."""
    
    print("\n" + "="*80)
    print("EXAMPLE 2: Define Migrations")
    print("="*80)
    
    # Migration: v1 -> v2
    migration_v1_to_v2 = FieldMigration(
        from_version="1.0.0",
        to_version="2.0.0",
        schema_name="Transaction",
        default_values={
            "payment_method": "card",  # Default for new required field
            "timestamp": None,
        }
    )
    migration_chain.register(migration_v1_to_v2)
    print("\n✅ Registered migration: v1.0.0 → v2.0.0")
    print("   - Adds default payment_method='card'")
    print("   - Adds optional timestamp field")
    
    # Migration: v2 -> v3
    migration_v2_to_v3 = FieldMigration(
        from_version="2.0.0",
        to_version="3.0.0",
        schema_name="Transaction",
        field_mappings={
            "customer_id": "buyer_id",
            "merchant_id": "seller_id",
        }
    )
    migration_chain.register(migration_v2_to_v3)
    print("\n✅ Registered migration: v2.0.0 → v3.0.0")
    print("   - Renames customer_id → buyer_id")
    print("   - Renames merchant_id → seller_id")


def example_3_migrate_data():
    """Example: Migrate data between versions."""
    
    print("\n" + "="*80)
    print("EXAMPLE 3: Migrate Data Between Versions")
    print("="*80)
    
    # Old data in v1 format
    v1_data = {
        "id": "txn_123",
        "amount": "99.99",
        "currency": "USD",
        "customer_id": "cust_456",
        "merchant_id": "mch_789",
    }
    
    print("\n📥 Original data (v1.0.0):")
    for key, value in v1_data.items():
        print(f"  {key}: {value}")
    
    # Migrate v1 → v2
    v2_data = migration_chain.migrate(
        schema_name="Transaction",
        data=v1_data,
        from_version="1.0.0",
        to_version="2.0.0"
    )
    
    print("\n✅ Migrated to v2.0.0:")
    for key, value in v2_data.items():
        print(f"  {key}: {value}")
    print("  (Added payment_method with default)")
    
    # Migrate v2 → v3 (or v1 → v3 directly with chaining)
    v3_data = migration_chain.migrate(
        schema_name="Transaction",
        data=v1_data,
        from_version="1.0.0",
        to_version="3.0.0"
    )
    
    print("\n✅ Migrated directly to v3.0.0 (automatic chaining):")
    for key, value in v3_data.items():
        print(f"  {key}: {value}")
    print("  (Renamed fields and added payment_method)")


def example_4_auto_upgrade():
    """Example: Automatically upgrade to latest version."""
    
    print("\n" + "="*80)
    print("EXAMPLE 4: Auto-Upgrade to Latest")
    print("="*80)
    
    # Old data
    old_data = {
        "id": "txn_999",
        "amount": "150.00",
        "currency": "EUR",
        "customer_id": "cust_old",
        "merchant_id": "mch_old",
    }
    
    print("\n📥 Input: v1.0.0 data")
    print(f"  Data: {old_data}")
    
    # Auto-upgrade to latest
    upgraded_model, version = auto_migrator.auto_upgrade(
        schema_name="Transaction",
        data=old_data,
        data_version="1.0.0"
    )
    
    print(f"\n✅ Auto-upgraded to v{version}")
    print(f"  Model type: {type(upgraded_model).__name__}")
    print(f"  Data: {upgraded_model.model_dump()}")


def example_5_version_negotiation():
    """Example: Client-server version negotiation."""
    
    print("\n" + "="*80)
    print("EXAMPLE 5: Version Negotiation")
    print("="*80)
    
    # Client requests v1.0.0
    print("\n📞 Client requests v1.0.0")
    schema = schema_registry.negotiate_version(
        schema_name="Transaction",
        requested_version="1.0.0",
        accept_newer=True
    )
    
    if schema:
        print(f"✅ Server provides: v{schema.version}")
        if schema.version != "1.0.0":
            print(f"   (Upgraded to newer compatible version)")
    
    # Client requests v2.0.0
    print("\n📞 Client requests v2.0.0")
    schema = schema_registry.negotiate_version(
        schema_name="Transaction",
        requested_version="2.0.0",
        accept_newer=True
    )
    
    if schema:
        print(f"✅ Server provides: v{schema.version}")


def example_6_compatibility_check():
    """Example: Check compatibility between versions."""
    
    print("\n" + "="*80)
    print("EXAMPLE 6: Compatibility Checking")
    print("="*80)
    
    # Check v1 → v2 compatibility
    print("\n🔍 Checking compatibility: v1.0.0 → v2.0.0")
    is_compatible, breaking_changes = CompatibilityChecker.is_backward_compatible(
        old_schema=TransactionV1,
        new_schema=TransactionV2
    )
    
    if is_compatible:
        print("✅ Backward compatible")
    else:
        print("❌ Breaking changes detected:")
        for change in breaking_changes:
            print(f"  - {change.description}")
    
    # Check v2 → v3 compatibility
    print("\n🔍 Checking compatibility: v2.0.0 → v3.0.0")
    is_compatible, breaking_changes = CompatibilityChecker.is_backward_compatible(
        old_schema=TransactionV2,
        new_schema=TransactionV3
    )
    
    if is_compatible:
        print("✅ Backward compatible")
    else:
        print("❌ Breaking changes detected:")
        for change in breaking_changes:
            print(f"  - {change.description}")
    
    # Suggest version bump
    print("\n💡 Version bump suggestion:")
    suggested = CompatibilityChecker.suggest_version_bump(
        old_schema=TransactionV2,
        new_schema=TransactionV3,
        current_version="2.0.0"
    )
    print(f"  Current: v2.0.0")
    print(f"  Suggested: v{suggested}")
    print(f"  Reason: Breaking changes detected → major version bump")


def example_7_deprecation():
    """Example: Deprecate old versions."""
    
    print("\n" + "="*80)
    print("EXAMPLE 7: Version Deprecation")
    print("="*80)
    
    # Deprecate v1.0.0
    sunset_date = datetime.utcnow() + timedelta(days=90)
    
    schema_registry.deprecate_version(
        schema_name="Transaction",
        version="1.0.0",
        sunset_date=sunset_date
    )
    
    print("\n⚠️  Deprecated v1.0.0")
    print(f"   Sunset date: {sunset_date.strftime('%Y-%m-%d')}")
    print("   Clients should upgrade to v2.0.0+")
    
    # Check if deprecated
    schema = schema_registry.get("Transaction", "1.0.0")
    if schema.is_deprecated():
        print(f"\n✅ v1.0.0 is marked as deprecated")
        print(f"   Sunset in {(schema.version_info.sunset_date - datetime.utcnow()).days} days")


def main():
    """Run all examples."""
    
    print("\n" + "="*80)
    print("SCHEMA VERSIONING EXAMPLES")
    print("="*80)
    
    example_1_register_versions()
    example_2_define_migrations()
    example_3_migrate_data()
    example_4_auto_upgrade()
    example_5_version_negotiation()
    example_6_compatibility_check()
    example_7_deprecation()
    
    print("\n" + "="*80)
    print("✅ ALL EXAMPLES COMPLETE")
    print("="*80)
    print("\nKey Takeaways:")
    print("  1. Register multiple schema versions")
    print("  2. Define migrations between versions")
    print("  3. Auto-upgrade data to latest version")
    print("  4. Version negotiation for APIs")
    print("  5. Compatibility checking (breaking changes)")
    print("  6. Deprecation with sunset dates")
    print("  7. Semantic versioning (major.minor.patch)")
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    main()

