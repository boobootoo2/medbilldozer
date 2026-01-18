# Canonical fact schema (single source of truth)

FACT_SCHEMA = {
    "patient_name": None,
    "date_of_birth": None,
    "date_of_service": None,
    "provider_name": None,
    "facility_name": None,
    "procedure_code": None,
    "document_type": None,
}

SCHEMA_ORDER = list(FACT_SCHEMA.keys())
