#!/bin/bash
#
# Complete Agent Deployment Workflow
# Usage: ./scripts/deploy_agent.sh <app-directory>
#
# Workflow: Test → Deploy → Run → View
#

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check arguments
if [ $# -lt 1 ]; then
    echo -e "${RED}Usage: $0 <app-directory>${NC}"
    echo
    echo "Example:"
    echo "  $0 ./my-chatbot"
    exit 1
fi

APP_DIR="$1"

# Check if directory exists
if [ ! -d "$APP_DIR" ]; then
    echo -e "${RED}❌ Directory not found: $APP_DIR${NC}"
    exit 1
fi

APP_NAME=$(basename "$APP_DIR")

echo
echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                           ║${NC}"
echo -e "${BLUE}║       Agent Deployment Workflow                           ║${NC}"
echo -e "${BLUE}║                                                           ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"
echo
echo -e "Agent: ${GREEN}$APP_NAME${NC}"
echo -e "Directory: ${GREEN}$APP_DIR${NC}"
echo

# Step 1: Test locally
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Step 1/4: Testing Locally${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo

if command -v dat &> /dev/null; then
    dat test "$APP_DIR"
else
    # Fallback to direct pytest - code validation only
    export TEST_APP_DIR="$(cd "$APP_DIR" && pwd)"
    pytest tests/test_code_structure.py -v --tb=short
fi

TEST_STATUS=$?

if [ $TEST_STATUS -ne 0 ]; then
    echo
    echo -e "${RED}❌ Code validation failed! Fix issues before deploying.${NC}"
    echo
    echo -e "${YELLOW}Common issues:${NC}"
    echo "  • Using /stream instead of /invocations"
    echo "  • Syntax errors in Python files"
    echo "  • Missing required files"
    exit 1
fi

echo
echo -e "${GREEN}✅ Code validation passed!${NC}"
echo

# Step 2: Deploy
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Step 2/4: Deploying to Databricks${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo

cd "$APP_DIR"

if ! command -v databricks &> /dev/null; then
    echo -e "${RED}❌ Databricks CLI not found${NC}"
    echo "Install: pip install databricks-cli"
    exit 1
fi

echo "Running: databricks bundle deploy"
databricks bundle deploy

DEPLOY_STATUS=$?

if [ $DEPLOY_STATUS -ne 0 ]; then
    echo
    echo -e "${RED}❌ Deploy failed!${NC}"
    exit 1
fi

echo
echo -e "${GREEN}✅ Deployed successfully!${NC}"
echo

# Step 3: Run/Start
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Step 3/4: Starting Application${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo

echo "Running: databricks bundle run"
databricks bundle run

RUN_STATUS=$?

if [ $RUN_STATUS -ne 0 ]; then
    echo
    echo -e "${RED}❌ Start failed!${NC}"
    exit 1
fi

echo
echo -e "${GREEN}✅ Application started!${NC}"
echo

# Step 4: View
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Step 4/4: View Application${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo

echo -e "${GREEN}✅ Deployment complete!${NC}"
echo
echo "Your agent is now running on Databricks Apps."
echo
echo "Next steps:"
echo "  1. Open Databricks workspace"
echo "  2. Navigate to: Compute → Apps"
echo "  3. Find your app: ${GREEN}$APP_NAME${NC}"
echo "  4. Click to open and test"
echo
echo "To view logs:"
echo "  databricks bundle logs"
echo

cd - > /dev/null
