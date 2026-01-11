"""
E2E Tests for L2 Assistant with Memory

Tests conversation memory, session management, and ResponsesAgent format.
Run: pytest tests/test_l2_memory.py -v
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import uuid


@pytest.fixture(scope="module")
def test_scaffold():
    """Generate a test L2 assistant scaffold in a temp directory."""
    temp_dir = tempfile.mkdtemp()
    scaffold_path = Path(temp_dir) / "test-l2-assistant"

    # Generate scaffold
    from databricks_agent_toolkit.scaffolds import ScaffoldGenerator
    generator = ScaffoldGenerator()
    generator.generate(
        level='assistant',
        name='test-l2-assistant',
        output_dir=str(scaffold_path),
        options={
            'model': 'databricks-meta-llama-3-1-70b-instruct',
            'enable_rag': False
        }
    )

    yield scaffold_path

    # Cleanup
    shutil.rmtree(temp_dir)


class TestScaffoldGeneration:
    """Test L2 assistant scaffold generation and structure."""

    def test_generates_all_files(self, test_scaffold):
        """Verify all required files are generated."""
        required_files = [
            'agent.py',
            'assistant.py',
            'memory_manager.py',
            'config.yaml',
            'requirements.txt',
            'README.md',
            'databricks.yml',
            'start_server.py'
        ]
        for filename in required_files:
            assert (test_scaffold / filename).exists(), f"Missing {filename}"

    def test_memory_manager_exists(self, test_scaffold):
        """Verify memory_manager.py is generated."""
        memory_file = test_scaffold / 'memory_manager.py'
        assert memory_file.exists()
        content = memory_file.read_text()
        assert 'class MemoryManager' in content
        assert 'Lakebase' in content
        assert 'store_message' in content
        assert 'get_conversation_history' in content

    def test_agent_has_memory_integration(self, test_scaffold):
        """Verify agent.py integrates memory."""
        agent_file = test_scaffold / 'agent.py'
        content = agent_file.read_text()
        assert 'from memory_manager import MemoryManager' in content
        assert 'memory = MemoryManager' in content
        assert 'memory.store_message' in content
        assert 'memory.initialize()' in content

    def test_config_has_memory_section(self, test_scaffold):
        """Verify config.yaml has memory configuration."""
        import yaml
        config_file = test_scaffold / 'config.yaml'
        config = yaml.safe_load(config_file.read_text())
        assert 'memory' in config
        assert 'max_history' in config['memory']
        assert config['memory']['max_history'] == 20

    def test_no_syntax_errors(self, test_scaffold):
        """Verify Python files have no syntax errors."""
        import py_compile

        for py_file in test_scaffold.glob('*.py'):
            try:
                py_compile.compile(str(py_file), doraise=True)
            except py_compile.PyCompileError as e:
                pytest.fail(f"Syntax error in {py_file.name}: {e}")


class TestMemoryManager:
    """Test MemoryManager functionality with mocked Lakebase."""

    @pytest.fixture
    def mock_lakebase(self):
        """Create a mock Lakebase instance."""
        mock = MagicMock()
        mock.conversations = []  # In-memory storage for testing

        def mock_store_message(session_id, role, content, metadata=None):
            mock.conversations.append({
                'session_id': session_id,
                'role': role,
                'content': content,
                'metadata': metadata,
                'timestamp': '2026-01-07T12:00:00'
            })

        def mock_get_conversation_history(session_id, limit=None):
            messages = [
                msg for msg in mock.conversations
                if msg['session_id'] == session_id
            ]
            if limit:
                messages = messages[-limit:]
            return messages

        def mock_clear_conversation(session_id):
            mock.conversations = [
                msg for msg in mock.conversations
                if msg['session_id'] != session_id
            ]

        mock.store_message = mock_store_message
        mock.get_conversation_history = mock_get_conversation_history
        mock.clear_conversation = mock_clear_conversation
        mock.create_conversations_table = Mock()
        mock.close = Mock()

        return mock

    @pytest.fixture
    def memory_manager(self, mock_lakebase, test_scaffold):
        """Create MemoryManager with mocked Lakebase."""
        import sys
        sys.path.insert(0, str(test_scaffold))

        with patch('databricks_agent_toolkit.integrations.Lakebase', return_value=mock_lakebase):
            from memory_manager import MemoryManager
            manager = MemoryManager(
                host='mock-host',
                database='mock-db',
                user='mock-user',
                password='mock-pass',
                max_history=20
            )
            manager.initialize()
            yield manager
            manager.close()

    def test_store_and_retrieve_message(self, memory_manager):
        """Test storing and retrieving a single message."""
        session_id = str(uuid.uuid4())

        # Store message
        memory_manager.store_message(session_id, "user", "Hello!")

        # Retrieve
        history = memory_manager.get_conversation_history(session_id)
        assert len(history) == 1
        assert history[0]['role'] == 'user'
        assert history[0]['content'] == 'Hello!'

    def test_conversation_flow(self, memory_manager):
        """Test a multi-turn conversation."""
        session_id = str(uuid.uuid4())

        # User message
        memory_manager.store_message(session_id, "user", "What is Python?")

        # Assistant response
        memory_manager.store_message(session_id, "assistant", "Python is a programming language.")

        # Another user message
        memory_manager.store_message(session_id, "user", "Tell me more")

        # Retrieve history
        history = memory_manager.get_conversation_history(session_id)
        assert len(history) == 3
        assert history[0]['role'] == 'user'
        assert history[1]['role'] == 'assistant'
        assert history[2]['role'] == 'user'

    def test_session_isolation(self, memory_manager):
        """Test that different sessions are isolated."""
        session1 = str(uuid.uuid4())
        session2 = str(uuid.uuid4())

        # Store in session 1
        memory_manager.store_message(session1, "user", "Session 1 message")

        # Store in session 2
        memory_manager.store_message(session2, "user", "Session 2 message")

        # Verify isolation
        history1 = memory_manager.get_conversation_history(session1)
        history2 = memory_manager.get_conversation_history(session2)

        assert len(history1) == 1
        assert len(history2) == 1
        assert history1[0]['content'] == "Session 1 message"
        assert history2[0]['content'] == "Session 2 message"

    def test_max_history_limit(self, memory_manager):
        """Test that max_history limit is respected."""
        session_id = str(uuid.uuid4())

        # Store 25 messages (max_history is 20)
        for i in range(25):
            role = "user" if i % 2 == 0 else "assistant"
            memory_manager.store_message(session_id, role, f"Message {i}")

        # Retrieve with limit
        history = memory_manager.get_conversation_history(session_id, limit=20)
        assert len(history) <= 20

    def test_clear_conversation(self, memory_manager):
        """Test clearing conversation history."""
        session_id = str(uuid.uuid4())

        # Store messages
        memory_manager.store_message(session_id, "user", "Hello")
        memory_manager.store_message(session_id, "assistant", "Hi!")

        # Verify stored
        history = memory_manager.get_conversation_history(session_id)
        assert len(history) == 2

        # Clear
        memory_manager.clear_conversation(session_id)

        # Verify cleared
        history = memory_manager.get_conversation_history(session_id)
        assert len(history) == 0

    def test_get_messages_for_llm(self, memory_manager):
        """Test formatting messages for LLM API."""
        session_id = str(uuid.uuid4())

        memory_manager.store_message(session_id, "user", "Hello")
        memory_manager.store_message(session_id, "assistant", "Hi there!")

        # Get formatted messages
        messages = memory_manager.get_messages_for_llm(session_id)

        assert len(messages) == 2
        assert messages[0] == {"role": "user", "content": "Hello"}
        assert messages[1] == {"role": "assistant", "content": "Hi there!"}


class TestAgentWithMemory:
    """Test agent.py with memory integration."""

    def test_agent_imports_memory_manager(self, test_scaffold):
        """Verify agent imports MemoryManager."""
        agent_file = test_scaffold / 'agent.py'
        content = agent_file.read_text()
        assert 'from memory_manager import MemoryManager' in content

    def test_agent_initializes_memory(self, test_scaffold):
        """Verify agent initializes memory on startup."""
        agent_file = test_scaffold / 'agent.py'
        content = agent_file.read_text()
        assert 'memory = MemoryManager(' in content
        assert 'memory.initialize()' in content

    def test_invoke_handler_stores_messages(self, test_scaffold):
        """Verify invoke handler stores messages in memory."""
        agent_file = test_scaffold / 'agent.py'
        content = agent_file.read_text()

        # Check that invoke_handler stores user message
        assert 'memory.store_message(session_id, "user"' in content

        # Check that it stores assistant response
        assert 'memory.store_message(session_id, "assistant"' in content

    def test_agent_uses_conversation_history(self, test_scaffold):
        """Verify agent retrieves conversation history."""
        agent_file = test_scaffold / 'agent.py'
        content = agent_file.read_text()
        assert '_build_messages_with_history' in content or 'get_messages_for_llm' in content

    def test_responses_agent_format(self, test_scaffold):
        """Verify agent returns ResponsesAgent format."""
        agent_file = test_scaffold / 'agent.py'
        content = agent_file.read_text()

        # Check imports
        assert 'from mlflow.types.responses import ResponsesAgentRequest, ResponsesAgentResponse' in content

        # Check return type
        assert 'ResponsesAgentResponse' in content
        assert '"type": "message"' in content
        assert '"type": "output_text"' in content


class TestLakebaseIntegration:
    """Test Lakebase integration class."""

    def test_lakebase_import(self):
        """Test that Lakebase can be imported."""
        try:
            from databricks_agent_toolkit.integrations import Lakebase
            assert Lakebase is not None
        except ImportError as e:
            pytest.skip(f"Lakebase not available: {e}")

    def test_lakebase_has_required_methods(self):
        """Test that Lakebase has all required methods."""
        try:
            from databricks_agent_toolkit.integrations import Lakebase

            required_methods = [
                'create_conversations_table',
                'store_message',
                'get_conversation_history',
                'clear_conversation',
                'execute',
                'query',
                'close'
            ]

            for method in required_methods:
                assert hasattr(Lakebase, method), f"Missing method: {method}"
        except ImportError:
            pytest.skip("Lakebase not available")


class TestCodeQuality:
    """Test code quality and best practices."""

    def test_no_duplicate_imports(self, test_scaffold):
        """Check for duplicate imports in generated files."""
        for py_file in test_scaffold.glob('*.py'):
            content = py_file.read_text()
            imports = [line for line in content.splitlines() if line.startswith(('import ', 'from '))]
            unique_imports = set(imports)
            assert len(imports) == len(unique_imports), f"Duplicate imports in {py_file.name}"

    def test_memory_manager_has_error_handling(self, test_scaffold):
        """Verify memory_manager has proper error handling."""
        memory_file = test_scaffold / 'memory_manager.py'
        content = memory_file.read_text()

        # Should have try-except blocks
        assert 'try:' in content
        assert 'except' in content

        # Should handle connection errors gracefully
        assert 'Could not' in content or 'Error' in content

    def test_agent_has_session_id_extraction(self, test_scaffold):
        """Verify agent extracts session_id from requests."""
        agent_file = test_scaffold / 'agent.py'
        content = agent_file.read_text()
        assert 'session_id' in content
        assert 'uuid.uuid4()' in content  # Should generate if missing


class TestDocumentation:
    """Test that documentation is complete."""

    def test_readme_mentions_memory(self, test_scaffold):
        """Verify README documents memory features."""
        readme = test_scaffold / 'README.md'
        content = readme.read_text()

        assert 'memory' in content.lower() or 'lakebase' in content.lower()
        assert 'conversation' in content.lower()

    def test_readme_has_lakebase_setup(self, test_scaffold):
        """Verify README has Lakebase setup instructions."""
        readme = test_scaffold / 'README.md'
        content = readme.read_text()

        assert 'LAKEBASE_HOST' in content or 'lakebase' in content.lower()
        assert 'environment' in content.lower() or 'env' in content.lower()

    def test_config_has_comments(self, test_scaffold):
        """Verify config.yaml has helpful comments."""
        config = test_scaffold / 'config.yaml'
        content = config.read_text()

        # Should have comments explaining memory config
        assert '#' in content
        assert 'memory' in content.lower()


def pytest_addoption(parser):
    """Add custom pytest options."""
    parser.addoption("--lakebase-host", action="store", default=None)
    parser.addoption("--lakebase-database", action="store", default=None)
    parser.addoption("--lakebase-user", action="store", default=None)
    parser.addoption("--lakebase-password", action="store", default=None)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
