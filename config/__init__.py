"""Configuration package for MedBillDozer.

Centralizes all application configuration constants, widget settings,
and feature flags.
"""

from .widget_config import (
    BILLDOZER_TOKEN,
    WIDGET_HEIGHT,
    WIDGET_SCROLLING,
)

from .constants import (
    # Data generation defaults
    DEFAULT_INSURANCE_COUNT,
    DEFAULT_PROVIDER_COUNT,
    DEFAULT_SEED,
    
    # Entity types
    ENTITY_TYPE_INSURANCE,
    ENTITY_TYPE_PROVIDER,
)

__all__ = [
    # Widget configuration
    'BILLDOZER_TOKEN',
    'WIDGET_HEIGHT',
    'WIDGET_SCROLLING',
    
    # Constants
    'DEFAULT_INSURANCE_COUNT',
    'DEFAULT_PROVIDER_COUNT',
    'DEFAULT_SEED',
    'ENTITY_TYPE_INSURANCE',
    'ENTITY_TYPE_PROVIDER',
]
