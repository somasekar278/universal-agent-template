#!/usr/bin/env python3
"""
Template Generator for SOTA Agent Framework

Scaffolds a new agent workflow project from the template.
Usage:
    python template_generator.py --domain "customer_support" --output ./my-support-agents
"""

import os
import argparse
import shutil
from pathlib import Path
from typing import Dict, Any


AGENT_TEMPLATE = """'''
{domain_title} Agent Implementation

Generated from SOTA Agent Framework template.
'''

from agents import Agent, AgentType, ExecutionPriority
from shared.schemas import AgentInput, AgentOutput
from datetime import datetime


class {agent_class_name}(Agent):
    '''
    {agent_description}
    
    This agent processes {domain_lower} requests and returns results.
    '''
    
    # Agent metadata
    agent_type = AgentType.{agent_type}
    execution_priority = ExecutionPriority.{priority}
    timeout_seconds = {timeout}
    
    def __init__(self, config: dict = None):
        super().__init__(config)
        # Initialize your agent-specific resources here
        # Example: self.model = load_model(config.get('model_name'))
    
    async def initialize(self) -> None:
        '''Initialize agent resources (called once at startup).'''
        await super().initialize()
        # TODO: Add your initialization logic
        # Example:
        # - Connect to databases
        # - Load models
        # - Establish connections
        pass
    
    async def process(self, request: AgentInput) -> AgentOutput:
        '''
        Process {domain_lower} request.
        
        Args:
            request: Standardized agent input
            
        Returns:
            Standardized agent output
        '''
        start_time = datetime.utcnow()
        
        # Extract your domain data
        domain_data = request.data
        
        # TODO: Implement your processing logic
        # Example:
        # result = await self.your_processing_method(domain_data)
        
        # For now, return a placeholder
        result_score = 0.5  # Replace with your logic
        result_narrative = "Placeholder result"  # Replace with your logic
        
        latency_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        return AgentOutput(
            request_id=request.request_id,
            agent_id=self.agent_id,
            risk_score=result_score,
            risk_narrative=result_narrative,
            recommended_action=self._score_to_action(result_score),
            confidence_score=0.8,
            started_at=start_time,
            completed_at=datetime.utcnow(),
            latency_ms=latency_ms,
            model_name=self.__class__.__name__,
        )
    
    async def cleanup(self) -> None:
        '''Clean up agent resources (called at shutdown).'''
        await super().cleanup()
        # TODO: Add your cleanup logic
        pass
    
    def _score_to_action(self, score: float) -> str:
        '''Convert score to action.'''
        # TODO: Customize for your domain
        if score > 0.8:
            return "high_priority"
        elif score > 0.5:
            return "medium_priority"
        else:
            return "low_priority"
"""


CONFIG_TEMPLATE = """# {domain_title} Agent Configuration
#
# Generated from SOTA Agent Framework template.
# Customize this configuration for your deployment.

agents:
  {agent_name}:
    class: "{module_path}.{agent_class_name}"
    enabled: true
    execution_mode: "{execution_mode}"  # Options: in_process, process_pool, ray_task
    timeout: {timeout}  # seconds
    retry_policy: "exponential"
    max_retries: 3
    
    # Custom configuration for your agent
    # Add any agent-specific parameters here
    # Example:
    # model_name: "your-model"
    # temperature: 0.7
"""


TEST_TEMPLATE = """'''
Tests for {domain_title} Agents

Generated from SOTA Agent Framework template.
'''

import pytest
from datetime import datetime
from shared.schemas import AgentInput, AgentOutput
from {module_path} import {agent_class_name}


@pytest.fixture
def test_config():
    '''Test configuration.'''
    return {{
        "model_name": "test-model",
        # Add your test config
    }}


@pytest.fixture
def sample_input():
    '''Sample agent input for testing.'''
    return AgentInput(
        request_id="test_123",
        data={{
            # Add your test data
            "id": "test_id",
            "timestamp": datetime.utcnow(),
        }},
        context={{}},
    )


@pytest.mark.asyncio
async def test_{agent_name}_initialization(test_config):
    '''Test agent initialization.'''
    agent = {agent_class_name}(test_config)
    await agent.initialize()
    
    assert agent.agent_id is not None
    assert agent.config == test_config
    
    await agent.cleanup()


@pytest.mark.asyncio
async def test_{agent_name}_process(test_config, sample_input):
    '''Test agent processing.'''
    agent = {agent_class_name}(test_config)
    await agent.initialize()
    
    result = await agent.process(sample_input)
    
    # Validate output
    assert isinstance(result, AgentOutput)
    assert result.request_id == sample_input.request_id
    assert result.agent_id is not None
    assert 0 <= result.risk_score <= 1
    assert result.latency_ms > 0
    
    await agent.cleanup()


@pytest.mark.asyncio
async def test_{agent_name}_timeout(test_config, sample_input):
    '''Test agent timeout handling.'''
    agent = {agent_class_name}(test_config)
    agent.timeout_seconds = 0.001  # Very short timeout
    
    # TODO: Add test for timeout behavior
    pass


@pytest.mark.asyncio
async def test_{agent_name}_error_handling(test_config):
    '''Test agent error handling.'''
    agent = {agent_class_name}(test_config)
    await agent.initialize()
    
    # Create invalid input
    invalid_input = AgentInput(
        request_id="invalid",
        data={{}},  # Empty data
        context={{}},
    )
    
    # TODO: Test how agent handles invalid input
    # result = await agent.process(invalid_input)
    # assert result is handled appropriately
    
    await agent.cleanup()


# Add more tests as needed
"""


