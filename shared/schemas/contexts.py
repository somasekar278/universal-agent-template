"""
Context schemas for merchants and customers.

Contextual information that agents retrieve to inform their fraud analysis.
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field


class MerchantRiskTier(str, Enum):
    """Merchant risk categorization."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class MerchantContext(BaseModel):
    """
    Merchant profile and historical context.
    
    Information about the merchant that helps agents assess transaction risk
    in the context of the merchant's business patterns.
    """
    
    merchant_id: str = Field(..., description="Merchant identifier")
    
    # Business info
    business_name: str = Field(..., description="Merchant business name")
    merchant_category: str = Field(..., description="MCC or business category")
    risk_tier: MerchantRiskTier = Field(..., description="Assigned risk tier")
    
    # Account details
    account_created_at: datetime = Field(..., description="Merchant account creation date")
    account_age_days: int = Field(..., ge=0)
    is_verified: bool = Field(default=False)
    
    # Transaction history
    total_transactions: int = Field(default=0, ge=0)
    total_volume: Decimal = Field(default=Decimal("0"), ge=0)
    avg_transaction_amount: Optional[Decimal] = Field(default=None, ge=0)
    
    # Risk metrics
    chargeback_count: int = Field(default=0, ge=0)
    chargeback_rate: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Chargeback rate (0-1)"
    )
    fraud_incident_count: int = Field(default=0, ge=0)
    
    # Geographic focus
    primary_countries: List[str] = Field(
        default_factory=list,
        description="Primary countries of operation"
    )
    
    # Recent activity
    transactions_last_30_days: int = Field(default=0, ge=0)
    volume_last_30_days: Decimal = Field(default=Decimal("0"), ge=0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "merchant_id": "mch_retail_001",
                "business_name": "Premium Electronics Ltd",
                "merchant_category": "electronics_retail",
                "risk_tier": "medium",
                "account_created_at": "2023-06-15T00:00:00Z",
                "account_age_days": 558,
                "is_verified": True,
                "total_transactions": 15420,
                "total_volume": "3250000.00",
                "avg_transaction_amount": "210.75",
                "chargeback_rate": 0.012,
                "primary_countries": ["GB", "FR", "DE"],
            }
        }


class CustomerContext(BaseModel):
    """
    Customer profile and behavioral context.
    
    Historical information about the customer's transaction patterns and
    risk indicators.
    """
    
    customer_id: str = Field(..., description="Customer identifier")
    
    # Account details
    account_created_at: datetime = Field(..., description="Customer account creation date")
    account_age_days: int = Field(..., ge=0)
    email_verified: bool = Field(default=False)
    phone_verified: bool = Field(default=False)
    
    # Transaction history
    total_transactions: int = Field(default=0, ge=0)
    successful_transactions: int = Field(default=0, ge=0)
    declined_transactions: int = Field(default=0, ge=0)
    
    total_spend: Decimal = Field(default=Decimal("0"), ge=0)
    avg_transaction_amount: Optional[Decimal] = Field(default=None, ge=0)
    max_transaction_amount: Optional[Decimal] = Field(default=None, ge=0)
    
    # Behavioral patterns
    preferred_payment_methods: List[str] = Field(default_factory=list)
    transaction_countries: List[str] = Field(
        default_factory=list,
        description="Countries where customer has transacted"
    )
    home_country: Optional[str] = Field(default=None)
    
    # Device history
    known_devices: int = Field(default=0, ge=0)
    known_ip_addresses: int = Field(default=0, ge=0)
    
    # Risk indicators
    fraud_incidents: int = Field(default=0, ge=0)
    disputes_filed: int = Field(default=0, ge=0)
    chargebacks: int = Field(default=0, ge=0)
    
    # Recent activity
    last_transaction_at: Optional[datetime] = Field(default=None)
    transactions_last_30_days: int = Field(default=0, ge=0)
    spend_last_30_days: Decimal = Field(default=Decimal("0"), ge=0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "customer_id": "cust_987654321",
                "account_created_at": "2024-03-10T00:00:00Z",
                "account_age_days": 290,
                "email_verified": True,
                "phone_verified": True,
                "total_transactions": 47,
                "successful_transactions": 45,
                "total_spend": "8940.50",
                "avg_transaction_amount": "190.22",
                "preferred_payment_methods": ["card"],
                "transaction_countries": ["GB"],
                "home_country": "GB",
                "known_devices": 2,
                "fraud_incidents": 0,
            }
        }

