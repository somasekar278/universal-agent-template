"""
Scaffold Generator

Generates L1-L5 agent scaffolds from Jinja2 templates.
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional

from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger(__name__)


class ScaffoldGenerator:
    """
    Generate agent scaffolds from templates.

    Example:
        generator = ScaffoldGenerator()
        generator.generate(
            level="l3",
            name="customer-support",
            output_dir="./customer-support",
            options={
                "model": "databricks-claude-sonnet-4-5",
                "enable_mcp": True
            }
        )
    """

    def __init__(self):
        """Initialize scaffold generator."""
        self.templates_dir = Path(__file__).parent / "templates"

        # Initialize Jinja2 environment
        # We're generating code templates, not rendering user input - XSS not applicable
        self.jinja_env = Environment(  # nosec B701
            loader=FileSystemLoader(str(self.templates_dir)), trim_blocks=True, lstrip_blocks=True
        )

        logger.info(f"✅ Scaffold generator initialized: {self.templates_dir}")

    def generate(self, level: str, name: str, output_dir: str, options: Optional[Dict[str, Any]] = None):
        """
        Generate agent scaffold.

        Args:
            level: Agent type (chatbot, assistant, api, workflow, system)
            name: Agent name
            output_dir: Output directory path
            options: Generation options (model, enable_mcp, ui, etc.)

        Example:
            generator.generate(
                level="workflow",
                name="research-agent",
                output_dir="./research-agent",
                options={
                    "model": "databricks-claude-sonnet-4-5",
                    "workflow": "plan-act-critique",
                    "enable_optimization": True,
                    "ui": "streamlit"
                }
            )
        """
        options = options or {}

        # Check if using official Databricks UI templates
        ui = options.get("ui", "fastapi")
        if ui in ["streamlit", "gradio", "dash"]:
            logger.info(f"🚀 Using official Databricks {ui.capitalize()} template")
            from .databricks_template_integrator import generate_with_databricks_template

            return generate_with_databricks_template(name, level, options, output_dir)

        # Validate level
        valid_levels = ["chatbot", "assistant"]
        if level not in valid_levels:
            raise ValueError(
                f"Invalid level: {level}. Currently available: {', '.join(valid_levels)}. "
                "More scaffolds (api, workflow, system) coming in future releases."
            )

        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        logger.info(f"🚀 Generating {level} scaffold: {name}")
        logger.info(f"   Output: {output_path.absolute()}")

        # Prepare template context
        context = {
            "name": name,
            "level": level,
            "model": options.get("model", "databricks-claude-sonnet-4-5"),  # Modern default
            "enable_mcp": options.get("enable_mcp", False),
            "enable_optimization": options.get("enable_optimization", False),
            "enable_memory": options.get("enable_memory", True if level != "l1" else False),
            "workflow": options.get("workflow", "plan-act-critique"),
            "agents": options.get("agents", ["agent_a", "agent_b"]),
            "enable_a2a": options.get("enable_a2a", False),
            # RAG options (L2+)
            "enable_rag": options.get("enable_rag", False),
            "rag_backend": options.get("rag_backend", "pgvector"),
            "rag_source": options.get("rag_source", None),
            "index_type": options.get("index_type", "ivfflat"),
            "vector_search_endpoint": options.get("vector_search_endpoint", "one-env-shared-endpoint-0"),
            "vector_search_index": options.get("vector_search_index", None),
        }

        # Generate files based on level
        template_mapping = self._get_template_mapping(level)

        for output_file, template_file in template_mapping.items():
            self._render_template(template_file=template_file, output_file=output_path / output_file, context=context)

        logger.info(f"✅ Generated {level} scaffold: {name}")

        # Validate generated scaffold
        try:
            from databricks_agent_toolkit.scaffolds.validator import validate_scaffold

            logger.info("\n🔍 Validating generated scaffold...")
            is_valid = validate_scaffold(str(output_path), level, cli_options=options)
            if not is_valid:
                logger.warning("   ⚠️  Validation found issues. Please review above.")
        except Exception as e:
            logger.warning(f"   ⚠️  Validation skipped: {e}")

        logger.info("\n📁 Next steps:")
        logger.info(f"   cd {output_dir}")
        logger.info("   pip install -r requirements.txt")
        if level == "chatbot":
            logger.info("   python chatbot.py  # CLI")
            logger.info("   # Or: python start_server.py  # Web app")
        elif level == "assistant":
            logger.info("   python assistant.py  # CLI")
            logger.info("   # Or: python start_server.py  # Web app")
        else:
            logger.info("   # See README.md for instructions")

    def _get_template_mapping(self, level: str) -> Dict[str, str]:
        """
        Get template file mapping for a level.

        Returns dict of {output_filename: template_filename}
        """
        mappings = {
            "chatbot": {
                "agent.py": f"{level}/agent.py.jinja2",  # Agent logic (v0.2.0)
                "start_server.py": f"{level}/start_server.py.jinja2",  # FastAPI server (v0.2.0)
                "chatbot.py": f"{level}/chatbot.py.jinja2",  # CLI version
                "config.yaml": f"{level}/config.yaml.jinja2",
                "requirements.txt": f"{level}/requirements.txt.jinja2",
                "databricks.yml": f"{level}/databricks.yml.jinja2",  # Asset Bundle (recommended)
                "app.yaml": f"{level}/app.yaml.jinja2",  # App config for bundle
                "databricks-app.yml": f"{level}/databricks-app.yml.jinja2",  # Legacy
                "README.md": f"{level}/README.md.jinja2",
            },
            "assistant": {
                "agent.py": f"{level}/agent.py.jinja2",  # Agent logic (v0.2.0)
                "start_server.py": f"{level}/start_server.py.jinja2",  # FastAPI server (v0.2.0)
                "assistant.py": f"{level}/assistant.py.jinja2",  # CLI version
                "memory_manager.py": f"{level}/memory_manager.py.jinja2",
                "rag_manager.py": f"{level}/rag_manager.py.jinja2",
                "config.yaml": f"{level}/config.yaml.jinja2",
                "requirements.txt": f"{level}/requirements.txt.jinja2",
                "databricks.yml": f"{level}/databricks.yml.jinja2",  # Asset Bundle (recommended)
                "app.yaml": f"{level}/app.yaml.jinja2",  # App config for bundle
                "databricks-app.yml": f"{level}/databricks-app.yml.jinja2",  # Legacy
                "README.md": f"{level}/README.md.jinja2",
            },
            # More scaffold types coming in future releases:
            # - api (L3): FastAPI production endpoint
            # - workflow (L4): LangGraph workflows
            # - system (L5): Multi-agent with A2A
        }

        return mappings.get(level, {})

    def _render_template(self, template_file: str, output_file: Path, context: Dict[str, Any]):
        """
        Render a Jinja2 template to output file.

        Args:
            template_file: Template file path (relative to templates_dir)
            output_file: Output file path
            context: Template context variables
        """
        try:
            # Load and render template
            template = self.jinja_env.get_template(template_file)
            rendered = template.render(**context)

            # Write to output file
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(rendered)

            logger.debug(f"   ✅ Generated: {output_file.name}")

        except Exception as e:
            logger.error(f"   ❌ Failed to render {template_file}: {e}")
            raise

    def list_levels(self) -> Dict[str, Dict[str, Any]]:
        """
        List available scaffold types with descriptions.

        Returns:
            Dict of scaffold info
        """
        return {
            "chatbot": {
                "name": "Simple Chatbot",
                "complexity": "Beginner",
                "time": "2-4 hours",
                "description": "Stateless chatbot using Databricks Model Serving",
                "features": ["LLM integration", "Basic MLflow tracing"],
            },
            "assistant": {
                "name": "Context-Aware Assistant",
                "complexity": "Intermediate",
                "time": "4-8 hours",
                "description": "Assistant with conversation memory using Lakebase",
                "features": ["Session management", "Memory (Lakebase)", "MLflow logging"],
            },
            "api": {
                "name": "Production API",
                "complexity": "Intermediate+",
                "time": "8-16 hours",
                "description": "Production-ready FastAPI application",
                "features": ["FastAPI", "Error handling", "Health checks", "Optional MCP"],
            },
            "workflow": {
                "name": "Complex Workflow",
                "complexity": "Advanced",
                "time": "16-32 hours",
                "description": "LangGraph workflow with optimization",
                "features": ["LangGraph", "Plan-Act-Critique", "Auto-optimization", "MCP tools"],
            },
            "system": {
                "name": "Multi-Agent System",
                "complexity": "Expert",
                "time": "32-64 hours",
                "description": "Multi-agent coordination with A2A",
                "features": ["LangGraph", "Multi-agent", "A2A protocol", "Per-agent MCP", "Cross-agent optimization"],
            },
        }
