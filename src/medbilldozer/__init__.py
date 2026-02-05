"""
medBillDozer - Medical Bill Analysis and Error Detection

This is the new Python best-practices structure for medBillDozer.
The package is gradually migrating from _modules/ to src/medbilldozer/.

For backward compatibility during migration, imports from both paths are supported:
    from medbilldozer.core import ...      # New style (preferred)
    from _modules.core import ...          # Old style (deprecated)
"""

__version__ = "0.2.0"
__author__ = "medBillDozer Team"

# Package metadata
__all__ = [
    "core",
    "providers", 
    "ui",
    "data",
    "extractors",
    "ingest",
    "prompts",
    "utils",
]
