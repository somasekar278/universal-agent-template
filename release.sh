#!/bin/bash
# PyPI Release Helper Script
# Usage: ./release.sh [version]
# Example: ./release.sh 0.1.6

set -e

VERSION=$1

if [ -z "$VERSION" ]; then
    echo "❌ Error: Version required"
    echo "Usage: ./release.sh <version>"
    echo "Example: ./release.sh 0.1.6"
    exit 1
fi

echo "🚀 Starting release $VERSION..."
echo ""

# Update version in pyproject.toml
echo "📝 Updating version to $VERSION..."
sed -i '' "s/version = \".*\"/version = \"$VERSION\"/" pyproject.toml

# Clean old builds
echo "🧹 Cleaning old builds..."
rm -rf dist/ build/ *.egg-info

# Build package
echo "📦 Building package..."
./venv/bin/python -m build

# Upload to PyPI (uses ~/.pypirc)
echo "📤 Uploading to PyPI..."
./venv/bin/python -m twine upload dist/*

# Git commit and push
echo "📌 Committing to git..."
git add pyproject.toml
git commit -m "Release $VERSION" || echo "No changes to commit"

echo "🔄 Pushing to GitHub..."
git push origin main

echo ""
echo "✅ Release $VERSION complete!"
echo "📦 PyPI: https://pypi.org/project/databricks-agent-toolkit/$VERSION/"
echo "📂 GitHub: https://github.com/somasekar278/databricks-agent-toolkit"
