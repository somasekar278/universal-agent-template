# Agent Deployment Workflow

## The New Process: Generate → Test → Deploy → Run → View

Testing is now built into the deployment workflow to catch bugs **before** they reach Databricks.

---

## 🚀 Quick Start

### Option 1: Automated (Recommended)

One command that does everything:

```bash
# Generate agent
dat generate chatbot my-bot

# Test → Deploy → Run (all in one)
./scripts/deploy_agent.sh my-bot
```

### Option 2: Step-by-Step

Full control over each step:

```bash
# 1. Generate
dat generate chatbot my-bot

# 2. Test (locally, ~10 seconds)
dat test my-bot

# 3. Deploy (to Databricks)
cd my-bot
databricks bundle deploy

# 4. Run (start the app)
databricks bundle run

# 5. View (open in browser)
# Go to: Databricks → Compute → Apps → my-bot
```

---

## 📋 Detailed Workflow

### Step 1: Generate

Create your agent scaffold:

```bash
# L1 Chatbot (simple)
dat generate chatbot my-bot

# L2 Assistant (with memory)
dat generate assistant my-assistant

# L2 with RAG
dat generate assistant doc-bot --enable-rag
```

**Output:**
- Generated code in `./my-bot/`
- All required files
- Ready to test

### Step 2: Test ⭐ NEW!

**This catches bugs before deployment!**

```bash
dat test my-bot
```

**What it tests (ALL apps, L1-L5):**
- ✅ No `/stream` endpoint in code (catches the bug!)
- ✅ Uses `/invocations` correctly
- ✅ Python syntax is valid
- ✅ Has required files (agent.py, config.yaml, etc.)
- ✅ MLflow decorators used correctly

**Fast:** Takes ~2 seconds
**Simple:** No server needed, works for all apps
**Effective:** Catches the endpoint bug before deploying

### Step 3: Deploy

Upload to Databricks:

```bash
cd my-bot
databricks bundle deploy
```

**What happens:**
- Code uploaded to Databricks workspace
- App configuration deployed
- Resources created

### Step 4: Run

Start the application:

```bash
databricks bundle run
```

**What happens:**
- App server starts
- Endpoints become available
- Ready for traffic

### Step 5: View

Open in browser:

1. Go to Databricks workspace
2. Navigate to: **Compute → Apps**
3. Find your app: `my-bot`
4. Click to open

---

## 🎯 Why Test Locally First?

### Before (Old Way)
```
Generate → Deploy → Run → BUG! → Fix → Deploy → Run → BUG! → ...
```
- ⏰ Each deploy takes 2-3 minutes
- 😫 Trial and error on Databricks
- 💸 Wastes time and compute

### After (New Way)
```
Generate → Test (10s) → ✅ → Deploy → Run → ✅ Works!
```
- ⚡ Test in 10 seconds locally
- ✅ Catch bugs before deploying
- 🎯 Deploy with confidence

---

## 🔧 CLI Commands

### `dat generate`

Generate agent scaffolds:

```bash
dat generate <type> <name> [options]

# Examples
dat generate chatbot my-bot
dat generate assistant my-assistant
dat generate assistant doc-bot --enable-rag
```

### `dat test` ⭐ NEW!

Test agent locally:

```bash
dat test <app-directory> [options]

# Examples
dat test ./my-bot
dat test ./my-assistant --port 8001
dat test ./my-bot --skip-integration  # Quick syntax check only
```

**Options:**
- `--port PORT`: Port for test server (default: 8000)
- `--skip-integration`: Skip full tests, only check syntax

### `dat auth`

Check Databricks authentication:

```bash
dat auth check
```

---

## 🛠️ Scripts

### `deploy_agent.sh`

Complete deployment workflow in one command:

```bash
./scripts/deploy_agent.sh <app-directory>

# Example
./scripts/deploy_agent.sh ./my-bot
```

**What it does:**
1. Tests locally
2. Deploys to Databricks
3. Starts the app
4. Shows you where to view it

**Stops if tests fail** - prevents deploying broken code!

### `test_streaming_endpoints.sh`

Test streaming endpoints for all apps:

```bash
./scripts/test_streaming_endpoints.sh
```

Useful for CI/CD or testing multiple apps.

---

## 🐛 Troubleshooting

### Test Fails: "/invocations endpoint does not exist"

**Problem:** Server didn't start or wrong port

**Fix:**
```bash
# Check if port is in use
lsof -i :8000

# Try different port
dat test ./my-bot --port 8001
```

### Test Fails: "Using /stream endpoint"

**Problem:** Code uses wrong endpoint (common bug!)

**Fix:** Check `start_server.py`:
- ✅ Should use: `fetch('/invocations', { ... stream: true })`
- ❌ Wrong: `fetch('/stream', ...)`

See: `docs/MLFLOW_AGENT_SERVER_API.md`

### Deploy Fails: "Authentication error"

**Problem:** Databricks credentials not set

**Fix:**
```bash
# Check auth
dat auth check

# Set credentials
export DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
export DATABRICKS_TOKEN=your-token
```

### App Doesn't Start After Deploy

**Problem:** Could be various issues

**Fix:**
```bash
# Check logs
cd my-bot
databricks bundle logs

# Common issues:
# - Missing dependencies in requirements.txt
# - Environment variables not set
# - Port conflicts
```

---

## 📚 Additional Resources

- **API Reference:** `docs/MLFLOW_AGENT_SERVER_API.md`
- **Testing Guide:** `tests/README_PREVENTING_ENDPOINT_BUGS.md`
- **Full Documentation:** `docs/GETTING_STARTED.md`

---

## 🎓 Examples

### Example 1: Simple Chatbot

```bash
# Generate
dat generate chatbot hello-bot

# Test (takes ~10 seconds)
dat test hello-bot

# Output:
# ✅ /invocations endpoint exists
# ✅ /stream does not exist
# ✅ Streaming works
# ✅ All tests passed!

# Deploy (all in one)
./scripts/deploy_agent.sh hello-bot
```

### Example 2: Assistant with Memory

```bash
# Generate
dat generate assistant support-bot

# Test
dat test support-bot

# Deploy step-by-step
cd support-bot
databricks bundle deploy
databricks bundle run
```

### Example 3: CI/CD Pipeline

```yaml
# .github/workflows/deploy.yml
name: Deploy Agent

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install dependencies
        run: pip install databricks-agent-toolkit pytest requests

      - name: Test locally
        run: dat test ./my-agent

      - name: Deploy to Databricks
        if: success()
        env:
          DATABRICKS_HOST: ${{ secrets.DATABRICKS_HOST }}
          DATABRICKS_TOKEN: ${{ secrets.DATABRICKS_TOKEN }}
        run: ./scripts/deploy_agent.sh ./my-agent
```

---

## ✅ Checklist

Before deploying to production:

- [ ] Generated agent with `dat generate`
- [ ] Tested locally with `dat test` (all tests pass)
- [ ] Reviewed generated code
- [ ] Set up Databricks credentials
- [ ] Deployed with `databricks bundle deploy`
- [ ] Started with `databricks bundle run`
- [ ] Verified in Databricks Apps UI
- [ ] Tested end-to-end in browser

---

**Last Updated:** 2026-01-11
**Workflow Version:** 2.0 (with integrated testing)
