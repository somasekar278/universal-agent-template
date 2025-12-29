"""
Fraud signal schemas.

Data structures representing various fraud detection signals and indicators
that feed into agent reasoning.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field


class VelocitySignal(BaseModel):
    """Transaction velocity indicators."""
    
    transactions_last_hour: int = Field(default=0, ge=0)
    transactions_last_day: int = Field(default=0, ge=0)
    transactions_last_week: int = Field(default=0, ge=0)
    
    total_amount_last_hour: Decimal = Field(default=Decimal("0"), ge=0)
    total_amount_last_day: Decimal = Field(default=Decimal("0"), ge=0)
    
    unique_merchants_last_day: int = Field(default=0, ge=0)
    unique_countries_last_day: int = Field(default=0, ge=0)
    
    # Velocity anomaly flags
    is_velocity_anomaly: bool = Field(default=False)
    velocity_score: float = Field(default=0.0, ge=0.0, le=1.0)


class AmountAnomalySignal(BaseModel):
    """Transaction amount anomaly indicators."""
    
    customer_avg_transaction: Optional[Decimal] = Field(default=None, ge=0)
    customer_max_transaction: Optional[Decimal] = Field(default=None, ge=0)
    merchant_avg_transaction: Optional[Decimal] = Field(default=None, ge=0)
    
    # Anomaly scoring
    is_amount_anomaly: bool = Field(default=False)
    amount_z_score: Optional[float] = Field(default=None, description="Z-score vs customer history")
    amount_percentile: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=100.0,
        description="Percentile vs customer history"
    )


class LocationSignal(BaseModel):
    """Geographic and location-based signals."""
    
    customer_home_country: Optional[str] = Field(default=None)
    customer_recent_countries: List[str] = Field(default_factory=list)
    
    distance_from_last_transaction_km: Optional[float] = Field(default=None, ge=0)
    time_since_last_transaction_seconds: Optional[float] = Field(default=None, ge=0)
    
    # Location anomaly flags
    is_location_mismatch: bool = Field(default=False)
    is_impossible_travel: bool = Field(
        default=False,
        description="Transaction location impossible given time since last txn"
    )
    location_risk_score: float = Field(default=0.0, ge=0.0, le=1.0)


class DeviceSignal(BaseModel):
    """Device and browser fingerprinting signals."""
    
    device_id: Optional[str] = Field(default=None)
    is_new_device: bool = Field(default=False)
    device_age_days: Optional[int] = Field(default=None, ge=0)
    
    device_transaction_count: int = Field(default=0, ge=0)
    device_customer_count: int = Field(
        default=1,
        ge=1,
        description="Number of customers using this device"
    )
    
    # Device risk flags
    is_device_anomaly: bool = Field(default=False)
    is_device_shared: bool = Field(default=False, description="Device used by multiple customers")
    device_risk_score: float = Field(default=0.0, ge=0.0, le=1.0)


class FraudSignals(BaseModel):
    """
    Aggregated fraud signals for a transaction.
    
    Combines multiple signal types into a comprehensive fraud indicator set
    that agents can reason over.
    """
    
    transaction_id: str = Field(..., description="Associated transaction ID")
    computed_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Signal categories
    velocity: VelocitySignal = Field(default_factory=VelocitySignal)
    amount_anomaly: AmountAnomalySignal = Field(default_factory=AmountAnomalySignal)
    location: LocationSignal = Field(default_factory=LocationSignal)
    device: DeviceSignal = Field(default_factory=DeviceSignal)
    
    # Rules triggered
    rules_triggered: List[str] = Field(
        default_factory=list,
        description="List of fraud rule names that triggered"
    )
    
    # Composite scores
    overall_signal_strength: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Composite signal strength score"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "transaction_id": "txn_1234567890",
                "computed_at": "2025-12-25T14:30:05Z",
                "velocity": {
                    "transactions_last_hour": 5,
                    "transactions_last_day": 12,
                    "total_amount_last_day": "2450.00",
                    "is_velocity_anomaly": True,
                    "velocity_score": 0.85,
                },
                "rules_triggered": ["HIGH_VELOCITY", "NEW_DEVICE", "LOCATION_MISMATCH"],
                "overall_signal_strength": 0.78,
            }
        }

