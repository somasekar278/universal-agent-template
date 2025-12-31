#!/usr/bin/env python3
"""
SOTA Agent Framework - Interactive Learning Mode

Guides users through building progressively complex agents,
from simple chatbot to autonomous multi-agent systems.
"""

import sys
from pathlib import Path
from typing import Optional
import shutil


LEVELS = {
    "1": {
        "name": "Simple Chatbot",
        "description": "Learn core agents, schemas, and routing",
        "time": "2-3 hours",
        "complexity": "⭐ Basic",
        "learns": [
            "Agent base class and process() method",
            "Pydantic schemas for type safety",
            "Agent registry and routing",
            "YAML configuration basics"
        ],
        "validates": [
            "agents.base", "agents.registry", 
            "shared.schemas", "shared.config_loader"
        ]
    },
    "2": {
        "name": "Context-Aware Assistant",
        "description": "Add memory to remember past interactions",
        "time": "3-4 hours",
        "complexity": "⭐⭐ Intermediate",
        "learns": [
            "Memory management and storage",
            "Retrieval strategies (recency, semantic)",
            "Context window management",
            "Memory configuration"
        ],
        "validates": [
            "memory.manager", "memory.stores", 
            "memory.strategies", "memory.context"
        ]
    },
    "3": {
        "name": "Production API",
        "description": "Deploy as REST API with monitoring",
        "time": "4-6 hours",
        "complexity": "⭐⭐⭐ Advanced",
        "learns": [
            "FastAPI service creation",
            "Health checks and metrics",
            "OpenTelemetry tracing",
            "Feature flags and A/B testing",
            "Background workers"
        ],
        "validates": [
            "services.api", "monitoring.health_check",
            "telemetry.tracer", "experiments.tracker"
        ]
    },
    "4": {
        "name": "Complex Workflow",
        "description": "Build autonomous Plan-Act-Critique loops",
        "time": "6-8 hours",
        "complexity": "⭐⭐⭐⭐ Expert",
        "learns": [
            "LangGraph workflows",
            "Reasoning optimization",
            "Prompt optimization (DSPy/TextGrad)",
            "Agent benchmarking",
            "Execution visualization"
        ],
        "validates": [
            "orchestration.langgraph.workflow", "reasoning.optimizer",
            "optimization.prompt_optimizer", "evaluation.runner"
        ]
    },
    "5": {
        "name": "Autonomous Multi-Agent System",
        "description": "Full SOTA system with all features + A2A protocol",
        "time": "8-12 hours",
        "complexity": "⭐⭐⭐⭐⭐ SOTA",
        "learns": [
            "Official A2A protocol (Linux Foundation standard)",
            "Cross-framework agent communication",
            "MCP integration",
            "Semantic embeddings & memory graphs",
            "Unity Catalog integration",
            "Databricks deployment (Terraform)",
            "Complete observability"
        ],
        "validates": [
            "agents.a2a", "agents.mcp_client", "memory.embeddings",
            "uc_registry.prompt_registry", "infra"
        ]
    }
}


def print_banner():
    """Print learning mode banner"""
    print("\n" + "="*70)
    print("🎓 SOTA Agent Framework - Interactive Learning Mode")
    print("="*70)
    print("\nLearn by building: From simple chatbot to autonomous multi-agent system")
    print()


def show_overview():
    """Show overview of all levels"""
    print("📚 Learning Path Overview\n")
    
    for level_id, info in LEVELS.items():
        print(f"Level {level_id}: {info['name']} {info['complexity']}")
        print(f"  📝 {info['description']}")
        print(f"  ⏱️  Time: {info['time']}")
        print()
    
    print("💡 Each level builds on the previous, introducing new concepts gradually.\n")


def show_level_details(level_id: str):
    """Show detailed information about a specific level"""
    if level_id not in LEVELS:
        print(f"❌ Invalid level: {level_id}")
        return
    
    info = LEVELS[level_id]
    
    print(f"\n{'='*70}")
    print(f"Level {level_id}: {info['name']} {info['complexity']}")
    print(f"{'='*70}\n")
    
    print(f"📝 {info['description']}")
    print(f"⏱️  Time: {info['time']}")
    print()
    
    print("✨ What You'll Learn:")
    for item in info['learns']:
        print(f"  ✅ {item}")
    print()
    
    print("🧪 What You'll Validate:")
    for module in info['validates']:
        print(f"  📦 {module}")
    print()


