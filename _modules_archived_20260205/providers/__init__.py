"""
Backward compatibility shim for _modules.providers

This module has been migrated to medbilldozer.providers.
Imports from _modules.providers will continue to work but are deprecated.

Prefer: from medbilldozer.providers import ...
Old:    from _modules.providers import ...
"""

# Re-export everything from the new location
from medbilldozer.providers import *  # noqa: F401, F403

# Optional: Add deprecation warning
# import warnings
# warnings.warn(
#     "_modules.providers is deprecated, use medbilldozer.providers",
#     DeprecationWarning,
#     stacklevel=2
# )
