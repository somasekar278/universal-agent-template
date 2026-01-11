"""
Human Feedback to Prompt Optimization

Bridges the gap between human feedback on production outputs and GEPA optimization.
Eliminates the need for LLM judges when you have direct human feedback.

Based on the observation that:
- GEPA requires: {"inputs": {...}, "expectations": {"expected_response": ...}}
- MLflow provides: Traces with human feedback assessments
- Gap: No direct path from human feedback → optimized prompts (without judges)

This module provides that direct path.
"""

from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
import mlflow
from mlflow.entities import AssessmentSource, AssessmentSourceType
from mlflow.entities.trace import Trace
from mlflow.genai.scorers import scorer
from .gepa_optimizer import GepaOptimizer, GepaResult


# Note: SME ratings alone (without corrections) cannot be used directly for GEPA.
# You must first align a judge using those ratings, then use the aligned judge for GEPA.
# See: https://docs.databricks.com/aws/en/mlflow3/genai/eval-monitor/align-judges
#
# Valid optimization paths:
# 1. SME Corrections → GEPA (direct path, use optimize_from_feedback with corrected_output)
# 2. SME Ratings → Align Judges → GEPA (indirect path, requires judge alignment first)


@dataclass
class HumanFeedback:
    """Human feedback on an agent output."""
    trace_id: str
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    human_assessment: str  # e.g., "excellent", "good", "poor"
    human_rationale: Optional[str] = None
    corrected_output: Optional[str] = None  # SME's corrected version
    timestamp: datetime = field(default_factory=datetime.now)


