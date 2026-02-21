"""Application-Level Constants.

Defines constants used across the application for data generation,
entity types, and default values.
"""

import os

# ==============================================================================
# ANALYTICS CONFIGURATION
# ==============================================================================

# Google Analytics 4 measurement ID (optional)
# Set via GA4_MEASUREMENT_ID environment variable or Streamlit secrets
# Leave unset to disable analytics
GA4_MEASUREMENT_ID = os.environ.get('GA4_MEASUREMENT_ID', None)


# ==============================================================================
# DATA GENERATION DEFAULTS
# ==============================================================================

# Default number of insurance plans to generate for fictional data
DEFAULT_INSURANCE_COUNT = 30

# Default number of healthcare providers to generate for fictional data
DEFAULT_PROVIDER_COUNT = 10000

# Default random seed for reproducible fictional data generation
DEFAULT_SEED = 42


# ==============================================================================
# ENTITY TYPE IDENTIFIERS
# ==============================================================================

# Entity type identifier for insurance plans
ENTITY_TYPE_INSURANCE = "insurance"

# Entity type identifier for healthcare providers
ENTITY_TYPE_PROVIDER = "provider"
