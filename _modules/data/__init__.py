"""Data generation and management modules.

This package contains modules for generating fictional healthcare data
for demo and educational purposes.
"""

from .fictional_entities import (
    # Type definitions
    HealthcareEntity,
    InsuranceCompany,
    HealthcareProvider,
    
    # Main generation functions
    generate_fictional_insurance_companies,
    generate_fictional_healthcare_providers,
    get_all_fictional_entities,
    
    # Utility functions
    get_entity_by_id,
    filter_providers_by_specialty,
    filter_providers_by_insurance,
    get_entity_stats,
    
    # Validation
    validate_entity_uniqueness,
    validate_entity_structure,
    
    # Constants
    DEFAULT_INSURANCE_COUNT,
    DEFAULT_PROVIDER_COUNT,
    DEFAULT_SEED,
    ENTITY_TYPE_INSURANCE,
    ENTITY_TYPE_PROVIDER,
    AVAILABLE_SPECIALTIES,
    AVAILABLE_STATES,
)

from .health_data_ingestion import (
    # Main ingestion function
    import_sample_data,
    
    # Extraction functions
    extract_insurance_plan_from_entity,
    extract_provider_from_entity,
    
    # Batch functions
    import_multiple_entities,
    
    # Storage helper
    store_import_job_in_session,
    
    # Generator functions
    generate_fake_document,
    generate_line_items_from_insurance,
    generate_line_items_from_provider,
    
    # Utilities
    generate_fake_claim_number,
    generate_fake_date,
    generate_realistic_claim_amounts,
)

from .portal_templates import (
    # Portal HTML generators
    generate_insurance_portal_html,
    generate_provider_portal_html,
    generate_pharmacy_portal_html,
)

__all__ = [
    # Types
    'HealthcareEntity',
    'InsuranceCompany',
    'HealthcareProvider',
    
    # Fictional entity generation
    'generate_fictional_insurance_companies',
    'generate_fictional_healthcare_providers',
    'get_all_fictional_entities',
    'get_entity_by_id',
    'filter_providers_by_specialty',
    'filter_providers_by_insurance',
    'get_entity_stats',
    'validate_entity_uniqueness',
    'validate_entity_structure',
    
    # Data ingestion
    'import_sample_data',
    'extract_insurance_plan_from_entity',
    'extract_provider_from_entity',
    'import_multiple_entities',
    'store_import_job_in_session',
    'generate_fake_document',
    'generate_line_items_from_insurance',
    'generate_line_items_from_provider',
    'generate_fake_claim_number',
    'generate_fake_date',
    'generate_realistic_claim_amounts',
    
    # Portal templates
    'generate_insurance_portal_html',
    'generate_provider_portal_html',
    'generate_pharmacy_portal_html',
    
    # Constants
    'DEFAULT_INSURANCE_COUNT',
    'DEFAULT_PROVIDER_COUNT',
    'DEFAULT_SEED',
    'ENTITY_TYPE_INSURANCE',
    'ENTITY_TYPE_PROVIDER',
    'AVAILABLE_SPECIALTIES',
    'AVAILABLE_STATES',
]
