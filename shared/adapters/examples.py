"""
Example usage of schema adapters for multi-tenant deployment.

Demonstrates how to onboard customers with different schemas in minutes.
"""

from datetime import datetime
from decimal import Decimal

from shared.adapters import (
    DefaultTransactionAdapter,
    StripeTransactionAdapter,
    AdyenTransactionAdapter,
)
from shared.adapters.base import adapter_registry
from shared.adapters.transaction_adapters import ConfigurableTransactionAdapter


def example_1_stripe_adapter():
    """Example: Converting Stripe event to canonical schema."""
    
    print("\n" + "="*80)
    print("EXAMPLE 1: Stripe Transaction Adapter")
    print("="*80)
    
    # Stripe event (their format)
    stripe_event = {
        "id": "ch_stripe_123",
        "amount": 12345,  # Amount in cents
        "currency": "usd",
        "created": 1703520000,  # Unix timestamp
        "customer": "cus_xyz789",
        "payment_method_details": {
            "type": "card",
            "card": {
                "brand": "visa",
                "last4": "4242",
                "country": "US",
            }
        },
        "customer_data": {
            "account_age_days": 365,
            "disputes_count": 0,
            "email_verified": True,
            "phone_verified": True,
        },
        "metadata": {
            "merchant_id": "mch_tech_store",
            "merchant_country": "US",
            "merchant_category": "electronics",
            "merchant_verified": True,
        },
        "receipt_ip": "192.0.2.1",
        "status": "succeeded",
    }
    
    print("\n📥 INPUT (Stripe format):")
    print(f"  ID: {stripe_event['id']}")
    print(f"  Amount: {stripe_event['amount']} cents")
    print(f"  Currency: {stripe_event['currency']}")
    print(f"  Status: {stripe_event['status']}")
    
    # Convert to canonical format
    adapter = StripeTransactionAdapter()
    canonical_txn = adapter.to_canonical(stripe_event)
    
    print("\n✅ OUTPUT (Canonical format):")
    print(f"  ID: {canonical_txn.id}")
    print(f"  Amount: ${canonical_txn.amount} (Decimal)")
    print(f"  Currency: {canonical_txn.currency}")
    print(f"  Status: {canonical_txn.status}")
    print(f"  Payment Method: {canonical_txn.payment_method.type}")
    print(f"    - Brand: {canonical_txn.payment_method.card_brand}")
    print(f"    - Last4: {canonical_txn.payment_method.last4}")
    print(f"    - Country: {canonical_txn.payment_method.issuer_country}")
    print(f"  Customer: {canonical_txn.customer.id}")
    print(f"    - Account Age: {canonical_txn.customer.account_age_days} days")
    print(f"    - Email Verified: {canonical_txn.customer.email_verified}")
    print(f"  Merchant: {canonical_txn.merchant.id}")
    print(f"  Device IP: {canonical_txn.device.ip}")
    
    print("\n💡 Key Transformation:")
    print(f"  - Amount: 12345 cents → ${canonical_txn.amount}")
    print(f"  - Currency: 'usd' → '{canonical_txn.currency}'")
    print(f"  - Status: 'succeeded' → '{canonical_txn.status}'")
    print(f"  - Timestamp: Unix {stripe_event['created']} → {canonical_txn.timestamp}")


