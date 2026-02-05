"""
Backward compatibility shim for _modules.core

This module has been migrated to medbilldozer.core.
Imports from _modules.core will continue to work but are deprecated.

Prefer: from medbilldozer.core import ...
Old:    from _modules.core import ...
"""

# Re-export everything from the new location
from medbilldozer.core import *  # noqa: F401, F403

# Optional: Add deprecation warning
# import warnings
# warnings.warn(
#     "_modules.core is deprecated, use medbilldozer.core",
#     DeprecationWarning,
#     stacklevel=2
# )
