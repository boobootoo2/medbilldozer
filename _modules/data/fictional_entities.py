"""Fictional Healthcare Entity Generator

This module generates deterministic fictional healthcare entities for demo purposes.
ALL entities are completely fictional and not affiliated with any real organizations.

Uses seeded randomness to ensure consistent data generation across sessions.
"""

import random
from typing import List, TypedDict
import streamlit as st


# ==============================================================================
# Type Definitions
# ==============================================================================


class HealthcareEntity(TypedDict):
    """Base type for healthcare entities."""
    id: str
    name: str
    entity_type: str  # "insurance" | "provider"
    demo_portal_html: str


class InsuranceCompany(HealthcareEntity):
    """Fictional insurance company entity."""
    entity_type: str  # Always "insurance"
    network_size: str  # "national" | "regional" | "local"
    plan_types: List[str]  # ["HMO", "PPO", "EPO", etc.]


class HealthcareProvider(HealthcareEntity):
    """Fictional healthcare provider entity."""
    entity_type: str  # Always "provider"
    specialty: str
    location_city: str
    location_state: str
    accepts_insurance: List[str]  # List of insurance company IDs


# ==============================================================================
# Data Sources (Fictional Components)
# ==============================================================================

# Fictional insurance company name components
INSURANCE_PREFIXES = [
    "American", "United", "National", "Pacific", "Atlantic", "Mountain",
    "Great Lakes", "Sunshine", "Liberty", "Eagle", "Guardian", "Premier",
    "Mutual", "Federal", "State", "Regional", "Metropolitan", "Capital",
    "Commonwealth", "Horizon", "Beacon", "Summit", "Alliance", "Trust",
    "Heritage", "Advantage", "Choice", "First", "Primary", "Select"
]

INSURANCE_ROOTS = [
    "Health", "Medical", "Care", "Life", "Shield", "Cross", "Star",
    "Benefit", "Assurance", "Security", "Wellness", "Family", "Community",
    "Partner", "Plus", "Pro", "Elite", "Prime", "Standard", "Classic"
]

INSURANCE_SUFFIXES = [
    "Group", "Corp", "Inc", "LLC", "Plan", "Network", "System",
    "Association", "Fund", "Cooperative", "Alliance", "Partners"
]

# Fictional provider specialties
PROVIDER_SPECIALTIES = [
    "Family Medicine", "Internal Medicine", "Pediatrics", "Cardiology",
    "Dermatology", "Orthopedics", "Neurology", "Psychiatry", "Oncology",
    "Radiology", "Anesthesiology", "Emergency Medicine", "Surgery",
    "Obstetrics and Gynecology", "Ophthalmology", "Otolaryngology",
    "Urology", "Gastroenterology", "Endocrinology", "Rheumatology",
    "Pulmonology", "Nephrology", "Hematology", "Infectious Disease",
    "Allergy and Immunology", "Physical Medicine", "Pathology",
    "General Practice", "Urgent Care", "Sports Medicine"
]

# Fictional provider name components
PROVIDER_FIRST_NAMES = [
    "James", "Maria", "Robert", "Jennifer", "Michael", "Linda", "William",
    "Patricia", "David", "Elizabeth", "Richard", "Susan", "Joseph", "Jessica",
    "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Nancy", "Daniel",
    "Lisa", "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra",
    "Donald", "Ashley", "Steven", "Kimberly", "Paul", "Emily", "Andrew",
    "Donna", "Joshua", "Michelle", "Kenneth", "Carol", "Kevin", "Amanda",
    "Brian", "Dorothy", "George", "Melissa", "Timothy", "Deborah", "Ronald",
    "Stephanie", "Edward", "Rebecca", "Jason", "Sharon", "Jeffrey", "Laura"
]

PROVIDER_LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
    "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
    "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark",
    "Ramirez", "Lewis", "Robinson", "Walker", "Young", "Allen", "King",
    "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores", "Green",
    "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
    "Carter", "Roberts", "Gomez", "Phillips", "Evans", "Turner", "Diaz",
    "Parker", "Cruz", "Edwards", "Collins", "Reyes", "Stewart", "Morris"
]

