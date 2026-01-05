"""Trace context management - stub."""

from dataclasses import dataclass

@dataclass
class TraceContext:
    """Trace context."""
    trace_id: str
    span_id: str
    agent_id: str

def get_trace_context() -> TraceContext:
    """Get current trace context."""
    return TraceContext("", "", "")

def set_trace_context(context: TraceContext):
    """Set trace context."""
    pass
