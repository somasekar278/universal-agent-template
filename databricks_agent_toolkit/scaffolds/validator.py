"""
Scaffold Validator

Validates generated scaffolds to ensure all required features are present.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class ScaffoldValidator:
    """
    Validates generated scaffolds for completeness and correctness.

    Checks:
    - Required files exist
    - Key features are implemented (MLflow tracing, memory, RAG, etc.)
    - Configuration is valid
    - Dependencies are correct
    """

    def __init__(self, scaffold_path: str, scaffold_type: str):
        """
        Initialize validator.

        Args:
            scaffold_path: Path to generated scaffold
            scaffold_type: Type of scaffold (chatbot, assistant, api, workflow, system)
        """
        self.path = Path(scaffold_path)
        self.type = scaffold_type
        self.errors = []
        self.warnings = []

    def validate(self, cli_options: Optional[Dict[str, Any]] = None) -> Tuple[bool, List[str], List[str]]:
        """
        Run all validation checks.

        Args:
            cli_options: Optional CLI options used to generate the scaffold (for validation)

        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        self.errors = []
        self.warnings = []
        self.cli_options = cli_options or {}

        # Required file checks
        self._check_required_files()

        # Feature checks based on scaffold type
        if self.type == "chatbot":
            self._validate_chatbot()
        elif self.type == "assistant":
            self._validate_assistant()

        # Common checks
        self._validate_config()
        self._validate_dependencies()
        self._validate_mlflow_integration()

        # CLI-to-config validation (if CLI options provided)
        if self.cli_options:
            self._validate_cli_to_config_mapping()

        is_valid = len(self.errors) == 0
        return is_valid, self.errors, self.warnings

    def _check_required_files(self):
        """Check that required files exist"""
        required_files = ["config.yaml", "requirements.txt", "README.md", "databricks-app.yml"]

        for file in required_files:
            if not (self.path / file).exists():
                self.errors.append(f"Missing required file: {file}")

    def _validate_chatbot(self):
        """Validate chatbot-specific features"""
        # Check for chatbot.py or app.py
        has_cli = (self.path / "chatbot.py").exists()
        has_app = (self.path / "app.py").exists()

        if not (has_cli or has_app):
            self.errors.append("Missing chatbot.py or app.py")

        # Check for MLflow tracing in implementation
        if has_app:
            self._check_file_contains(
                "app.py", ["mlflow.set_experiment", "auto_trace"], "MLflow tracing may not be configured in app.py"
            )

    def _validate_assistant(self):
        """Validate assistant-specific features"""
        # Check for required files
        required = ["assistant.py", "app.py", "memory_manager.py"]
        for file in required:
            if not (self.path / file).exists():
                self.errors.append(f"Missing required file for assistant: {file}")

        # Check memory integration
        if (self.path / "app.py").exists():
            self._check_file_contains(
                "app.py",
                ["MemoryManager", "memory.store_message", "memory.get_messages"],
                "Memory integration may not be implemented in app.py",
            )

        # Check MLflow tracing (more thorough)
        self._check_file_contains(
            "app.py", ["mlflow.set_experiment", "auto_trace"], "MLflow tracing may not be configured"
        )

        # Check if DatabricksLLM actually uses tracing properly
        # MLflow 3.x requires either mlflow.trace() decorator or proper span context
        if (self.path / "app.py").exists():
            app_content = (self.path / "app.py").read_text()

            # Check if using async and proper MLflow context
            if "async def chat" in app_content or "async def" in app_content:
                # For async endpoints, MLflow tracing needs special handling
                if "mlflow.trace" not in app_content and "@mlflow.trace" not in app_content:
                    self.warnings.append(
                        "Async endpoint detected but no @mlflow.trace decorator found. "
                        "MLflow tracing may not work correctly in async Flask routes. "
                        "Consider adding @mlflow.trace() decorator or ensuring DatabricksLLM "
                        "logs traces independently."
                    )

        # Check RAG support
        if (self.path / "rag_manager.py").exists():
            self._check_file_contains(
                "app.py", ["RAGManager", "rag.retrieve"], "RAG integration may not be implemented"
            )

            # Validate RAG manager has UC Volume support
            self._check_file_contains(
                "rag_manager.py",
                ["_list_uc_volume_files", "_read_file_content", "/Volumes/"],
                "RAG manager may not support UC Volumes",
            )

            # Check for OAuth M2M auth in RAG
            self._check_file_contains(
                "rag_manager.py",
                ["_get_auth_token", "DATABRICKS_CLIENT_ID"],
                "RAG manager may not support OAuth M2M authentication",
            )

        # Check for assessments/feedback (important for MLflow 3)
        config_path = self.path / "config.yaml"
        if config_path.exists():
            config_content = config_path.read_text()
            if "assessments:" not in config_content:
                self.warnings.append(
                    "No assessments configuration found. MLflow Assessments allow users "
                    "to provide feedback on traces via the MLflow UI, which is crucial "
                    "for continuous improvement."
                )

    def _validate_config(self):
        """Validate configuration file"""
        config_path = self.path / "config.yaml"

        if not config_path.exists():
            return

        content = config_path.read_text()

        # Check for required config sections
        required_sections = ["type", "name", "model", "mlflow"]
        for section in required_sections:
            if f"{section}:" not in content:
                self.errors.append(f"Missing required config section: {section}")

        # Type-specific config validation
        if self.type == "assistant":
            if "memory:" not in content:
                self.errors.append("Missing memory configuration for assistant")

            # Check if RAG config exists (optional but should be there)
            if "rag:" not in content:
                self.warnings.append("No RAG configuration found (optional feature)")

    def _validate_dependencies(self):
        """Validate requirements.txt"""
        req_path = self.path / "requirements.txt"

        if not req_path.exists():
            return

        content = req_path.read_text()

        # Check for core dependency
        if "databricks-agent-toolkit" not in content:
            self.errors.append("Missing databricks-agent-toolkit in requirements.txt")

        # Type-specific dependencies
        if self.type == "assistant":
            if "psycopg2-binary" not in content:
                self.warnings.append("Missing psycopg2-binary for Lakebase support")

    def _validate_mlflow_integration(self):
        """Validate MLflow integration"""
        # Check for MLflow in requirements
        req_path = self.path / "requirements.txt"
        if req_path.exists():
            content = req_path.read_text()
            if "mlflow" not in content:
                self.warnings.append("MLflow not in requirements.txt")

        # Check for MLflow experiment configuration
        config_path = self.path / "config.yaml"
        if config_path.exists():
            content = config_path.read_text()
            if "experiment:" not in content:
                self.warnings.append("No MLflow experiment configured")

    def _check_file_contains(self, filename: str, patterns: List[str], error_msg: str):
        """
        Check if file contains all patterns.

        Args:
            filename: File to check
            patterns: List of strings that should be in the file
            error_msg: Error message if patterns not found
        """
        file_path = self.path / filename

        if not file_path.exists():
            return

        content = file_path.read_text()

        missing = [p for p in patterns if p not in content]
        if missing:
            self.warnings.append(f"{error_msg} (missing: {', '.join(missing)})")

    def _validate_cli_to_config_mapping(self):
        """
        Validate that CLI options are properly reflected in generated config.

        This catches issues where:
        - CLI options aren't passed to templates
        - Templates don't use Jinja2 variables correctly
        - Generated config doesn't match CLI intent
        """
        config_path = self.path / "config.yaml"

        if not config_path.exists():
            return

        import yaml

        try:
            with open(config_path) as f:
                config = yaml.safe_load(f)
        except Exception as e:
            self.warnings.append(f"Could not parse config.yaml for CLI validation: {e}")
            return

        # Validate RAG options (L2+)
        if self.type == "assistant":
            # Check enable_rag
            if self.cli_options.get("enable_rag"):
                rag_enabled = config.get("rag", {}).get("enabled", False)
                if not rag_enabled:
                    self.errors.append(
                        "CLI: --enable-rag specified, but config.yaml has rag.enabled: false. "
                        "Template may not be using {{enable_rag}} variable correctly."
                    )

            # Check rag_source
            if self.cli_options.get("rag_source"):
                config_source = config.get("rag", {}).get("source")
                cli_source = self.cli_options.get("rag_source")
                if config_source != cli_source and config_source == "null":
                    self.errors.append(
                        f"CLI: --rag-source={cli_source}, but config.yaml has source: null. "
                        "Template may not be using {{rag_source}} variable correctly."
                    )

            # Check rag_backend
            if self.cli_options.get("rag_backend"):
                config_backend = config.get("rag", {}).get("backend", "pgvector")
                cli_backend = self.cli_options.get("rag_backend")
                if config_backend != cli_backend:
                    self.errors.append(
                        f"CLI: --rag-backend={cli_backend}, but config.yaml has backend: {config_backend}. "
                        "Template may not be using {{rag_backend}} variable correctly."
                    )

            # Check index_type
            if self.cli_options.get("index_type"):
                config_index = config.get("rag", {}).get("index_type", "ivfflat")
                cli_index = self.cli_options.get("index_type")
                if config_index != cli_index:
                    self.warnings.append(
                        f"CLI: --index-type={cli_index}, but config.yaml has index_type: {config_index}. "
                        "Verify template is using {{index_type}} variable correctly."
                    )

            # Check vector_search_index
            if self.cli_options.get("vector_search_index"):
                config_vs_index = config.get("rag", {}).get("index_name")
                cli_vs_index = self.cli_options.get("vector_search_index")
                if config_vs_index != cli_vs_index and config_vs_index == "null":
                    self.errors.append(
                        f"CLI: --vector-search-index={cli_vs_index}, but config.yaml has index_name: null. "
                        "Template may not be using {{vector_search_index}} variable correctly."
                    )

        # Validate model option (all levels)
        if self.cli_options.get("model"):
            config_model = config.get("model", {}).get("endpoint")
            cli_model = self.cli_options.get("model")
            if config_model != cli_model:
                self.warnings.append(
                    f"CLI: --model={cli_model}, but config.yaml has endpoint: {config_model}. "
                    "Verify template is using {{model}} variable correctly."
                )

    def print_report(self):
        """Print validation report"""
        print(f"\n{'='*60}")
        print(f"Scaffold Validation Report: {self.type} at {self.path}")
        print(f"{'='*60}")

        if not self.errors and not self.warnings:
            print("✅ All checks passed!")
        else:
            if self.errors:
                print(f"\n❌ Errors ({len(self.errors)}):")
                for error in self.errors:
                    print(f"   - {error}")

            if self.warnings:
                print(f"\n⚠️  Warnings ({len(self.warnings)}):")
                for warning in self.warnings:
                    print(f"   - {warning}")

        print(f"{'='*60}\n")


def validate_scaffold(scaffold_path: str, scaffold_type: str, cli_options: Optional[Dict[str, Any]] = None) -> bool:
    """
    Validate a generated scaffold.

    Args:
        scaffold_path: Path to scaffold directory
        scaffold_type: Type of scaffold (chatbot, assistant, etc.)
        cli_options: Optional CLI options used to generate the scaffold

    Returns:
        True if valid, False otherwise
    """
    validator = ScaffoldValidator(scaffold_path, scaffold_type)
    is_valid, errors, warnings = validator.validate(cli_options=cli_options)
    validator.print_report()
    return is_valid