def example_2_configurable_adapter():
    """Example: Fully custom schema using ConfigurableAdapter."""
    
    print("\n" + "="*80)
    print("EXAMPLE 2: Custom Schema with ConfigurableAdapter")
    print("="*80)
    
    # Customer's completely custom format
    custom_event = {
        "txn": {
            "ref_number": "TXN-2025-12345",
            "event_timestamp": 1703520000,
            "total_amount_cents": 9999,
            "currency_code": "gbp",
        },
        "payment": {
            "method": "card",
            "card_details": {
                "bin_number": "411111",
                "last_four": "1111",
                "issuing_country": "GB",
                "network": "visa",
            }
        },
        "buyer": {
            "customer_id": "CUST-UK-001",
            "country": "GB",
            "account_age": 180,
            "dispute_count": 0,
            "email_status": {"verified": True},
            "phone_status": {"verified": False},
        },
        "seller": {
            "merchant_code": "MERCH-UK-RETAIL",
            "business_country": "GB",
            "mcc_code": "5411",
            "kyc_complete": True,
        },
        "session": {
            "ip_address": "81.2.69.142",
            "device_id": "dev_fingerprint_uk_001",
            "vpn_detected": False,
            "browser_agent": "Mozilla/5.0...",
        }
    }
    
    print("\n📥 INPUT (Custom format):")
    print(f"  Transaction Ref: {custom_event['txn']['ref_number']}")
    print(f"  Total (cents): {custom_event['txn']['total_amount_cents']}")
    print(f"  Currency: {custom_event['txn']['currency_code']}")
    print(f"  Card BIN: {custom_event['payment']['card_details']['bin_number']}")
    
    # Configure adapter with field mappings
    config = {
        "field_mappings": {
            "id": "txn.ref_number",
            "timestamp": "txn.event_timestamp",
            "amount": "txn.total_amount_cents",
            "currency": "txn.currency_code",
            
            "payment_method.type": "payment.method",
            "payment_method.bin": "payment.card_details.bin_number",
            "payment_method.last4": "payment.card_details.last_four",
            "payment_method.issuer_country": "payment.card_details.issuing_country",
            "payment_method.card_brand": "payment.card_details.network",
            
            "customer.id": "buyer.customer_id",
            "customer.country": "buyer.country",
            "customer.account_age_days": "buyer.account_age",
            "customer.prior_disputes": "buyer.dispute_count",
            "customer.email_verified": "buyer.email_status.verified",
            "customer.phone_verified": "buyer.phone_status.verified",
            
            "merchant.id": "seller.merchant_code",
            "merchant.country": "seller.business_country",
            "merchant.category": "seller.mcc_code",
            "merchant.is_verified": "seller.kyc_complete",
            
            "device.ip": "session.ip_address",
            "device.fingerprint_id": "session.device_id",
            "device.is_vpn": "session.vpn_detected",
            "device.user_agent": "session.browser_agent",
        },
        "transformations": {
            "amount": {"divide": 100},
            "currency": {"uppercase": True},
            "timestamp": {"from_unix": True},
        },
        "defaults": {
            "status": "pending",
            "fraud_label": "unknown",
        }
    }
    
    # Create adapter with config
    adapter = ConfigurableTransactionAdapter(config=config)
    canonical_txn = adapter.to_canonical(custom_event)
    
    print("\n✅ OUTPUT (Canonical format):")
    print(f"  ID: {canonical_txn.id}")
    print(f"  Amount: £{canonical_txn.amount}")
    print(f"  Currency: {canonical_txn.currency}")
    print(f"  Payment Method BIN: {canonical_txn.payment_method.bin}")
    print(f"  Customer: {canonical_txn.customer.id}")
    print(f"  Merchant: {canonical_txn.merchant.id}")
    print(f"  Device IP: {canonical_txn.device.ip}")
    
    print("\n💡 Key Transformations:")
    print(f"  - Field mapping: 'txn.ref_number' → 'id'")
    print(f"  - Amount: 9999 cents → £{canonical_txn.amount}")
    print(f"  - Currency: 'gbp' → '{canonical_txn.currency}'")
    print(f"  - Nested extraction: 'buyer.email_status.verified' → {canonical_txn.customer.email_verified}")


