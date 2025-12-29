"""
Evaluation and scoring schemas.

Data structures for MLflow evaluation, custom scorers, and feedback loops.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class FeedbackSignal(str, Enum):
    """Types of feedback signals."""
    MERCHANT_APPEAL = "merchant_appeal"
    MANUAL_REVIEW = "manual_review"
    CHARGEBACK = "chargeback"
    DISPUTE_RESOLUTION = "dispute_resolution"
    FALSE_POSITIVE = "false_positive"
    FALSE_NEGATIVE = "false_negative"


class ScorerMetrics(BaseModel):
    """
    Metrics computed by MLflow custom scorers.
    
    Used to evaluate agent performance on high-risk transactions.
    """
    
    # Classification metrics
    accuracy: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    precision: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    recall: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    f1_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    
    # Fraud-specific metrics
    false_positive_rate: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    false_negative_rate: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    
    # Business metrics
    caught_fraud_value: Optional[float] = Field(
        default=None,
        ge=0,
        description="Total value of fraud caught"
    )
    missed_fraud_value: Optional[float] = Field(
        default=None,
        ge=0,
        description="Total value of fraud missed"
    )
    false_decline_value: Optional[float] = Field(
        default=None,
        ge=0,
        description="Value of legitimate transactions incorrectly declined"
    )
    
    # Narrative quality (for LLM-as-judge)
    narrative_clarity_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    narrative_completeness_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    narrative_accuracy_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "accuracy": 0.92,
                "precision": 0.88,
                "recall": 0.85,
                "f1_score": 0.865,
                "false_positive_rate": 0.08,
                "caught_fraud_value": 125000.00,
                "narrative_clarity_score": 0.91,
            }
        }


class EvaluationRecord(BaseModel):
    """
    Complete evaluation record for an agent prediction.
    
    Links agent output to ground truth, scorer metrics, and feedback signals.
    """
    
    evaluation_id: str = Field(..., description="Unique evaluation ID")
    request_id: str = Field(..., description="Associated request ID")
    transaction_id: str = Field(..., description="Associated transaction ID")
    
    # Prediction and ground truth
    predicted_action: str = Field(..., description="Agent's recommended action")
    predicted_risk_score: float = Field(..., ge=0.0, le=1.0)
    ground_truth_label: str = Field(..., description="Actual fraud label")
    
    # Evaluation outcome
    is_correct: bool = Field(..., description="Whether prediction was correct")
    is_false_positive: bool = Field(default=False)
    is_false_negative: bool = Field(default=False)
    
    # Metrics
    scorer_metrics: ScorerMetrics = Field(..., description="Computed metrics")
    
    # Feedback
    feedback_signals: list[FeedbackSignal] = Field(
        default_factory=list,
        description="Feedback signals received"
    )
    feedback_timestamp: Optional[datetime] = Field(default=None)
    feedback_notes: Optional[str] = Field(default=None)
    
    # MLflow tracking
    mlflow_run_id: Optional[str] = Field(default=None, description="Associated MLflow run")
    mlflow_experiment_id: Optional[str] = Field(default=None)
    
    # Agent details
    agent_id: str = Field(..., description="Agent that made prediction")
    model_name: str = Field(..., description="LLM model used")
    prompt_version: Optional[str] = Field(default=None, description="Prompt version from UC")
    
    # Timing
    evaluated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Additional metadata
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional evaluation metadata"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "evaluation_id": "eval_xyz789",
                "request_id": "req_abc123",
                "transaction_id": "txn_1234567890",
                "predicted_action": "review",
                "predicted_risk_score": 0.78,
                "ground_truth_label": "fraud",
                "is_correct": True,
                "is_false_positive": False,
                "is_false_negative": False,
                "scorer_metrics": {"accuracy": 0.92},
                "agent_id": "agent_narrative_xyz",
                "model_name": "meta-llama-3.1-70b-instruct",
                "prompt_version": "system_prompt_v3",
            }
        }

