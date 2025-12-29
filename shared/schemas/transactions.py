"""
Transaction data schemas.

Core transaction data structures representing payment events that need
fraud detection analysis.
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class PaymentMethod(str, Enum):
    """Payment method types."""
    CARD = "card"
    BANK_TRANSFER = "bank_transfer"
    DIGITAL_WALLET = "digital_wallet"
    CRYPTO = "crypto"
    BUY_NOW_PAY_LATER = "bnpl"


class TransactionStatus(str, Enum):
    """Transaction processing status."""
    PENDING = "pending"
    APPROVED = "approved"
    DECLINED = "declined"
    REVIEW = "review"
    REFUNDED = "refunded"


class FraudLabel(str, Enum):
    """Ground truth fraud labels for evaluation."""
    LEGITIMATE = "legitimate"
    FRAUD = "fraud"
    DISPUTED = "disputed"
    CHARGEBACK = "chargeback"
    UNKNOWN = "unknown"


class Transaction(BaseModel):
    """
    Core transaction record.
    
    Represents a payment transaction with all relevant metadata for
    fraud detection analysis.
    """
    
    # Core identifiers
    transaction_id: str = Field(..., description="Unique transaction identifier")
    merchant_id: str = Field(..., description="Merchant identifier")
    customer_id: str = Field(..., description="Customer identifier")
    
    # Transaction details
    timestamp: datetime = Field(..., description="Transaction timestamp (UTC)")
    amount: Decimal = Field(..., ge=0, description="Transaction amount")
    currency: str = Field(..., min_length=3, max_length=3, description="ISO 4217 currency code")
    payment_method: PaymentMethod = Field(..., description="Payment method used")
    
    # Status and labeling
    status: TransactionStatus = Field(default=TransactionStatus.PENDING)
    fraud_label: FraudLabel = Field(default=FraudLabel.UNKNOWN, description="Ground truth label")
    
    # Risk scoring
    ml_risk_score: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="ML model risk score (0=safe, 1=fraud)"
    )
    
    # Device and network
    device_fingerprint: Optional[str] = Field(default=None, description="Device fingerprint hash")
    ip_address: Optional[str] = Field(default=None, description="Client IP address")
    user_agent: Optional[str] = Field(default=None, description="Client user agent")
    
    # Location
    country_code: Optional[str] = Field(default=None, min_length=2, max_length=2)
    city: Optional[str] = Field(default=None)
    latitude: Optional[float] = Field(default=None, ge=-90, le=90)
    longitude: Optional[float] = Field(default=None, ge=-180, le=180)
    
    # Additional metadata
    metadata: dict = Field(
        default_factory=dict,
        description="Additional transaction metadata"
    )
    
    @field_validator('currency')
    @classmethod
    def validate_currency_uppercase(cls, v: str) -> str:
        """Ensure currency code is uppercase."""
        return v.upper()
    
    @field_validator('country_code')
    @classmethod
    def validate_country_uppercase(cls, v: Optional[str]) -> Optional[str]:
        """Ensure country code is uppercase."""
        return v.upper() if v else None
    
    class Config:
        json_schema_extra = {
            "example": {
                "transaction_id": "txn_1234567890",
                "merchant_id": "mch_retail_001",
                "customer_id": "cust_987654321",
                "timestamp": "2025-12-25T14:30:00Z",
                "amount": "499.99",
                "currency": "GBP",
                "payment_method": "card",
                "status": "pending",
                "fraud_label": "unknown",
                "ml_risk_score": 0.72,
                "device_fingerprint": "fp_abc123def456",
                "ip_address": "203.0.113.42",
                "country_code": "GB",
                "city": "London",
            }
        }

