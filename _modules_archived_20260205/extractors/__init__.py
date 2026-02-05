"""
Backward compatibility shim for _modules.extractors

This module has been migrated to medbilldozer.extractors.
Imports from _modules.extractors will continue to work but are deprecated.

Prefer: from medbilldozer.extractors import ...
Old:    from _modules.extractors import ...
"""

# Re-export everything from the new location
from medbilldozer.extractors import *  # noqa: F401, F403

# Optional: Add deprecation warning
# import warnings
# warnings.warn(
#     "_modules.extractors is deprecated, use medbilldozer.extractors",
#     DeprecationWarning,
#     stacklevel=2
# )
