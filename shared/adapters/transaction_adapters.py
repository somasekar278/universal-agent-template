"""
Transaction schema adapters for different payment processors.

These adapters show how to quickly adapt to different customer schemas
while keeping core logic unchanged.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict

from shared.schemas import (
    NestedTransaction,
    PaymentMethodDetails,
    CustomerDetails,
    MerchantDetails,
    DeviceDetails,
)
from .base import SchemaAdapter


class DefaultTransactionAdapter(SchemaAdapter[NestedTransaction, Dict[str, Any]]):
    """
    Default adapter for our canonical NestedTransaction schema.
    
    Use this when customer data already matches our schema.
    """
    
    def to_canonical(self, source: Dict[str, Any]) -> NestedTransaction:
        """Direct validation - customer schema matches ours."""
        return NestedTransaction.model_validate(source)
    
    def from_canonical(self, target: NestedTransaction) -> Dict[str, Any]:
        """Direct serialization."""
        return target.model_dump(exclude_none=True)


class StripeTransactionAdapter(SchemaAdapter[NestedTransaction, Dict[str, Any]]):
    """
    Adapter for Stripe payment events.
    
    Converts Stripe's schema to our canonical NestedTransaction.
    
    Example Stripe event:
    {
        "id": "ch_abc123",
        "amount": 12345,  # cents
        "currency": "usd",
        "payment_method_details": {
            "type": "card",
            "card": {
                "brand": "visa",
                "last4": "4242",
                "country": "US"
            }
        },
        "customer": "cus_xyz",
        "metadata": {...}
    }
    """
    
    def to_canonical(self, source: Dict[str, Any]) -> NestedTransaction:
        """Convert Stripe event to canonical schema."""
        
        # Extract payment method details
        pm_details = source.get("payment_method_details", {})
        card_details = pm_details.get("card", {})
        
        payment_method = PaymentMethodDetails(
            type="card",
            bin=self._get_nested_value(source, "payment_method.card.bin"),
            last4=card_details.get("last4"),
            issuer_country=card_details.get("country"),
            card_brand=card_details.get("brand"),
        )
        
        # Extract customer details
        customer_data = source.get("customer_data", {})
        customer = CustomerDetails(
            id=source.get("customer", "unknown"),
            country=customer_data.get("address", {}).get("country"),
            account_age_days=customer_data.get("account_age_days", 0),
            prior_disputes=customer_data.get("disputes_count", 0),
            email_verified=customer_data.get("email_verified", False),
            phone_verified=customer_data.get("phone_verified", False),
        )
        
        # Extract merchant details
        metadata = source.get("metadata", {})
        merchant = MerchantDetails(
            id=metadata.get("merchant_id", "unknown"),
            country=metadata.get("merchant_country"),
            category=metadata.get("merchant_category", "unknown"),
            is_verified=metadata.get("merchant_verified", False),
        )
        
        # Extract device details
        device = DeviceDetails(
            ip=source.get("receipt_ip", "0.0.0.0"),
            fingerprint_id=source.get("payment_method", {}).get("fingerprint", "unknown"),
            is_vpn=False,  # Stripe doesn't provide this
        )
        
        # Convert amount from cents to decimal
        amount = Decimal(source.get("amount", 0)) / 100
        
        return NestedTransaction(
            id=source["id"],
            timestamp=datetime.fromtimestamp(source.get("created", 0)),
            amount=amount,
            currency=source.get("currency", "usd").upper(),
            payment_method=payment_method,
            customer=customer,
            merchant=merchant,
            device=device,
            status=self._map_stripe_status(source.get("status")),
            fraud_label="unknown",
        )
    
    def from_canonical(self, target: NestedTransaction) -> Dict[str, Any]:
        """Convert canonical schema back to Stripe format."""
        return {
            "id": target.id,
            "amount": int(target.amount * 100),  # Convert to cents
            "currency": target.currency.lower(),
            "created": int(target.timestamp.timestamp()),
            "customer": target.customer.id,
            "payment_method_details": {
                "type": target.payment_method.type,
                "card": {
                    "last4": target.payment_method.last4,
                    "brand": target.payment_method.card_brand,
                    "country": target.payment_method.issuer_country,
                }
            },
            "metadata": {
                "merchant_id": target.merchant.id,
                "merchant_country": target.merchant.country,
            }
        }
    
    def _map_stripe_status(self, stripe_status: str) -> str:
        """Map Stripe status to our canonical status."""
        mapping = {
            "succeeded": "approved",
            "pending": "pending",
            "failed": "declined",
            "requires_action": "review",
        }
        return mapping.get(stripe_status, "pending")


class AdyenTransactionAdapter(SchemaAdapter[NestedTransaction, Dict[str, Any]]):
    """
    Adapter for Adyen payment notifications.
    
    Example Adyen notification:
    {
        "pspReference": "8535296650153317",
        "originalReference": null,
        "merchantAccountCode": "YourMerchantAccount",
        "merchantReference": "YOUR_REFERENCE",
        "value": 1000,  # cents
        "currency": "EUR",
        "eventCode": "AUTHORISATION",
        "success": "true",
        "paymentMethod": "visa",
        "additionalData": {
            "cardBin": "411111",
            "cardSummary": "1111",
            "expiryDate": "03/2030"
        }
    }
    """
    
    def to_canonical(self, source: Dict[str, Any]) -> NestedTransaction:
        """Convert Adyen notification to canonical schema."""
        
        additional_data = source.get("additionalData", {})
        
        payment_method = PaymentMethodDetails(
            type="card",
            bin=additional_data.get("cardBin"),
            last4=additional_data.get("cardSummary"),
            issuer_country=additional_data.get("issuerCountry"),
            card_brand=source.get("paymentMethod"),
        )
        
        # Extract from config or additional data
        customer = CustomerDetails(
            id=source.get("shopperReference", "unknown"),
            country=source.get("shopperCountry"),
            account_age_days=self.config.get("customer_account_age_days", 0),
            prior_disputes=0,  # Not in Adyen notification
            email_verified=False,
        )
        
        merchant = MerchantDetails(
            id=source.get("merchantAccountCode", "unknown"),
            country=self.config.get("merchant_country"),
            category=self.config.get("merchant_category", "unknown"),
            is_verified=True,
        )
        
        device = DeviceDetails(
            ip=additional_data.get("shopperIP", "0.0.0.0"),
            fingerprint_id=additional_data.get("deviceFingerprint", "unknown"),
            is_vpn=False,
        )
        
        amount = Decimal(source.get("value", 0)) / 100
        
        return NestedTransaction(
            id=source["pspReference"],
            timestamp=datetime.fromtimestamp(
                int(source.get("eventDate", datetime.now().timestamp()))
            ),
            amount=amount,
            currency=source.get("currency", "EUR"),
            payment_method=payment_method,
            customer=customer,
            merchant=merchant,
            device=device,
            status=self._map_adyen_status(source.get("eventCode"), source.get("success")),
        )
    
    def from_canonical(self, target: NestedTransaction) -> Dict[str, Any]:
        """Convert canonical schema back to Adyen format."""
        return {
            "pspReference": target.id,
            "merchantAccountCode": target.merchant.id,
            "value": int(target.amount * 100),
            "currency": target.currency,
            "paymentMethod": target.payment_method.card_brand,
            "additionalData": {
                "cardBin": target.payment_method.bin,
                "cardSummary": target.payment_method.last4,
                "shopperIP": target.device.ip,
            }
        }
    
    def _map_adyen_status(self, event_code: str, success: str) -> str:
        """Map Adyen event code to our canonical status."""
        if event_code == "AUTHORISATION":
            return "approved" if success == "true" else "declined"
        elif event_code == "PENDING":
            return "pending"
        elif event_code == "FRAUD_REVIEW":
            return "review"
        return "pending"


class ConfigurableTransactionAdapter(SchemaAdapter[NestedTransaction, Dict[str, Any]]):
    """
    Fully configurable adapter using field mapping configuration.
    
    This adapter can handle ANY customer schema by providing field mappings
    in the configuration. Perfect for rapid customer onboarding.
    
    Config example:
    {
        "field_mappings": {
            "id": "transaction.id",
            "timestamp": "transaction.created_at",
            "amount": "transaction.amount_cents",
            "currency": "transaction.currency_code",
            "payment_method.type": "payment.method",
            "payment_method.bin": "payment.card.bin_number",
            "customer.id": "buyer.customer_id",
        },
        "transformations": {
            "amount": {"divide": 100},  # Convert cents to decimal
            "currency": {"uppercase": true},
            "timestamp": {"from_unix": true}
        },
        "defaults": {
            "device.is_vpn": false,
            "customer.prior_disputes": 0
        }
    }
    """
    
    def to_canonical(self, source: Dict[str, Any]) -> NestedTransaction:
        """Convert using configuration-based field mappings."""
        
        field_mappings = self.config.get("field_mappings", {})
        transformations = self.config.get("transformations", {})
        defaults = self.config.get("defaults", {})
        
        # Build canonical dict from source using mappings
        canonical_dict = {}
        
        for target_field, source_path in field_mappings.items():
            value = self._get_nested_value(source, source_path)
            
            # Apply transformations
            if target_field in transformations:
                value = self._apply_transformation(value, transformations[target_field])
            
            if value is not None:
                self._set_nested_value(canonical_dict, target_field, value)
        
        # Apply defaults for missing fields
        for field, default_value in defaults.items():
            if self._get_nested_value(canonical_dict, field) is None:
                self._set_nested_value(canonical_dict, field, default_value)
        
        # Validate and construct nested transaction
        return NestedTransaction.model_validate(canonical_dict)
    
    def from_canonical(self, target: NestedTransaction) -> Dict[str, Any]:
        """Reverse mapping from canonical to customer schema."""
        
        field_mappings = self.config.get("field_mappings", {})
        target_dict = target.model_dump()
        source_dict = {}
        
        # Reverse the mapping
        for target_field, source_path in field_mappings.items():
            value = self._get_nested_value(target_dict, target_field)
            if value is not None:
                self._set_nested_value(source_dict, source_path, value)
        
        return source_dict
    
    def _apply_transformation(self, value: Any, transform: Dict[str, Any]) -> Any:
        """Apply transformation rules to a value."""
        
        if "divide" in transform:
            value = Decimal(str(value)) / transform["divide"]
        
        if "multiply" in transform:
            value = Decimal(str(value)) * transform["multiply"]
        
        if "uppercase" in transform and transform["uppercase"]:
            value = str(value).upper()
        
        if "lowercase" in transform and transform["lowercase"]:
            value = str(value).lower()
        
        if "from_unix" in transform and transform["from_unix"]:
            value = datetime.fromtimestamp(int(value))
        
        if "to_unix" in transform and transform["to_unix"]:
            value = int(value.timestamp())
        
        return value

