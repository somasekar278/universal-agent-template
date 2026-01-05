"""
Evaluation Harness for Agent Benchmarking

Orchestrates test execution and metric evaluation.
"""

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
import time
import asyncio
from pathlib import Path

from .metrics import Metric, EvaluationResult, MetricResult


@dataclass
class TestCase:
    """
    A single test case for agent evaluation.

    Contains:
    - Input data
    - Expected output/behavior
    - Metrics to evaluate
    - Metadata
    """
    id: str
    name: str
    input_data: Dict[str, Any]
    expected_output: Dict[str, Any]
    metrics: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)

    def matches_filters(self, filters: Dict[str, Any]) -> bool:
        """Check if test case matches filters."""
        if not filters:
            return True

        # Tag filtering
        if 'tags' in filters:
            required_tags = filters['tags']
            if not all(tag in self.tags for tag in required_tags):
                return False

        # Metadata filtering
        if 'metadata' in filters:
            for key, value in filters['metadata'].items():
                if self.metadata.get(key) != value:
                    return False

        return True


@dataclass
class BenchmarkSuite:
    """
    Collection of test cases for a specific domain/scenario.

    Example suites:
    - fraud_detection
    - customer_support
    - data_enrichment
    """
    name: str
    description: str
    test_cases: List[TestCase] = field(default_factory=list)
    default_metrics: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_test_case(self, test_case: TestCase):
        """Add a test case to the suite."""
        self.test_cases.append(test_case)

    def get_test_cases(self, filters: Optional[Dict[str, Any]] = None) -> List[TestCase]:
        """Get test cases matching filters."""
        if not filters:
            return self.test_cases

        return [tc for tc in self.test_cases if tc.matches_filters(filters)]

    @classmethod
    def from_yaml(cls, path: Path) -> "BenchmarkSuite":
        """Load benchmark suite from YAML file."""
        import yaml

        with open(path) as f:
            data = yaml.safe_load(f)

        suite = cls(
            name=data['name'],
            description=data['description'],
            default_metrics=data.get('default_metrics', []),
            metadata=data.get('metadata', {})
        )

        for tc_data in data.get('test_cases', []):
            test_case = TestCase(
                id=tc_data['id'],
                name=tc_data['name'],
                input_data=tc_data['input'],
                expected_output=tc_data['expected'],
                metrics=tc_data.get('metrics', suite.default_metrics),
                metadata=tc_data.get('metadata', {}),
                tags=tc_data.get('tags', [])
            )
            suite.add_test_case(test_case)

        return suite

    def to_yaml(self, path: Path):
        """Save benchmark suite to YAML file."""
        import yaml

        data = {
            'name': self.name,
            'description': self.description,
            'default_metrics': self.default_metrics,
            'metadata': self.metadata,
            'test_cases': [
                {
                    'id': tc.id,
                    'name': tc.name,
                    'input': tc.input_data,
                    'expected': tc.expected_output,
                    'metrics': tc.metrics,
                    'metadata': tc.metadata,
                    'tags': tc.tags
                }
                for tc in self.test_cases
            ]
        }

        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)


class EvaluationHarness:
    """
    Orchestrates agent evaluation.

    Features:
    - Runs test cases against agents
    - Applies metrics
    - Collects results
    - Handles errors gracefully
    """

    def __init__(
        self,
        metrics: Dict[str, Metric],
        parallel: bool = False,
        max_workers: int = 4
    ):
        """
        Initialize harness.

        Args:
            metrics: Dictionary of metric_name -> Metric instance
            parallel: Whether to run tests in parallel
            max_workers: Max parallel workers
        """
        self.metrics = metrics
        self.parallel = parallel
        self.max_workers = max_workers

    async def evaluate_agent(
        self,
        agent_name: str,
        agent_callable: Callable,
        test_cases: List[TestCase],
        suite_name: Optional[str] = None
    ) -> List[EvaluationResult]:
        """
        Evaluate an agent on multiple test cases.

        Args:
            agent_name: Name of the agent being tested
            agent_callable: Async function that takes input and returns output
            test_cases: List of test cases to run
            suite_name: Optional suite name for metadata

        Returns:
            List of EvaluationResult, one per test case
        """
        if self.parallel:
            tasks = [
                self._evaluate_single(agent_name, agent_callable, tc, suite_name)
                for tc in test_cases
            ]
            return await asyncio.gather(*tasks, return_exceptions=True)
        else:
            results = []
            for tc in test_cases:
                result = await self._evaluate_single(agent_name, agent_callable, tc, suite_name)
                results.append(result)
            return results

    async def _evaluate_single(
        self,
        agent_name: str,
        agent_callable: Callable,
        test_case: TestCase,
        suite_name: Optional[str] = None
    ) -> EvaluationResult:
        """Evaluate a single test case."""
        start_time = time.time()

        try:
            # Execute agent
            agent_output = await agent_callable(test_case.input_data)

            # Calculate execution time
            execution_time_ms = (time.time() - start_time) * 1000

            # Prepare context for metrics
            context = {
                'input': test_case.input_data,
                'execution_time_ms': execution_time_ms,
                'test_case': test_case,
                **test_case.metadata
            }

            # Evaluate metrics
            metric_results = []
            for metric_name in test_case.metrics:
                if metric_name not in self.metrics:
                    metric_results.append(MetricResult(
                        metric_name=metric_name,
                        score=0.0,
                        passed=False,
                        error=f"Metric '{metric_name}' not found"
                    ))
                    continue

                try:
                    metric = self.metrics[metric_name]
                    result = await metric.evaluate(
                        agent_output,
                        test_case.expected_output,
                        context
                    )
                    metric_results.append(result)
                except Exception as e:
                    metric_results.append(MetricResult(
                        metric_name=metric_name,
                        score=0.0,
                        passed=False,
                        error=str(e)
                    ))

            # Calculate overall score
            if metric_results:
                overall_score = sum(m.score for m in metric_results) / len(metric_results)
                passed = all(m.passed for m in metric_results)
            else:
                overall_score = 0.0
                passed = False

            return EvaluationResult(
                agent_name=agent_name,
                test_case_id=test_case.id,
                metrics=metric_results,
                overall_score=overall_score,
                passed=passed,
                execution_time_ms=execution_time_ms,
                metadata={
                    'suite': suite_name,
                    'test_name': test_case.name,
                    'tags': test_case.tags
                }
            )

        except Exception as e:
            # Agent execution failed
            execution_time_ms = (time.time() - start_time) * 1000

            return EvaluationResult(
                agent_name=agent_name,
                test_case_id=test_case.id,
                metrics=[
                    MetricResult(
                        metric_name="execution",
                        score=0.0,
                        passed=False,
                        error=str(e)
                    )
                ],
                overall_score=0.0,
                passed=False,
                execution_time_ms=execution_time_ms,
                metadata={
                    'suite': suite_name,
                    'test_name': test_case.name,
                    'error': str(e)
                }
            )

    def evaluate_agent_sync(
        self,
        agent_name: str,
        agent_callable: Callable,
        test_cases: List[TestCase],
        suite_name: Optional[str] = None
    ) -> List[EvaluationResult]:
        """Synchronous wrapper for evaluate_agent."""
        return asyncio.run(
            self.evaluate_agent(agent_name, agent_callable, test_cases, suite_name)
        )
