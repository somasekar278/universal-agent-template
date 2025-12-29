"""
Core data schemas for the Realtime Insights & Alerts system.

This module provides Pydantic models for all data structures used throughout
the system, ensuring type safety and validation.
"""

from .transactions import (
    Transaction,
    PaymentMethod,
    TransactionStatus,
    FraudLabel,
)

from .nested_transaction import (
    NestedTransaction,
    PaymentMethodDetails,
    CustomerDetails,
    MerchantDetails,
    DeviceDetails,
)

from .fraud_signals import (
    FraudSignals,
    VelocitySignal,
    AmountAnomalySignal,
    LocationSignal,
    DeviceSignal,
)

from .contexts import (
    MerchantContext,
    CustomerContext,
    MerchantRiskTier,
)

from .agent_io import (
    AgentInput,
    AgentOutput,
    AgentAction,
    ReasoningStep,
    ToolCall,
    ToolResult,
)

from .evaluation import (
    EvaluationRecord,
    ScorerMetrics,
    FeedbackSignal,
)

from .telemetry import (
    TelemetryEvent,
    AgentTrace,
    MCPToolTrace,
    LLMTrace,
)

from .mcp_tools import (
    BINLookupResult,
    IPGeoLookupResult,
    SanctionsCheckResult,
    VelocityAnomalyResult,
    MCPToolResults,
)

from .embeddings import (
    Embedding,
    ConversationMessage,
    ConversationHistory,
    MerchantContextWithEmbedding,
    CustomerContextWithEmbedding,
    SimilarCaseResult,
)

from .optimization import (
    FewShotExample,
    PromptVersion,
    DSPyOptimizerMetadata,
    HighRiskSelectionMetadata,
    StreamingOutput,
)

__all__ = [
    # Transactions
    "Transaction",
    "PaymentMethod",
    "TransactionStatus",
    "FraudLabel",
    # Nested Transactions
    "NestedTransaction",
    "PaymentMethodDetails",
    "CustomerDetails",
    "MerchantDetails",
    "DeviceDetails",
    # Fraud Signals
    "FraudSignals",
    "VelocitySignal",
    "AmountAnomalySignal",
    "LocationSignal",
    "DeviceSignal",
    # Contexts
    "MerchantContext",
    "CustomerContext",
    "MerchantRiskTier",
    # Agent I/O
    "AgentInput",
    "AgentOutput",
    "AgentAction",
    "ReasoningStep",
    "ToolCall",
    "ToolResult",
    # Evaluation
    "EvaluationRecord",
    "ScorerMetrics",
    "FeedbackSignal",
    # Telemetry
    "TelemetryEvent",
    "AgentTrace",
    "MCPToolTrace",
    "LLMTrace",
    # MCP Tool Results
    "BINLookupResult",
    "IPGeoLookupResult",
    "SanctionsCheckResult",
    "VelocityAnomalyResult",
    "MCPToolResults",
    # Embeddings & Memory
    "Embedding",
    "ConversationMessage",
    "ConversationHistory",
    "MerchantContextWithEmbedding",
    "CustomerContextWithEmbedding",
    "SimilarCaseResult",
    # Optimization
    "FewShotExample",
    "PromptVersion",
    "DSPyOptimizerMetadata",
    "HighRiskSelectionMetadata",
    "StreamingOutput",
]

