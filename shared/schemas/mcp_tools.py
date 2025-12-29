"""
MCP Tool Result Schemas.

Specific data structures for various MCP tool results used in fraud detection.
These represent the enrichment data returned by different MCP servers.
"""

from typing import Optional, List
from pydantic import BaseModel, Field


class BINLookupResult(BaseModel):
    """
    BIN (Bank Identification Number) lookup result.
    
    Returned by MCP enrichment server for card BIN analysis.
    """
    
    bin: str = Field(..., description="6-digit BIN")
    issuer: str = Field(..., description="Issuing bank name")
    country: str = Field(..., description="Issuing country code")
    risk_level: float = Field(..., ge=0.0, le=1.0, description="BIN risk score")
    card_type: str = Field(..., description="credit, debit, prepaid")
    card_brand: Optional[str] = Field(default=None, description="visa, mastercard, amex, etc")
    is_commercial: Optional[bool] = Field(default=None)
    
    class Config:
        json_schema_extra = {
            "example": {
                "bin": "559021",
                "issuer": "Example Bank Nigeria",
                "country": "NG",
                "risk_level": 0.91,
                "card_type": "credit",
                "card_brand": "mastercard",
                "is_commercial": False,
            }
        }


class IPGeoLookupResult(BaseModel):
    """
    IP geolocation and risk lookup result.
    
    Returned by MCP enrichment server for IP analysis.
    """
    
    ip_address: str = Field(..., description="IP address analyzed")
    country: str = Field(..., description="Detected country code")
    region: Optional[str] = Field(default=None, description="State/region")
    city: Optional[str] = Field(default=None)
    latitude: Optional[float] = Field(default=None)
    longitude: Optional[float] = Field(default=None)
    
    risk_level: float = Field(..., ge=0.0, le=1.0, description="IP risk score")
    is_vpn: bool = Field(default=False)
    is_proxy: bool = Field(default=False)
    is_tor: bool = Field(default=False)
    is_datacenter: bool = Field(default=False)
    
    isp: Optional[str] = Field(default=None, description="Internet Service Provider")
    asn: Optional[str] = Field(default=None, description="Autonomous System Number")
    
    class Config:
        json_schema_extra = {
            "example": {
                "ip_address": "192.0.2.1",
                "country": "US",
                "region": "CA",
                "city": "San Francisco",
                "risk_level": 0.1,
                "is_vpn": False,
                "is_proxy": False,
                "isp": "Example ISP",
            }
        }


class SanctionsCheckResult(BaseModel):
    """
    Sanctions and watchlist screening result.
    
    Returned by MCP enrichment server for compliance checks.
    """
    
    merchant_sanctioned: bool = Field(default=False)
    customer_sanctioned: bool = Field(default=False)
    country_watchlist_hit: bool = Field(default=False)
    
    ofac_hit: bool = Field(default=False, description="OFAC sanctions list")
    eu_sanctions_hit: bool = Field(default=False)
    un_sanctions_hit: bool = Field(default=False)
    
    watchlist_matches: List[str] = Field(
        default_factory=list,
        description="List of watchlist names with matches"
    )
    
    risk_level: float = Field(default=0.0, ge=0.0, le=1.0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "merchant_sanctioned": False,
                "customer_sanctioned": False,
                "country_watchlist_hit": False,
                "ofac_hit": False,
                "watchlist_matches": [],
                "risk_level": 0.0,
            }
        }


class VelocityAnomalyResult(BaseModel):
    """
    Real-time velocity anomaly detection result.
    
    Returned by MCP risk-calculation server.
    """
    
    deviation_factor: float = Field(
        ...,
        ge=0.0,
        description="How many standard deviations from normal"
    )
    flagged: bool = Field(..., description="Whether anomaly threshold exceeded")
    
    # Baseline metrics
    typical_hourly_txns: int = Field(..., ge=0)
    typical_daily_txns: int = Field(..., ge=0)
    typical_hourly_amount: Optional[float] = Field(default=None, ge=0)
    
    # Current metrics
    current_hour_txns: int = Field(..., ge=0)
    current_day_txns: int = Field(..., ge=0)
    current_hour_amount: Optional[float] = Field(default=None, ge=0)
    
    # Anomaly details
    anomaly_type: str = Field(
        ...,
        description="count_spike, amount_spike, merchant_diversity, geo_diversity"
    )
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "deviation_factor": 5.7,
                "flagged": True,
                "typical_hourly_txns": 2,
                "typical_daily_txns": 15,
                "current_hour_txns": 13,
                "current_day_txns": 28,
                "anomaly_type": "count_spike",
                "confidence": 0.95,
            }
        }


class MCPToolResults(BaseModel):
    """
    Aggregated MCP tool enrichment results.
    
    Contains all enrichment data fetched via MCP tools for a transaction.
    """
    
    transaction_id: str = Field(..., description="Associated transaction ID")
    
    bin_lookup: Optional[BINLookupResult] = Field(default=None)
    ip_geo_lookup: Optional[IPGeoLookupResult] = Field(default=None)
    sanctions_check: Optional[SanctionsCheckResult] = Field(default=None)
    velocity_anomaly: Optional[VelocityAnomalyResult] = Field(default=None)
    
    # Can add more tool results as needed
    additional_checks: dict = Field(
        default_factory=dict,
        description="Additional MCP tool results"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "transaction_id": "txn_0001",
                "bin_lookup": {
                    "bin": "559021",
                    "issuer": "Example Bank",
                    "country": "NG",
                    "risk_level": 0.91,
                    "card_type": "credit",
                },
                "velocity_anomaly": {
                    "deviation_factor": 5.7,
                    "flagged": True,
                    "typical_hourly_txns": 2,
                    "current_hour_txns": 13,
                },
            }
        }

