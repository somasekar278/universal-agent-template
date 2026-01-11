"""
Prompt Optimization Module

Advanced prompt optimization using:
- DSPy: Task prompt optimization
- TextGrad: System prompt optimization
- GEPA: Production prompt optimization (MLflow)
- Auto-optimization pipelines
- A/B testing framework
- Prompt versioning integration

Install:
    pip install sota-agent-framework[optimization]

Usage:
    from optimization import DSPyOptimizer, TextGradOptimizer, GepaOptimizer

    # Optimize task prompt with DSPy
    dspy_optimizer = DSPyOptimizer()
    optimized_prompt = dspy_optimizer.optimize(
        task="fraud_detection",
        training_data=examples
    )

    # Optimize system prompt with TextGrad
    textgrad_optimizer = TextGradOptimizer()
    optimized_system = textgrad_optimizer.optimize(
        system_prompt=initial_prompt,
        evaluation_data=test_cases
    )

    # Optimize production prompts with GEPA
    gepa_optimizer = GepaOptimizer()
    result = gepa_optimizer.optimize(
        predict_fn=agent_function,
        train_data=training_data,
        prompt_uris=["prompts:/my_agent/1"]
    )
"""

from .dspy_optimizer import (
    DSPyOptimizer,
    DSPyConfig,
    OptimizationResult
)

from .textgrad_optimizer import (
    TextGradOptimizer,
    TextGradConfig,
    SystemPromptResult
)

from .gepa_optimizer import (
    GepaOptimizer,
    GepaResult,
    create_custom_scorer
)

from .dspy_gepa_optimizer import (
    DSPyGepaOptimizer,
    DSPyGepaResult,
    create_dspy_metric,
    convert_to_dspy_examples
)

from .human_feedback_optimizer import (
    HumanFeedbackOptimizer,
    HumanFeedback,
    log_corrected_feedback,
    create_sme_feedback_scorer
)

from .prompt_optimizer import (
    PromptOptimizer,
    OptimizationPipeline,
    PromptCandidate
)

from .ab_testing import (
    ABTestFramework,
    PromptVariant,
    TestResult
)

__all__ = [
    # DSPy
    "DSPyOptimizer",
    "DSPyConfig",
    "OptimizationResult",

    # TextGrad
    "TextGradOptimizer",
    "TextGradConfig",
    "SystemPromptResult",

    # GEPA (MLflow)
    "GepaOptimizer",
    "GepaResult",
    "create_custom_scorer",

    # GEPA (DSPy)
    "DSPyGepaOptimizer",
    "DSPyGepaResult",
    "create_dspy_metric",
    "convert_to_dspy_examples",

    # Human Feedback (Direct to GEPA)
    "HumanFeedbackOptimizer",
    "HumanFeedback",
    "log_corrected_feedback",
    "create_sme_feedback_scorer",

    # Unified
    "PromptOptimizer",
    "OptimizationPipeline",
    "PromptCandidate",

    # A/B Testing
    "ABTestFramework",
    "PromptVariant",
    "TestResult",
]
