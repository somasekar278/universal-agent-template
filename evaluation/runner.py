"""
Benchmark Runner

Orchestrates full benchmark execution across multiple agents and suites.
"""

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from pathlib import Path
import asyncio
import importlib.util
import sys

from .harness import EvaluationHarness, BenchmarkSuite, TestCase
from .metrics import (
    Metric,
    ToolCallMetric,
    PlanCorrectnessMetric,
    HallucinationMetric,
    LatencyMetric,
    CoherenceMetric,
    AccuracyMetric,
    EvaluationResult
)
from .reporters import (
    MarkdownReporter,
    JSONReporter,
    HTMLReporter,
    LeaderboardGenerator
)


@dataclass
class BenchmarkConfig:
    """Configuration for benchmark run."""
    suite_names: List[str] = field(default_factory=list)  # "all" or specific suites
    agent_names: List[str] = field(default_factory=list)  # "all" or specific agents
    metrics: List[str] = field(default_factory=lambda: [
        "tool_call_success",
        "plan_correctness",
        "hallucination_rate",
        "latency",
        "coherence",
        "accuracy"
    ])
    filters: Dict[str, Any] = field(default_factory=dict)
    parallel: bool = False
    max_workers: int = 4
    output_dir: Path = field(default_factory=lambda: Path("benchmark_results"))
    report_formats: List[str] = field(default_factory=lambda: ["md", "json"])
    generate_leaderboard: bool = True

    @classmethod
    def from_cli_args(cls, args) -> "BenchmarkConfig":
        """Create config from CLI arguments."""
        return cls(
            suite_names=args.suite if args.suite != ["all"] else [],
            agent_names=args.agents if args.agents != ["all"] else [],
            metrics=args.metrics.split(",") if args.metrics else None,
            parallel=args.parallel,
            max_workers=args.max_workers,
            output_dir=Path(args.output_dir),
            report_formats=args.report.split(",") if args.report else ["md"],
            generate_leaderboard=not args.no_leaderboard
        )


