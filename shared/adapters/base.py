"""
Base adapter classes and registry for schema transformations.

Provides the foundation for converting customer-specific schemas to our
canonical internal schemas.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Type, Optional, TypeVar, Generic
from pydantic import BaseModel


T = TypeVar('T', bound=BaseModel)
S = TypeVar('S', bound=BaseModel)


class SchemaAdapter(ABC, Generic[T, S]):
    """
    Base class for schema adapters.
    
    Adapters convert from customer schema (source) to canonical schema (target).
    
    Type parameters:
        T: Target (canonical) schema type
        S: Source (customer) schema type
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize adapter with optional configuration.
        
        Args:
            config: Customer-specific configuration (field mappings, defaults, etc.)
        """
        self.config = config or {}
    
    @abstractmethod
    def to_canonical(self, source: S | Dict[str, Any]) -> T:
        """
        Convert customer schema to canonical schema.
        
        Args:
            source: Customer data (as model or dict)
            
        Returns:
            Canonical schema instance
        """
        pass
    
    @abstractmethod
    def from_canonical(self, target: T) -> S | Dict[str, Any]:
        """
        Convert canonical schema back to customer schema.
        
        Args:
            target: Canonical schema instance
            
        Returns:
            Customer schema (as model or dict)
        """
        pass
    
    def _get_nested_value(self, data: Dict[str, Any], path: str, default: Any = None) -> Any:
        """
        Get nested value from dict using dot notation.
        
        Example:
            _get_nested_value(data, "payment.card.bin")
        """
        keys = path.split('.')
        value = data
        
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return default
            
            if value is None:
                return default
        
        return value
    
    def _set_nested_value(self, data: Dict[str, Any], path: str, value: Any) -> None:
        """Set nested value in dict using dot notation."""
        keys = path.split('.')
        current = data
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value


class AdapterRegistry:
    """
    Registry for schema adapters.
    
    Allows dynamic selection of adapters based on customer identifier.
    """
    
    def __init__(self):
        self._adapters: Dict[str, Type[SchemaAdapter]] = {}
        self._configs: Dict[str, Dict[str, Any]] = {}
    
    def register(
        self,
        customer_id: str,
        adapter_class: Type[SchemaAdapter],
        config: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Register an adapter for a customer.
        
        Args:
            customer_id: Customer identifier
            adapter_class: Adapter class to use
            config: Customer-specific configuration
        """
        self._adapters[customer_id] = adapter_class
        self._configs[customer_id] = config or {}
    
    def get_adapter(self, customer_id: str) -> SchemaAdapter:
        """
        Get adapter instance for a customer.
        
        Args:
            customer_id: Customer identifier
            
        Returns:
            Adapter instance
            
        Raises:
            KeyError: If customer not registered
        """
        if customer_id not in self._adapters:
            raise KeyError(f"No adapter registered for customer: {customer_id}")
        
        adapter_class = self._adapters[customer_id]
        config = self._configs[customer_id]
        
        return adapter_class(config=config)
    
    def list_customers(self) -> list[str]:
        """List all registered customers."""
        return list(self._adapters.keys())


# Global registry instance
adapter_registry = AdapterRegistry()

