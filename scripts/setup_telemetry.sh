#!/bin/bash

#############################################################################
# Turnkey Telemetry Setup Script
#
# Based on: https://github.com/vivian-xie-db/e2e-chatbot-zerobus
#
# This script sets up Zerobus telemetry in one command:
#   1. Generates protobuf schema from Unity Catalog table
#   2. Compiles proto to Python module
#   3. Tests the connection
#
# Usage:
#   ./scripts/setup_telemetry.sh
#
# Or set environment variables and run:
#   UC_ENDPOINT="https://..." TABLE="..." ./scripts/setup_telemetry.sh
#############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "================================================================================"
echo "🎯 Agent Framework - Turnkey Telemetry Setup"
echo "================================================================================"
echo ""

# Check if required environment variables are set
if [ -z "$UC_ENDPOINT" ]; then
    echo -e "${YELLOW}UC_ENDPOINT not set${NC}"
    read -p "Unity Catalog endpoint URL: " UC_ENDPOINT
fi

if [ -z "$TABLE" ]; then
    echo -e "${YELLOW}TABLE not set${NC}"
    read -p "Unity Catalog table (catalog.schema.table): " TABLE
fi

if [ -z "$CLIENT_ID" ]; then
    echo -e "${YELLOW}CLIENT_ID not set${NC}"
    read -p "Databricks OAuth client ID: " CLIENT_ID
fi

if [ -z "$CLIENT_SECRET" ]; then
    echo -e "${YELLOW}CLIENT_SECRET not set${NC}"
    read -sp "Databricks OAuth client secret: " CLIENT_SECRET
    echo ""
fi

# Optional parameters
MESSAGE_NAME="${MESSAGE_NAME:-AgentTelemetry}"
OUTPUT="${OUTPUT:-record.proto}"

echo ""
echo "================================================================================"
echo "🔧 Configuration"
echo "================================================================================"
echo "UC Endpoint:   $UC_ENDPOINT"
echo "Table:         $TABLE"
echo "Client ID:     $CLIENT_ID"
echo "Proto Message: $MESSAGE_NAME"
echo "Output File:   $OUTPUT"
echo ""

# Step 1: Check dependencies
echo "================================================================================"
echo "📦 Step 1: Checking Dependencies"
echo "================================================================================"

# Check if telemetry extras are installed
if python -c "import opentelemetry, grpc, google.protobuf" 2>/dev/null; then
    echo -e "${GREEN}✅ Telemetry dependencies installed${NC}"
else
    echo -e "${RED}❌ Telemetry dependencies not installed${NC}"
    echo ""
    echo "Install with:"
    echo "  pip install sota-agent-framework[telemetry]"
    echo ""
    exit 1
fi

# Check if zerobus tools are available
if python -c "import zerobus.tools.generate_proto" 2>/dev/null; then
    echo -e "${GREEN}✅ Zerobus SDK installed${NC}"
else
    echo -e "${YELLOW}⚠️  Zerobus SDK not found (optional)${NC}"
    echo "   For full Zerobus support, get the SDK from Databricks"
fi

echo ""

# Step 2: Generate protobuf schema from UC table
echo "================================================================================"
echo "📋 Step 2: Generating Protobuf Schema"
echo "================================================================================"

echo "Generating $OUTPUT from $TABLE..."

if python -m zerobus.tools.generate_proto \
    --uc-endpoint "$UC_ENDPOINT" \
    --table "$TABLE" \
    --client-id "$CLIENT_ID" \
    --client-secret "$CLIENT_SECRET" \
    --proto-msg "$MESSAGE_NAME" \
    --output "$OUTPUT"; then
    echo -e "${GREEN}✅ Generated $OUTPUT${NC}"
else
    echo -e "${RED}❌ Failed to generate protobuf schema${NC}"
    echo ""
    echo "Make sure:"
    echo "  1. The table exists in Unity Catalog"
    echo "  2. Your credentials are correct"
    echo "  3. You have read permissions on the table"
    echo ""
    exit 1
fi

echo ""

# Step 3: Compile protobuf to Python
echo "================================================================================"
echo "📦 Step 3: Compiling Protobuf"
echo "================================================================================"

echo "Compiling $OUTPUT to Python..."

if python -m grpc_tools.protoc \
    --python_out=. \
    --proto_path=. \
    "$OUTPUT"; then

    PROTO_MODULE="${OUTPUT%.proto}_pb2.py"
    echo -e "${GREEN}✅ Compiled to $PROTO_MODULE${NC}"
else
    echo -e "${RED}❌ Compilation failed${NC}"
    exit 1
fi

echo ""

# Step 4: Update configuration
echo "================================================================================"
echo "⚙️  Step 4: Updating Configuration"
echo "================================================================================"

CONFIG_FILE="config/agent_config.yaml"

if [ -f "$CONFIG_FILE" ]; then
    echo "Updating $CONFIG_FILE..."

    # Update the zerobus section
    python - <<EOF
import yaml
from pathlib import Path

config_file = Path("$CONFIG_FILE")
with open(config_file, 'r') as f:
    config = yaml.safe_load(f)

# Update telemetry.zerobus section
if 'telemetry' not in config:
    config['telemetry'] = {}
if 'zerobus' not in config['telemetry']:
    config['telemetry']['zerobus'] = {}

config['telemetry']['zerobus'].update({
    'enabled': True,
    'uc_endpoint': '$UC_ENDPOINT',
    'table': '$TABLE',
    'proto_file': '$OUTPUT',
    'proto_message': '$MESSAGE_NAME'
})

with open(config_file, 'w') as f:
    yaml.safe_dump(config, f, default_flow_style=False, sort_keys=False)

print('✅ Updated configuration')
EOF

else
    echo -e "${YELLOW}⚠️  Config file not found: $CONFIG_FILE${NC}"
    echo "   Telemetry will use environment variables"
fi

echo ""

# Step 5: Test connection
echo "================================================================================"
echo "🧪 Step 5: Testing Connection"
echo "================================================================================"

echo "Testing telemetry connection..."

# Simple connection test
if python -c "
import sys
sys.path.insert(0, '.')
from telemetry.zerobus_integration import ZerobusClient

config = {
    'uc_endpoint': '$UC_ENDPOINT',
    'table': '$TABLE',
    'client_id': '$CLIENT_ID',
    'client_secret': '$CLIENT_SECRET'
}

client = ZerobusClient(config)
test_event = {
    'event_type': 'test',
    'agent_id': 'setup_test',
    'message': 'Telemetry setup test'
}

if client.log_event(test_event):
    print('✅ Connection test passed!')
    sys.exit(0)
else:
    print('❌ Connection test failed')
    sys.exit(1)
" 2>&1; then
    echo -e "${GREEN}✅ Telemetry is working!${NC}"
else
    echo -e "${YELLOW}⚠️  Test inconclusive (but setup is complete)${NC}"
    echo "   You can test later with: agent-telemetry test"
fi

echo ""

# Done!
echo "================================================================================"
echo "✅ TELEMETRY SETUP COMPLETE!"
echo "================================================================================"
echo ""
echo "Your agents will now automatically stream telemetry to:"
echo "  📊 Unity Catalog table: $TABLE"
echo ""
echo "Next steps:"
echo "  1. Query telemetry:"
echo "     SELECT * FROM $TABLE LIMIT 10;"
echo ""
echo "  2. Build dashboards in Databricks SQL"
echo ""
echo "  3. Monitor in real-time:"
echo "     agent-telemetry status"
echo ""
echo "📚 Documentation: docs/TELEMETRY.md"
echo ""
echo "================================================================================"
