#!/usr/bin/env python3
"""
Template Validation Script
Validates all scaffold templates by generating test apps and checking for common issues.
"""
import os
import re
import sys
import shutil
import tempfile
import subprocess
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

WORKSPACE_ROOT = Path(__file__).parent.parent


def validate_python_syntax(file_path: Path) -> list[str]:
    """Compile Python file to check for syntax errors."""
    errors = []
    try:
        with open(file_path, 'r') as f:
            code = f.read()
        compile(code, str(file_path), 'exec')
    except SyntaxError as e:
        errors.append(f"Python syntax error in {file_path.name}: {e}")
    return errors


def validate_javascript(file_path: Path) -> list[str]:
    """Check for common JavaScript issues in Python files containing HTML/JS."""
    errors = []
    try:
        with open(file_path, 'r') as f:
            content = f.read()

        # Check for unescaped newline (should be \\n in Python string, becomes \n in JS)
        # In Python triple-quoted strings, we need split('\\n') which outputs split('\n') in HTML
        if r"split('\n')" in content or r'split("\n")' in content:
            # Check if it's actually in the CHAT_HTML string (not in a comment or other context)
            if 'CHAT_HTML' in content and (r"split('\n')" in content or r'split("\n")' in content):
                errors.append(f"{file_path.name}: Found split('\\n') - should be split('\\\\n') in Python string")

        # Check for inline event handlers (should use addEventListener)
        if re.search(r'onclick=|onkeypress=|onsubmit=', content):
            errors.append(f"{file_path.name}: Found inline event handlers - should use addEventListener")

        # Check for {{ streaming }} without proper replacement logic
        if re.search(r'const STREAMING = \{\{ streaming', content):
            errors.append(f"{file_path.name}: Found unreplaced {{ streaming }} in JavaScript")

        # Check for missing Cache-Control headers
        if 'response_class=HTMLResponse' in content and 'Cache-Control' not in content:
            errors.append(f"{file_path.name}: Missing Cache-Control headers for HTML response")

    except Exception as e:
        errors.append(f"Error reading {file_path.name}: {e}")

    return errors


def validate_required_files(app_dir: Path) -> list[str]:
    """Check that all required files exist."""
    errors = []
    required = ['start_server.py', 'agent.py', 'config.yaml', 'databricks.yml', 'requirements.txt']
    for file in required:
        if not (app_dir / file).exists():
            errors.append(f"Missing required file: {file}")
    return errors


def validate_mlflow_decorators(agent_file: Path) -> list[str]:
    """Check that agent.py has proper MLflow decorators."""
    errors = []
    try:
        with open(agent_file, 'r') as f:
            content = f.read()

        if not re.search(r'@(invoke|stream)\(', content):
            errors.append(f"agent.py: Missing @invoke() or @stream() decorator")

        if '@invoke(' in content and '@stream(' in content:
            errors.append(f"agent.py: Has both @invoke and @stream decorators - should only have one")

    except Exception as e:
        errors.append(f"Error reading agent.py: {e}")

    return errors


def generate_and_validate(template_type: str, app_name: str, streaming: bool, temp_dir: Path) -> dict:
    """Generate an app from template and validate it."""
    results = {
        'template': template_type,
        'streaming': streaming,
        'app_name': app_name,
        'errors': [],
        'warnings': []
    }

    # Generate the app
    cmd = [
        'python3', '-m', 'databricks_agent_toolkit.cli.main',
        'generate', template_type, app_name,
        '--model', 'databricks-claude-sonnet-4'
    ]
    if streaming:
        cmd.append('--streaming')

    try:
        result = subprocess.run(
            cmd,
            cwd=temp_dir,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            results['errors'].append(f"Generation failed: {result.stderr}")
            return results

    except Exception as e:
        results['errors'].append(f"Generation error: {e}")
        return results

    app_dir = temp_dir / app_name

    # Validate required files
    results['errors'].extend(validate_required_files(app_dir))

    # Validate Python syntax
    for py_file in app_dir.glob('*.py'):
        results['errors'].extend(validate_python_syntax(py_file))

    # Validate JavaScript in start_server.py
    if (app_dir / 'start_server.py').exists():
        results['errors'].extend(validate_javascript(app_dir / 'start_server.py'))

    # Validate MLflow decorators
    if (app_dir / 'agent.py').exists():
        results['errors'].extend(validate_mlflow_decorators(app_dir / 'agent.py'))

    return results


def main():
    print("=" * 70)
    print("🔍 VALIDATING ALL SCAFFOLD TEMPLATES")
    print("=" * 70)
    print()

    # Test cases: (template_type, streaming)
    test_cases = [
        ('chatbot', False, 'test-chatbot-batch'),
        ('chatbot', True, 'test-chatbot-stream'),
        ('assistant', False, 'test-assistant-batch'),
        ('assistant', True, 'test-assistant-stream'),
    ]

    all_results = []
    total_errors = 0

    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        for template_type, streaming, app_name in test_cases:
            mode = "streaming" if streaming else "batch"
            print(f"📦 Testing {template_type} ({mode})...")

            results = generate_and_validate(template_type, app_name, streaming, temp_path)
            all_results.append(results)

            if results['errors']:
                print(f"   ❌ {len(results['errors'])} error(s) found")
                for error in results['errors']:
                    print(f"      • {error}")
                total_errors += len(results['errors'])
            else:
                print(f"   ✅ Passed all checks")

            print()

    # Summary
    print("=" * 70)
    print("📊 VALIDATION SUMMARY")
    print("=" * 70)
    print()

    for results in all_results:
        mode = "streaming" if results['streaming'] else "batch"
        status = "❌ FAILED" if results['errors'] else "✅ PASSED"
        print(f"{status}: {results['template']} ({mode})")
        if results['errors']:
            print(f"         {len(results['errors'])} error(s)")

    print()
    print(f"Total errors: {total_errors}")
    print()

    if total_errors > 0:
        print("❌ VALIDATION FAILED - Fix templates before using")
        sys.exit(1)
    else:
        print("✅ ALL TEMPLATES VALID - Ready to use")
        sys.exit(0)


if __name__ == '__main__':
    main()
