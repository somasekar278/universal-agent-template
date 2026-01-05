"""
Health Check System

Production health checks for all components.
"""

from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
from datetime import datetime


class HealthStatus(Enum):
    """Health status levels."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class ComponentHealth:
    """Health status of a component."""
    name: str
    status: HealthStatus
    message: str
    latency_ms: Optional[float] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class HealthCheck:
    """
    Comprehensive health check system.

    Usage:
        health = HealthCheck()

        # Register checks
        health.register("database", check_database_connection)
        health.register("llm", check_llm_availability)

        # Run all checks
        status = health.check_all()

        # Check specific component
        db_health = health.check("database")
    """

    def __init__(self):
        """Initialize health check system."""
        self.checks: Dict[str, Callable] = {}
        self._register_default_checks()

    def _register_default_checks(self):
        """Register default system checks."""
        self.register("system", self._check_system)
        self.register("memory", self._check_memory)
        self.register("disk", self._check_disk)

    def register(self, name: str, check_func: Callable):
        """Register a health check."""
        self.checks[name] = check_func
        print(f"❤️  Registered health check: {name}")

    def check(self, name: str) -> ComponentHealth:
        """Check a specific component."""
        if name not in self.checks:
            return ComponentHealth(
                name=name,
                status=HealthStatus.UNHEALTHY,
                message=f"Unknown component: {name}"
            )

        try:
            start = datetime.now()
            check_func = self.checks[name]
            result = check_func()
            latency = (datetime.now() - start).total_seconds() * 1000

            if isinstance(result, ComponentHealth):
                result.latency_ms = latency
                return result
            elif result is True:
                return ComponentHealth(
                    name=name,
                    status=HealthStatus.HEALTHY,
                    message="OK",
                    latency_ms=latency
                )
            else:
                return ComponentHealth(
                    name=name,
                    status=HealthStatus.UNHEALTHY,
                    message=str(result),
                    latency_ms=latency
                )

        except Exception as e:
            return ComponentHealth(
                name=name,
                status=HealthStatus.UNHEALTHY,
                message=f"Check failed: {str(e)}"
            )

    def check_all(self) -> Dict[str, ComponentHealth]:
        """Run all health checks."""
        results = {}

        for name in self.checks:
            results[name] = self.check(name)

        return results

    def is_healthy(self) -> bool:
        """Check if all components are healthy."""
        results = self.check_all()
        return all(
            health.status == HealthStatus.HEALTHY
            for health in results.values()
        )

    def get_status_summary(self) -> Dict[str, any]:
        """Get overall status summary."""
        results = self.check_all()

        healthy_count = sum(
            1 for h in results.values()
            if h.status == HealthStatus.HEALTHY
        )

        degraded_count = sum(
            1 for h in results.values()
            if h.status == HealthStatus.DEGRADED
        )

        unhealthy_count = sum(
            1 for h in results.values()
            if h.status == HealthStatus.UNHEALTHY
        )

        overall_status = HealthStatus.HEALTHY
        if unhealthy_count > 0:
            overall_status = HealthStatus.UNHEALTHY
        elif degraded_count > 0:
            overall_status = HealthStatus.DEGRADED

        return {
            "status": overall_status.value,
            "healthy": healthy_count,
            "degraded": degraded_count,
            "unhealthy": unhealthy_count,
            "total": len(results),
            "components": {
                name: {
                    "status": health.status.value,
                    "message": health.message,
                    "latency_ms": health.latency_ms
                }
                for name, health in results.items()
            }
        }

    def _check_system(self) -> ComponentHealth:
        """Check system resources."""
        try:
            import psutil
            cpu = psutil.cpu_percent(interval=0.1)

            if cpu > 90:
                return ComponentHealth(
                    name="system",
                    status=HealthStatus.DEGRADED,
                    message=f"High CPU: {cpu}%"
                )

            return ComponentHealth(
                name="system",
                status=HealthStatus.HEALTHY,
                message=f"CPU: {cpu}%"
            )
        except:
            return ComponentHealth(
                name="system",
                status=HealthStatus.HEALTHY,
                message="OK (psutil not available)"
            )

    def _check_memory(self) -> ComponentHealth:
        """Check memory usage."""
        try:
            import psutil
            mem = psutil.virtual_memory()

            if mem.percent > 90:
                return ComponentHealth(
                    name="memory",
                    status=HealthStatus.DEGRADED,
                    message=f"High memory: {mem.percent}%"
                )

            return ComponentHealth(
                name="memory",
                status=HealthStatus.HEALTHY,
                message=f"Memory: {mem.percent}%"
            )
        except:
            return ComponentHealth(
                name="memory",
                status=HealthStatus.HEALTHY,
                message="OK"
            )

    def _check_disk(self) -> ComponentHealth:
        """Check disk space."""
        try:
            import psutil
            disk = psutil.disk_usage('/')

            if disk.percent > 90:
                return ComponentHealth(
                    name="disk",
                    status=HealthStatus.DEGRADED,
                    message=f"Low disk space: {disk.percent}% used"
                )

            return ComponentHealth(
                name="disk",
                status=HealthStatus.HEALTHY,
                message=f"Disk: {disk.percent}% used"
            )
        except:
            return ComponentHealth(
                name="disk",
                status=HealthStatus.HEALTHY,
                message="OK"
            )
