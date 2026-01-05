"""
E2E Tests for Chatbot Scaffold

Run: pytest tests/test_e2e_chatbot.py -v
"""

import pytest
import subprocess
import time
import requests
import tempfile
import shutil
from pathlib import Path


@pytest.fixture(scope="module")
def test_scaffold():
    """Generate a test scaffold in a temp directory."""
    temp_dir = tempfile.mkdtemp()
    scaffold_path = Path(temp_dir) / "test-chatbot"

    # Generate scaffold
    from databricks_agent_toolkit.scaffolds import ScaffoldGenerator
    generator = ScaffoldGenerator()
    generator.generate(
        level='chatbot',
        name='test-chatbot',
        output_dir=str(scaffold_path),
        options={'model': 'databricks-gpt-5-2'}
    )

    yield scaffold_path

    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture(scope="module")
def running_app(test_scaffold):
    """Start the Flask app for testing."""
    import os
    env = os.environ.copy()
    env.update({
        'DATABRICKS_HOST': os.getenv('DATABRICKS_HOST', 'https://demo.cloud.databricks.com'),
        'DATABRICKS_CLIENT_ID': os.getenv('DATABRICKS_CLIENT_ID', 'test-client'),
        'DATABRICKS_CLIENT_SECRET': os.getenv('DATABRICKS_CLIENT_SECRET', 'test-secret'),
        'DATABRICKS_APP_PORT': '8099'
    })

    # Start app
    process = subprocess.Popen(
        ['python3', 'app.py'],
        cwd=test_scaffold,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # Wait for app to start
    time.sleep(3)

    yield 'http://localhost:8099'

    # Cleanup
    process.terminate()
    process.wait()


class TestScaffoldGeneration:
    """Test scaffold generation and structure."""

    def test_generates_all_files(self, test_scaffold):
        """Verify all required files are generated."""
        required_files = [
            'app.py',
            'chatbot.py',
            'config.yaml',
            'requirements.txt',
            'README.md',
            'databricks.yml',
            'app.yaml'
        ]
        for filename in required_files:
            assert (test_scaffold / filename).exists(), f"Missing {filename}"

    def test_code_is_lean(self, test_scaffold):
        """Verify generated code is optimized (< 300 lines total)."""
        chatbot_lines = len((test_scaffold / 'chatbot.py').read_text().splitlines())
        app_lines = len((test_scaffold / 'app.py').read_text().splitlines())
        total_lines = chatbot_lines + app_lines

        assert chatbot_lines < 100, f"chatbot.py too long: {chatbot_lines} lines"
        assert app_lines < 250, f"app.py too long: {app_lines} lines"
        assert total_lines < 350, f"Total code too long: {total_lines} lines"

    def test_no_syntax_errors(self, test_scaffold):
        """Verify Python files have no syntax errors."""
        import py_compile

        for py_file in test_scaffold.glob('*.py'):
            try:
                py_compile.compile(str(py_file), doraise=True)
            except py_compile.PyCompileError as e:
                pytest.fail(f"Syntax error in {py_file.name}: {e}")


class TestAppEndpoints:
    """Test Flask app endpoints."""

    def test_health_endpoint(self, running_app):
        """Test /health endpoint."""
        response = requests.get(f"{running_app}/health")
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
        assert 'model' in data
        assert 'port' in data

    def test_home_page_loads(self, running_app):
        """Test home page returns HTML."""
        response = requests.get(running_app)
        assert response.status_code == 200
        assert 'text/html' in response.headers['Content-Type']
        assert 'bubble' in response.text  # Check for bubble CSS

    def test_chat_bubbles_present(self, running_app):
        """Test chat bubble styling is present."""
        response = requests.get(running_app)
        html = response.text

        # Check for bubble classes
        assert '.bubble' in html
        assert '.user' in html
        assert '.assistant' in html
        assert 'border-radius: 18px' in html
        assert '#007AFF' in html  # User bubble color


class TestChatFunctionality:
    """Test chat functionality (requires real credentials)."""

    @pytest.mark.skipif(
        not all([
            pytest.config.getoption('--databricks-host', default=None),
            pytest.config.getoption('--databricks-client-id', default=None)
        ]),
        reason="Databricks credentials not provided"
    )
    def test_non_streaming_chat(self, running_app):
        """Test non-streaming chat endpoint."""
        response = requests.post(
            f"{running_app}/api/chat",
            json={'message': 'Say hello'},
            headers={'Content-Type': 'application/json'}
        )

        assert response.status_code == 200
        data = response.json()
        assert 'response' in data
        assert len(data['response']) > 0


class TestCodeQuality:
    """Test code quality and optimization."""

    def test_no_duplicate_imports(self, test_scaffold):
        """Check for duplicate imports."""
        for py_file in test_scaffold.glob('*.py'):
            content = py_file.read_text()
            imports = [line for line in content.splitlines() if line.startswith(('import ', 'from '))]
            unique_imports = set(imports)
            assert len(imports) == len(unique_imports), f"Duplicate imports in {py_file.name}"

    def test_no_excessive_comments(self, test_scaffold):
        """Ensure code isn't bloated with comments."""
        for py_file in test_scaffold.glob('*.py'):
            lines = py_file.read_text().splitlines()
            comment_lines = [l for l in lines if l.strip().startswith('#')]
            code_lines = [l for l in lines if l.strip() and not l.strip().startswith('#')]

            if code_lines:
                comment_ratio = len(comment_lines) / len(code_lines)
                assert comment_ratio < 0.3, f"Too many comments in {py_file.name}: {comment_ratio:.0%}"


def pytest_addoption(parser):
    """Add custom pytest options."""
    parser.addoption("--databricks-host", action="store", default=None)
    parser.addoption("--databricks-client-id", action="store", default=None)
    parser.addoption("--databricks-client-secret", action="store", default=None)
