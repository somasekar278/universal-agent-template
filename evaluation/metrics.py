"""
Evaluation Metrics for Agent Benchmarking

Comprehensive metrics for measuring agent quality and performance.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import time
from abc import ABC, abstractmethod


class MetricType(str, Enum):
    """Types of evaluation metrics."""
    QUALITY = "quality"
    PERFORMANCE = "performance"
    RELIABILITY = "reliability"
    COST = "cost"


@dataclass
class MetricResult:
    """Result from a single metric evaluation."""
    metric_name: str
    score: float  # 0.0 to 1.0
    passed: bool
    threshold: Optional[float] = None
    details: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


@dataclass
class EvaluationResult:
    """Complete evaluation result for an agent."""
    agent_name: str
    test_case_id: str
    metrics: List[MetricResult]
    overall_score: float
    passed: bool
    execution_time_ms: float
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get_metric(self, name: str) -> Optional[MetricResult]:
        """Get specific metric result."""
        for metric in self.metrics:
            if metric.metric_name == name:
                return metric
        return None


class Metric(ABC):
    """
    Base class for evaluation metrics.

    All metrics implement evaluate() method that returns MetricResult.
    """

    def __init__(self, name: str, threshold: float = 0.7):
        """
        Initialize metric.

        Args:
            name: Metric name
            threshold: Minimum passing score (0.0-1.0)
        """
        self.name = name
        self.threshold = threshold

    @abstractmethod
    async def evaluate(
        self,
        agent_output: Any,
        expected_output: Any,
        context: Dict[str, Any]
    ) -> MetricResult:
        """
        Evaluate agent output.

        Args:
            agent_output: Agent's output
            expected_output: Expected/ground truth output
            context: Additional context (input, metadata, etc.)

        Returns:
            MetricResult with score and details
        """
        pass


class ToolCallMetric(Metric):
    """
    Evaluates tool call success rate.

    Metrics:
    - Tool call success rate
    - Correct tool selection
    - Valid tool arguments
    - Tool call ordering
    """

    def __init__(self, threshold: float = 0.9):
        super().__init__("tool_call_success", threshold)

    async def evaluate(
        self,
        agent_output: Any,
        expected_output: Any,
        context: Dict[str, Any]
    ) -> MetricResult:
        """Evaluate tool call quality."""
        details = {}

        # Extract tool calls from agent output
        tool_calls = self._extract_tool_calls(agent_output, context)
        expected_tools = expected_output.get("expected_tools", [])

        if not expected_tools:
            # No expected tools, check if agent made any
            score = 1.0 if not tool_calls else 0.8
            details["no_expectations"] = True
        else:
            # Check tool call correctness
            correct_tools = 0
            correct_args = 0
            total_expected = len(expected_tools)

            for expected in expected_tools:
                # Check if tool was called
                matching_call = self._find_matching_call(expected, tool_calls)
                if matching_call:
                    correct_tools += 1
                    # Check arguments
                    if self._validate_arguments(expected, matching_call):
                        correct_args += 1

            score = (correct_tools / total_expected * 0.6 +
                    correct_args / total_expected * 0.4)

            details["correct_tools"] = correct_tools
            details["correct_args"] = correct_args
            details["total_expected"] = total_expected
            details["tool_calls_made"] = len(tool_calls)

        passed = score >= self.threshold

        return MetricResult(
            metric_name=self.name,
            score=score,
            passed=passed,
            threshold=self.threshold,
            details=details
        )

    def _extract_tool_calls(self, output: Any, context: Dict) -> List[Dict]:
        """Extract tool calls from agent output."""
        # Check various output formats
        if hasattr(output, 'metadata') and 'tool_calls' in output.metadata:
            return output.metadata['tool_calls']
        elif isinstance(output, dict) and 'tool_calls' in output:
            return output['tool_calls']
        elif 'execution_results' in context:
            # From LangGraph workflow
            return [{'tool': r.get('agent')} for r in context['execution_results']]
        return []

    def _find_matching_call(self, expected: Dict, calls: List[Dict]) -> Optional[Dict]:
        """Find matching tool call."""
        expected_name = expected.get('tool') or expected.get('name')
        for call in calls:
            call_name = call.get('tool') or call.get('name')
            if call_name == expected_name:
                return call
        return None

    def _validate_arguments(self, expected: Dict, actual: Dict) -> bool:
        """Validate tool call arguments."""
        expected_args = expected.get('arguments', {})
        actual_args = actual.get('arguments', {})

        # Check all expected arguments are present
        for key, value in expected_args.items():
            if key not in actual_args:
                return False
            # Optionally check values match
            if value is not None and actual_args[key] != value:
                return False

        return True


class PlanCorrectnessMetric(Metric):
    """
    Evaluates planning quality.

    Metrics:
    - Plan structure correctness
    - Step ordering
    - Dependency handling
    - Completeness
    """

    def __init__(self, threshold: float = 0.8):
        super().__init__("plan_correctness", threshold)

    async def evaluate(
        self,
        agent_output: Any,
        expected_output: Any,
        context: Dict[str, Any]
    ) -> MetricResult:
        """Evaluate plan quality."""
        details = {}

        # Extract plan
        plan = self._extract_plan(agent_output, context)
        expected_plan = expected_output.get("expected_plan", {})

        if not expected_plan:
            # No expected plan, just check if plan exists
            score = 1.0 if plan else 0.0
            details["no_expectations"] = True
        else:
            scores = []

            # Check required steps present
            required_steps = expected_plan.get("required_steps", [])
            if required_steps:
                steps_present = sum(
                    1 for step in required_steps
                    if self._step_in_plan(step, plan)
                )
                step_score = steps_present / len(required_steps)
                scores.append(("steps", step_score, 0.4))
                details["steps_present"] = steps_present
                details["steps_required"] = len(required_steps)

            # Check step ordering
            required_order = expected_plan.get("required_order", [])
            if required_order:
                order_score = self._check_order(required_order, plan)
                scores.append(("order", order_score, 0.3))
                details["order_score"] = order_score

            # Check dependencies
            if plan and isinstance(plan, list):
                dep_score = self._check_dependencies(plan)
                scores.append(("dependencies", dep_score, 0.3))
                details["dependency_score"] = dep_score

            # Calculate weighted score
            score = sum(s * w for _, s, w in scores) if scores else 0.5

        passed = score >= self.threshold

        return MetricResult(
            metric_name=self.name,
            score=score,
            passed=passed,
            threshold=self.threshold,
            details=details
        )

    def _extract_plan(self, output: Any, context: Dict) -> Optional[List]:
        """Extract plan from output."""
        if 'plan' in context:
            return context['plan']
        elif hasattr(output, 'metadata') and 'plan' in output.metadata:
            return output.metadata['plan']
        elif isinstance(output, dict) and 'plan' in output:
            return output['plan']
        return None

    def _step_in_plan(self, step: str, plan: List) -> bool:
        """Check if step is in plan."""
        if not plan:
            return False
        for plan_step in plan:
            if isinstance(plan_step, dict):
                agent = plan_step.get('agent') or plan_step.get('step')
                if agent == step or step in str(agent):
                    return True
            elif step in str(plan_step):
                return True
        return False

    def _check_order(self, required_order: List[str], plan: List) -> float:
        """Check if plan follows required ordering."""
        plan_order = [
            p.get('agent') or p.get('step')
            for p in plan
            if isinstance(p, dict)
        ]

        # Check if required steps appear in order
        last_index = -1
        for step in required_order:
            try:
                index = plan_order.index(step)
                if index < last_index:
                    return 0.5  # Out of order
                last_index = index
            except ValueError:
                return 0.0  # Missing step

        return 1.0

    def _check_dependencies(self, plan: List) -> float:
        """Check if dependencies are satisfied."""
        # Simple heuristic: check if steps with dependencies come after their deps
        violations = 0
        total_deps = 0

        for i, step in enumerate(plan):
            if not isinstance(step, dict):
                continue

            deps = step.get('dependencies', [])
            total_deps += len(deps)

            for dep in deps:
                # Check if dependency appears before this step
                dep_found = False
                for j in range(i):
                    prev_step = plan[j]
                    if isinstance(prev_step, dict):
                        if prev_step.get('step') == dep:
                            dep_found = True
                            break

                if not dep_found:
                    violations += 1

        if total_deps == 0:
            return 1.0

        return 1.0 - (violations / total_deps)


class HallucinationMetric(Metric):
    """
    Evaluates hallucination rate.

    Detects:
    - Fabricated facts
    - Incorrect references
    - Made-up tool names
    - Invalid data in output
    """

    def __init__(self, threshold: float = 0.9):
        super().__init__("hallucination_rate", threshold)

    async def evaluate(
        self,
        agent_output: Any,
        expected_output: Any,
        context: Dict[str, Any]
    ) -> MetricResult:
        """Evaluate hallucination rate (lower is better, so we invert)."""
        details = {}

        hallucinations = 0
        checks = 0

        # Check 1: Tool names
        tool_calls = self._extract_tool_calls(agent_output, context)
        available_tools = context.get('available_tools', [])
        if available_tools:
            for call in tool_calls:
                checks += 1
                tool_name = call.get('tool') or call.get('name')
                if tool_name not in available_tools:
                    hallucinations += 1
            details["invalid_tools"] = hallucinations

        # Check 2: Required fields in output
        required_fields = expected_output.get("required_fields", [])
        output_dict = agent_output if isinstance(agent_output, dict) else {}
        if hasattr(agent_output, 'result'):
            output_dict = agent_output.result

        for field in required_fields:
            checks += 1
            if field not in output_dict:
                hallucinations += 1

        details["missing_fields"] = len(required_fields) - len([
            f for f in required_fields if f in output_dict
        ])

        # Check 3: Fabricated numeric values
        numeric_checks = expected_output.get("numeric_ranges", {})
        for field, (min_val, max_val) in numeric_checks.items():
            if field in output_dict:
                checks += 1
                value = output_dict[field]
                if not isinstance(value, (int, float)) or value < min_val or value > max_val:
                    hallucinations += 1

        # Calculate score (invert hallucination rate)
        if checks == 0:
            score = 1.0
        else:
            hallucination_rate = hallucinations / checks
            score = 1.0 - hallucination_rate

        details["hallucinations"] = hallucinations
        details["total_checks"] = checks

        passed = score >= self.threshold

        return MetricResult(
            metric_name=self.name,
            score=score,
            passed=passed,
            threshold=self.threshold,
            details=details
        )

    def _extract_tool_calls(self, output: Any, context: Dict) -> List[Dict]:
        """Extract tool calls."""
        if hasattr(output, 'metadata') and 'tool_calls' in output.metadata:
            return output.metadata['tool_calls']
        return []


class LatencyMetric(Metric):
    """
    Evaluates execution latency.

    Compares actual latency against budget.
    """

    def __init__(self, threshold: float = 0.8, latency_budget_ms: int = 1000):
        super().__init__("latency", threshold)
        self.latency_budget_ms = latency_budget_ms

    async def evaluate(
        self,
        agent_output: Any,
        expected_output: Any,
        context: Dict[str, Any]
    ) -> MetricResult:
        """Evaluate latency."""
        # Get actual latency
        actual_ms = context.get('execution_time_ms', 0)
        budget_ms = expected_output.get('latency_budget_ms', self.latency_budget_ms)

        # Score based on how much under budget
        if actual_ms <= budget_ms:
            score = 1.0
        else:
            # Penalty for going over budget
            overage = (actual_ms - budget_ms) / budget_ms
            score = max(0.0, 1.0 - overage)

        details = {
            "actual_ms": actual_ms,
            "budget_ms": budget_ms,
            "within_budget": actual_ms <= budget_ms
        }

        passed = score >= self.threshold

        return MetricResult(
            metric_name=self.name,
            score=score,
            passed=passed,
            threshold=self.threshold,
            details=details
        )


class CoherenceMetric(Metric):
    """
    Evaluates agent output coherence.

    Checks:
    - Logical consistency
    - Completeness
    - Relevance to input
    """

    def __init__(self, threshold: float = 0.7):
        super().__init__("coherence", threshold)

    async def evaluate(
        self,
        agent_output: Any,
        expected_output: Any,
        context: Dict[str, Any]
    ) -> MetricResult:
        """Evaluate coherence."""
        scores = []

        # Check 1: Output is not empty
        if agent_output:
            scores.append(0.3)

        # Check 2: Contains expected keys/structure
        expected_structure = expected_output.get("structure", {})
        if expected_structure:
            output_dict = agent_output if isinstance(agent_output, dict) else {}
            if hasattr(agent_output, 'result'):
                output_dict = agent_output.result

            matching_keys = sum(
                1 for key in expected_structure
                if key in output_dict
            )
            if expected_structure:
                scores.append(0.4 * (matching_keys / len(expected_structure)))

        # Check 3: Confidence/quality indicators present
        if hasattr(agent_output, 'confidence_score'):
            scores.append(0.3)

        score = sum(scores) if scores else 0.5
        passed = score >= self.threshold

        return MetricResult(
            metric_name=self.name,
            score=score,
            passed=passed,
            threshold=self.threshold,
            details={"subscores": scores}
        )


class AccuracyMetric(Metric):
    """
    Evaluates domain-specific accuracy.

    Compares agent output against ground truth.
    """

    def __init__(self, threshold: float = 0.8):
        super().__init__("accuracy", threshold)

    async def evaluate(
        self,
        agent_output: Any,
        expected_output: Any,
        context: Dict[str, Any]
    ) -> MetricResult:
        """Evaluate accuracy."""
        ground_truth = expected_output.get("ground_truth", {})

        if not ground_truth:
            # No ground truth provided
            return MetricResult(
                metric_name=self.name,
                score=0.5,
                passed=False,
                threshold=self.threshold,
                details={"no_ground_truth": True}
            )

        output_dict = agent_output if isinstance(agent_output, dict) else {}
        if hasattr(agent_output, 'result'):
            output_dict = agent_output.result

        # Compare output to ground truth
        matches = 0
        total = len(ground_truth)

        for key, expected_value in ground_truth.items():
            if key in output_dict:
                actual_value = output_dict[key]
                if self._values_match(expected_value, actual_value):
                    matches += 1

        score = matches / total if total > 0 else 0.0
        passed = score >= self.threshold

        return MetricResult(
            metric_name=self.name,
            score=score,
            passed=passed,
            threshold=self.threshold,
            details={"matches": matches, "total": total}
        )

    def _values_match(self, expected: Any, actual: Any, tolerance: float = 0.01) -> bool:
        """Check if values match with tolerance for floats."""
        if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
            return abs(expected - actual) <= tolerance
        return expected == actual