EXAMPLE_USAGE_TEMPLATE = """'''
Example usage of {domain_title} agents

Generated from SOTA Agent Framework template.
'''

import asyncio
from agents import AgentRouter
from shared.schemas import AgentInput


async def main():
    '''Example usage of your agents.'''
    
    # Step 1: Load agents from config
    router = AgentRouter.from_yaml("config/{module_path}_config.yaml")
    print("✅ Agents loaded from config!")
    
    # Step 2: Create sample input
    agent_input = AgentInput(
        request_id="example_123",
        data={{
            # Add your domain-specific data here
            "id": "sample_id",
            # ...
        }},
        context={{}},
    )
    
    # Step 3: Execute agent
    print("\\n🤖 Executing agent...")
    result = await router.route("{agent_name}", agent_input)
    
    # Step 4: Handle result
    print("\\n✅ Agent completed!")
    print(f"Request ID: {{result.request_id}}")
    print(f"Score: {{result.risk_score:.3f}}")
    print(f"Action: {{result.recommended_action}}")
    print(f"Narrative: {{result.risk_narrative}}")
    print(f"Latency: {{result.latency_ms:.2f}}ms")


if __name__ == "__main__":
    asyncio.run(main())
"""


README_TEMPLATE = """# {domain_title} Agents

Generated from SOTA Agent Framework template.

## Overview

This project implements AI agents for {domain_lower} using the SOTA Agent Framework.

## Project Structure

```
.
├── {module_path}/           # Agent implementations
│   ├── __init__.py
│   └── agents.py
├── config/                  # Configuration files
│   └── {module_path}_config.yaml
├── tests/                   # Tests
│   └── test_{module_path}.py
├── examples/                # Usage examples
│   └── example_usage.py
├── requirements.txt         # Dependencies
└── README.md               # This file
```

## Getting Started

### 1. Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Edit `config/{module_path}_config.yaml` to customize agent behavior:

```yaml
agents:
  {agent_name}:
    enabled: true
    execution_mode: "in_process"  # or "ray_task" for distributed
    timeout: {timeout}
```

### 3. Usage

```python
from agents import AgentRouter
from shared.schemas import AgentInput

# Load agents
router = AgentRouter.from_yaml("config/{module_path}_config.yaml")

# Create input
agent_input = AgentInput(
    request_id="req_123",
    data=your_data
)

# Execute
result = await router.route("{agent_name}", agent_input)
```

### 4. Run Example

```bash
python examples/example_usage.py
```

## Development

### Run Tests

```bash
pytest tests/
```

### Add New Agent

1. Create agent class in `{module_path}/agents.py`
2. Add configuration in `config/{module_path}_config.yaml`
3. Write tests in `tests/test_{module_path}.py`

## Next Steps

- [ ] Implement your domain-specific logic in agent classes
- [ ] Customize configuration for your deployment
- [ ] Add integration with your existing pipeline
- [ ] Write additional tests
- [ ] Deploy to your environment

## Resources

- [SOTA Agent Framework Documentation](../docs/)
- [Template Guide](../docs/TEMPLATE_GUIDE.md)
- [Configuration System](../docs/CONFIGURATION_SYSTEM.md)

## License

MIT
"""


REQUIREMENTS_TEMPLATE = """# Requirements for {domain_title} Agents
# Generated from SOTA Agent Framework template

# Core dependencies (required)
pydantic>=2.0.0
pyyaml>=6.0
python-dateutil>=2.8.0

# Async support
asyncio-mqtt>=0.16.0  # If using message queues
aiohttp>=3.8.0  # If making HTTP calls

# Execution backends (optional, install as needed)
ray[default]>=2.0.0  # For distributed execution

# Testing
pytest>=7.0.0
pytest-asyncio>=0.21.0
pytest-cov>=4.0.0

# Development tools
black>=23.0.0
ruff>=0.1.0
mypy>=1.0.0
"""


