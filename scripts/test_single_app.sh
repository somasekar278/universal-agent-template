#!/bin/bash
#
# Test a Single Agent App
# Usage: ./scripts/test_single_app.sh <app-directory>
#

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

if [ $# -lt 1 ]; then
    echo -e "${RED}Usage: $0 <app-directory>${NC}"
    echo
    echo "Example:"
    echo "  $0 ./l1-chatbot-streaming"
    exit 1
fi

APP_DIR="$1"

if [ ! -d "$APP_DIR" ]; then
    echo -e "${RED}❌ Directory not found: $APP_DIR${NC}"
    exit 1
fi

APP_NAME=$(basename "$APP_DIR")

echo
echo -e "🧪 Testing: ${GREEN}$APP_NAME${NC}"
echo "   (Code validation - no server required)"
echo

# Set environment for this specific app
export TEST_APP_DIR="$(cd "$APP_DIR" && pwd)"

# Run code structure tests (works for all apps)
pytest tests/test_code_structure.py -v --tb=short

if [ $? -eq 0 ]; then
    echo
    echo -e "${GREEN}✅ Code validation passed!${NC}"
    echo
    echo "Safe to deploy:"
    echo "  cd $APP_DIR"
    echo "  databricks bundle deploy"
    echo "  databricks bundle run"
else
    echo
    echo -e "${RED}❌ Code validation failed!${NC}"
    exit 1
fi
