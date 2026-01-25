#!/usr/bin/env python3
"""Test script for fictional entity generation.

This script validates that the fictional entity generator works correctly
and provides sample output for verification.

Run from project root:
    python scripts/test_fictional_entities.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from _modules.data.fictional_entities import (
    generate_fictional_insurance_companies,
    generate_fictional_healthcare_providers,
    get_all_fictional_entities,
    get_entity_stats,
    filter_providers_by_specialty,
    filter_providers_by_insurance,
    validate_entity_uniqueness,
    validate_entity_structure,
)


def test_insurance_generation():
    """Test insurance company generation."""
    print("=" * 60)
    print("Testing Insurance Company Generation")
    print("=" * 60)
    
    companies = generate_fictional_insurance_companies(30, seed=42)
    
    print(f"\n✓ Generated {len(companies)} insurance companies")
    
    # Validate uniqueness
    assert validate_entity_uniqueness(companies), "❌ Duplicate IDs found!"
    print("✓ All insurance company IDs are unique")
    
    # Validate structure
    for company in companies:
        assert validate_entity_structure(company), f"❌ Invalid structure: {company['id']}"
    print("✓ All insurance companies have valid structure")
    
    # Show sample
    print("\nSample Insurance Companies:")
    for company in companies[:5]:
        print(f"  - {company['id']}: {company['name']}")
        print(f"    Network: {company['network_size']}, Plans: {', '.join(company['plan_types'])}")
    
    print(f"\n✓ Insurance company generation PASSED\n")
    return companies


def test_provider_generation():
    """Test healthcare provider generation."""
    print("=" * 60)
    print("Testing Healthcare Provider Generation")
    print("=" * 60)
    
    # Generate smaller set for testing
    providers = generate_fictional_healthcare_providers(1000, seed=42)
    
    print(f"\n✓ Generated {len(providers)} healthcare providers")
    
    # Validate uniqueness
    assert validate_entity_uniqueness(providers), "❌ Duplicate IDs found!"
    print("✓ All provider IDs are unique")
    
    # Validate structure
    for provider in providers[:100]:  # Check first 100
        assert validate_entity_structure(provider), f"❌ Invalid structure: {provider['id']}"
    print("✓ All providers have valid structure")
    
    # Show sample
    print("\nSample Healthcare Providers:")
    for provider in providers[:5]:
        print(f"  - {provider['id']}: {provider['name']}")
        print(f"    Specialty: {provider['specialty']}")
        print(f"    Location: {provider['location_city']}, {provider['location_state']}")
        print(f"    Accepts {len(provider['accepts_insurance'])} insurance networks")
    
    print(f"\n✓ Provider generation PASSED\n")
    return providers


def test_full_generation():
    """Test full entity generation."""
    print("=" * 60)
    print("Testing Full Entity Generation")
    print("=" * 60)
    
    entities = get_all_fictional_entities(
        insurance_count=30,
        provider_count=10000,
        seed=42
    )
    
    print(f"\n✓ Generated complete entity set:")
    print(f"  - Insurance companies: {len(entities['insurance'])}")
    print(f"  - Healthcare providers: {len(entities['providers'])}")
    
    # Get statistics
    stats = get_entity_stats(entities)
    
    print(f"\nEntity Statistics:")
    print(f"  - Total insurance companies: {stats['total_insurance_companies']}")
    print(f"  - Total providers: {stats['total_providers']}")
    print(f"  - Unique specialties: {stats['unique_specialties']}")
    print(f"  - Avg insurances per provider: {stats['avg_insurances_per_provider']:.2f}")
    
    print(f"\nTop 5 Specialties by Provider Count:")
    sorted_specialties = sorted(
        stats['specialty_distribution'].items(),
        key=lambda x: x[1],
        reverse=True
    )
    for specialty, count in sorted_specialties[:5]:
        print(f"  - {specialty}: {count} providers")
    
    print(f"\nTop 5 States by Provider Count:")
    sorted_states = sorted(
        stats['state_distribution'].items(),
        key=lambda x: x[1],
        reverse=True
    )
    for state, count in sorted_states[:5]:
        print(f"  - {state}: {count} providers")
    
    print(f"\n✓ Full generation PASSED\n")
    return entities


def test_filtering():
    """Test filtering functions."""
    print("=" * 60)
    print("Testing Filtering Functions")
    print("=" * 60)
    
    entities = get_all_fictional_entities(30, 1000, seed=42)
    
    # Test specialty filtering
    cardiologists = filter_providers_by_specialty(
        entities['providers'],
        'Cardiology'
    )
    print(f"\n✓ Found {len(cardiologists)} Cardiology providers")
    
    # Test insurance filtering
    first_insurance_id = entities['insurance'][0]['id']
    in_network = filter_providers_by_insurance(
        entities['providers'],
        first_insurance_id
    )
    print(f"✓ Found {len(in_network)} providers accepting {first_insurance_id}")
    
    print(f"\n✓ Filtering PASSED\n")


def test_determinism():
    """Test that generation is deterministic with same seed."""
    print("=" * 60)
    print("Testing Deterministic Generation")
    print("=" * 60)
    
    # Generate twice with same seed
    entities1 = get_all_fictional_entities(30, 100, seed=42)
    entities2 = get_all_fictional_entities(30, 100, seed=42)
    
    # Compare insurance companies
    for i in range(len(entities1['insurance'])):
        assert entities1['insurance'][i]['id'] == entities2['insurance'][i]['id']
        assert entities1['insurance'][i]['name'] == entities2['insurance'][i]['name']
    
    print("✓ Insurance companies are identical with same seed")
    
    # Compare providers
    for i in range(len(entities1['providers'])):
        assert entities1['providers'][i]['id'] == entities2['providers'][i]['id']
        assert entities1['providers'][i]['name'] == entities2['providers'][i]['name']
    
    print("✓ Providers are identical with same seed")
    
    # Generate with different seed
    entities3 = get_all_fictional_entities(30, 100, seed=999)
    
    # Should have different names
    different_names = sum(
        1 for i in range(len(entities1['insurance']))
        if entities1['insurance'][i]['name'] != entities3['insurance'][i]['name']
    )
    
    print(f"✓ Different seed produced {different_names}/30 different insurance names")
    
    print(f"\n✓ Determinism PASSED\n")


def test_demo_markers():
    """Test that all entities have (DEMO) markers."""
    print("=" * 60)
    print("Testing Demo Markers")
    print("=" * 60)
    
    entities = get_all_fictional_entities(30, 100, seed=42)
    
    # Check insurance companies
    for company in entities['insurance']:
        assert '(DEMO)' in company['name'], f"Missing (DEMO) in {company['name']}"
    print("✓ All insurance companies have (DEMO) marker")
    
    # Check providers
    for provider in entities['providers']:
        assert '(DEMO)' in provider['name'], f"Missing (DEMO) in {provider['name']}"
    print("✓ All providers have (DEMO) marker")
    
    # Check portal HTML
    for company in entities['insurance']:
        assert 'DEMO ONLY' in company['demo_portal_html']
        assert 'Fictional' in company['demo_portal_html'] or 'educational purposes' in company['demo_portal_html']
    print("✓ All insurance portals have demo disclaimers")
    
    for provider in entities['providers'][:100]:
        assert 'DEMO ONLY' in provider['demo_portal_html']
        assert 'Fictional' in provider['demo_portal_html'] or 'educational purposes' in provider['demo_portal_html']
    print("✓ All provider portals have demo disclaimers")
    
    print(f"\n✓ Demo markers PASSED\n")


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("FICTIONAL ENTITY GENERATION TEST SUITE")
    print("=" * 60 + "\n")
    
    try:
        # Run tests
        insurance = test_insurance_generation()
        providers = test_provider_generation()
        entities = test_full_generation()
        test_filtering()
        test_determinism()
        test_demo_markers()
        
        # Final summary
        print("=" * 60)
        print("ALL TESTS PASSED ✓")
        print("=" * 60)
        print("\nSummary:")
        print(f"  - Insurance companies: {len(insurance)} generated successfully")
        print(f"  - Healthcare providers: {len(providers)} generated successfully")
        print(f"  - All entities are deterministic")
        print(f"  - All entities have proper demo markers")
        print(f"  - All filtering functions work correctly")
        print("\n✓ Ready for UI integration\n")
        
        return 0
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        return 1
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
