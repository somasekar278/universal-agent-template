"""
Prompt Optimization Module

Advanced prompt optimization using:
- DSPy: Task prompt optimization
- TextGrad: System prompt optimization
- Auto-optimization pipelines
- A/B testing framework
- Prompt versioning integration

Install:
    pip install sota-agent-framework[optimization]

Usage:
    from optimization import DSPyOptimizer, TextGradOptimizer

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

    # Unified
    "PromptOptimizer",
    "OptimizationPipeline",
    "PromptCandidate",

    # A/B Testing
    "ABTestFramework",
    "PromptVariant",
    "TestResult",
]
