"""
Backward compatibility shim for _modules.prompts

This module has been migrated to medbilldozer.prompts.
Imports from _modules.prompts will continue to work but are deprecated.

Prefer: from medbilldozer.prompts import ...
Old:    from _modules.prompts import ...
"""

# Re-export everything from the new location
from medbilldozer.prompts import *  # noqa: F401, F403

# Optional: Add deprecation warning
# import warnings
# warnings.warn(
#     "_modules.prompts is deprecated, use medbilldozer.prompts",
#     DeprecationWarning,
#     stacklevel=2
# )
