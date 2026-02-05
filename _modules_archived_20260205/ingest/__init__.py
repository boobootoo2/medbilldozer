"""
Backward compatibility shim for _modules.ingest

This module has been migrated to medbilldozer.ingest.
Imports from _modules.ingest will continue to work but are deprecated.

Prefer: from medbilldozer.ingest import ...
Old:    from _modules.ingest import ...
"""

# Re-export everything from the new location
from medbilldozer.ingest import *  # noqa: F401, F403

# Optional: Add deprecation warning
# import warnings
# warnings.warn(
#     "_modules.ingest is deprecated, use medbilldozer.ingest",
#     DeprecationWarning,
#     stacklevel=2
# )
