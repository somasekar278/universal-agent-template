#!/bin/bash
set -e

echo "🧹 Cleaning up project for v0.3.0 release..."
echo ""

# Remove test apps
echo "📦 Removing test apps..."
rm -rf l1-chatbot l1-dash l1-gradio l1-streamlit-test l2-* 2>/dev/null || true

# Remove temporary documentation
echo "📄 Removing temporary docs..."
rm -f CRITICAL_FIX_ASYNC.md DSPY_GEPA_INTEGRATION.md FIXES_APPLIED.md
rm -f GEPA_INTEGRATION_SUMMARY.md LOCKED_AGENTS_DEPLOYMENT.md
rm -f STREAMING_FIX_SUMMARY.md 2>/dev/null || true

# Remove old dist files
echo "🗑️  Cleaning old build artifacts..."
rm -rf dist/*.whl dist/*.tar.gz 2>/dev/null || true
rm -rf build/ *.egg-info/ 2>/dev/null || true

# Remove __pycache__
echo "🗂️  Removing Python cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

echo ""
echo "✅ Cleanup complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Review CHANGELOG.md"
echo "   2. Update version in pyproject.toml to 0.3.0"
echo "   3. Build: python -m build"
echo "   4. Test install: pip install dist/databricks_agent_toolkit-0.3.0-py3-none-any.whl"
echo "   5. Publish: twine upload dist/*"
echo ""