def create_level_project(level_id: str, output_dir: Optional[str] = None):
    """Create starter project for a specific level"""
    if level_id not in LEVELS:
        print(f"❌ Invalid level: {level_id}")
        return False
    
    info = LEVELS[level_id]
    
    # Determine output directory
    if output_dir is None:
        output_dir = f"learning_level{level_id}_{info['name'].lower().replace(' ', '_')}"
    
    output_path = Path(output_dir).resolve()
    
    # Check if directory exists
    if output_path.exists():
        print(f"⚠️  Directory already exists: {output_path}")
        response = input("Overwrite? (y/N): ").strip().lower()
        if response != 'y':
            print("Cancelled.")
            return False
        shutil.rmtree(output_path)
    
    # Create directory structure
    print(f"\n📁 Creating Level {level_id} project: {output_path}")
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Create subdirectories
    (output_path / "tests").mkdir(exist_ok=True)
    
    # Create files based on level
    create_level_files(level_id, output_path)
    
    print(f"\n✅ Level {level_id} project created!")
    print(f"\n📖 Next Steps:")
    print(f"   1. cd {output_dir}")
    print(f"   2. Read INSTRUCTIONS.md for detailed guidance")
    print(f"   3. Complete the TODOs in each file")
    print(f"   4. Run: python main.py")
    print(f"   5. Test: pytest tests/")
    print()
    
    return True


def create_level_files(level_id: str, output_path: Path):
    """Create starter files for a specific level"""
    
    info = LEVELS[level_id]
    
    # Create README
    readme_content = f"""# Level {level_id}: {info['name']}

**{info['description']}**

## Overview

{info['complexity']} - Estimated time: {info['time']}

### What You'll Learn

{chr(10).join(f'- {item}' for item in info['learns'])}

### What You'll Build

See `INSTRUCTIONS.md` for step-by-step guidance.

## Quick Start

```bash
# Install dependencies (if not already done)
pip install -e ..

# Run the example
python main.py

# Run tests
pytest tests/
```

## Files

- `main.py` - Main entry point (start here!)
- `agent.py` - Agent implementation (complete the TODOs)
- `schemas.py` - Input/Output schemas
- `config.yaml` - Configuration
- `tests/test_agent.py` - Tests to verify your implementation
- `INSTRUCTIONS.md` - Detailed step-by-step guide

## Resources

- Framework docs: `../docs/`
- Learning path: `../LEARNING_PATH.md`
- Source code: `../agents/`, `../memory/`, etc.

## Need Help?

1. Read `INSTRUCTIONS.md`
2. Check `../LEARNING_PATH.md`
3. Look at framework source code
4. Run `sota-learn --help`

**Good luck! You've got this! 🚀**
"""
    (output_path / "README.md").write_text(readme_content)
    
    # Create instructions
    instructions = create_instructions(level_id)
    (output_path / "INSTRUCTIONS.md").write_text(instructions)
    
    # Create level-specific starter files
    if level_id == "1":
        create_level1_files(output_path)
    elif level_id == "2":
        create_level2_files(output_path)
    elif level_id == "3":
        create_level3_files(output_path)
    elif level_id == "4":
        create_level4_files(output_path)
    elif level_id == "5":
        create_level5_files(output_path)


