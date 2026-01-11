#!/bin/bash
#
# Test Streaming Endpoints
# Run this before deploying any streaming app to catch endpoint bugs
#

set -e

echo "🧪 Testing Agent Code Validation..."
echo

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}❌ pytest not found. Install it:${NC}"
    echo "   pip install pytest"
    exit 1
fi

# Run code structure tests
echo "Running code validation tests (no server required)..."
echo

if pytest tests/test_code_structure.py -v -s; then
    echo
    echo -e "${GREEN}✅ All code validation tests passed!${NC}"
    echo
    echo "Safe to deploy to Databricks."
    exit 0
else
    echo
    echo -e "${RED}❌ Code validation tests failed!${NC}"
    echo
    echo -e "${YELLOW}Common issues:${NC}"
    echo "  1. Using /stream instead of /invocations"
    echo "  2. Syntax errors in Python files"
    echo "  3. Missing required files or configurations"
    exit 1
fi
