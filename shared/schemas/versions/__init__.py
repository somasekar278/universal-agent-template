"""
Versioned schema definitions.

This package contains different versions of our schemas organized by version.

Structure:
    versions/
    ├── v1/            # Version 1.x.x schemas
    ├── v2/            # Version 2.x.x schemas
    └── current/       # Symlink to latest stable version
"""

# Current (latest) version imports
from .v1 import *

__version__ = "1.0.0"