def example_3_multi_tenant_registry():
    """Example: Multi-tenant deployment with adapter registry."""
    
    print("\n" + "="*80)
    print("EXAMPLE 3: Multi-Tenant Deployment")
    print("="*80)
    
    # Register adapters for different customers
    adapter_registry.register("stripe_customer", StripeTransactionAdapter)
    adapter_registry.register("adyen_customer", AdyenTransactionAdapter, {"merchant_country": "NL"})
    adapter_registry.register("custom_customer", ConfigurableTransactionAdapter, {
        "field_mappings": {
            "id": "transaction_id",
            "amount": "amount_cents",
            "currency": "curr",
        },
        "transformations": {
            "amount": {"divide": 100},
            "currency": {"uppercase": True},
        }
    })
    
    print("\n✅ Registered Customers:")
    for customer in adapter_registry.list_customers():
        print(f"  - {customer}")
    
    # Process events for different customers
    print("\n📤 Processing Events:")
    
    # Customer 1: Stripe
    stripe_event = {
        "id": "ch_123",
        "amount": 5000,
        "currency": "usd",
        "created": 1703520000,
        "customer": "cus_abc",
        "payment_method_details": {"type": "card", "card": {"last4": "4242"}},
        "customer_data": {},
        "metadata": {},
    }
    
    adapter = adapter_registry.get_adapter("stripe_customer")
    txn = adapter.to_canonical(stripe_event)
    print(f"\n  Stripe Customer:")
    print(f"    Input ID: {stripe_event['id']}")
    print(f"    Canonical ID: {txn.id}")
    print(f"    Amount: ${txn.amount}")
    
    # Customer 2: Custom
    custom_event = {
        "transaction_id": "TXN-999",
        "amount_cents": 7500,
        "curr": "eur",
    }
    
    adapter = adapter_registry.get_adapter("custom_customer")
    txn = adapter.to_canonical(custom_event)
    print(f"\n  Custom Customer:")
    print(f"    Input ID: {custom_event['transaction_id']}")
    print(f"    Canonical ID: {txn.id}")
    print(f"    Amount: €{txn.amount}")
    
    print("\n💡 Key Benefit:")
    print("  Same core logic processes all customers!")
    print("  Add new customer = Add config file (no code changes)")


def example_4_deployment_time():
    """Example: Calculate time to deploy to new customer."""
    
    print("\n" + "="*80)
    print("EXAMPLE 4: Deployment Time Calculation")
    print("="*80)
    
    print("\n⏱️  Time to Deploy to New Customer:")
    print("\n  Step 1: Analyze customer schema")
    print("    Time: 5 minutes")
    print("    Action: Review sample events, identify field mappings")
    
    print("\n  Step 2: Create adapter config")
    print("    Time: 5-10 minutes")
    print("    Action: Write YAML config with field mappings")
    
    print("\n  Step 3: Test with sample data")
    print("    Time: 2-3 minutes")
    print("    Action: Validate transformations work correctly")
    
    print("\n  Step 4: Deploy to production")
    print("    Time: 1 minute")
    print("    Action: Load config, no code changes needed")
    
    print("\n  ✅ TOTAL TIME: ~15 minutes")
    print("\n  Compare to:")
    print("    - Without adapters: 1-2 weeks (custom code per customer)")
    print("    - With adapters: 15 minutes (config file only)")
    print("\n  🚀 100x faster deployment!")


def main():
    """Run all examples."""
    
    print("\n" + "="*80)
    print("SCHEMA ADAPTER EXAMPLES")
    print("Rapid Multi-Tenant Deployment")
    print("="*80)
    
    example_1_stripe_adapter()
    example_2_configurable_adapter()
    example_3_multi_tenant_registry()
    example_4_deployment_time()
    
    print("\n" + "="*80)
    print("✅ ALL EXAMPLES COMPLETE")
    print("="*80)
    print("\nKey Takeaways:")
    print("  1. Pre-built adapters for common providers (Stripe, Adyen)")
    print("  2. ConfigurableAdapter for any custom schema")
    print("  3. Adapter registry for multi-tenant deployment")
    print("  4. ~15 minutes to onboard new customer")
    print("  5. Core logic remains unchanged across all customers")
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    main()

