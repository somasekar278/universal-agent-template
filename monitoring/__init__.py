"""
Monitoring Module

Production monitoring and observability:
- Health checks
- Metrics collection
- Alerting
- Performance monitoring
- Service status

Usage:
    from monitoring import HealthCheck, MetricsCollector

    # Health checks
    health = HealthCheck()
    status = health.check_all()

    # Metrics
    metrics = MetricsCollector()
    metrics.record_latency("agent_execution", 150.5)
"""

from .health_check import (
    HealthCheck,
    HealthStatus,
    ComponentHealth
)

from .metrics_collector import (
    MetricsCollector,
    Metric,
    MetricType
)

from .alerting import (
    AlertManager,
    Alert,
    AlertSeverity
)

from .performance import (
    PerformanceMonitor,
    PerformanceReport
)

__all__ = [
    # Health
    "HealthCheck",
    "HealthStatus",
    "ComponentHealth",

    # Metrics
    "MetricsCollector",
    "Metric",
    "MetricType",

    # Alerting
    "AlertManager",
    "Alert",
    "AlertSeverity",

    # Performance
    "PerformanceMonitor",
    "PerformanceReport",
]
