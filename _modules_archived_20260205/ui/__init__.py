"""
Backward compatibility shim for _modules.ui

This module has been migrated to medbilldozer.ui.
Imports from _modules.ui will continue to work but are deprecated.

Prefer: from medbilldozer.ui import ...
Old:    from _modules.ui import ...
"""

# Re-export everything from the new location
from medbilldozer.ui import *  # noqa: F401, F403

# Optional: Add deprecation warning
# import warnings
# warnings.warn(
#     "_modules.ui is deprecated, use medbilldozer.ui",
#     DeprecationWarning,
#     stacklevel=2
# )
