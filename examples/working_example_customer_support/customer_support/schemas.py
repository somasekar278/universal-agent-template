"""
Customer Support domain-specific schemas.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class TicketPriority(str, Enum):
    """Ticket priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TicketCategory(str, Enum):
    """Ticket categories."""
    TECHNICAL = "technical"
    BILLING = "billing"
    ACCOUNT = "account"
    FEATURE_REQUEST = "feature_request"
    BUG_REPORT = "bug_report"
    GENERAL = "general"


class SupportTicket(BaseModel):
    """Customer support ticket."""
    
    ticket_id: str = Field(..., description="Unique ticket identifier")
    customer_id: str = Field(..., description="Customer identifier")
    subject: str = Field(..., description="Ticket subject")
    description: str = Field(..., description="Ticket description/body")
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Optional metadata
    customer_tier: Optional[str] = Field(None, description="Customer tier (free, pro, enterprise)")
    previous_tickets: int = Field(0, description="Number of previous tickets")
    account_age_days: int = Field(0, description="Account age in days")
    
    def __str__(self):
        return f"Ticket {self.ticket_id}: {self.subject}"


class TicketClassification(BaseModel):
    """Result of ticket classification."""
    
    category: TicketCategory
    priority: TicketPriority
    urgency_score: float = Field(..., ge=0.0, le=1.0, description="Urgency score 0-1")
    estimated_resolution_time: int = Field(..., description="Estimated time to resolve in minutes")
    confidence: float = Field(..., ge=0.0, le=1.0)


class SentimentAnalysis(BaseModel):
    """Sentiment analysis result."""
    
    sentiment: str = Field(..., description="Overall sentiment (positive, neutral, negative)")
    sentiment_score: float = Field(..., ge=-1.0, le=1.0, description="Sentiment score -1 to 1")
    emotions: List[str] = Field(default_factory=list, description="Detected emotions")
    frustration_level: float = Field(..., ge=0.0, le=1.0, description="Frustration level 0-1")


class SuggestedResponse(BaseModel):
    """Suggested response for the ticket."""
    
    response_text: str
    tone: str = Field(..., description="Response tone (empathetic, professional, friendly)")
    includes_escalation: bool = Field(False, description="Whether to escalate")
    recommended_actions: List[str] = Field(default_factory=list)
    confidence: float = Field(..., ge=0.0, le=1.0)