def create_instructions(level_id: str) -> str:
    """Create detailed instructions for a level"""
    
    instructions = {
        "1": """# Level 1: Simple Chatbot - Step-by-Step Instructions

## Goal
Build a simple Q&A chatbot that demonstrates core agent concepts.

## Step 1: Define Schemas (schemas.py)

**Objective**: Create type-safe input/output models

1. Open `schemas.py`
2. Find the TODO comments
3. Define `ChatInput` with:
   - `question: str` - The user's question
   - `user_id: str` - User identifier
4. Define `ChatOutput` with:
   - `answer: str` - The bot's response
   - `confidence: float` - Confidence score (0-1)

**Why?** Pydantic validates data automatically, preventing bugs.

## Step 2: Create Agent (agent.py)

**Objective**: Implement the core agent logic

1. Open `agent.py`
2. Your agent should inherit from `Agent`
3. Implement the `process()` method
4. For now, simple logic is fine (e.g., keyword matching)

**Key concepts:**
- All agents must implement `process()`
- Input is validated by Pydantic
- Output should match your schema

## Step 3: Main Application (main.py)

**Objective**: Register and route to your agent

1. Open `main.py`
2. Import your agent and schemas
3. Create an `AgentRegistry`
4. Register your agent
5. Route a test question

## Step 4: Configuration (config.yaml)

**Objective**: Learn configuration management

1. Open `config.yaml`
2. Add configuration for your agent
3. Load config in your agent

## Step 5: Tests (tests/test_agent.py)

**Objective**: Verify everything works

1. Open `tests/test_agent.py`
2. Complete test cases
3. Run: `pytest tests/`

## Verification

✅ `python main.py` runs without errors  
✅ Agent responds to questions  
✅ All tests pass  
✅ You understand agent basics  

## Next Level

Once complete, run: `sota-learn start 2`

**Congratulations on completing Level 1!** 🎉
""",
        "2": """# Level 2: Context-Aware Assistant - Instructions

## Goal
Add memory so your agent remembers past interactions.

## Key Concepts

**Memory Manager**: Orchestrates storage and retrieval  
**Stores**: Where memories are saved (in-memory, disk, Delta Lake)  
**Strategies**: How to retrieve (recency, semantic, importance)  

## Implementation Steps

[Similar detailed instructions for Level 2]

## Verification

✅ Agent remembers previous questions  
✅ Context improves responses  
✅ Memory storage works  
✅ Retrieval strategies work  

## Next Level

Run: `sota-learn start 3`
""",
        # Add similar for levels 3, 4, 5
    }
    
    return instructions.get(level_id, f"# Level {level_id} Instructions\n\nDetailed instructions coming soon...")


def create_level1_files(output_path: Path):
    """Create starter files for Level 1"""
    
    # schemas.py
    schemas = '''"""
Level 1: Schemas

Define your input and output data models using Pydantic.
"""

from pydantic import BaseModel, Field


# TODO: Define your ChatInput schema
class ChatInput(BaseModel):
    """Input schema for chat agent"""
    # TODO: Add 'question' field (str)
    # TODO: Add 'user_id' field (str)
    pass


# TODO: Define your ChatOutput schema
class ChatOutput(BaseModel):
    """Output schema for chat agent"""
    # TODO: Add 'answer' field (str)
    # TODO: Add 'confidence' field (float, between 0 and 1)
    pass
'''
    (output_path / "schemas.py").write_text(schemas)
    
    # agent.py
    agent = '''"""
Level 1: Agent Implementation

Create a simple chatbot agent.
"""

import sys
from pathlib import Path

# Add framework to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.base import Agent
from schemas import ChatInput, ChatOutput


# TODO: Create your SimpleChatAgent class
class SimpleChatAgent(Agent):
    """A simple Q&A chatbot agent"""
    
    def __init__(self, name: str = "chat_agent"):
        super().__init__(name=name)
    
    async def process(self, input_data: ChatInput) -> ChatOutput:
        """
        Process a chat question and return an answer.
        
        TODO: Implement your logic here!
        
        For now, you can:
        1. Check for keywords in the question
        2. Return canned responses
        3. Add a simple confidence score
        
        Later you'll make this more sophisticated!
        """
        
        # TODO: Your implementation here
        question = input_data.question.lower()
        
        # Example: Simple keyword matching
        if "hello" in question or "hi" in question:
            answer = "Hello! How can I help you today?"
            confidence = 0.9
        # TODO: Add more conditions
        else:
            answer = "I'm not sure I understand. Can you rephrase that?"
            confidence = 0.3
        
        return ChatOutput(answer=answer, confidence=confidence)
'''
    (output_path / "agent.py").write_text(agent)
    
    # main.py
    main = '''"""
Level 1: Main Application

Register your agent and route requests to it.
"""

import asyncio
import sys
from pathlib import Path

# Add framework to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.registry import AgentRegistry
from agent import SimpleChatAgent
from schemas import ChatInput


async def main():
    """Main application"""
    
    print("🤖 Level 1: Simple Chatbot\\n")
    
    # TODO: Create agent registry
    registry = AgentRegistry()
    
    # TODO: Create and register your agent
    chat_agent = SimpleChatAgent()
    registry.register("chat", chat_agent)
    
    # TODO: Test with some questions
    test_questions = [
        "Hello!",
        "What is your name?",
        "How does this work?",
    ]
    
    for question in test_questions:
        print(f"\\n💬 Question: {question}")
        
        # TODO: Route to agent and get response
        input_data = ChatInput(question=question, user_id="user_123")
        result = await registry.route("chat", input_data)
        
        print(f"🤖 Answer: {result.answer}")
        print(f"📊 Confidence: {result.confidence:.2f}")
    
    print("\\n✅ Level 1 Complete!\\n")


if __name__ == "__main__":
    asyncio.run(main())
'''
    (output_path / "main.py").write_text(main)
    
    # config.yaml
    config = '''# Level 1: Configuration

agent:
  name: "simple_chat_agent"
  type: "chat"
  
  # TODO: Add your configuration
  settings:
    default_confidence: 0.5
    
# TODO: Experiment with different settings
'''
    (output_path / "config.yaml").write_text(config)
    
    # test_agent.py
    test = '''"""
Level 1: Tests

Verify your agent works correctly.
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agent import SimpleChatAgent
from schemas import ChatInput


@pytest.mark.asyncio
async def test_agent_responds():
    """Test that agent returns a response"""
    agent = SimpleChatAgent()
    
    input_data = ChatInput(question="Hello", user_id="test_user")
    result = await agent.process(input_data)
    
    assert result.answer is not None
    assert len(result.answer) > 0
    assert 0 <= result.confidence <= 1


@pytest.mark.asyncio
async def test_greeting_response():
    """Test greeting responses"""
    agent = SimpleChatAgent()
    
    input_data = ChatInput(question="Hi there!", user_id="test_user")
    result = await agent.process(input_data)
    
    # TODO: Add assertions for your expected behavior
    assert result.confidence > 0.5


# TODO: Add more tests!
'''
    (output_path / "tests" / "test_agent.py").write_text(test)
    
    # __init__.py for tests
    (output_path / "tests" / "__init__.py").write_text("")


