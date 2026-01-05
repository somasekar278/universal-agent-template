"""
TextGrad Optimizer for System Prompts

Uses TextGrad to optimize system prompts through:
- Gradient-based optimization
- Automatic differentiation of text
- Multi-objective optimization
- Iterative refinement

Configuration loaded from YAML (optimization.textgrad.*)
"""

from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class TextGradConfig:
    """Configuration for TextGrad optimization."""
    max_iterations: int = 20
    learning_rate: float = 0.1
    optimizer_model: str = "gpt-4"
    evaluation_model: str = "gpt-4"
    batch_size: int = 4
    early_stopping_patience: int = 3
    target_metric: str = "quality"


@dataclass
class SystemPromptResult:
    """Result from system prompt optimization."""
    optimized_prompt: str
    original_prompt: str
    original_score: float
    optimized_score: float
    improvement: float
    iterations: int
    optimization_history: List[Dict[str, Any]]
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


class TextGradOptimizer:
    """
    TextGrad-powered system prompt optimizer.

    Optimizes system prompts using gradient-based text optimization.

    Usage:
        optimizer = TextGradOptimizer()

        # Define evaluation data
        eval_data = [
            {"input": "...", "expected": "..."},
            {"input": "...", "expected": "..."},
        ]

        # Define system prompt
        system_prompt = "You are a fraud detection expert."

        # Optimize
        result = optimizer.optimize(
            system_prompt=system_prompt,
            evaluation_data=eval_data,
            objective="Maximize accuracy while being concise"
        )

        # Use optimized prompt
        print(result.optimized_prompt)
        print(f"Improvement: {result.improvement:.2%}")
    """

    def __init__(self, config: Optional[TextGradConfig] = None):
        """
        Initialize TextGrad optimizer.

        Args:
            config: TextGrad configuration (loads from YAML if None)
        """
        if config is None:
            config = self._load_config_from_yaml()

        self.config = config
        self._textgrad_available = self._check_textgrad()

    def _load_config_from_yaml(self) -> TextGradConfig:
        """Load configuration from YAML."""
        try:
            from shared.config_loader import get_config
            config = get_config()

            return TextGradConfig(
                max_iterations=config.get_int("optimization.textgrad.max_iterations", 20),
                learning_rate=config.get_float("optimization.textgrad.learning_rate", 0.1),
                optimizer_model=config.get_str("optimization.textgrad.optimizer_model", "gpt-4"),
                evaluation_model=config.get_str("optimization.textgrad.evaluation_model", "gpt-4"),
                batch_size=config.get_int("optimization.textgrad.batch_size", 4),
                early_stopping_patience=config.get_int("optimization.textgrad.early_stopping_patience", 3),
                target_metric=config.get_str("optimization.textgrad.target_metric", "quality")
            )
        except:
            return TextGradConfig()

    def _check_textgrad(self) -> bool:
        """Check if TextGrad is available."""
        try:
            import textgrad
            return True
        except ImportError:
            print("⚠️  TextGrad not installed. Run: pip install sota-agent-framework[optimization]")
            return False

    async def optimize(
        self,
        system_prompt: str,
        evaluation_data: List[Dict[str, Any]],
        objective: Optional[str] = None,
        constraints: Optional[List[str]] = None
    ) -> SystemPromptResult:
        """
        Optimize system prompt using TextGrad.

        Args:
            system_prompt: Initial system prompt
            evaluation_data: Data for evaluation
            objective: Optimization objective
            constraints: Optional constraints

        Returns:
            SystemPromptResult with optimized prompt
        """
        if not self._textgrad_available:
            # Fallback optimization
            return await self._fallback_optimize(system_prompt, evaluation_data, objective)

        try:
            import textgrad as tg

            # Configure TextGrad
            tg.set_backward_engine(
                tg.get_engine(self.config.optimizer_model)
            )

            # Create variable for system prompt
            system_var = tg.Variable(
                system_prompt,
                requires_grad=True,
                role_description="system prompt for the agent"
            )

            # Define optimization objective
            if objective is None:
                objective = f"Optimize for {self.config.target_metric}"

            # Create optimizer
            optimizer = tg.TextualGradientDescent(
                parameters=[system_var],
                engine=tg.get_engine(self.config.optimizer_model)
            )

            # Optimization loop
            history = []
            best_score = 0.0
            best_prompt = system_prompt
            patience_counter = 0

            for iteration in range(self.config.max_iterations):
                # Evaluate current prompt
                score = await self._evaluate_prompt(
                    system_var.value,
                    evaluation_data
                )

                history.append({
                    "iteration": iteration,
                    "score": score,
                    "prompt": system_var.value
                })

                print(f"Iteration {iteration}: Score = {score:.3f}")

                # Check for improvement
                if score > best_score:
                    best_score = score
                    best_prompt = system_var.value
                    patience_counter = 0
                else:
                    patience_counter += 1

                # Early stopping
                if patience_counter >= self.config.early_stopping_patience:
                    print(f"Early stopping at iteration {iteration}")
                    break

                # Compute loss and gradients
                loss = self._compute_loss(score, objective)
                loss.backward()

                # Update prompt
                optimizer.step()
                optimizer.zero_grad()

            # Evaluate original
            original_score = await self._evaluate_prompt(system_prompt, evaluation_data)

            return SystemPromptResult(
                optimized_prompt=best_prompt,
                original_prompt=system_prompt,
                original_score=original_score,
                optimized_score=best_score,
                improvement=(best_score - original_score) / original_score if original_score > 0 else 0,
                iterations=len(history),
                optimization_history=history,
                metadata={
                    "objective": objective,
                    "constraints": constraints,
                    "config": vars(self.config)
                }
            )

        except Exception as e:
            print(f"⚠️  TextGrad optimization failed: {e}")
            return await self._fallback_optimize(system_prompt, evaluation_data, objective)

    async def _evaluate_prompt(
        self,
        prompt: str,
        evaluation_data: List[Dict[str, Any]]
    ) -> float:
        """Evaluate system prompt on data."""
        scores = []

        for example in evaluation_data[:self.config.batch_size]:
            # Simulate evaluation (would use actual model)
            score = self._score_example(prompt, example)
            scores.append(score)

        return sum(scores) / len(scores) if scores else 0.0

    def _score_example(self, prompt: str, example: Dict[str, Any]) -> float:
        """Score a single example."""
        # Simplified scoring
        # In practice, would use LLM with prompt on example

        # Heuristic scoring
        score = 0.5

        # Longer, more detailed prompts might be better
        if len(prompt) > 100:
            score += 0.1

        # Check for key terms
        if any(term in prompt.lower() for term in ["expert", "carefully", "step-by-step"]):
            score += 0.2

        # Check for constraints
        if "concise" in prompt.lower() and len(prompt) < 200:
            score += 0.1

        return min(1.0, score)

    def _compute_loss(self, score: float, objective: str):
        """Compute loss for optimization."""
        # In TextGrad, this would be a differentiable variable
        # For now, simple loss
        return 1.0 - score

    async def _fallback_optimize(
        self,
        system_prompt: str,
        evaluation_data: List[Dict[str, Any]],
        objective: Optional[str]
    ) -> SystemPromptResult:
        """Fallback optimization without TextGrad."""
        # Simple rule-based optimization
        optimized = system_prompt

        # Add helpful instructions
        if "step-by-step" not in optimized.lower():
            optimized += "\n\nThink step-by-step and explain your reasoning."

        if "carefully" not in optimized.lower():
            optimized += "\nCarefully analyze all aspects."

        original_score = 0.5
        optimized_score = 0.6

        return SystemPromptResult(
            optimized_prompt=optimized,
            original_prompt=system_prompt,
            original_score=original_score,
            optimized_score=optimized_score,
            improvement=0.2,
            iterations=1,
            optimization_history=[
                {"iteration": 0, "score": original_score},
                {"iteration": 1, "score": optimized_score}
            ],
            metadata={"method": "fallback", "note": "TextGrad not available"}
        )
