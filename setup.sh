#!/bin/bash
# SOTA Agent Framework - One-Time Setup Script

echo "🚀 Setting up SOTA Agent Framework..."
echo ""

# Check if Python is available
if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
    echo "❌ Python is not installed. Please install Python 3.9+ first."
    exit 1
fi

# Use python3 if available, otherwise python
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

echo "📦 Installing dependencies..."
$PYTHON_CMD -m pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies. Please check the error above."
    exit 1
fi

echo ""
echo "🔧 Installing framework as editable package..."
$PYTHON_CMD -m pip install -e .

if [ $? -ne 0 ]; then
    echo "❌ Failed to install framework. Please check the error above."
    exit 1
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "🎉 You're ready to generate agent projects!"
echo ""
echo "Try it now:"
echo "  python template_generator.py --domain \"your_domain\" --output ./your_project"
echo ""
echo "See GETTING_STARTED.md for more information."

