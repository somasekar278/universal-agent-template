"""
Report Generators for Benchmark Results

Generates reports in various formats: Markdown, JSON, HTML, and Leaderboards.
"""

from typing import Dict, List, Any
from pathlib import Path
from abc import ABC, abstractmethod
import json
from datetime import datetime

from .metrics import EvaluationResult


class Reporter(ABC):
    """Base class for report generators."""

    @abstractmethod
    async def generate(
        self,
        results: Dict[str, List[EvaluationResult]],
        output_path: Path
    ):
        """Generate report."""
        pass


class MarkdownReporter(Reporter):
    """Generates Markdown reports."""

    async def generate(
        self,
        results: Dict[str, List[EvaluationResult]],
        output_path: Path
    ):
        """Generate Markdown report."""
        lines = []

        # Header
        lines.append("# Agent Benchmark Report")
        lines.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"\n**Agents Tested:** {len(results)}")

        total_tests = sum(len(r) for r in results.values())
        lines.append(f"**Total Test Cases:** {total_tests}")
        lines.append("\n---\n")

        # Per-agent results
        for agent_name, agent_results in results.items():
            lines.append(f"\n## Agent: {agent_name}\n")

            if not agent_results:
                lines.append("*No test results*\n")
                continue

            # Summary stats
            passed = sum(1 for r in agent_results if r.passed)
            total = len(agent_results)
            pass_rate = (passed / total * 100) if total > 0 else 0
            avg_score = sum(r.overall_score for r in agent_results) / total
            avg_time = sum(r.execution_time_ms for r in agent_results) / total

            lines.append(f"**Pass Rate:** {pass_rate:.1f}% ({passed}/{total})")
            lines.append(f"**Average Score:** {avg_score:.3f}")
            lines.append(f"**Average Latency:** {avg_time:.1f}ms\n")

            # Detailed results table
            lines.append("### Detailed Results\n")
            lines.append("| Test Case | Status | Score | Latency (ms) | Metrics |")
            lines.append("|-----------|--------|-------|--------------|---------|")

            for result in agent_results:
                status = "✅ PASS" if result.passed else "❌ FAIL"
                metrics_summary = self._format_metrics(result)

                lines.append(
                    f"| {result.test_case_id} | {status} | "
                    f"{result.overall_score:.3f} | {result.execution_time_ms:.1f} | "
                    f"{metrics_summary} |"
                )

            lines.append("")

            # Metric breakdown
            lines.append("### Metric Breakdown\n")
            metric_scores = self._aggregate_metrics(agent_results)

            for metric_name, avg_score in metric_scores.items():
                lines.append(f"- **{metric_name}:** {avg_score:.3f}")

            lines.append("\n---\n")

        # Write to file
        output_path.write_text("\n".join(lines))

    def _format_metrics(self, result: EvaluationResult) -> str:
        """Format metrics for table."""
        metrics_str = []
        for metric in result.metrics:
            status = "✓" if metric.passed else "✗"
            metrics_str.append(f"{metric.metric_name}:{status}")
        return ", ".join(metrics_str[:3])  # Limit to 3 for readability

    def _aggregate_metrics(self, results: List[EvaluationResult]) -> Dict[str, float]:
        """Aggregate metric scores."""
        metric_totals = {}
        metric_counts = {}

        for result in results:
            for metric in result.metrics:
                if metric.metric_name not in metric_totals:
                    metric_totals[metric.metric_name] = 0.0
                    metric_counts[metric.metric_name] = 0

                metric_totals[metric.metric_name] += metric.score
                metric_counts[metric.metric_name] += 1

        return {
            name: total / metric_counts[name]
            for name, total in metric_totals.items()
        }


class JSONReporter(Reporter):
    """Generates JSON reports."""

    async def generate(
        self,
        results: Dict[str, List[EvaluationResult]],
        output_path: Path
    ):
        """Generate JSON report."""
        report = {
            "generated_at": datetime.now().isoformat(),
            "agents": {}
        }

        for agent_name, agent_results in results.items():
            agent_data = {
                "total_tests": len(agent_results),
                "passed": sum(1 for r in agent_results if r.passed),
                "failed": sum(1 for r in agent_results if not r.passed),
                "average_score": (
                    sum(r.overall_score for r in agent_results) / len(agent_results)
                    if agent_results else 0.0
                ),
                "average_latency_ms": (
                    sum(r.execution_time_ms for r in agent_results) / len(agent_results)
                    if agent_results else 0.0
                ),
                "results": [
                    self._result_to_dict(r) for r in agent_results
                ]
            }
            report["agents"][agent_name] = agent_data

        output_path.write_text(json.dumps(report, indent=2))

    def _result_to_dict(self, result: EvaluationResult) -> Dict[str, Any]:
        """Convert EvaluationResult to dict."""
        return {
            "test_case_id": result.test_case_id,
            "passed": result.passed,
            "overall_score": result.overall_score,
            "execution_time_ms": result.execution_time_ms,
            "metrics": [
                {
                    "name": m.metric_name,
                    "score": m.score,
                    "passed": m.passed,
                    "threshold": m.threshold,
                    "details": m.details,
                    "error": m.error
                }
                for m in result.metrics
            ],
            "metadata": result.metadata
        }


