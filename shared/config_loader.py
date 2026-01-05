"""
YAML Configuration Loader

Loads and manages configuration from YAML files with:
- Environment variable substitution
- Environment-specific overrides
- Validation
- Unity Catalog integration

Usage:
    from shared.config_loader import load_config, get_config

    # Load configuration
    config = load_config("config/sota_config.yaml")

    # Access nested values
    catalog = config.get("databricks.unity_catalog.catalog_name")

    # Get typed values
    enabled = config.get_bool("telemetry.enabled")
    batch_size = config.get_int("telemetry.exporters.delta_lake.batch_size")
"""

from typing import Any, Optional, Dict
from pathlib import Path
import os
import re
import yaml


class Config:
    """Configuration object with nested access."""

    def __init__(self, data: Dict[str, Any], environment: str = "production"):
        """
        Initialize configuration.

        Args:
            data: Configuration dictionary
            environment: Environment name (dev, staging, production)
        """
        self._data = data
        self._environment = environment
        self._apply_environment_overrides()

    def _apply_environment_overrides(self):
        """Apply environment-specific overrides."""
        if "deployment" in self._data and "environments" in self._data["deployment"]:
            env_overrides = self._data["deployment"]["environments"].get(self._environment, {})
            self._merge_dict(self._data, env_overrides)

    def _merge_dict(self, base: Dict, override: Dict):
        """Recursively merge override into base."""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_dict(base[key], value)
            else:
                base[key] = value

    def get(self, path: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-separated path.

        Args:
            path: Dot-separated path (e.g., "databricks.unity_catalog.catalog_name")
            default: Default value if path not found

        Returns:
            Configuration value or default
        """
        keys = path.split(".")
        value = self._data

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def get_str(self, path: str, default: str = "") -> str:
        """Get string value."""
        return str(self.get(path, default))

    def get_int(self, path: str, default: int = 0) -> int:
        """Get integer value."""
        value = self.get(path, default)
        return int(value) if value is not None else default

    def get_float(self, path: str, default: float = 0.0) -> float:
        """Get float value."""
        value = self.get(path, default)
        return float(value) if value is not None else default

    def get_bool(self, path: str, default: bool = False) -> bool:
        """Get boolean value."""
        value = self.get(path, default)
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ("true", "yes", "1", "on")
        return bool(value)

    def get_list(self, path: str, default: list = None) -> list:
        """Get list value."""
        value = self.get(path, default or [])
        return value if isinstance(value, list) else default or []

    def get_dict(self, path: str, default: dict = None) -> dict:
        """Get dictionary value."""
        value = self.get(path, default or {})
        return value if isinstance(value, dict) else default or {}

    @property
    def environment(self) -> str:
        """Get current environment."""
        return self._environment

    @property
    def data(self) -> Dict:
        """Get raw configuration data."""
        return self._data

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return self._data.copy()


class ConfigLoader:
    """Configuration loader with YAML parsing and variable substitution."""

    def __init__(self):
        """Initialize loader."""
        self._env_pattern = re.compile(r'\$\{([^}]+)\}')

    def load(self, config_path: str, environment: Optional[str] = None) -> Config:
        """
        Load configuration from YAML file.

        Args:
            config_path: Path to YAML configuration file
            environment: Environment name (auto-detected if None)

        Returns:
            Config object
        """
        # Resolve path
        path = Path(config_path)
        if not path.is_absolute():
            # Try relative to project root
            root = self._find_project_root()
            if root:
                path = root / config_path

        # Check if in Databricks and try UC Volume
        if not path.exists() and self._in_databricks():
            path = self._try_uc_volume_path(config_path)

        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        # Load YAML
        with open(path, 'r') as f:
            data = yaml.safe_load(f)

        # Substitute environment variables
        data = self._substitute_env_vars(data)

        # Determine environment
        if environment is None:
            environment = data.get("environment", "production")
            # Override from env var if set
            environment = os.environ.get("SOTA_ENVIRONMENT", environment)

        return Config(data, environment)

    def _substitute_env_vars(self, obj: Any) -> Any:
        """
        Recursively substitute environment variables.

        Supports ${VAR} syntax.
        """
        if isinstance(obj, dict):
            return {k: self._substitute_env_vars(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._substitute_env_vars(item) for item in obj]
        elif isinstance(obj, str):
            return self._env_pattern.sub(
                lambda m: os.environ.get(m.group(1), m.group(0)),
                obj
            )
        return obj

    def _find_project_root(self) -> Optional[Path]:
        """Find project root directory."""
        current = Path.cwd()

        # Look for indicators of project root
        indicators = ["pyproject.toml", "setup.py", ".git", "config"]

        for _ in range(10):  # Max 10 levels up
            if any((current / indicator).exists() for indicator in indicators):
                return current
            parent = current.parent
            if parent == current:
                break
            current = parent

        return None

    def _in_databricks(self) -> bool:
        """Check if running in Databricks."""
        return "DATABRICKS_RUNTIME_VERSION" in os.environ

    def _try_uc_volume_path(self, config_path: str) -> Path:
        """Try to find config in Unity Catalog Volume."""
        # Default location in UC Volume
        # /Volumes/{catalog}/{schema}/agent_configs/sota_config.yaml
        volume_path = "/Volumes/sota_agents/production/agent_configs"
        filename = Path(config_path).name
        return Path(volume_path) / filename


# Global configuration instance
_config: Optional[Config] = None


def load_config(config_path: str = "config/sota_config.yaml", environment: Optional[str] = None) -> Config:
    """
    Load configuration from YAML file.

    Args:
        config_path: Path to configuration file
        environment: Environment name (auto-detected if None)

    Returns:
        Config object
    """
    global _config
    loader = ConfigLoader()
    _config = loader.load(config_path, environment)
    return _config


def get_config() -> Config:
    """
    Get global configuration instance.

    Loads default config if not already loaded.

    Returns:
        Config object
    """
    global _config
    if _config is None:
        _config = load_config()
    return _config


def reload_config(config_path: str = "config/sota_config.yaml", environment: Optional[str] = None) -> Config:
    """
    Reload configuration.

    Args:
        config_path: Path to configuration file
        environment: Environment name

    Returns:
        Config object
    """
    global _config
    _config = None
    return load_config(config_path, environment)
