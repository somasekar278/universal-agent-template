"""
Embedding and vector schemas for Lakebase integration.

Data structures for vector embeddings used in RAG, semantic search,
and conversation memory.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class Embedding(BaseModel):
    """
    Vector embedding representation.
    
    Used for semantic search, similarity matching, and RAG in Lakebase.
    """
    
    vector: List[float] = Field(
        ...,
        description="Embedding vector (typically 768 or 1536 dimensions)"
    )
    
    model_name: str = Field(
        default="text-embedding-ada-002",
        description="Embedding model used"
    )
    
    dimension: int = Field(..., ge=1, description="Vector dimension")
    
    def __len__(self) -> int:
        """Return embedding dimension."""
        return len(self.vector)
    
    class Config:
        json_schema_extra = {
            "example": {
                "vector": [0.12, 0.34, 0.56, 0.78],  # Truncated for brevity
                "model_name": "text-embedding-ada-002",
                "dimension": 1536,
            }
        }


class ConversationMessage(BaseModel):
    """
    Individual message in agent conversation history.
    
    Stored in Lakebase with embeddings for semantic retrieval.
    """
    
    message_id: str = Field(..., description="Unique message ID")
    timestamp: datetime = Field(..., description="Message timestamp")
    
    role: str = Field(..., description="system, agent, tool, user")
    content: str = Field(..., description="Message content")
    
    embedding: Optional[Embedding] = Field(
        default=None,
        description="Semantic embedding of message content"
    )
    
    # Context
    transaction_id: Optional[str] = Field(default=None)
    tool_call_id: Optional[str] = Field(
        default=None,
        description="If this is a tool result message"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "message_id": "msg_001",
                "timestamp": "2025-12-25T14:12:10Z",
                "role": "agent",
                "content": "IP and BIN mismatch detected, flagged for fraud.",
                "embedding": {
                    "vector": [0.21, 0.43, 0.78],
                    "dimension": 1536,
                },
                "transaction_id": "txn_0001",
            }
        }


class ConversationHistory(BaseModel):
    """
    Complete conversation history for an agent execution.
    
    Stored in Lakebase for conversation memory and retrieval.
    """
    
    agent_id: str = Field(..., description="Agent identifier")
    transaction_id: str = Field(..., description="Associated transaction")
    
    messages: List[ConversationMessage] = Field(
        default_factory=list,
        description="Ordered list of conversation messages"
    )
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Summary embedding for entire conversation
    conversation_embedding: Optional[Embedding] = Field(
        default=None,
        description="Embedding of entire conversation for similarity search"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "agent_id": "narrative_agent_001",
                "transaction_id": "txn_0001",
                "messages": [
                    {
                        "message_id": "msg_001",
                        "timestamp": "2025-12-25T14:12:10Z",
                        "role": "agent",
                        "content": "IP and BIN mismatch detected.",
                    }
                ],
            }
        }


class MerchantContextWithEmbedding(BaseModel):
    """
    Merchant context enriched with embedding for similarity search.
    
    Extends base merchant context with vector representation.
    """
    
    merchant_id: str = Field(...)
    merchant_risk_tier: str = Field(...)
    
    weekly_velocity: int = Field(default=0, ge=0)
    usual_top_countries: List[str] = Field(default_factory=list)
    recent_chargebacks_7d: int = Field(default=0, ge=0)
    
    avg_txn_amount_30d: Optional[float] = Field(default=None, ge=0)
    chargeback_rate_90d: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    
    # Embedding for merchant profile
    embedding: Optional[Embedding] = Field(
        default=None,
        description="Embedding of merchant profile for similarity search"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "merchant_id": "mch_001",
                "merchant_risk_tier": "medium",
                "weekly_velocity": 143,
                "usual_top_countries": ["US", "CA", "UK"],
                "recent_chargebacks_7d": 2,
                "avg_txn_amount_30d": 210.50,
                "chargeback_rate_90d": 0.02,
                "embedding": {
                    "vector": [0.12, 0.34, 0.56],
                    "dimension": 768,
                },
            }
        }


class CustomerContextWithEmbedding(BaseModel):
    """
    Customer context enriched with embedding for similarity search.
    """
    
    customer_id: str = Field(...)
    account_age_days: int = Field(..., ge=0)
    
    prior_disputes: int = Field(default=0, ge=0)
    email_verified: bool = Field(default=False)
    phone_verified: bool = Field(default=False)
    
    typical_transaction_amount: Optional[float] = Field(default=None, ge=0)
    transaction_count_30d: int = Field(default=0, ge=0)
    
    # Embedding for customer behavior profile
    embedding: Optional[Embedding] = Field(
        default=None,
        description="Embedding of customer behavior for similarity search"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "customer_id": "cust_001",
                "account_age_days": 365,
                "prior_disputes": 0,
                "email_verified": True,
                "phone_verified": True,
                "embedding": {
                    "vector": [0.45, 0.67, 0.89],
                    "dimension": 768,
                },
            }
        }


class SimilarCaseResult(BaseModel):
    """
    Similar fraud case retrieved from Lakebase via vector similarity.
    
    Used for few-shot learning and context augmentation.
    """
    
    case_id: str = Field(..., description="Historical case ID")
    transaction_id: str = Field(..., description="Historical transaction ID")
    
    similarity_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Cosine similarity to current case"
    )
    
    # Historical case details
    fraud_label: str = Field(..., description="Ground truth label")
    agent_decision: str = Field(..., description="Agent's decision")
    was_correct: bool = Field(..., description="Whether agent was correct")
    
    # Case summary
    case_summary: str = Field(..., description="Brief case description")
    risk_factors: List[str] = Field(default_factory=list)
    
    embedding: Embedding = Field(..., description="Case embedding")
    
    class Config:
        json_schema_extra = {
            "example": {
                "case_id": "case_hist_123",
                "transaction_id": "txn_hist_456",
                "similarity_score": 0.89,
                "fraud_label": "fraud",
                "agent_decision": "decline",
                "was_correct": True,
                "case_summary": "BIN/IP country mismatch, velocity spike",
                "risk_factors": ["BIN_MISMATCH", "VELOCITY_ANOMALY"],
            }
        }

