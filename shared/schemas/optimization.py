"""
Optimization metadata schemas for DSPy and TextGrad.

Data structures for tracking prompt optimization, few-shot examples,
and scorer results.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class FewShotExample(BaseModel):
    """
    Few-shot example for prompt optimization.
    
    Used by DSPy BootstrapFewShot to improve task prompts.
    """
    
    example_id: str = Field(..., description="Unique example ID")
    
    # Input-output pair
    input: str = Field(..., description="Example input (transaction context)")
    output: str = Field(..., description="Desired output (risk narrative)")
    
    # Metadata
    transaction_id: Optional[str] = Field(default=None)
    fraud_label: Optional[str] = Field(default=None, description="Ground truth")
    
    quality_score: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Quality rating of this example"
    )
    
    # Usage tracking
    times_used: int = Field(default=0, ge=0)
    success_rate: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Success rate when using this example"
    )
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "example_id": "ex_001",
                "input": "Transaction: $1500 from new device, BIN country NE, IP country US...",
                "output": "HIGH RISK: BIN/IP mismatch with new device. Recommend decline.",
                "fraud_label": "fraud",
                "quality_score": 0.95,
            }
        }


class PromptVersion(BaseModel):
    """
    Versioned prompt template.
    
    Tracks prompt versions in Unity Catalog for reproducibility.
    """
    
    prompt_id: str = Field(..., description="Unique prompt identifier")
    version: str = Field(..., description="Version string (e.g., v1.3)")
    
    prompt_type: str = Field(
        ...,
        description="system, task, chain_of_thought, react"
    )
    
    content: str = Field(..., description="Actual prompt template")
    
    # Optimization provenance
    optimized_by: Optional[str] = Field(
        default=None,
        description="dspy, textgrad, manual"
    )
    optimizer_config: Dict[str, Any] = Field(
        default_factory=dict,
        description="Optimizer configuration used"
    )
    
    # Performance metrics
    avg_accuracy: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    avg_latency_ms: Optional[float] = Field(default=None, ge=0)
    
    # UC tracking
    uc_path: Optional[str] = Field(
        default=None,
        description="Unity Catalog path where stored"
    )
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "prompt_id": "system_prompt_fraud",
                "version": "v2.1",
                "prompt_type": "system",
                "content": "You are a fraud detection expert. Analyze transactions for...",
                "optimized_by": "textgrad",
                "avg_accuracy": 0.92,
                "uc_path": "main.prompts.system_fraud_v2_1",
            }
        }


class DSPyOptimizerMetadata(BaseModel):
    """
    Metadata from DSPy optimization run.
    
    Tracks task prompt optimization results and selected examples.
    """
    
    run_id: str = Field(..., description="Optimization run ID")
    transaction_id: Optional[str] = Field(
        default=None,
        description="If optimizing for specific transaction"
    )
    
    # Prompt versions used
    task_prompt_version: str = Field(..., description="Task prompt version")
    system_prompt_version: str = Field(..., description="System prompt version")
    
    # Optimizer details
    optimizer_type: str = Field(
        ...,
        description="MIPRO, COPRO, BootstrapFewShot"
    )
    
    # Scorer results
    scorer_results: Dict[str, float] = Field(
        default_factory=dict,
        description="Metric name -> score mapping"
    )
    
    # Specific metrics
    accuracy: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    relevance: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    drift_detected: bool = Field(
        default=False,
        description="Whether prompt drift detected"
    )
    action_needed: bool = Field(
        default=False,
        description="Whether re-optimization needed"
    )
    
    # Selected few-shot examples
    examples_selected: List[FewShotExample] = Field(
        default_factory=list,
        description="Few-shot examples selected for this run"
    )
    
    # MLflow tracking
    mlflow_run_id: Optional[str] = Field(default=None)
    
    optimized_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "run_id": "opt_run_123",
                "transaction_id": "txn_0001",
                "task_prompt_version": "v1.3",
                "system_prompt_version": "v2.1",
                "optimizer_type": "MIPRO",
                "scorer_results": {
                    "accuracy": 0.92,
                    "relevance": 0.87,
                    "latency": 245.5,
                },
                "accuracy": 0.92,
                "relevance": 0.87,
                "drift_detected": False,
                "action_needed": True,
                "examples_selected": [
                    {
                        "example_id": "ex_001",
                        "input": "...",
                        "output": "...",
                    }
                ],
            }
        }


class HighRiskSelectionMetadata(BaseModel):
    """
    Metadata for high-risk transaction selection.
    
    Determines which transactions get detailed MLflow scoring vs. sampling.
    """
    
    transaction_id: str = Field(...)
    
    # Selection criteria
    is_high_risk: bool = Field(..., description="Selected for detailed evaluation")
    risk_score: float = Field(..., ge=0.0, le=1.0)
    selection_threshold: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Threshold used for selection"
    )
    
    # Reasons for selection
    selection_reasons: List[str] = Field(
        default_factory=list,
        description="Why this transaction was selected"
    )
    
    # Evaluation configuration
    should_run_mlflow_scorers: bool = Field(default=False)
    should_log_detailed_trace: bool = Field(default=False)
    should_trigger_manual_review: bool = Field(default=False)
    
    # Performance optimization
    use_cached_embeddings: bool = Field(
        default=False,
        description="Whether to use prefetched embeddings from Redis"
    )
    embedding_cache_key: Optional[str] = Field(default=None)
    
    selected_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "transaction_id": "txn_0001",
                "is_high_risk": True,
                "risk_score": 0.91,
                "selection_threshold": 0.7,
                "selection_reasons": [
                    "risk_score_above_threshold",
                    "velocity_anomaly_detected",
                    "bin_ip_mismatch",
                ],
                "should_run_mlflow_scorers": True,
                "should_log_detailed_trace": True,
                "use_cached_embeddings": True,
                "embedding_cache_key": "emb:merchant:mch_001",
            }
        }


class StreamingOutput(BaseModel):
    """
    Simplified output for dashboard streaming.
    
    Lightweight structure for real-time display.
    """
    
    transaction_id: str = Field(...)
    narrative: str = Field(..., description="Concise risk narrative")
    risk_score: float = Field(..., ge=0.0, le=1.0)
    recommended_action: str = Field(..., description="approve, decline, review")
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Optional enrichment
    key_risk_factors: Optional[List[str]] = Field(default=None)
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "transaction_id": "txn_0001",
                "narrative": "BIN issued in Nigeria, merchant in US, IP from CA, 3 prior chargebacks. Strong fraud signal. Decline.",
                "risk_score": 0.91,
                "recommended_action": "decline",
                "timestamp": "2025-12-25T14:12:15Z",
                "key_risk_factors": ["BIN_MISMATCH", "CHARGEBACKS", "GEO_ANOMALY"],
                "confidence": 0.94,
            }
        }

