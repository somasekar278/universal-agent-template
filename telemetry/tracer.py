"""
OpenTelemetry tracer for agent workflows.

Automatically detects Databricks environment and configures appropriately.
"""

from typing import Optional, Callable, Any
from functools import wraps
from datetime import datetime
import os


class TraceContext:
    """Trace context for agent execution."""

    def __init__(self, trace_id: str, span_id: str, agent_id: str):
        self.trace_id = trace_id
        self.span_id = span_id
        self.agent_id = agent_id
        self.start_time = datetime.now()
        self.attributes = {}


class AgentTracer:
    """
    Agent execution tracer.

    Integrates with OpenTelemetry and exports to Delta Lake.
    Configuration loaded from YAML.
    """

    def __init__(self, service_name: Optional[str] = None, config: Optional[Any] = None):
        # Load config from YAML if not provided
        if config is None:
            from shared.config_loader import get_config
            config = get_config()

        self.config = config
        self.service_name = service_name or config.get_str("telemetry.service_name", "sota-agent-framework")
        self.enabled = config.get_bool("telemetry.enabled", True)
        self._tracer = None
        self._exporter = None
        self._in_databricks = self._check_databricks()

    def _check_databricks(self) -> bool:
        """Check if running in Databricks."""
        return "DATABRICKS_RUNTIME_VERSION" in os.environ

    def initialize(self):
        """Initialize OpenTelemetry."""
        try:
            from opentelemetry import trace
            from opentelemetry.sdk.trace import TracerProvider
            from opentelemetry.sdk.trace.export import BatchSpanProcessor

            # Create provider
            provider = TracerProvider()
            trace.set_tracer_provider(provider)

            # Add exporter
            if self._in_databricks:
                # Use Delta Lake exporter
                from .exporter import DeltaLakeExporter
                exporter = DeltaLakeExporter()
            else:
                # Use console exporter for local dev
                from opentelemetry.sdk.trace.export import ConsoleSpanExporter
                exporter = ConsoleSpanExporter()

            provider.add_span_processor(BatchSpanProcessor(exporter))

            self._tracer = trace.get_tracer(self.service_name)
            self._exporter = exporter

            print(f"✅ Telemetry initialized (Databricks: {self._in_databricks})")

        except ImportError:
            print("⚠️  OpenTelemetry not installed. Run: pip install sota-agent-framework[telemetry]")
            self.enabled = False
        except Exception as e:
            print(f"⚠️  Failed to initialize telemetry: {e}")
            self.enabled = False

    def start_span(self, name: str, attributes: Optional[dict] = None):
        """Start a new span."""
        if not self.enabled or not self._tracer:
            return None

        span = self._tracer.start_span(name)

        if attributes:
            for key, value in attributes.items():
                span.set_attribute(key, str(value))

        return span

    def trace_function(self, func: Callable) -> Callable:
        """Decorator to trace a function."""
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            if not self.enabled:
                return await func(*args, **kwargs)

            with self.start_span(func.__name__) as span:
                try:
                    result = await func(*args, **kwargs)
                    if span:
                        span.set_attribute("status", "success")
                    return result
                except Exception as e:
                    if span:
                        span.set_attribute("status", "error")
                        span.set_attribute("error", str(e))
                    raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            if not self.enabled:
                return func(*args, **kwargs)

            with self.start_span(func.__name__) as span:
                try:
                    result = func(*args, **kwargs)
                    if span:
                        span.set_attribute("status", "success")
                    return result
                except Exception as e:
                    if span:
                        span.set_attribute("status", "error")
                        span.set_attribute("error", str(e))
                    raise

        # Return appropriate wrapper
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper


# Global tracer instance
_tracer: Optional[AgentTracer] = None


def init_telemetry(service_name: str = "sota-agent-framework"):
    """
    Initialize telemetry.

    Auto-detects Databricks and configures appropriately.

    Args:
        service_name: Service name for traces
    """
    global _tracer
    _tracer = AgentTracer(service_name)
    _tracer.initialize()


def get_tracer() -> AgentTracer:
    """Get global tracer instance."""
    global _tracer
    if _tracer is None:
        init_telemetry()
    return _tracer


def trace_agent(func: Callable) -> Callable:
    """
    Decorator to trace agent execution.

    Usage:
        @trace_agent
        async def my_agent(input_data):
            return process(input_data)
    """
    tracer = get_tracer()
    return tracer.trace_function(func)


def trace_tool_call(tool_name: str):
    """
    Decorator to trace tool calls.

    Usage:
        @trace_tool_call("my_tool")
        async def call_tool(input):
            return result
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            tracer = get_tracer()
            with tracer.start_span(f"tool.{tool_name}") as span:
                if span:
                    span.set_attribute("tool.name", tool_name)
                try:
                    result = await func(*args, **kwargs)
                    if span:
                        span.set_attribute("status", "success")
                    return result
                except Exception as e:
                    if span:
                        span.set_attribute("status", "error")
                        span.set_attribute("error", str(e))
                    raise
        return wrapper
    return decorator
