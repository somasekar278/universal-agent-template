"""
Telemetry Module

OpenTelemetry integration for comprehensive agent observability:
- Traces: Agent execution flows
- Metrics: Performance indicators
- Logs: Structured logging
- Delta Lake: All data streamed to Delta for analysis

Pipeline: OTEL → Zerobus → Delta Lake

Install:
    pip install sota-agent-framework[telemetry]

Usage:
    from telemetry import init_telemetry, trace_agent

    # Initialize (auto-configures for Databricks)
    init_telemetry()

    # Trace agent execution
    @trace_agent
    async def my_agent(input_data):
        return process(input_data)
"""

from .tracer import (
    init_telemetry,
    trace_agent,
    trace_tool_call,
    get_tracer,
    AgentTracer
)

from .metrics import (
    record_metric,
    record_latency,
    record_cost,
    record_tokens,
    MetricsRecorder
)

from .exporter import (
    DeltaLakeExporter,
    ZerobusExporter,
    ExporterConfig
)

from .context import (
    get_trace_context,
    set_trace_context,
    TraceContext
)

__all__ = [
    # Tracer
    "init_telemetry",
    "trace_agent",
    "trace_tool_call",
    "get_tracer",
    "AgentTracer",

    # Metrics
    "record_metric",
    "record_latency",
    "record_cost",
    "record_tokens",
    "MetricsRecorder",

    # Exporter
    "DeltaLakeExporter",
    "ZerobusExporter",
    "ExporterConfig",

    # Context
    "get_trace_context",
    "set_trace_context",
    "TraceContext",
]