class HumanFeedbackOptimizer:
    """
    Optimize prompts from human feedback (corrections, not just ratings).

    Important: This optimizer requires SMEs to provide CORRECTED OUTPUTS, not just ratings!

    Valid paths for optimization:
    1. ✅ SME Corrections → GEPA (use this class)
    2. ✅ SME Ratings → Align Judges → GEPA (use Databricks Align Judges first)
    3. ❌ SME Ratings → GEPA (NOT POSSIBLE without judge alignment)

    Why ratings alone don't work:
    - GEPA needs ground truth (what the output SHOULD be)
    - Ratings tell you an output is "poor" but not what "excellent" looks like
    - Must either have corrections OR train a judge to evaluate quality

    Usage:
        # Collect human feedback WITH corrections
        feedback = [
            {
                "trace_id": "...",
                "inputs": {"question": "..."},
                "outputs": {"answer": "..."},
                "human_assessment": "poor",
                "corrected_output": "Better answer here"  # Required!
            }
        ]

        # Optimize directly
        optimizer = HumanFeedbackOptimizer()
        result = optimizer.optimize_from_feedback(
            predict_fn=my_agent,
            feedback=feedback,
            prompt_uris=["prompts:/my_agent/1"]
        )

    For ratings-only workflow:
        See: https://docs.databricks.com/aws/en/mlflow3/genai/eval-monitor/align-judges
    """

    def __init__(
        self,
        gepa_reflection_model: str = "databricks-claude-sonnet-4",
        gepa_max_calls: int = 100
    ):
        """
        Initialize human feedback optimizer.

        Args:
            gepa_reflection_model: Model for GEPA reflection
            gepa_max_calls: Max optimization iterations
        """
        self.gepa_optimizer = GepaOptimizer(
            reflection_model=gepa_reflection_model,
            max_metric_calls=gepa_max_calls
        )


    def optimize_from_feedback(
        self,
        predict_fn: Callable,
        feedback: List[Dict[str, Any]],
        prompt_uris: List[str],
        feedback_strategy: str = "corrected",
        quality_threshold: Optional[str] = None,
        **kwargs
    ) -> GepaResult:
        """
        Optimize prompts directly from human feedback.

        Args:
            predict_fn: Agent function to optimize
            feedback: List of human feedback dicts with:
                - inputs: Agent inputs
                - outputs: Agent outputs
                - human_assessment: Rating (excellent/good/fair/poor)
                - corrected_output: (Optional) SME's corrected version
                - human_rationale: (Optional) Explanation
            prompt_uris: Prompts to optimize
            feedback_strategy: How to use feedback:
                - "corrected": Use SME-corrected outputs as ground truth (requires corrected_output)
                - "positive": Use highly-rated outputs as-is (assumes they're good enough)
                - "negative": Learn from corrections of poor outputs only
            quality_threshold: Filter feedback (e.g., "good" = keep good+ only)
            **kwargs: Additional GEPA arguments

        Important:
            This method requires actual corrected outputs (ground truth), not just ratings!

            If you only have ratings (no corrections):
            1. Use Databricks Align Judges to train a judge from ratings
            2. Use the aligned judge to score outputs
            3. Then use GEPA with the judge-scored outputs

            See: https://docs.databricks.com/aws/en/mlflow3/genai/eval-monitor/align-judges

        Returns:
            GepaResult with optimized prompts

        Example:
            feedback = [
                {
                    "inputs": {"question": "What is AI?"},
                    "outputs": {"answer": "AI is computers"},
                    "human_assessment": "poor",
                    "corrected_output": "AI is artificial intelligence..."
                }
            ]

            result = optimizer.optimize_from_feedback(
                predict_fn=my_agent,
                feedback=feedback,
                prompt_uris=["prompts:/qa/1"],
                feedback_strategy="corrected"  # Requires corrected_output!
            )
        """
        print(f"🔧 Converting human feedback to training data...")
        print(f"   Strategy: {feedback_strategy}")
        print(f"   Feedback items: {len(feedback)}")

        # Convert human feedback to GEPA training format
        train_data = self._convert_feedback_to_training(
            feedback=feedback,
            strategy=feedback_strategy,
            quality_threshold=quality_threshold
        )

        print(f"   Training examples: {len(train_data)}")
        print()

        if not train_data:
            raise ValueError(
                f"No valid training data after filtering. "
                f"Strategy: {feedback_strategy}, "
                f"Threshold: {quality_threshold}"
            )

        # Optimize with GEPA
        result = self.gepa_optimizer.optimize(
            predict_fn=predict_fn,
            train_data=train_data,
            prompt_uris=prompt_uris,
            **kwargs
        )

        # Add feedback metadata
        result.metadata.update({
            "feedback_strategy": feedback_strategy,
            "quality_threshold": quality_threshold,
            "total_feedback": len(feedback),
            "used_feedback": len(train_data)
        })

        return result

    def optimize_from_traces(
        self,
        predict_fn: Callable,
        experiment_id: str,
        prompt_uris: List[str],
        feedback_name: str,
        feedback_strategy: str = "corrected",
        quality_threshold: Optional[str] = None,
        max_traces: int = 100,
        **kwargs
    ) -> GepaResult:
        """
        Optimize prompts from MLflow traces with human feedback.

        Directly reads human feedback from MLflow traces and optimizes.
        No judge alignment required!

        Args:
            predict_fn: Agent function
            experiment_id: MLflow experiment ID
            prompt_uris: Prompts to optimize
            feedback_name: Name of the human feedback assessment
            feedback_strategy: How to use feedback
            quality_threshold: Filter by quality
            max_traces: Max traces to process
            **kwargs: Additional GEPA arguments

        Returns:
            GepaResult with optimized prompts

        Example:
            # SMEs have provided feedback in MLflow UI
            result = optimizer.optimize_from_traces(
                predict_fn=my_agent,
                experiment_id="my-exp-123",
                prompt_uris=["prompts:/qa/1"],
                feedback_name="quality",
                feedback_strategy="corrected"
            )
        """
        print(f"🔍 Fetching traces with human feedback...")
        print(f"   Experiment: {experiment_id}")
        print(f"   Feedback name: {feedback_name}")

        # Fetch traces with human feedback
        traces = mlflow.search_traces(
            experiment_ids=[experiment_id],
            max_results=max_traces,
            return_type="list"
        )

        # Extract human feedback
        feedback = self._extract_feedback_from_traces(
            traces=traces,
            feedback_name=feedback_name
        )

        print(f"   Found {len(feedback)} traces with human feedback")
        print()

        # Optimize
        return self.optimize_from_feedback(
            predict_fn=predict_fn,
            feedback=feedback,
            prompt_uris=prompt_uris,
            feedback_strategy=feedback_strategy,
            quality_threshold=quality_threshold,
            **kwargs
        )

    def _convert_feedback_to_training(
        self,
        feedback: List[Dict[str, Any]],
        strategy: str,
        quality_threshold: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Convert human feedback to GEPA training format."""
        train_data = []

        # Quality ranking
        quality_rank = {
            "excellent": 4,
            "good": 3,
            "fair": 2,
            "poor": 1
        }

        threshold_rank = quality_rank.get(quality_threshold, 0) if quality_threshold else 0

        for item in feedback:
            # Filter by quality
            assessment = item.get("human_assessment", "").lower()
            if quality_threshold and quality_rank.get(assessment, 0) < threshold_rank:
                continue

            inputs = item.get("inputs", {})
            outputs = item.get("outputs", {})

            # Determine expected response based on strategy
            expected_response = None

            if strategy == "corrected":
                # Use SME's corrected version if available
                expected_response = item.get("corrected_output")
                if not expected_response:
                    # Fall back to original if rated good+
                    if quality_rank.get(assessment, 0) >= 3:
                        expected_response = outputs.get("answer") or outputs.get("response") or str(outputs)

            elif strategy == "positive":
                # Only use highly-rated outputs
                if quality_rank.get(assessment, 0) >= 3:
                    expected_response = outputs.get("answer") or outputs.get("response") or str(outputs)

            elif strategy == "negative":
                # Learn from corrections of poor outputs
                if quality_rank.get(assessment, 0) <= 2:
                    expected_response = item.get("corrected_output")

            # Add to training data if we have an expectation
            if expected_response:
                train_data.append({
                    "inputs": inputs,
                    "expectations": {"expected_response": expected_response}
                })

        return train_data

    def _extract_feedback_from_traces(
        self,
        traces: List[Trace],
        feedback_name: str
    ) -> List[Dict[str, Any]]:
        """Extract human feedback from MLflow traces."""
        feedback = []

        for trace in traces:
            # Get trace inputs/outputs
            if not trace.data.spans:
                continue

            root_span = trace.data.spans[0]
            inputs = root_span.inputs or {}
            outputs = root_span.outputs or {}

            # Find human feedback
            assessments = trace.search_assessments(name=feedback_name)
            human_assessments = [
                a for a in assessments
                if a.source.source_type == AssessmentSourceType.HUMAN
            ]

            if not human_assessments:
                continue

            # Use most recent human assessment
            assessment = human_assessments[-1]

            feedback.append({
                "trace_id": trace.info.request_id,
                "inputs": inputs,
                "outputs": outputs,
                "human_assessment": assessment.value,
                "human_rationale": assessment.rationale,
                "corrected_output": assessment.metadata.get("corrected_output") if assessment.metadata else None
            })

        return feedback


def log_corrected_feedback(
    trace_id: str,
    assessment_name: str,
    assessment_value: str,
    corrected_output: str,
    rationale: Optional[str] = None,
    source_id: str = "sme_correction"
):
    """
    Log human feedback with corrected output to MLflow.

    Use this when SMEs provide corrections to agent outputs.

    Args:
        trace_id: MLflow trace ID
        assessment_name: Name of the assessment (e.g., "quality")
        assessment_value: Rating (e.g., "poor", "excellent")
        corrected_output: SME's corrected version
        rationale: Optional explanation
        source_id: Identifier for the SME/reviewer

    Example:
        log_corrected_feedback(
            trace_id="abc123",
            assessment_name="quality",
            assessment_value="poor",
            corrected_output="The correct answer is...",
            rationale="Original answer was too vague"
        )
    """
    mlflow.log_feedback(
        trace_id=trace_id,
        name=assessment_name,
        value=assessment_value,
        rationale=rationale,
        metadata={"corrected_output": corrected_output},
        source=AssessmentSource(
            source_type=AssessmentSourceType.HUMAN,
            source_id=source_id
        )
    )
