#!/usr/bin/env python3
"""
Clean up temporary test files and folders.

Runs automatically before each commit via pre-commit hook.
"""

import os
import shutil
import sys
from pathlib import Path

# Temp directories to clean up
TEMP_DIRS = [
    '/tmp/e2e-test-assistant',
    '/tmp/lean-chatbot-test',
    '/tmp/rag-vector-search-test',
    '/tmp/simple-chatbot',
    '/tmp/test-assistant-e2e',
    '/tmp/test-assistant-rag',
    '/tmp/test-chatbot-v2',
    '/tmp/test-cli-validation',
    '/tmp/test-fix-v20',
    '/tmp/test-hex',
    '/tmp/test-rag-assistant',
    '/tmp/test-simple',
    '/tmp/test-streaming-bot',
    '/tmp/test-streaming-chatbot',
]

# Temp files to clean up
TEMP_FILES = [
    '/tmp/app.log',
    '/tmp/lean-app.log',
    '/tmp/lean-app-streaming.log',
    '/tmp/test-chatbot-minimal.py',
    '/tmp/test_rag_chat.py',
    '/tmp/test_rag_components.py',
    '/tmp/chat-bubble-preview.html',
    '/tmp/deployment-guide.txt',
]

# Patterns to match (for wildcard cleanup)
TEMP_PATTERNS = [
    '/tmp/test-*.py',
    '/tmp/*-test-*',
    '/tmp/*chatbot*',
    '/tmp/*assistant*',
]


def cleanup_temp_files():
    """Remove temporary test files and directories."""
    cleaned = []
    
    # Clean up directories
    for temp_dir in TEMP_DIRS:
        if os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
                cleaned.append(f"📁 {temp_dir}")
            except Exception as e:
                print(f"⚠️  Could not remove {temp_dir}: {e}", file=sys.stderr)
    
    # Clean up files
    for temp_file in TEMP_FILES:
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
                cleaned.append(f"📄 {temp_file}")
            except Exception as e:
                print(f"⚠️  Could not remove {temp_file}: {e}", file=sys.stderr)
    
    # Clean up pattern-matched files
    import glob
    for pattern in TEMP_PATTERNS:
        for path in glob.glob(pattern):
            if os.path.isfile(path):
                try:
                    os.remove(path)
                    cleaned.append(f"📄 {path}")
                except Exception:
                    pass
            elif os.path.isdir(path):
                try:
                    shutil.rmtree(path)
                    cleaned.append(f"📁 {path}")
                except Exception:
                    pass
    
    # Report results
    if cleaned:
        print(f"🧹 Cleaned up {len(cleaned)} temporary items:")
        for item in cleaned[:5]:  # Show first 5
            print(f"   {item}")
        if len(cleaned) > 5:
            print(f"   ... and {len(cleaned) - 5} more")
    else:
        print("✅ No temporary files to clean up")
    
    return True


if __name__ == '__main__':
    try:
        success = cleanup_temp_files()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Cleanup failed: {e}", file=sys.stderr)
        sys.exit(1)