class HTMLReporter(Reporter):
    """Generates HTML reports with interactive charts."""

    async def generate(
        self,
        results: Dict[str, List[EvaluationResult]],
        output_path: Path
    ):
        """Generate HTML report."""
        html = self._generate_html(results)
        output_path.write_text(html)

    def _generate_html(self, results: Dict[str, List[EvaluationResult]]) -> str:
        """Generate HTML content."""
        # Build HTML with embedded CSS and basic charts
        html_parts = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            "<meta charset='utf-8'>",
            "<title>Agent Benchmark Report</title>",
            "<style>",
            self._get_css(),
            "</style>",
            "</head>",
            "<body>",
            "<div class='container'>",
            f"<h1>Agent Benchmark Report</h1>",
            f"<p class='timestamp'>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>",
        ]

        # Summary table
        html_parts.append("<h2>Summary</h2>")
        html_parts.append("<table>")
        html_parts.append("<tr><th>Agent</th><th>Tests</th><th>Pass Rate</th><th>Avg Score</th><th>Avg Latency</th></tr>")

        for agent_name, agent_results in results.items():
            if not agent_results:
                continue

            passed = sum(1 for r in agent_results if r.passed)
            total = len(agent_results)
            pass_rate = (passed / total * 100) if total > 0 else 0
            avg_score = sum(r.overall_score for r in agent_results) / total
            avg_time = sum(r.execution_time_ms for r in agent_results) / total

            html_parts.append(
                f"<tr>"
                f"<td><strong>{agent_name}</strong></td>"
                f"<td>{total}</td>"
                f"<td>{pass_rate:.1f}%</td>"
                f"<td>{avg_score:.3f}</td>"
                f"<td>{avg_time:.1f}ms</td>"
                f"</tr>"
            )

        html_parts.append("</table>")

        # Detailed results per agent
        for agent_name, agent_results in results.items():
            html_parts.append(f"<h2>Agent: {agent_name}</h2>")

            if not agent_results:
                html_parts.append("<p><em>No results</em></p>")
                continue

            html_parts.append("<table>")
            html_parts.append("<tr><th>Test Case</th><th>Status</th><th>Score</th><th>Latency</th><th>Metrics</th></tr>")

            for result in agent_results:
                status_class = "pass" if result.passed else "fail"
                status_text = "✅ PASS" if result.passed else "❌ FAIL"

                metrics_html = "<br>".join(
                    f"{m.metric_name}: {m.score:.2f}"
                    for m in result.metrics[:5]  # Limit display
                )

                html_parts.append(
                    f"<tr>"
                    f"<td>{result.test_case_id}</td>"
                    f"<td class='{status_class}'>{status_text}</td>"
                    f"<td>{result.overall_score:.3f}</td>"
                    f"<td>{result.execution_time_ms:.1f}ms</td>"
                    f"<td><small>{metrics_html}</small></td>"
                    f"</tr>"
                )

            html_parts.append("</table>")

        html_parts.extend([
            "</div>",
            "</body>",
            "</html>"
        ])

        return "\n".join(html_parts)

    def _get_css(self) -> str:
        """Get CSS styles."""
        return """
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            border-bottom: 3px solid #0066cc;
            padding-bottom: 10px;
        }
        h2 {
            color: #555;
            margin-top: 30px;
            border-bottom: 1px solid #ddd;
            padding-bottom: 8px;
        }
        .timestamp {
            color: #666;
            font-size: 14px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background: #f8f9fa;
            font-weight: 600;
            color: #333;
        }
        tr:hover {
            background: #f8f9fa;
        }
        .pass {
            color: #28a745;
            font-weight: 600;
        }
        .fail {
            color: #dc3545;
            font-weight: 600;
        }
        """


class LeaderboardGenerator(Reporter):
    """Generates leaderboard ranking agents."""

    async def generate(
        self,
        results: Dict[str, List[EvaluationResult]],
        output_path: Path
    ):
        """Generate leaderboard."""
        # Calculate rankings
        rankings = []

        for agent_name, agent_results in results.items():
            if not agent_results:
                continue

            passed = sum(1 for r in agent_results if r.passed)
            total = len(agent_results)
            avg_score = sum(r.overall_score for r in agent_results) / total
            avg_time = sum(r.execution_time_ms for r in agent_results) / total

            # Calculate composite score
            pass_rate = passed / total
            # Score: 70% based on accuracy, 20% on pass rate, 10% on speed
            speed_score = max(0, 1.0 - (avg_time / 5000))  # Normalize to 5s
            composite = (avg_score * 0.7 + pass_rate * 0.2 + speed_score * 0.1)

            rankings.append({
                "agent": agent_name,
                "composite_score": composite,
                "avg_score": avg_score,
                "pass_rate": pass_rate,
                "avg_latency_ms": avg_time,
                "total_tests": total
            })

        # Sort by composite score
        rankings.sort(key=lambda x: x["composite_score"], reverse=True)

        # Generate markdown
        lines = [
            "# 🏆 Agent Leaderboard",
            f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "\n## Rankings\n",
            "| Rank | Agent | Composite Score | Avg Score | Pass Rate | Avg Latency | Tests |",
            "|------|-------|-----------------|-----------|-----------|-------------|-------|"
        ]

        for i, ranking in enumerate(rankings, 1):
            medal = self._get_medal(i)
            lines.append(
                f"| {medal} {i} | **{ranking['agent']}** | "
                f"{ranking['composite_score']:.3f} | "
                f"{ranking['avg_score']:.3f} | "
                f"{ranking['pass_rate']*100:.1f}% | "
                f"{ranking['avg_latency_ms']:.1f}ms | "
                f"{ranking['total_tests']} |"
            )

        lines.append("\n---\n")
        lines.append("### Scoring Methodology\n")
        lines.append("- **Composite Score** = 70% Accuracy + 20% Pass Rate + 10% Speed")
        lines.append("- Higher scores are better")
        lines.append("- Latency normalized to 5000ms budget")

        output_path.write_text("\n".join(lines))

    def _get_medal(self, rank: int) -> str:
        """Get medal emoji for rank."""
        if rank == 1:
            return "🥇"
        elif rank == 2:
            return "🥈"
        elif rank == 3:
            return "🥉"
        return "  "
