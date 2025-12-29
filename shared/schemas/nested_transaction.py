"""
Nested transaction schema matching actual event structure.

This provides an alternative to the normalized Transaction schema,
with nested payment_method, customer, merchant, and device objects
as they appear in real streaming events.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class PaymentMethodDetails(BaseModel):
    """Nested payment method details."""
    
    type: str = Field(..., description="card, bank_transfer, wallet, crypto")
    
    # Card-specific fields
    bin: Optional[str] = Field(default=None, description="6-digit BIN")
    last4: Optional[str] = Field(default=None, description="Last 4 digits")
    issuer_country: Optional[str] = Field(default=None, description="Issuing country")
    card_brand: Optional[str] = Field(default=None, description="visa, mastercard, etc")
    
    # Additional method details
    wallet_provider: Optional[str] = Field(default=None, description="For digital wallets")
    bank_name: Optional[str] = Field(default=None, description="For bank transfers")


class CustomerDetails(BaseModel):
    """Nested customer details in transaction event."""
    
    id: str = Field(..., description="Customer ID")
    country: Optional[str] = Field(default=None, description="Customer country")
    account_age_days: int = Field(..., ge=0)
    
    prior_disputes: int = Field(default=0, ge=0)
    email_verified: bool = Field(default=False)
    phone_verified: bool = Field(default=False)
    
    total_transaction_count: Optional[int] = Field(default=None, ge=0)


class MerchantDetails(BaseModel):
    """Nested merchant details in transaction event."""
    
    id: str = Field(..., description="Merchant ID")
    country: Optional[str] = Field(default=None, description="Merchant country")
    category: str = Field(..., description="Merchant category/MCC")
    
    avg_txn_amount_30d: Optional[float] = Field(default=None, ge=0)
    chargeback_rate_90d: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    
    is_verified: bool = Field(default=False)


class DeviceDetails(BaseModel):
    """Nested device details in transaction event."""
    
    ip: str = Field(..., description="IP address")
    fingerprint_id: str = Field(..., description="Device fingerprint ID")
    
    is_vpn: bool = Field(default=False)
    is_proxy: bool = Field(default=False)
    is_tor: bool = Field(default=False)
    
    user_agent: Optional[str] = Field(default=None)
    screen_resolution: Optional[str] = Field(default=None)


class NestedTransaction(BaseModel):
    """
    Transaction with nested payment/customer/merchant/device details.
    
    This matches the actual event structure from your data example.
    Use this for event ingestion and streaming; convert to normalized
    Transaction schema for storage/processing if needed.
    """
    
    # Core transaction fields
    id: str = Field(..., description="Transaction ID")
    timestamp: datetime = Field(..., description="Transaction timestamp (UTC)")
    amount: float = Field(..., ge=0, description="Transaction amount")
    currency: str = Field(..., min_length=3, max_length=3, description="ISO 4217 currency")
    
    # Nested objects
    payment_method: PaymentMethodDetails = Field(..., description="Payment method details")
    customer: CustomerDetails = Field(..., description="Customer details")
    merchant: MerchantDetails = Field(..., description="Merchant details")
    device: DeviceDetails = Field(..., description="Device details")
    
    # Status and risk
    status: Optional[str] = Field(default="pending", description="Transaction status")
    ml_risk_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    fraud_label: Optional[str] = Field(default="unknown", description="Ground truth if known")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "txn_0001",
                "timestamp": "2025-12-25T14:12:00Z",
                "amount": 123.45,
                "currency": "USD",
                "payment_method": {
                    "type": "card",
                    "bin": "559021",
                    "last4": "4628",
                    "issuer_country": "US",
                },
                "customer": {
                    "id": "cust_001",
                    "country": "US",
                    "account_age_days": 365,
                    "prior_disputes": 0,
                    "email_verified": True,
                },
                "merchant": {
                    "id": "mch_001",
                    "country": "US",
                    "category": "Digital Goods",
                    "avg_txn_amount_30d": 210.50,
                    "chargeback_rate_90d": 0.02,
                },
                "device": {
                    "ip": "192.0.2.1",
                    "fingerprint_id": "fp_001",
                    "is_vpn": False,
                },
                "ml_risk_score": 0.75,
            }
        }

