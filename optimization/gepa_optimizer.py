"""
GEPA (MLflow) Prompt Optimizer

Uses MLflow's GepaPromptOptimizer for production prompt optimization:
- Iterative prompt refinement
- LLM-driven reflection
- Automated feedback loops
- Multi-prompt optimization
- Framework-agnostic

Based on: https://mlflow.org/docs/latest/genai/prompt-registry/optimize-prompts/
"""

from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
import mlflow
from mlflow.genai.optimize import GepaPromptOptimizer
from mlflow.genai.scorers import Correctness, Safety, Professionalism


@dataclass
class GepaResult:
    """Result from GEPA optimization."""
    original_prompts: List[Dict[str, Any]]
    optimized_prompts: List[Any]  # PromptVersion objects
    initial_score: Optional[float] = None
    final_score: Optional[float] = None
    improvement: Optional[float] = None
    optimizer_name: str = "GEPA"
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


class GepaOptimizer:
    """
    MLflow GEPA prompt optimizer.

    GEPA (Generative Edit-based Prompt Adaptation) uses LLM-driven
    reflection and automated feedback to iteratively refine prompts.

    Usage:
        optimizer = GepaOptimizer(
            reflection_model="databricks-claude-sonnet-4",
            max_metric_calls=100
        )

        result = optimizer.optimize(
            predict_fn=agent_function,
            train_data=dataset,
            prompt_uris=["prompts:/my_prompt/1"],
            scorers=["correctness", "safety"]
        )
    """

    def __init__(
        self,
        reflection_model: str = "databricks-claude-sonnet-4",
        max_metric_calls: int = 100,
        display_progress_bar: bool = True
    ):
        """
        Initialize GEPA optimizer.

        Args:
            reflection_model: Model to use for reflection (e.g., "openai:/gpt-5")
            max_metric_calls: Maximum number of optimization iterations
            display_progress_bar: Show progress during optimization
        """
        self.reflection_model = reflection_model
        self.max_metric_calls = max_metric_calls
        self.display_progress_bar = display_progress_bar

    def optimize(
        self,
        predict_fn: Callable,
        train_data: List[Dict[str, Any]],
        prompt_uris: List[str],
        scorers: Optional[List[Any]] = None,
        aggregation: Optional[Callable] = None,
        **kwargs
    ) -> GepaResult:
        """
        Optimize prompts using GEPA.

        Args:
            predict_fn: Function that uses the prompts to make predictions
            train_data: Training dataset in format:
                [
                    {
                        "inputs": {"param": value},
                        "expectations": {"expected_response": value}
                    }
                ]
            prompt_uris: List of prompt URIs to optimize (e.g., ["prompts:/qa/1"])
            scorers: List of scorers (str or scorer objects):
                - "correctness": Check output correctness
                - "safety": Check output safety
                - "professionalism": Check professionalism
                Or pass custom @scorer decorated functions
            aggregation: Optional function to aggregate multiple scorer results
            **kwargs: Additional arguments

        Returns:
            GepaResult with optimized prompts
        """
        # Create optimizer
        optimizer = GepaPromptOptimizer(
            reflection_model=self.reflection_model,
            max_metric_calls=self.max_metric_calls,
            display_progress_bar=self.display_progress_bar
        )

        # Prepare scorers
        if scorers is None:
            scorers = ["correctness"]

        scorer_objects = []
        for scorer in scorers:
            if isinstance(scorer, str):
                scorer_objects.append(self._get_builtin_scorer(scorer))
            else:
                scorer_objects.append(scorer)

        # Run optimization
        print(f"🔧 Optimizing {len(prompt_uris)} prompt(s) with GEPA...")
        print(f"   Model: {self.reflection_model}")
        print(f"   Budget: {self.max_metric_calls} calls")
        print(f"   Scorers: {[s.__name__ if hasattr(s, '__name__') else str(s) for s in scorer_objects]}")

        result = mlflow.genai.optimize_prompts(
            predict_fn=predict_fn,
            train_data=train_data,
            prompt_uris=prompt_uris,
            optimizer=optimizer,
            scorers=scorer_objects,
            aggregation=aggregation
        )

        # Calculate improvement
        improvement = None
        if result.initial_eval_score and result.final_eval_score:
            improvement = (result.final_eval_score - result.initial_eval_score) / result.initial_eval_score

        # Store original prompts info
        original_prompts = []
        for uri in prompt_uris:
            prompt = mlflow.genai.load_prompt(uri)
            original_prompts.append({
                "uri": uri,
                "name": prompt.name,
                "version": prompt.version,
                "template": prompt.template
            })

        gepa_result = GepaResult(
            original_prompts=original_prompts,
            optimized_prompts=result.optimized_prompts,
            initial_score=result.initial_eval_score,
            final_score=result.final_eval_score,
            improvement=improvement,
            metadata={
                "reflection_model": self.reflection_model,
                "max_metric_calls": self.max_metric_calls,
                "num_prompts": len(prompt_uris),
                "scorers": [s.__name__ if hasattr(s, '__name__') else str(s) for s in scorer_objects]
            }
        )

        # Print results
        print(f"\n✅ GEPA Optimization Complete!")
        if gepa_result.initial_score and gepa_result.final_score:
            print(f"   Initial score: {gepa_result.initial_score:.3f}")
            print(f"   Final score: {gepa_result.final_score:.3f}")
            if improvement:
                print(f"   Improvement: {improvement:.2%}")

        for i, opt_prompt in enumerate(result.optimized_prompts):
            print(f"\n   Prompt {i+1}: {opt_prompt.name} v{opt_prompt.version}")
            print(f"   URI: {opt_prompt.uri}")

        return gepa_result

    def _get_builtin_scorer(self, scorer_name: str):
        """Get built-in scorer by name."""
        scorer_map = {
            "correctness": Correctness(model=self.reflection_model),
            "safety": Safety(model=self.reflection_model),
            "professionalism": Professionalism(model=self.reflection_model)
        }

        if scorer_name not in scorer_map:
            raise ValueError(
                f"Unknown scorer: {scorer_name}. "
                f"Available: {list(scorer_map.keys())}"
            )

        return scorer_map[scorer_name]


def create_custom_scorer(name: str, description: str, evaluation_fn: Callable):
    """
    Create a custom scorer for GEPA optimization.

    Usage:
        from mlflow.genai.scorers import scorer

        @scorer
        def brevity_scorer(outputs: Any):
            '''Prefer shorter outputs (max 50 chars).'''
            return min(1.0, 50 / max(len(outputs), 1))

        optimizer = GepaOptimizer()
        result = optimizer.optimize(
            predict_fn=fn,
            train_data=data,
            prompt_uris=uris,
            scorers=[brevity_scorer]
        )

    Args:
        name: Scorer name
        description: Scorer description
        evaluation_fn: Function to evaluate outputs

    Returns:
        Decorated scorer function
    """
    from mlflow.genai.scorers import scorer

    @scorer
    def custom_scorer(*args, **kwargs):
        return evaluation_fn(*args, **kwargs)

    custom_scorer.__name__ = name
    custom_scorer.__doc__ = description

    return custom_scorer
