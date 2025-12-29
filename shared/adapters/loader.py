"""
Dynamic adapter loading from configuration files.

Enables loading customer-specific adapters from YAML configs without code changes.
"""

import yaml
from pathlib import Path
from typing import Optional

from .base import adapter_registry, SchemaAdapter
from .transaction_adapters import (
    DefaultTransactionAdapter,
    StripeTransactionAdapter,
    AdyenTransactionAdapter,
    ConfigurableTransactionAdapter,
)


# Map adapter class names to actual classes
ADAPTER_CLASSES = {
    "DefaultTransactionAdapter": DefaultTransactionAdapter,
    "StripeTransactionAdapter": StripeTransactionAdapter,
    "AdyenTransactionAdapter": AdyenTransactionAdapter,
    "ConfigurableTransactionAdapter": ConfigurableTransactionAdapter,
}


def load_adapter_config(config_path: str | Path) -> dict:
    """
    Load adapter configuration from YAML file.
    
    Args:
        config_path: Path to YAML config file
        
    Returns:
        Configuration dictionary
    """
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config


def register_adapter_from_config(config_path: str | Path) -> None:
    """
    Register an adapter from a configuration file.
    
    Args:
        config_path: Path to YAML config file
    """
    config = load_adapter_config(config_path)
    
    customer_id = config.get("customer_id")
    adapter_class_name = config.get("adapter_class")
    adapter_config = config.get("config", {})
    
    if not customer_id:
        raise ValueError(f"Missing 'customer_id' in {config_path}")
    
    if not adapter_class_name:
        raise ValueError(f"Missing 'adapter_class' in {config_path}")
    
    adapter_class = ADAPTER_CLASSES.get(adapter_class_name)
    if not adapter_class:
        raise ValueError(
            f"Unknown adapter class: {adapter_class_name}. "
            f"Available: {list(ADAPTER_CLASSES.keys())}"
        )
    
    adapter_registry.register(customer_id, adapter_class, adapter_config)
    print(f"✓ Registered adapter for customer '{customer_id}' using {adapter_class_name}")


def load_all_adapters(adapters_dir: str | Path) -> None:
    """
    Load all adapter configurations from a directory.
    
    Args:
        adapters_dir: Directory containing YAML adapter configs
    """
    adapters_path = Path(adapters_dir)
    
    if not adapters_path.exists():
        print(f"Warning: Adapters directory not found: {adapters_dir}")
        return
    
    for config_file in adapters_path.glob("*.yaml"):
        try:
            register_adapter_from_config(config_file)
        except Exception as e:
            print(f"✗ Failed to load {config_file}: {e}")


def get_adapter_for_customer(customer_id: str) -> SchemaAdapter:
    """
    Get adapter for a specific customer.
    
    Args:
        customer_id: Customer identifier
        
    Returns:
        Adapter instance
    """
    return adapter_registry.get_adapter(customer_id)


# Auto-load adapters on import
def auto_load_adapters():
    """Automatically load adapters from default location."""
    import os
    
    # Try to find config/adapters directory
    possible_paths = [
        Path("config/adapters"),
        Path(__file__).parent.parent.parent / "config" / "adapters",
    ]
    
    for path in possible_paths:
        if path.exists():
            load_all_adapters(path)
            break


# Uncomment to enable auto-loading
# auto_load_adapters()

