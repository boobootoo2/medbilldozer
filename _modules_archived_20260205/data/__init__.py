"""
Backward compatibility shim for _modules.data

This module has been migrated to medbilldozer.data.
Imports from _modules.data will continue to work but are deprecated.

Prefer: from medbilldozer.data import ...
Old:    from _modules.data import ...
"""

# Re-export everything from the new location
from medbilldozer.data import *  # noqa: F401, F403

# Optional: Add deprecation warning
# import warnings
# warnings.warn(
#     "_modules.data is deprecated, use medbilldozer.data",
#     DeprecationWarning,
#     stacklevel=2
# )
