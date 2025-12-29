"""
Tests for configuration system.

Tests YAML-based agent configuration loading.
"""

import pytest
import tempfile
import os
from pathlib import Path
from agents import AgentConfig, AgentConfigError


class TestConfigLoader:
    """Test configuration loading."""
    
    def test_load_yaml_valid(self):
        """Test loading valid YAML config."""
        # Create temp YAML file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
agents:
  test_agent:
    class: "agents.base.Agent"
    enabled: true
    execution_mode: "in_process"
    timeout: 30
""")
            config_path = f.name
        
        try:
            # Load config
            config = AgentConfig.from_yaml(config_path)
            
            # Verify structure
            assert "agents" in config
            assert "test_agent" in config["agents"]
            assert config["agents"]["test_agent"]["enabled"] is True
        
        finally:
            os.unlink(config_path)
    
    def test_load_yaml_missing_file(self):
        """Test loading non-existent file raises error."""
        with pytest.raises(AgentConfigError):
            AgentConfig.from_yaml("nonexistent.yaml")
    
    def test_load_yaml_invalid(self):
        """Test loading invalid YAML raises error."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: content:")
            config_path = f.name
        
        try:
            with pytest.raises(AgentConfigError):
                AgentConfig.from_yaml(config_path)
        finally:
            os.unlink(config_path)


class TestConfigValidation:
    """Test configuration validation."""
    
    def test_validate_missing_agents_key(self):
        """Test validation fails without 'agents' key."""
        config = {"wrong_key": {}}
        
        with pytest.raises(AgentConfigError, match="must have 'agents' key"):
            AgentConfig.validate(config)
    
    def test_validate_missing_class(self):
        """Test validation fails without 'class' field."""
        config = {
            "agents": {
                "test_agent": {
                    "enabled": True
                    # Missing 'class'
                }
            }
        }
        
        with pytest.raises(AgentConfigError, match="missing required field: 'class'"):
            AgentConfig.validate(config)
    
    def test_validate_invalid_execution_mode(self):
        """Test validation fails with invalid execution mode."""
        config = {
            "agents": {
                "test_agent": {
                    "class": "agents.base.Agent",
                    "execution_mode": "invalid_mode"
                }
            }
        }
        
        with pytest.raises(AgentConfigError, match="Invalid execution_mode"):
            AgentConfig.validate(config)
    
    def test_validate_execution_mode_aliases(self):
        """Test execution mode aliases are accepted."""
        config = {
            "agents": {
                "test_agent": {
                    "class": "agents.base.Agent",
                    "execution_mode": "async"  # Alias for ray_task
                }
            }
        }
        
        # Should not raise
        AgentConfig.validate(config)


def test_config_file_examples_valid():
    """Test that example config files are valid."""
    example_files = [
        "config/agents/example_basic.yaml",
        "config/agents/example_advanced.yaml",
        "config/agents/example_customer_sla.yaml",
    ]
    
    for example_file in example_files:
        if os.path.exists(example_file):
            # Should load without error
            config = AgentConfig.from_yaml(example_file)
            
            # Should validate
            AgentConfig.validate(config)

