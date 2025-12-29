"""
Schema adapters for customer-specific data transformations.

Adapters convert between customer-specific schemas and our canonical internal schemas,
enabling rapid deployment to new customers without changing core logic.
"""

from .base import SchemaAdapter, AdapterRegistry
from .transaction_adapters import (
    DefaultTransactionAdapter,
    StripeTransactionAdapter,
    AdyenTransactionAdapter,
)

__all__ = [
    "SchemaAdapter",
    "AdapterRegistry",
    "DefaultTransactionAdapter",
    "StripeTransactionAdapter",
    "AdyenTransactionAdapter",
]