PROVIDER_PRACTICE_TYPES = [
    "Medical Group", "Health Center", "Clinic", "Associates", "Medical Center",
    "Healthcare", "Physicians", "Practice", "Specialists", "Care Center",
    "Medical Associates", "Health Partners", "Wellness Center", "Family Practice"
]

# US States (for provider locations)
US_STATES = [
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
]

# Fictional cities (used with states)
CITIES = [
    "Springfield", "Riverside", "Greenville", "Fairview", "Madison",
    "Georgetown", "Arlington", "Franklin", "Clinton", "Salem",
    "Oxford", "Manchester", "Bristol", "Clayton", "Milton",
    "Newport", "Ashland", "Richmond", "Brookfield", "Chester"
]


# ==============================================================================
# Insurance Company Generation
# ==============================================================================

@st.cache_data(ttl=None)


def generate_fictional_insurance_companies(count: int = 30, seed: int = 42) -> List[InsuranceCompany]:
    """Generate deterministic fictional insurance companies.

    Args:
        count: Number of insurance companies to generate (default: 30)
        seed: Random seed for deterministic generation (default: 42)

    Returns:
        List of fictional insurance company entities

    Example:
        >>> companies = generate_fictional_insurance_companies(30)
        >>> len(companies)
        30
        >>> companies[0]['entity_type']
        'insurance'
    """
    random.seed(seed)
    companies: List[InsuranceCompany] = []

    network_types = ["national", "regional", "local"]
    plan_type_options = [
        ["HMO", "PPO"],
        ["HMO", "PPO", "EPO"],
        ["PPO", "POS"],
        ["HMO"],
        ["PPO"],
        ["HMO", "PPO", "EPO", "POS"],
        ["EPO", "POS"],
        ["PPO", "HDHP"]
    ]

    for i in range(count):
        # Generate unique fictional name
        prefix = random.choice(INSURANCE_PREFIXES)
        root = random.choice(INSURANCE_ROOTS)
        suffix = random.choice(INSURANCE_SUFFIXES)

        # Occasionally skip prefix or suffix for variety
        if random.random() < 0.3:
            name = f"{root} {suffix}"
        elif random.random() < 0.3:
            name = f"{prefix} {root}"
        else:
            name = f"{prefix} {root} {suffix}"

        # Add (DEMO) suffix to make it obvious
        name = f"{name} (DEMO)"

        company_id = f"demo_ins_{i+1:03d}"

        company: InsuranceCompany = {
            "id": company_id,
            "name": name,
            "entity_type": "insurance",
            "network_size": random.choice(network_types),
            "plan_types": random.choice(plan_type_options),
            "demo_portal_html": f"""
                <div style="padding: 20px; border: 2px dashed #ccc; border-radius: 8px; background: #f9f9f9;">
                    <h3>🛡️ {name}</h3>
                    <p><strong>Portal Type:</strong> Insurance Company Demo</p>
                    <p><strong>Network:</strong> {random.choice(network_types).title()}</p>
                    <p><em>⚠️ DEMO ONLY - Fictional insurance company for educational purposes</em></p>
                    <p style="font-size: 12px; color: #666;">
                        This is a simulated connection. No real credentials or PHI are transmitted.
                    </p>
                </div>
            """
        }

        companies.append(company)

    # Reset seed to avoid affecting other random operations
    random.seed()

    return companies


# ==============================================================================
# Healthcare Provider Generation
# ==============================================================================

@st.cache_data(ttl=None)


