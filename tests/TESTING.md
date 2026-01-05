# Testing & Code Optimization Guide

This document outlines our testing and code quality standards.

## 🎯 Our Standards

### Code Optimization Targets
- **chatbot.py template**: < 100 lines
- **app.py template**: < 250 lines
- **Total template code**: < 350 lines combined
- **Comment ratio**: < 30% of code lines
- **No duplicate imports or dead code**

### Testing Requirements
- ✅ **Unit tests** for all core functionality
- ✅ **E2E tests** for scaffold generation
- ✅ **Integration tests** for Databricks services (when credentials available)
- ✅ **Template size checks** (automated)
- ✅ **Code quality checks** (linting, formatting)

## 🚀 Quick Start

### 1. Install Test Dependencies
```bash
pip install -e ".[dev]"
pip install pytest pre-commit black flake8 isort
```

### 2. Setup Pre-commit Hooks
```bash
pre-commit install
```

Now checks run automatically before each commit!

### 3. Run Tests Locally
```bash
# Quick tests (no credentials needed)
./scripts/run_tests.sh

# Full E2E tests (requires Databricks credentials)
export DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
export DATABRICKS_CLIENT_ID=your-client-id
export DATABRICKS_CLIENT_SECRET=your-secret
./scripts/run_tests.sh --full
```

## 📋 Test Types

### Unit Tests
Test individual components in isolation.

```bash
pytest tests/ -v -m "not integration"
```

### Integration Tests
Test with real Databricks services (requires credentials).

```bash
pytest tests/test_e2e_chatbot.py -v \
  --databricks-host="$DATABRICKS_HOST" \
  --databricks-client-id="$DATABRICKS_CLIENT_ID" \
  --databricks-client-secret="$DATABRICKS_CLIENT_SECRET"
```

### Template Size Checks
Ensure templates stay lean.

```bash
python3 scripts/check_template_size.py
```

## 🔍 Code Quality Checks

### Format Code
```bash
black databricks_agent_toolkit/ --line-length=120
isort databricks_agent_toolkit/ --profile black
```

### Lint Code
```bash
flake8 databricks_agent_toolkit/ --max-line-length=120
```

### Run All Checks
```bash
pre-commit run --all-files
```

## 📊 CI/CD Pipeline

Our GitHub Actions workflow automatically:
1. ✅ Checks code formatting
2. ✅ Runs linting
3. ✅ Verifies template sizes
4. ✅ Runs unit tests
5. ✅ Tests scaffold generation
6. ✅ Runs E2E tests (on main branch with secrets)

View results: `.github/workflows/test.yml`

## 📝 Writing Tests

### Test File Structure
```
tests/
├── test_e2e_chatbot.py      # E2E tests for chatbot scaffold
├── test_e2e_assistant.py    # E2E tests for assistant scaffold
├── test_integrations.py     # Tests for Databricks integrations
└── test_scaffolds.py        # Tests for scaffold generation
```

### Example Test
```python
import pytest
from databricks_agent_toolkit.scaffolds import ScaffoldGenerator

def test_chatbot_generation():
    """Test chatbot scaffold generates correctly."""
    generator = ScaffoldGenerator()
    generator.generate('chatbot', 'test-bot', '/tmp/test', {})
    
    # Verify files exist
    assert Path('/tmp/test/app.py').exists()
    assert Path('/tmp/test/chatbot.py').exists()
```

### Mark Tests
```python
@pytest.mark.integration  # Requires Databricks credentials
def test_model_serving():
    ...

@pytest.mark.slow  # Long-running test
def test_large_dataset():
    ...
```

## 🛠️ Development Workflow

### Before Committing
1. Run tests: `./scripts/run_tests.sh`
2. Check formatting: `black . && isort .`
3. Verify pre-commit passes: `pre-commit run --all-files`

### Before Releasing
1. Run full E2E tests: `./scripts/run_tests.sh --full`
2. Check all templates: `python3 scripts/check_template_size.py`
3. Update version in `pyproject.toml`
4. Update `CHANGELOG.md`

## 🎨 Code Optimization Guidelines

### Keep Templates Lean
- **Remove verbose comments** - Code should be self-explanatory
- **Eliminate duplication** - DRY (Don't Repeat Yourself)
- **Simplify logic** - Fewer lines, clearer intent
- **Use Pythonic idioms** - List comprehensions, context managers, etc.

### Example: Before & After
**Before (verbose)**:
```python
# Load configuration from YAML file
config_path = Path(__file__).parent / "config.yaml"
with open(config_path) as f:
    config = yaml.safe_load(f)

# Get the model endpoint from config with default fallback
endpoint = config.get("model", {}).get("endpoint", "default-model")
```

**After (lean)**:
```python
config = yaml.safe_load((Path(__file__).parent / "config.yaml").read_text())
endpoint = config["model"]["endpoint"]
```

## 📈 Monitoring Code Size

Track template sizes over time:
```bash
# Check current sizes
wc -l databricks_agent_toolkit/scaffolds/templates/*/*.jinja2

# Compare with limits
python3 scripts/check_template_size.py
```

## ❓ Troubleshooting

### Tests Fail Locally But Pass in CI
- Check Python version (`python --version`)
- Ensure dependencies are up-to-date (`pip install -e ".[dev]" --upgrade`)

### Pre-commit Hook Fails
- Run manually: `pre-commit run --all-files`
- Update hooks: `pre-commit autoupdate`

### E2E Tests Timeout
- Increase timeout in test config
- Check Databricks workspace availability

## 📚 Resources

- **pytest docs**: https://docs.pytest.org/
- **pre-commit docs**: https://pre-commit.com/
- **Black formatter**: https://black.readthedocs.io/
- **flake8 linter**: https://flake8.pycqa.org/

---

**Remember**: Every code change should include tests and maintain our optimization standards! 🚀

