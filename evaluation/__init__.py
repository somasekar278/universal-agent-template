"""
Agent Evaluation & Benchmarking Framework

Comprehensive evaluation suite for testing agent quality, performance, and reliability.

Features:
- Automated benchmarking
- Multi-metric evaluation
- Leaderboard generation
- Regression testing
- MLflow integration

Install:
    pip install sota-agent-framework[dev]

Usage:
    agent-benchmark run --suite fraud --agents all --report md
"""

from .metrics import (
    ToolCallMetric,
    PlanCorrectnessMetric,
    HallucinationMetric,
    LatencyMetric,
    CoherenceMetric,
    AccuracyMetric,
    MetricResult,
    EvaluationResult
)

from .harness import (
    EvaluationHarness,
    BenchmarkSuite,
    TestCase
)

from .runner import (
    BenchmarkRunner,
    BenchmarkConfig
)

from .reporters import (
    MarkdownReporter,
    JSONReporter,
    HTMLReporter,
    LeaderboardGenerator
)

__all__ = [
    # Metrics
    "ToolCallMetric",
    "PlanCorrectnessMetric",
    "HallucinationMetric",
    "LatencyMetric",
    "CoherenceMetric",
    "AccuracyMetric",
    "MetricResult",
    "EvaluationResult",

    # Harness
    "EvaluationHarness",
    "BenchmarkSuite",
    "TestCase",

    # Runner
    "BenchmarkRunner",
    "BenchmarkConfig",

    # Reporters
    "MarkdownReporter",
    "JSONReporter",
    "HTMLReporter",
    "LeaderboardGenerator",
]