def generate_fictional_healthcare_providers(
    count: int = 10000,
    seed: int = 42,
    insurance_company_ids: List[str] = None
) -> List[HealthcareProvider]:
    """Generate deterministic fictional healthcare providers.

    Args:
        count: Number of providers to generate (default: 10,000)
        seed: Random seed for deterministic generation (default: 42)
        insurance_company_ids: List of insurance company IDs to randomly assign

    Returns:
        List of fictional healthcare provider entities

    Example:
        >>> providers = generate_fictional_healthcare_providers(100)
        >>> len(providers)
        100
        >>> providers[0]['entity_type']
        'provider'
    """
    random.seed(seed)
    providers: List[HealthcareProvider] = []

    # Default insurance IDs if none provided
    if insurance_company_ids is None:
        insurance_company_ids = [f"demo_ins_{i+1:03d}" for i in range(30)]

    for i in range(count):
        # Generate provider name (Dr. FirstName LastName format or Practice name)
        if random.random() < 0.7:
            # Individual provider: Dr. FirstName LastName
            first_name = random.choice(PROVIDER_FIRST_NAMES)
            last_name = random.choice(PROVIDER_LAST_NAMES)
            provider_name = f"Dr. {first_name} {last_name}"
        else:
            # Group practice: LastName + Practice Type
            last_name = random.choice(PROVIDER_LAST_NAMES)
            practice_type = random.choice(PROVIDER_PRACTICE_TYPES)
            provider_name = f"{last_name} {practice_type}"

        # Add (DEMO) suffix
        provider_name = f"{provider_name} (DEMO)"

        provider_id = f"demo_prov_{i+1:06d}"
        specialty = random.choice(PROVIDER_SPECIALTIES)
        city = random.choice(CITIES)
        state = random.choice(US_STATES)

        # Randomly assign 1-5 insurance networks
        num_insurances = random.randint(1, 5)
        accepted_insurances = random.sample(
            insurance_company_ids,
            min(num_insurances, len(insurance_company_ids))
        )

        provider: HealthcareProvider = {
            "id": provider_id,
            "name": provider_name,
            "entity_type": "provider",
            "specialty": specialty,
            "location_city": city,
            "location_state": state,
            "accepts_insurance": accepted_insurances,
            "demo_portal_html": f"""
                <div style="padding: 20px; border: 2px dashed #ccc; border-radius: 8px; background: #f9f9f9;">
                    <h3>🏥 {provider_name}</h3>
                    <p><strong>Specialty:</strong> {specialty}</p>
                    <p><strong>Location:</strong> {city}, {state}</p>
                    <p><strong>Accepts:</strong> {len(accepted_insurances)} insurance networks</p>
                    <p><em>⚠️ DEMO ONLY - Fictional provider for educational purposes</em></p>
                    <p style="font-size: 12px; color: #666;">
                        This is a simulated connection. No real credentials or PHI are transmitted.
                    </p>
                </div>
            """
        }

        providers.append(provider)

    # Reset seed to avoid affecting other random operations
    random.seed()

    return providers


# ==============================================================================
# Utility Functions
# ==============================================================================

@st.cache_data(ttl=None)


def get_all_fictional_entities(
    insurance_count: int = 30,
    provider_count: int = 10000,
    seed: int = 42
) -> dict:
    """Generate all fictional entities in one call.

    Args:
        insurance_count: Number of insurance companies (default: 30)
        provider_count: Number of healthcare providers (default: 10,000)
        seed: Random seed for deterministic generation (default: 42)

    Returns:
        Dictionary with 'insurance' and 'providers' keys

    Example:
        >>> entities = get_all_fictional_entities(30, 100)
        >>> len(entities['insurance'])
        30
        >>> len(entities['providers'])
        100
    """
    # Generate insurance companies first
    insurance_companies = generate_fictional_insurance_companies(insurance_count, seed)

    # Extract IDs for provider generation
    insurance_ids = [company['id'] for company in insurance_companies]

    # Generate providers with insurance network assignments
    providers = generate_fictional_healthcare_providers(
        provider_count,
        seed,
        insurance_ids
    )

    return {
        'insurance': insurance_companies,
        'providers': providers
    }


def get_entity_by_id(entity_id: str, entities: List[HealthcareEntity]) -> HealthcareEntity | None:
    """Find an entity by ID.

    Args:
        entity_id: The entity ID to search for
        entities: List of entities to search in

    Returns:
        Entity dict if found, None otherwise

    Example:
        >>> companies = generate_fictional_insurance_companies(30)
        >>> entity = get_entity_by_id('demo_ins_001', companies)
        >>> entity['entity_type']
        'insurance'
    """
    for entity in entities:
        if entity['id'] == entity_id:
            return entity
    return None