def to_snake_case(text: str) -> str:
    """Convert text to snake_case."""
    import re
    text = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
    text = re.sub('([a-z0-9])([A-Z])', r'\1_\2', text)
    return text.replace(' ', '_').replace('-', '_').lower()


def to_pascal_case(text: str) -> str:
    """Convert text to PascalCase."""
    words = text.replace('_', ' ').replace('-', ' ').split()
    return ''.join(word.capitalize() for word in words)


def generate_project(
    domain: str,
    output_dir: str,
    agent_type: str = "ENRICHMENT",
    priority: str = "NORMAL",
    timeout: int = 30,
    execution_mode: str = "async"
):
    """
    Generate a new agent project from template.
    
    Args:
        domain: Domain name (e.g., "customer_support", "fraud_detection")
        output_dir: Output directory for generated project
        agent_type: Agent type (CRITICAL_PATH, ENRICHMENT, ORCHESTRATION)
        priority: Priority (CRITICAL, HIGH, NORMAL, LOW)
        timeout: Timeout in seconds
        execution_mode: Execution mode (in_process, process_pool, ray_task)
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Generate naming variants
    domain_snake = to_snake_case(domain)
    domain_pascal = to_pascal_case(domain)
    agent_name = f"{domain_snake}_agent"
    agent_class_name = f"{domain_pascal}Agent"
    module_path = domain_snake
    
    context = {
        "domain_title": domain.replace('_', ' ').title(),
        "domain_lower": domain.replace('_', ' ').lower(),
        "agent_name": agent_name,
        "agent_class_name": agent_class_name,
        "agent_description": f"Agent for processing {domain.replace('_', ' ')} requests",
        "module_path": module_path,
        "agent_type": agent_type,
        "priority": priority,
        "timeout": timeout,
        "execution_mode": execution_mode,
    }
    
    # Create directory structure
    agent_dir = output_path / module_path
    agent_dir.mkdir(exist_ok=True)
    
    config_dir = output_path / "config"
    config_dir.mkdir(exist_ok=True)
    
    tests_dir = output_path / "tests"
    tests_dir.mkdir(exist_ok=True)
    
    examples_dir = output_path / "examples"
    examples_dir.mkdir(exist_ok=True)
    
    # Generate files
    files = {
        agent_dir / "__init__.py": f"from .agents import {agent_class_name}\n\n__all__ = ['{agent_class_name}']\n",
        agent_dir / "agents.py": AGENT_TEMPLATE.format(**context),
        config_dir / f"{module_path}_config.yaml": CONFIG_TEMPLATE.format(**context),
        tests_dir / "__init__.py": "",
        tests_dir / f"test_{module_path}.py": TEST_TEMPLATE.format(**context),
        examples_dir / "example_usage.py": EXAMPLE_USAGE_TEMPLATE.format(**context),
        output_path / "README.md": README_TEMPLATE.format(**context),
        output_path / "requirements.txt": REQUIREMENTS_TEMPLATE.format(**context),
    }
    
    for file_path, content in files.items():
        file_path.write_text(content)
        print(f"✅ Created: {file_path.relative_to(output_path)}")
    
    print(f"\n🎉 Project generated successfully at: {output_path}")
    print("\nNext steps:")
    print(f"1. cd {output_path}")
    print("2. pip install -r requirements.txt")
    print(f"3. Implement your logic in {module_path}/agents.py")
    print("4. Run example: python examples/example_usage.py")
    print("5. Run tests: pytest tests/")


def main():
    parser = argparse.ArgumentParser(
        description="Generate a new agent workflow from SOTA Agent Framework template"
    )
    parser.add_argument(
        "--domain",
        required=True,
        help="Domain name (e.g., customer_support, fraud_detection)"
    )
    parser.add_argument(
        "--output",
        default="./generated_agent_project",
        help="Output directory (default: ./generated_agent_project)"
    )
    parser.add_argument(
        "--agent-type",
        choices=["CRITICAL_PATH", "ENRICHMENT", "ORCHESTRATION"],
        default="ENRICHMENT",
        help="Agent type (default: ENRICHMENT)"
    )
    parser.add_argument(
        "--priority",
        choices=["CRITICAL", "HIGH", "NORMAL", "LOW"],
        default="NORMAL",
        help="Execution priority (default: NORMAL)"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Timeout in seconds (default: 30)"
    )
    parser.add_argument(
        "--execution-mode",
        choices=["in_process", "process_pool", "ray_task"],
        default="ray_task",
        help="Execution mode (default: ray_task)"
    )
    
    args = parser.parse_args()
    
    generate_project(
        domain=args.domain,
        output_dir=args.output,
        agent_type=args.agent_type,
        priority=args.priority,
        timeout=args.timeout,
        execution_mode=args.execution_mode,
    )


if __name__ == "__main__":
    main()

