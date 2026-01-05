"""Metrics recording - stub."""

def record_metric(name: str, value: float, attributes: dict = None):
    """Record a metric."""
    pass

def record_latency(operation: str, duration_ms: float):
    """Record latency metric."""
    pass

def record_cost(operation: str, cost: float):
    """Record cost metric."""
    pass

def record_tokens(operation: str, tokens: int):
    """Record token usage."""
    pass

class MetricsRecorder:
    """Metrics recorder."""
    pass
