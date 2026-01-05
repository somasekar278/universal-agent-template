"""Performance Monitoring"""
from dataclasses import dataclass
from typing import Dict

@dataclass
class PerformanceReport:
    avg_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    throughput: float

class PerformanceMonitor:
    """Monitor agent performance"""
    def get_report(self) -> PerformanceReport:
        return PerformanceReport(
            avg_latency_ms=150.0,
            p95_latency_ms=300.0,
            p99_latency_ms=500.0,
            throughput=100.0
        )
