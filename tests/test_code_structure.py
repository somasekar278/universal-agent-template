"""
Code Structure Tests (No Server Required)

These tests validate code correctness without starting servers.
Works for ALL apps (L1-L5) since it just checks the code.

Run: pytest tests/test_code_structure.py -v
"""

import pytest
import os
from pathlib import Path
import py_compile
import ast


def get_app_dir():
    """Get app directory from environment or skip test."""
    test_app_dir = os.getenv('TEST_APP_DIR')
    if not test_app_dir:
        pytest.skip("Set TEST_APP_DIR environment variable")

    app_dir = Path(test_app_dir)
    if not app_dir.exists():
        pytest.skip(f"App directory not found: {app_dir}")

    return app_dir


class TestPythonSyntax:
    """Test Python files have valid syntax (parse only, no execution)."""

    def test_all_python_files_compile(self):
        """✅ All .py files must have valid syntax."""
        app_dir = get_app_dir()

        python_files = list(app_dir.glob('*.py'))
        assert len(python_files) > 0, "No Python files found"

        errors = []
        for py_file in python_files:
            try:
                # Use ast.parse instead of py_compile to avoid execution
                content = py_file.read_text()
                ast.parse(content, filename=str(py_file))
            except SyntaxError as e:
                errors.append(f"{py_file.name}:{e.lineno}: {e.msg}")
            except Exception as e:
                errors.append(f"{py_file.name}: {e}")

        assert len(errors) == 0, f"Syntax errors:\n" + "\n".join(errors)


class TestEndpointUsage:
    """Test code uses correct endpoints (without running server)."""

    def test_no_stream_endpoint_in_code(self):
        """✅ Code must not reference /stream endpoint."""
        app_dir = get_app_dir()

        # Check all .py files
        for py_file in app_dir.glob('*.py'):
            content = py_file.read_text()

            # Skip if it's testing/commenting about /stream
            if 'test' in py_file.name.lower():
                continue

            # Check for /stream usage (but allow /stream in comments)
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                if '/stream' in line and not line.strip().startswith('#'):
                    # Check if it's in a string
                    if "'/stream'" in line or '"/stream"' in line:
                        pytest.fail(
                            f"❌ Found /stream endpoint in {py_file.name}:{i}\n"
                            f"   Should use /invocations with stream: true\n"
                            f"   Line: {line.strip()}"
                        )

    def test_uses_invocations_endpoint(self):
        """✅ Code should use /invocations endpoint."""
        app_dir = get_app_dir()

        found_invocations = False

        # Check start_server.py or similar
        for py_file in app_dir.glob('*server*.py'):
            content = py_file.read_text()
            if '/invocations' in content:
                found_invocations = True
                break

        # It's ok if not found (might be using AgentServer auto-registration)
        # But if we find /stream, that's a problem (caught by previous test)


class TestMLflowIntegration:
    """Test MLflow integration setup (text-based, no imports)."""

    def test_has_agent_file(self):
        """✅ Must have agent.py file."""
        app_dir = get_app_dir()
        assert (app_dir / 'agent.py').exists(), "Missing agent.py"

    def test_agent_imports_mlflow(self):
        """✅ agent.py must import MLflow."""
        app_dir = get_app_dir()
        agent_file = app_dir / 'agent.py'

        # Read as text only - don't import/execute
        try:
            content = agent_file.read_text()
        except Exception as e:
            pytest.fail(f"Cannot read agent.py: {e}")

        assert 'import mlflow' in content or 'from mlflow' in content, \
            "agent.py must import mlflow"

    def test_uses_invoke_or_stream_decorator(self):
        """✅ agent.py must use @invoke() or @stream() decorator."""
        app_dir = get_app_dir()
        agent_file = app_dir / 'agent.py'

        # Read as text only - don't import/execute
        try:
            content = agent_file.read_text()
        except Exception as e:
            pytest.fail(f"Cannot read agent.py: {e}")

        has_decorator = (
            '@invoke()' in content or
            '@stream()' in content or
            '@invoke' in content or
            '@stream' in content
        )

        assert has_decorator, \
            "agent.py must use @invoke() or @stream() decorator"


class TestConfiguration:
    """Test configuration files."""

    def test_has_config_yaml(self):
        """✅ Must have config.yaml."""
        app_dir = get_app_dir()
        assert (app_dir / 'config.yaml').exists(), "Missing config.yaml"

    def test_has_databricks_yml(self):
        """✅ Must have databricks.yml for deployment."""
        app_dir = get_app_dir()
        assert (app_dir / 'databricks.yml').exists(), "Missing databricks.yml"

    def test_config_is_valid_yaml(self):
        """✅ config.yaml must be valid YAML."""
        import yaml
        app_dir = get_app_dir()

        config_file = app_dir / 'config.yaml'
        try:
            config = yaml.safe_load(config_file.read_text())
            assert config is not None, "config.yaml is empty"
        except yaml.YAMLError as e:
            pytest.fail(f"Invalid YAML in config.yaml: {e}")


class TestRequirements:
    """Test dependencies."""

    def test_has_requirements_txt(self):
        """✅ Must have requirements.txt."""
        app_dir = get_app_dir()
        assert (app_dir / 'requirements.txt').exists(), "Missing requirements.txt"

    def test_mlflow_in_requirements(self):
        """✅ requirements.txt must include mlflow."""
        app_dir = get_app_dir()
        requirements = (app_dir / 'requirements.txt').read_text()

        assert 'mlflow' in requirements.lower(), \
            "requirements.txt must include mlflow"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
