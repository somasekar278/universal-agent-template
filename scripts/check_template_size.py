#!/usr/bin/env python3
"""
Check that template files stay lean and optimized.

Fails if templates exceed size limits.
"""

import sys
from pathlib import Path

# Define limits (lines of code)
LIMITS = {
    'chatbot/chatbot.py.jinja2': 100,
    'chatbot/app.py.jinja2': 250,
    'assistant/assistant.py.jinja2': 150,
    'assistant/app.py.jinja2': 300,
}

def check_template_sizes():
    """Check all template files against size limits."""
    templates_dir = Path('databricks_agent_toolkit/scaffolds/templates')
    failed = []

    print("📏 Checking template sizes...")
    print("-" * 50)

    for template_path, max_lines in LIMITS.items():
        full_path = templates_dir / template_path

        if not full_path.exists():
            print(f"⚠️  {template_path}: File not found")
            continue

        line_count = len(full_path.read_text().splitlines())
        status = "✅" if line_count <= max_lines else "❌"

        print(f"{status} {template_path}: {line_count}/{max_lines} lines")

        if line_count > max_lines:
            failed.append((template_path, line_count, max_lines))

    print("-" * 50)

    if failed:
        print("\n❌ Template size checks FAILED:")
        for path, actual, limit in failed:
            print(f"   {path}: {actual} lines (limit: {limit})")
        print("\nOptimize templates to reduce line count.")
        return False

    print("✅ All templates within size limits")
    return True


if __name__ == '__main__':
    success = check_template_sizes()
    sys.exit(0 if success else 1)