class BenchmarkRunner:
    """
    Main benchmark orchestrator.

    Features:
    - Auto-discovers benchmark suites
    - Loads agents dynamically
    - Runs evaluations
    - Generates reports
    - Creates leaderboards
    """

    def __init__(
        self,
        config: BenchmarkConfig,
        benchmark_dir: Path = Path("benchmarks"),
        agents_dir: Path = Path("agents")
    ):
        """
        Initialize runner.

        Args:
            config: Benchmark configuration
            benchmark_dir: Directory containing benchmark suite YAML files
            agents_dir: Directory containing agent modules
        """
        self.config = config
        self.benchmark_dir = benchmark_dir
        self.agents_dir = agents_dir

        # Initialize metrics
        self.metrics = self._initialize_metrics()

        # Initialize harness
        self.harness = EvaluationHarness(
            metrics=self.metrics,
            parallel=config.parallel,
            max_workers=config.max_workers
        )

    def _initialize_metrics(self) -> Dict[str, Metric]:
        """Initialize all metrics."""
        return {
            "tool_call_success": ToolCallMetric(threshold=0.9),
            "plan_correctness": PlanCorrectnessMetric(threshold=0.8),
            "hallucination_rate": HallucinationMetric(threshold=0.9),
            "latency": LatencyMetric(threshold=0.8, latency_budget_ms=1000),
            "coherence": CoherenceMetric(threshold=0.7),
            "accuracy": AccuracyMetric(threshold=0.8),
        }

    def discover_suites(self) -> List[BenchmarkSuite]:
        """Discover all benchmark suites."""
        if not self.benchmark_dir.exists():
            print(f"⚠️  Benchmark directory not found: {self.benchmark_dir}")
            return []

        suites = []
        for yaml_file in self.benchmark_dir.glob("*.yaml"):
            try:
                suite = BenchmarkSuite.from_yaml(yaml_file)

                # Filter by suite name if specified
                if self.config.suite_names and suite.name not in self.config.suite_names:
                    continue

                suites.append(suite)
                print(f"✓ Loaded suite: {suite.name} ({len(suite.test_cases)} test cases)")
            except Exception as e:
                print(f"✗ Failed to load suite {yaml_file}: {e}")

        return suites

    def discover_agents(self) -> Dict[str, Callable]:
        """
        Discover all agents.

        Looks for agent modules with an `evaluate` function.
        """
        agents = {}

        if not self.agents_dir.exists():
            print(f"⚠️  Agents directory not found: {self.agents_dir}")
            return agents

        for agent_file in self.agents_dir.glob("*.py"):
            if agent_file.name.startswith("_"):
                continue

            agent_name = agent_file.stem

            # Filter by agent name if specified
            if self.config.agent_names and agent_name not in self.config.agent_names:
                continue

            try:
                # Load module
                spec = importlib.util.spec_from_file_location(agent_name, agent_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Look for evaluate function or Agent class
                if hasattr(module, 'evaluate'):
                    agents[agent_name] = module.evaluate
                    print(f"✓ Loaded agent: {agent_name}")
                elif hasattr(module, 'Agent'):
                    # Wrap Agent class
                    agent_instance = module.Agent()
                    agents[agent_name] = agent_instance.process
                    print(f"✓ Loaded agent: {agent_name} (class-based)")
                else:
                    print(f"⚠️  Agent {agent_name} has no 'evaluate' function or 'Agent' class")
            except Exception as e:
                print(f"✗ Failed to load agent {agent_name}: {e}")

        return agents

    async def run(self) -> Dict[str, List[EvaluationResult]]:
        """
        Run full benchmark.

        Returns:
            Dictionary mapping agent_name -> list of EvaluationResults
        """
        print("=" * 60)
        print("🚀 SOTA Agent Benchmark Runner")
        print("=" * 60)

        # Discover suites and agents
        print("\n📦 Discovering benchmark suites...")
        suites = self.discover_suites()

        if not suites:
            print("❌ No benchmark suites found!")
            return {}

        print(f"\n🤖 Discovering agents...")
        agents = self.discover_agents()

        if not agents:
            print("❌ No agents found!")
            return {}

        # Run evaluations
        print(f"\n⚡ Running evaluations...")
        print(f"   Suites: {len(suites)}")
        print(f"   Agents: {len(agents)}")
        print(f"   Parallel: {self.config.parallel}")
        print()

        all_results = {}

        for agent_name, agent_callable in agents.items():
            print(f"\n🔍 Evaluating: {agent_name}")
            agent_results = []

            for suite in suites:
                print(f"   Suite: {suite.name}...", end=" ")

                # Get test cases
                test_cases = suite.get_test_cases(self.config.filters)

                if not test_cases:
                    print("(no matching test cases)")
                    continue

                # Run evaluation
                try:
                    results = await self.harness.evaluate_agent(
                        agent_name=agent_name,
                        agent_callable=agent_callable,
                        test_cases=test_cases,
                        suite_name=suite.name
                    )
                    agent_results.extend(results)

                    # Print summary
                    passed = sum(1 for r in results if r.passed)
                    total = len(results)
                    print(f"✓ {passed}/{total} passed")

                except Exception as e:
                    print(f"✗ Error: {e}")

            all_results[agent_name] = agent_results

        # Generate reports
        print(f"\n📊 Generating reports...")
        await self._generate_reports(all_results)

        print(f"\n✅ Benchmark complete!")
        print(f"   Results saved to: {self.config.output_dir}")

        return all_results

    async def _generate_reports(self, results: Dict[str, List[EvaluationResult]]):
        """Generate all configured reports."""
        self.config.output_dir.mkdir(parents=True, exist_ok=True)

        # Markdown report
        if "md" in self.config.report_formats:
            reporter = MarkdownReporter()
            report_path = self.config.output_dir / "benchmark_report.md"
            await reporter.generate(results, report_path)
            print(f"   ✓ Markdown: {report_path}")

        # JSON report
        if "json" in self.config.report_formats:
            reporter = JSONReporter()
            report_path = self.config.output_dir / "benchmark_results.json"
            await reporter.generate(results, report_path)
            print(f"   ✓ JSON: {report_path}")

        # HTML report
        if "html" in self.config.report_formats:
            reporter = HTMLReporter()
            report_path = self.config.output_dir / "benchmark_report.html"
            await reporter.generate(results, report_path)
            print(f"   ✓ HTML: {report_path}")

        # Leaderboard
        if self.config.generate_leaderboard:
            leaderboard = LeaderboardGenerator()
            leaderboard_path = self.config.output_dir / "leaderboard.md"
            await leaderboard.generate(results, leaderboard_path)
            print(f"   ✓ Leaderboard: {leaderboard_path}")

    def run_sync(self) -> Dict[str, List[EvaluationResult]]:
        """Synchronous wrapper for run()."""
        return asyncio.run(self.run())