def filter_providers_by_specialty(
    providers: List[HealthcareProvider],
    specialty: str
) -> List[HealthcareProvider]:
    """Filter providers by specialty.

    Args:
        providers: List of provider entities
        specialty: Specialty to filter by

    Returns:
        Filtered list of providers

    Example:
        >>> providers = generate_fictional_healthcare_providers(1000)
        >>> cardiologists = filter_providers_by_specialty(providers, 'Cardiology')
        >>> all(p['specialty'] == 'Cardiology' for p in cardiologists)
        True
    """
    return [p for p in providers if p['specialty'] == specialty]


def filter_providers_by_insurance(
    providers: List[HealthcareProvider],
    insurance_id: str
) -> List[HealthcareProvider]:
    """Filter providers by accepted insurance.

    Args:
        providers: List of provider entities
        insurance_id: Insurance company ID to filter by

    Returns:
        Filtered list of providers that accept this insurance

    Example:
        >>> entities = get_all_fictional_entities(30, 1000)
        >>> in_network = filter_providers_by_insurance(
        ...     entities['providers'],
        ...     'demo_ins_001'
        ... )
        >>> all('demo_ins_001' in p['accepts_insurance'] for p in in_network)
        True
    """
    return [p for p in providers if insurance_id in p['accepts_insurance']]


def get_entity_stats(entities: dict) -> dict:
    """Calculate statistics about generated entities.

    Args:
        entities: Dictionary from get_all_fictional_entities()

    Returns:
        Dictionary with statistics

    Example:
        >>> entities = get_all_fictional_entities(30, 1000)
        >>> stats = get_entity_stats(entities)
        >>> stats['total_insurance_companies']
        30
        >>> stats['total_providers']
        1000
    """
    providers = entities['providers']
    insurance = entities['insurance']

    # Count providers by specialty
    specialty_counts = {}
    for provider in providers:
        spec = provider['specialty']
        specialty_counts[spec] = specialty_counts.get(spec, 0) + 1

    # Count providers by state
    state_counts = {}
    for provider in providers:
        state = provider['location_state']
        state_counts[state] = state_counts.get(state, 0) + 1

    return {
        'total_insurance_companies': len(insurance),
        'total_providers': len(providers),
        'unique_specialties': len(specialty_counts),
        'specialty_distribution': specialty_counts,
        'state_distribution': state_counts,
        'avg_insurances_per_provider': sum(
            len(p['accepts_insurance']) for p in providers
        ) / len(providers) if providers else 0
    }


# ==============================================================================
# Validation
# ==============================================================================


def validate_entity_uniqueness(entities: List[HealthcareEntity]) -> bool:
    """Validate that all entity IDs are unique.

    Args:
        entities: List of entities to validate

    Returns:
        True if all IDs are unique, False otherwise
    """
    ids = [e['id'] for e in entities]
    return len(ids) == len(set(ids))


def validate_entity_structure(entity: HealthcareEntity) -> bool:
    """Validate that an entity has required fields.

    Args:
        entity: Entity to validate

    Returns:
        True if entity is valid, False otherwise
    """
    required_fields = ['id', 'name', 'entity_type', 'demo_portal_html']
    return all(field in entity for field in required_fields)


# ==============================================================================
# Constants for External Use
# ==============================================================================

# Default generation parameters
DEFAULT_INSURANCE_COUNT = 30
DEFAULT_PROVIDER_COUNT = 10000
DEFAULT_SEED = 42

# Entity type constants
ENTITY_TYPE_INSURANCE = "insurance"
ENTITY_TYPE_PROVIDER = "provider"

# Available specialties (for UI filters)
AVAILABLE_SPECIALTIES = sorted(PROVIDER_SPECIALTIES)

# Available states (for UI filters)
AVAILABLE_STATES = sorted(US_STATES)

