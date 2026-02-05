"""
Backward compatibility shim for _modules.utils

This module has been migrated to medbilldozer.utils.
Imports from _modules.utils will continue to work but are deprecated.

Prefer: from medbilldozer.utils import ...
Old:    from _modules.utils import ...
"""

# Re-export everything from the new location
from medbilldozer.utils import *  # noqa: F401, F403

# Optional: Add deprecation warning
# import warnings
# warnings.warn(
#     "_modules.utils is deprecated, use medbilldozer.utils",
#     DeprecationWarning,
#     stacklevel=2
# )
