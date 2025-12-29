"""
Version 1.0.0 schemas.

This is the initial stable version of our schemas.
All v1.x.x versions are backward compatible with 1.0.0.
"""

# Re-export current schemas as v1
from shared.schemas.transactions import Transaction as TransactionV1
from shared.schemas.nested_transaction import NestedTransaction as NestedTransactionV1
from shared.schemas.agent_io import AgentOutput as AgentOutputV1, AgentInput as AgentInputV1
from shared.schemas.telemetry import TelemetryEvent as TelemetryEventV1


__all__ = [
    "TransactionV1",
    "NestedTransactionV1",
    "AgentOutputV1",
    "AgentInputV1",
    "TelemetryEventV1",
]

__version__ = "1.0.0"

