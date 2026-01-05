#!/bin/bash
# Comprehensive Test & Optimization Runner
# Usage: ./scripts/run_tests.sh [--full]

set -e

echo "🧪 Databricks Agent Toolkit - Test Suite"
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if full tests requested
FULL_TESTS=false
if [[ "$1" == "--full" ]]; then
    FULL_TESTS=true
fi

# 1. Code Quality Checks
echo "📊 Step 1: Code Quality Checks"
echo "--------------------------------"

# Check Python syntax
echo "  • Checking Python syntax..."
python3 -m py_compile databricks_agent_toolkit/**/*.py 2>/dev/null && \
    echo -e "    ${GREEN}✓${NC} No syntax errors" || \
    echo -e "    ${RED}✗${NC} Syntax errors found"

# Check for common issues
echo "  • Checking for TODO/FIXME..."
TODO_COUNT=$(grep -r "TODO\|FIXME" databricks_agent_toolkit/ --include="*.py" | wc -l)
if [ "$TODO_COUNT" -gt 0 ]; then
    echo -e "    ${YELLOW}⚠${NC}  Found $TODO_COUNT TODO/FIXME comments"
fi

# Line count check (templates)
echo "  • Checking template line counts..."
CHATBOT_PY=$(wc -l < databricks_agent_toolkit/scaffolds/templates/chatbot/chatbot.py.jinja2)
APP_PY=$(wc -l < databricks_agent_toolkit/scaffolds/templates/chatbot/app.py.jinja2)

if [ "$CHATBOT_PY" -lt 100 ]; then
    echo -e "    ${GREEN}✓${NC} chatbot.py: $CHATBOT_PY lines (target: <100)"
else
    echo -e "    ${RED}✗${NC} chatbot.py: $CHATBOT_PY lines (target: <100)"
fi

if [ "$APP_PY" -lt 250 ]; then
    echo -e "    ${GREEN}✓${NC} app.py: $APP_PY lines (target: <250)"
else
    echo -e "    ${RED}✗${NC} app.py: $APP_PY lines (target: <250)"
fi

echo ""

# 2. Unit Tests (if pytest available)
echo "📦 Step 2: Unit Tests"
echo "---------------------"
if command -v pytest &> /dev/null; then
    pytest tests/ -v --tb=short -m "not integration" || echo -e "${RED}Some tests failed${NC}"
else
    echo -e "${YELLOW}⚠${NC}  pytest not installed, skipping unit tests"
fi

echo ""

# 3. Scaffold Generation Test
echo "🏗️  Step 3: Scaffold Generation"
echo "-------------------------------"
echo "  • Generating test chatbot scaffold..."

TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"

python3 -c "
from databricks_agent_toolkit.scaffolds import ScaffoldGenerator
generator = ScaffoldGenerator()
generator.generate('chatbot', 'test-bot', '.', {'model': 'test-model'})
print('✅ Scaffold generated successfully')
" 2>&1

# Verify files
REQUIRED_FILES=("app.py" "chatbot.py" "config.yaml" "README.md" "databricks.yml")
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "  ${GREEN}✓${NC} $file exists"
    else
        echo -e "  ${RED}✗${NC} $file missing"
    fi
done

cd - > /dev/null
rm -rf "$TEMP_DIR"

echo ""

# 4. Full E2E Tests (optional, requires credentials)
if [ "$FULL_TESTS" = true ]; then
    echo "🚀 Step 4: Full E2E Tests (with Model Serving)"
    echo "-----------------------------------------------"
    
    if [ -z "$DATABRICKS_HOST" ]; then
        echo -e "${YELLOW}⚠${NC}  Skipping: DATABRICKS_HOST not set"
        echo "   Set credentials to run full tests:"
        echo "   export DATABRICKS_HOST=..."
        echo "   export DATABRICKS_CLIENT_ID=..."
        echo "   export DATABRICKS_CLIENT_SECRET=..."
    else
        pytest tests/test_e2e_chatbot.py -v --tb=short \
            --databricks-host="$DATABRICKS_HOST" \
            --databricks-client-id="$DATABRICKS_CLIENT_ID" \
            --databricks-client-secret="$DATABRICKS_CLIENT_SECRET" || \
            echo -e "${RED}E2E tests failed${NC}"
    fi
else
    echo "💡 Step 4: Full E2E Tests"
    echo "-------------------------"
    echo "  Skipped (run with --full to enable)"
    echo "  Requires: DATABRICKS_HOST, DATABRICKS_CLIENT_ID, DATABRICKS_CLIENT_SECRET"
fi

echo ""
echo "========================================"
echo -e "${GREEN}✅ Test suite complete!${NC}"
echo ""
echo "Quick commands:"
echo "  • Run full tests: ./scripts/run_tests.sh --full"
echo "  • Run specific test: pytest tests/test_e2e_chatbot.py::TestClassName::test_name -v"
echo ""

