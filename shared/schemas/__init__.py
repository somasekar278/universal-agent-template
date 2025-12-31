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

# Generic schemas for learning path (Levels 1-5)
from .learning import (
    # Level 1: Simple Chatbot
    ChatInput,
    ChatOutput,
    # Level 2: Context-Aware
    ContextAwareInput,
    ContextAwareOutput,
    # Level 3: Production API
    APIRequest,
    APIResponse,
    HealthCheckResponse,
    # Level 4: Complex Workflow
    WorkflowInput,
    WorkflowOutput,
    TaskStep,
    TaskStatus,
    # Level 5: Multi-Agent
    CollaborationRequest,
    CollaborationResponse,
    AgentCapabilityInfo,
    # Universal (all levels)
    UniversalInput,
    UniversalOutput,
    # Helpers
    get_input_schema_for_level,
    get_output_schema_for_level,
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
    # Learning Path Schemas (Generic)
    "ChatInput",
    "ChatOutput",
    "ContextAwareInput",
    "ContextAwareOutput",
    "APIRequest",
    "APIResponse",
    "HealthCheckResponse",
    "WorkflowInput",
    "WorkflowOutput",
    "TaskStep",
    "TaskStatus",
    "CollaborationRequest",
    "CollaborationResponse",
    "AgentCapabilityInfo",
    "UniversalInput",
    "UniversalOutput",
    "get_input_schema_for_level",
    "get_output_schema_for_level",
]