def create_level2_files(output_path: Path):
    """Create starter files for Level 2"""
    # Similar pattern with memory integration
    (output_path / "README.md").write_text("# Level 2: Context-Aware Assistant\n\nComing soon...")


def create_level3_files(output_path: Path):
    """Create starter files for Level 3"""
    (output_path / "README.md").write_text("# Level 3: Production API\n\nComing soon...")


def create_level4_files(output_path: Path):
    """Create starter files for Level 4"""
    (output_path / "README.md").write_text("# Level 4: Complex Workflow\n\nComing soon...")


def create_level5_files(output_path: Path):
    """Create starter files for Level 5"""
    (output_path / "README.md").write_text("# Level 5: Autonomous Multi-Agent\n\nComing soon...")


def main():
    """Main CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="SOTA Agent Framework - Interactive Learning Mode",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  sota-learn                    # Show overview
  sota-learn info 1             # Show Level 1 details
  sota-learn start 1            # Create Level 1 project
  sota-learn start 2 --output my-level2  # Custom output directory

Learn by building: From simple chatbot to autonomous multi-agent system!
        """
    )
    
    parser.add_argument(
        "command",
        nargs="?",
        choices=["info", "start", "overview"],
        default="overview",
        help="Command to run"
    )
    
    parser.add_argument(
        "level",
        nargs="?",
        choices=["1", "2", "3", "4", "5"],
        help="Level number (1-5)"
    )
    
    parser.add_argument(
        "--output", "-o",
        help="Output directory for project"
    )
    
    args = parser.parse_args()
    
    print_banner()
    
    if args.command == "overview" or (args.command is None and args.level is None):
        show_overview()
        print("💡 To get started:")
        print("   sota-learn info 1     # Learn about Level 1")
        print("   sota-learn start 1    # Create Level 1 project")
        print()
    
    elif args.command == "info":
        if not args.level:
            print("❌ Please specify a level: sota-learn info <level>")
            sys.exit(1)
        show_level_details(args.level)
        print(f"💡 To start building:")
        print(f"   sota-learn start {args.level}")
        print()
    
    elif args.command == "start":
        if not args.level:
            print("❌ Please specify a level: sota-learn start <level>")
            sys.exit(1)
        success = create_level_project(args.level, args.output)
        if not success:
            sys.exit(1)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

