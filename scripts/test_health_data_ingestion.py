#!/usr/bin/env python3
"""Test script for healthcare data ingestion logic.

This script validates the import_sample_data function and related
ingestion functionality without requiring Streamlit UI.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from medbilldozer.data.fictional_entities import (
    generate_fictional_insurance_companies,
    generate_fictional_healthcare_providers,
)
from medbilldozer.data.health_data_ingestion import (
    import_sample_data,
    extract_insurance_plan_from_entity,
    extract_provider_from_entity,
    import_multiple_entities,
    generate_fake_claim_number,
    generate_fake_date,
    generate_realistic_claim_amounts,
)


def test_basic_ingestion():
    """Test basic import_sample_data functionality."""
    print("=" * 80)
    print("TEST 1: Basic Insurance Data Ingestion")
    print("=" * 80)

    # Generate a fictional insurance company
    insurance_companies = generate_fictional_insurance_companies(count=1, seed=42)
    insurance = insurance_companies[0]

    print(f"✓ Generated insurance entity: {insurance['name']}")

    # Import sample data
    import_job = import_sample_data(insurance, num_line_items=3)

    print(f"✓ Import job created: {import_job['job_id']}")
    print(f"  - Source type: {import_job['source_type']}")
    print(f"  - Source method: {import_job['source_method']}")
    print(f"  - Status: {import_job['status']}")
    print(f"  - Documents: {len(import_job['documents'])}")
    print(f"  - Line items: {len(import_job['line_items'])}")

    # Validate documents
    assert len(import_job['documents']) == 1, "Should have 1 document"
    doc = import_job['documents'][0]
    assert doc['status'] == 'extracted', "Document should be extracted"
    assert 'document_id' in doc, "Document should have ID"
    print(f"✓ Document validated: {doc['file_name']}")

    # Validate line items
    assert len(import_job['line_items']) == 3, "Should have 3 line items"
    for idx, item in enumerate(import_job['line_items'], 1):
        assert 'line_item_id' in item, "Line item should have ID"
        assert 'procedure_code' in item, "Line item should have procedure code"
        assert 'billed_amount' in item, "Line item should have billed amount"
        print(f"  Line {idx}: {item['procedure_code']} - {item['procedure_description']}")
        print(f"    Service: {item['service_date']} | Billed: ${item['billed_amount']:.2f} | Patient owes: ${item['patient_responsibility']:.2f}")

    print("✓ All line items validated\n")


def test_provider_ingestion():
    """Test provider data ingestion."""
    print("=" * 80)
    print("TEST 2: Provider Data Ingestion")
    print("=" * 80)

    # Generate a fictional provider
    providers = generate_fictional_healthcare_providers(count=1, seed=42)
    provider = providers[0]

    print(f"✓ Generated provider entity: {provider['name']}")
    print(f"  - Specialty: {provider['specialty']}")
    print(f"  - Location: {provider['location_city']}, {provider['location_state']}")

    # Import sample data
    import_job = import_sample_data(provider, num_line_items=4)

    print(f"✓ Import job created: {import_job['job_id']}")
    print(f"  - Source type: {import_job['source_type']}")
    print(f"  - Line items: {len(import_job['line_items'])}")

    # Validate line items have provider info
    for item in import_job['line_items']:
        assert item['provider_name'] == provider['name'], "Provider name should match"
        assert item['provider_npi'] is not None, "Should have NPI"

    print(f"✓ All line items have correct provider: {provider['name']}")
    print()


def test_extraction_functions():
    """Test insurance plan and provider extraction."""
    print("=" * 80)
    print("TEST 3: Extraction Functions")
    print("=" * 80)

    # Test insurance plan extraction
    insurance_companies = generate_fictional_insurance_companies(count=1, seed=42)
    insurance = insurance_companies[0]

    plan = extract_insurance_plan_from_entity(insurance)

    print(f"✓ Extracted InsurancePlan from {insurance['name']}")
    print(f"  - Plan ID: {plan['plan_id']}")
    print(f"  - Carrier: {plan['carrier_name']}")
    print(f"  - Plan Type: {plan['plan_type']}")
    print(f"  - Member ID: {plan['member_id']}")
    print(f"  - Deductible (individual): ${plan['deductible']['individual']:.0f}")
    print(f"  - Out-of-Pocket Max (individual): ${plan['out_of_pocket_max']['individual']:.0f}")
    print(f"  - Copay (primary care): ${plan['copay']['primary_care']:.0f}")

    assert 'plan_id' in plan, "Should have plan_id"
    assert 'carrier_name' in plan, "Should have carrier_name"
    assert 'deductible' in plan, "Should have deductible"
    print("✓ InsurancePlan structure validated\n")

    # Test provider extraction
    providers = generate_fictional_healthcare_providers(count=1, seed=42)
    provider_entity = providers[0]

    provider = extract_provider_from_entity(provider_entity)

    print(f"✓ Extracted Provider from {provider_entity['name']}")
    print(f"  - Provider ID: {provider['provider_id']}")
    print(f"  - Name: {provider['name']}")
    print(f"  - Specialty: {provider['specialty']}")
    print(f"  - NPI: {provider['npi']}")
    print(f"  - Tax ID: {provider['tax_id']}")
    print(f"  - In Network: {provider['in_network']}")
    print(f"  - Address: {provider['address']['city']}, {provider['address']['state']}")

    assert 'provider_id' in provider, "Should have provider_id"
    assert 'npi' in provider, "Should have NPI"
    assert 'specialty' in provider, "Should have specialty"
    print("✓ Provider structure validated\n")


def test_batch_import():
    """Test importing multiple entities."""
    print("=" * 80)
    print("TEST 4: Batch Import")
    print("=" * 80)

    # Generate multiple insurance companies
    insurance_companies = generate_fictional_insurance_companies(count=3, seed=42)

    print(f"✓ Generated {len(insurance_companies)} insurance companies")

    # Import all
    import_jobs = import_multiple_entities(insurance_companies, items_per_entity=2)

    print(f"✓ Created {len(import_jobs)} import jobs")

    total_line_items = sum(len(job['line_items']) for job in import_jobs)
    print(f"✓ Total line items across all jobs: {total_line_items}")

    assert len(import_jobs) == 3, "Should have 3 import jobs"
    assert total_line_items == 6, "Should have 6 total line items (2 per entity)"

    for idx, job in enumerate(import_jobs, 1):
        print(f"  Job {idx}: {job['source_type']} - {len(job['line_items'])} items")

    print("✓ Batch import validated\n")


def test_helper_functions():
    """Test helper utility functions."""
    print("=" * 80)
    print("TEST 5: Helper Functions")
    print("=" * 80)

    # Test claim number generation
    claim_num = generate_fake_claim_number()
    print(f"✓ Generated claim number: {claim_num}")
    assert claim_num.startswith("CLM-DEMO-"), "Claim number should have correct prefix"

    # Test date generation
    date = generate_fake_date(30)
    print(f"✓ Generated date (30 days ago): {date}")
    assert len(date) == 10, "Date should be in YYYY-MM-DD format"
    assert date.count('-') == 2, "Date should have 2 dashes"

    # Test amount generation
    amounts = generate_realistic_claim_amounts()
    print(f"✓ Generated claim amounts:")
    print(f"  - Billed: ${amounts['billed_amount']:.2f}")
    print(f"  - Allowed: ${amounts['allowed_amount']:.2f}")
    print(f"  - Paid by insurance: ${amounts['paid_by_insurance']:.2f}")
    print(f"  - Patient responsibility: ${amounts['patient_responsibility']:.2f}")

    assert amounts['allowed_amount'] <= amounts['billed_amount'], "Allowed should be <= billed"
    assert amounts['paid_by_insurance'] <= amounts['allowed_amount'], "Paid should be <= allowed"
    assert abs(amounts['patient_responsibility'] - (amounts['allowed_amount'] - amounts['paid_by_insurance'])) < 0.01, \
        "Patient responsibility should equal allowed - paid"

    print("✓ All helper functions validated\n")


def test_data_consistency():
    """Test data consistency and source marking."""
    print("=" * 80)
    print("TEST 6: Data Consistency & Source Marking")
    print("=" * 80)

    insurance_companies = generate_fictional_insurance_companies(count=1, seed=42)
    import_job = import_sample_data(insurance_companies[0])

    # Check source method
    assert import_job['source_method'] == 'demo_sample', "Source method should be 'demo_sample'"
    print(f"✓ Source method correctly set: {import_job['source_method']}")

    # Check status
    assert import_job['status'] == 'completed', "Status should be 'completed'"
    print(f"✓ Status correctly set: {import_job['status']}")

    # Check timestamps
    assert 'created_at' in import_job, "Should have created_at"
    assert 'completed_at' in import_job, "Should have completed_at"
    print(f"✓ Timestamps present: created_at, completed_at")

    # Check all line items have timestamps
    for item in import_job['line_items']:
        assert 'created_at' in item, "Line item should have created_at"
        assert 'line_item_id' in item, "Line item should have unique ID"
        assert 'import_job_id' in item, "Line item should reference job ID"
        assert item['import_job_id'] == import_job['job_id'], "Line item should reference correct job"

    print(f"✓ All {len(import_job['line_items'])} line items properly linked to job")
    print()


def run_all_tests():
    """Run all test functions."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "HEALTH DATA INGESTION TEST SUITE" + " " * 26 + "║")
    print("╚" + "=" * 78 + "╝")
    print()

    tests = [
        test_basic_ingestion,
        test_provider_ingestion,
        test_extraction_functions,
        test_batch_import,
        test_helper_functions,
        test_data_consistency,
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"✗ TEST FAILED: {e}\n")
            failed += 1
        except Exception as e:
            print(f"✗ TEST ERROR: {e}\n")
            failed += 1

    print("=" * 80)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 80)

    if failed == 0:
        print("\n🎉 ALL TESTS PASSED ✓\n")
        return 0
    else:
        print(f"\n❌ {failed} TESTS FAILED\n")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)

