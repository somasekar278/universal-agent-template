# Preventing Endpoint Bugs - Testing Strategy

## The Problem We Solved

**Root Cause:** L1 and L2 streaming apps were using `/stream` endpoint which doesn't exist in MLflow 3.6+. The correct endpoint is `/invocations` with `"stream": true`.

**Why It Happened:**
- No automated verification of MLflow Agent Server API compliance
- Documentation only, no enforcement

## Prevention Strategy

### 1. Code Structure Tests (`test_code_structure.py`)

**What It Tests:**
- ✅ Code doesn't reference `/stream` endpoint (catches the bug!)
- ✅ Uses `/invocations` correctly
- ✅ Python syntax is valid
- ✅ Required files exist (agent.py, config.yaml, etc.)
- ✅ MLflow integration is correct

**Why This Works:**
- No server needed - works for ALL apps (L1-L5)
- Fast (2 seconds vs 10+ seconds for server tests)
- Catches the endpoint bug in code before deployment
- Works even when apps need external services (databases, etc.)

### 2. Test Runner Script (`scripts/test_streaming_endpoints.sh`)

**Usage:**
```bash
./scripts/test_streaming_endpoints.sh
```

**Before deploying ANY streaming app, run this script. It will:**
- Run all integration tests
- Give clear pass/fail
- Suggest fixes if tests fail

### 3. CI/CD Integration (`.github/workflows/test.yml`)

**Automated Checks on Every Commit:**
- Run integration tests
- Verify endpoint compliance
- Block merge if tests fail

### 4. Pre-Deployment Checklist

**Before deploying to Databricks:**
```bash
# 1. Run integration tests
./scripts/test_streaming_endpoints.sh

# 2. Test locally first
cd l1-chatbot-streaming
python3 start_server.py

# 3. In another terminal, test the endpoint
curl -X POST http://localhost:8000/invocations \
  -H "Content-Type: application/json" \
  -d '{"input": [], "stream": true}'

# 4. Verify you see SSE format:
#    data: {...}
#    data: {...}
#    data: [DONE]

# 5. Deploy to Databricks
databricks bundle deploy && databricks bundle run
```

## How To Run Tests

### Test Any App (Recommended)
```bash
export TEST_APP_DIR="/path/to/your/app"
pytest tests/test_code_structure.py -v
```

### Using CLI
```bash
dat test ./my-app
```

### Using Script
```bash
./scripts/test_single_app.sh ./my-app
```

### Run Specific Test
```bash
export TEST_APP_DIR="./my-app"
pytest tests/test_code_structure.py::TestEndpointUsage::test_no_stream_endpoint_in_code -v
```

## What Each Test Does

### `TestPythonSyntax`
- **Purpose:** Ensure all Python files compile
- **Key Test:** All `.py` files have valid syntax

### `TestEndpointUsage`
- **Purpose:** Prevent the `/stream` endpoint bug
- **Key Tests:**
  - Code doesn't reference `/stream` endpoint ✅
  - Uses `/invocations` correctly ✅

### `TestMLflowIntegration`
- **Purpose:** Verify MLflow setup
- **Key Tests:**
  - Has `agent.py` file
  - Imports MLflow
  - Uses `@invoke()` or `@stream()` decorator

### `TestConfiguration`
- **Purpose:** Validate configuration files
- **Key Tests:**
  - Has `config.yaml`
  - Has `databricks.yml`
  - YAML is valid

### `TestRequirements`
- **Purpose:** Check dependencies
- **Key Tests:**
  - Has `requirements.txt`
  - Includes MLflow

## Adding Tests for New Features

### Template for New Streaming App Tests
```python
@pytest.fixture
def my_new_app_server():
    """Start my new streaming app."""
    app_dir = Path(__file__).parent.parent / "my-new-app"
    with ServerFixture(app_dir, port=8097) as server:
        yield server

class TestMyNewApp:
    def test_endpoints_correct(self, my_new_app_server):
        """Verify endpoints are correct."""
        # Should have /invocations
        response = requests.post(
            f"{my_new_app_server.base_url}/invocations",
            json={"input": []},
            timeout=5
        )
        assert response.status_code != 404

        # Should NOT have /stream
        response = requests.post(
            f"{my_new_app_server.base_url}/stream",
            json={"input": []},
            timeout=5
        )
        assert response.status_code == 404
```

## Continuous Improvement

### After Any MLflow Upgrade
1. Check [MLflow Release Notes](https://github.com/mlflow/mlflow/releases)
2. Update tests if API changes
3. Run full test suite
4. Update `docs/MLFLOW_AGENT_SERVER_API.md` if needed

### When Adding L3/L4/L5 Apps
1. Copy test template above
2. Add fixture for new app
3. Test specific features (tools, RAG, etc.)
4. Add to CI/CD workflow

### Monthly Review
- Run full test suite: `pytest tests/ -v`
- Check for flaky tests
- Update test data/fixtures
- Review test coverage

## Test Environment

### Requirements
```bash
pip install pytest requests
```

### Environment Variables (Optional)
```bash
export MLFLOW_TRACKING_URI=sqlite:///mlflow_test.db
export DATABRICKS_APP_PORT=8099
```

## Debugging Failed Tests

### Test Fails to Start Server
- Check if port is already in use: `lsof -i :8099`
- Check if dependencies installed: `pip install -r requirements.txt`
- Check server logs: Run server manually to see errors

### Endpoint Test Fails
- Check which endpoint failed: Look at test output
- Test endpoint manually: Use `curl` command
- Check MLflow version: `mlflow --version` (should be >= 3.6.0)

### Streaming Format Test Fails
- Capture raw response: Add `-s` flag to pytest
- Check SSE format: Should be `data: {...}\n`
- Verify [DONE] marker: Should be last line

## Success Metrics

**We'll know this works when:**
- ✅ No more incorrect endpoint bugs
- ✅ All streaming apps pass integration tests
- ✅ CI catches issues before merge
- ✅ Deployments are confident, not trial-and-error

## References

- MLflow Agent Server: https://mlflow.org/docs/latest/genai/serving/agent-server/
- Integration Tests: `tests/test_mlflow_agent_server_integration.py`
- API Reference: `docs/MLFLOW_AGENT_SERVER_API.md`
- Test Runner: `scripts/test_streaming_endpoints.sh`

---

**Last Updated:** 2026-01-11
**Test Coverage:** L1 Chatbot, L2 Assistant (both streaming)
**Next:** Add L3/L4/L5 when implemented
