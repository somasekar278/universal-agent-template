"""
Configuration system for plug-and-play agent deployment.

Enables customers to configure agents via YAML/dict without code changes.

Example usage:
    # Load from YAML
    router = AgentRouter.from_yaml("agents.yaml")
    
    # Load from dict
    config = {"agents": {...}}
    router = AgentRouter.from_config(config)
"""

from typing import Dict, Any, Optional, Type
from pathlib import Path
import yaml
import importlib
import logging

from .base import Agent, AgentExecutionError
from .execution import ExecutionMode
from .registry import AgentRegistry, AgentRouter


logger = logging.getLogger(__name__)


class AgentConfigError(Exception):
    """Raised when agent configuration is invalid."""
    pass


class AgentConfig:
    """
    Agent configuration loader.
    
    Supports loading agent configurations from:
    - YAML files
    - Python dictionaries
    - Environment variables (future)
    
    Configuration format:
    ```yaml
    agents:
      narrative:
        class: "fraud_agents.agents.narrative.NarrativeAgent"
        enabled: true
        execution_mode: "async"  # or "inline", "ray_task", etc.
        threshold: 0.7  # Custom config
        timeout: 30
        retry_policy: "exponential"
        max_retries: 3
    ```
    """
    
    @classmethod
    def from_yaml(cls, path: str) -> Dict[str, Any]:
        """
        Load configuration from YAML file.
        
        Args:
            path: Path to YAML config file
            
        Returns:
            Configuration dictionary
            
        Raises:
            AgentConfigError: If file not found or invalid YAML
        """
        config_path = Path(path)
        
        if not config_path.exists():
            raise AgentConfigError(f"Config file not found: {path}")
        
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            logger.info(f"Loaded config from {path}")
            return config
        
        except yaml.YAMLError as e:
            raise AgentConfigError(f"Invalid YAML in {path}: {str(e)}")
        
        except Exception as e:
            raise AgentConfigError(f"Failed to load config from {path}: {str(e)}")
    
    @classmethod
    def validate(cls, config: Dict[str, Any]) -> None:
        """
        Validate configuration structure.
        
        Args:
            config: Configuration dictionary
            
        Raises:
            AgentConfigError: If configuration is invalid
        """
        if not isinstance(config, dict):
            raise AgentConfigError("Config must be a dictionary")
        
        if "agents" not in config:
            raise AgentConfigError("Config must have 'agents' key")
        
        agents_config = config["agents"]
        
        if not isinstance(agents_config, dict):
            raise AgentConfigError("'agents' must be a dictionary")
        
        for agent_name, agent_config in agents_config.items():
            cls._validate_agent_config(agent_name, agent_config)
    
    @classmethod
    def _validate_agent_config(cls, agent_name: str, agent_config: Dict[str, Any]) -> None:
        """Validate single agent configuration."""
        
        # Required fields
        if "class" not in agent_config:
            raise AgentConfigError(f"Agent '{agent_name}' missing required field: 'class'")
        
        # Validate execution_mode if specified
        if "execution_mode" in agent_config:
            mode = agent_config["execution_mode"]
            
            # Map common aliases
            mode_map = {
                "async": "ray_task",
                "inline": "in_process",
                "ephemeral": "ray_task",
                "hot_pool": "process_pool",
            }
            
            normalized_mode = mode_map.get(mode, mode)
            
            try:
                ExecutionMode(normalized_mode)
            except ValueError:
                valid_modes = [m.value for m in ExecutionMode] + list(mode_map.keys())
                raise AgentConfigError(
                    f"Invalid execution_mode '{mode}' for agent '{agent_name}'. "
                    f"Valid modes: {valid_modes}"
                )
    
    @classmethod
    def load_agent_class(cls, class_path: str) -> Type[Agent]:
        """
        Dynamically load agent class from string path.
        
        Args:
            class_path: Dotted path to agent class, e.g. "fraud_agents.NarrativeAgent"
            
        Returns:
            Agent class
            
        Raises:
            AgentConfigError: If class cannot be loaded
        """
        try:
            # Split module and class name
            module_path, class_name = class_path.rsplit(".", 1)
            
            # Import module
            module = importlib.import_module(module_path)
            
            # Get class
            agent_class = getattr(module, class_name)
            
            # Verify it's an Agent subclass
            if not issubclass(agent_class, Agent):
                raise AgentConfigError(
                    f"{class_path} is not a subclass of Agent"
                )
            
            return agent_class
        
        except (ValueError, ImportError, AttributeError) as e:
            raise AgentConfigError(
                f"Failed to load agent class '{class_path}': {str(e)}"
            )
    
    @classmethod
    def create_registry(cls, config: Dict[str, Any]) -> AgentRegistry:
        """
        Create AgentRegistry from configuration.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Populated AgentRegistry
            
        Raises:
            AgentConfigError: If configuration is invalid
        """
        # Validate config
        cls.validate(config)
        
        # Create registry
        registry = AgentRegistry()
        
        # Register each agent
        agents_config = config["agents"]
        
        for agent_name, agent_config in agents_config.items():
            # Skip disabled agents
            if not agent_config.get("enabled", True):
                logger.info(f"Skipping disabled agent: {agent_name}")
                continue
            
            try:
                # Load agent class
                agent_class = cls.load_agent_class(agent_config["class"])
                
                # Normalize execution mode
                execution_mode_str = agent_config.get("execution_mode", "ray_task")
                
                # Map common aliases
                mode_map = {
                    "async": "ray_task",
                    "inline": "in_process",
                    "ephemeral": "ray_task",
                    "hot_pool": "process_pool",
                }
                
                execution_mode_str = mode_map.get(execution_mode_str, execution_mode_str)
                execution_mode = ExecutionMode(execution_mode_str)
                
                # Extract registration parameters
                timeout = agent_config.get("timeout")
                retry_policy = agent_config.get("retry_policy", "exponential")
                max_retries = agent_config.get("max_retries", 3)
                
                # Extract custom config (everything except known fields)
                known_fields = {
                    "class", "enabled", "execution_mode", "timeout", 
                    "retry_policy", "max_retries", "threshold"
                }
                custom_config = {
                    k: v for k, v in agent_config.items()
                    if k not in known_fields
                }
                
                # Add threshold to custom config if present
                if "threshold" in agent_config:
                    custom_config["threshold"] = agent_config["threshold"]
                
                # Register agent
                registry.register(
                    agent_name=agent_name,
                    agent_class=agent_class,
                    execution_mode=execution_mode,
                    timeout=timeout,
                    retry_policy=retry_policy,
                    max_retries=max_retries,
                    config=custom_config
                )
                
                logger.info(
                    f"Registered agent: {agent_name} "
                    f"(class={agent_class.__name__}, mode={execution_mode.value})"
                )
            
            except Exception as e:
                raise AgentConfigError(
                    f"Failed to register agent '{agent_name}': {str(e)}"
                )
        
        return registry

