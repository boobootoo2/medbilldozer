#!/usr/bin/env python3
"""Test suite for ingestion API.

Tests the programmatic API interface for healthcare data ingestion.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from _modules.ingest.api import (
    ingest_document,
    list_imports,
    get_normalized_data,
    get_import_status,
    clear_storage,
    get_storage_stats,
    IngestRequest,
)


def test_ingest_document():
    """Test document ingestion via API."""
    print("=" * 80)
    print("TEST 1: Document Ingestion API")
    print("=" * 80)

    # Clear storage first
    clear_storage()

    # Create payload
    payload = {
        "user_id": "demo_user_123",
        "entity_type": "insurance",
        "entity_id": "demo_ins_001",
        "metadata": {
            "source": "web_app",
            "ip_address": "192.168.1.1"
        },
        "num_line_items": 5
    }

    print(f"✓ Created payload for user: {payload['user_id']}")
    print(f"  Entity: {payload['entity_type']} - {payload['entity_id']}")

    # Ingest document
    response = ingest_document(payload)

    print(f"✓ Ingestion response:")
    print(f"  Success: {response.success}")
    print(f"  Job ID: {response.job_id}")
    print(f"  Message: {response.message}")
    print(f"  Documents created: {response.documents_created}")
    print(f"  Line items created: {response.line_items_created}")

    assert response.success, "Ingestion should succeed"
    assert response.job_id, "Should have job ID"
    assert response.documents_created == 1, "Should create 1 document"
    assert response.line_items_created == 5, "Should create 5 line items"
    assert len(response.errors) == 0, "Should have no errors"

    print("✓ All assertions passed\n")
    return response.job_id


def test_list_imports():
    """Test listing imports for a user."""
    print("=" * 80)
    print("TEST 2: List Imports API")
    print("=" * 80)

    # Clear and create test data
    clear_storage()

    user_id = "demo_user_456"

    # Create multiple imports
    payloads = [
        {"user_id": user_id, "entity_type": "insurance", "entity_id": "demo_ins_001"},
        {"user_id": user_id, "entity_type": "insurance", "entity_id": "demo_ins_002"},
        {"user_id": user_id, "entity_type": "provider", "entity_id": "demo_prov_000001"},
    ]

    for payload in payloads:
        response = ingest_document(payload)
        assert response.success, f"Ingestion should succeed for {payload['entity_id']}"

    print(f"✓ Created {len(payloads)} import jobs")

    # List imports
    list_response = list_imports(user_id)

    print(f"✓ List imports response:")
    print(f"  Success: {list_response.success}")
    print(f"  User ID: {list_response.user_id}")
    print(f"  Total imports: {list_response.total_imports}")

    assert list_response.success, "List should succeed"
    assert list_response.total_imports == 3, "Should have 3 imports"
    assert len(list_response.imports) == 3, "Should return 3 import summaries"

    # Check import summaries
    for idx, import_summary in enumerate(list_response.imports, 1):
        print(f"\n  Import {idx}:")
        print(f"    Job ID: {import_summary.job_id}")
        print(f"    Entity: {import_summary.entity_name}")
        print(f"    Type: {import_summary.entity_type}")
        print(f"    Status: {import_summary.status}")
        print(f"    Line items: {import_summary.line_items_count}")

        assert import_summary.status == "completed", "Status should be completed"
        assert import_summary.line_items_count > 0, "Should have line items"

    print("\n✓ All assertions passed\n")


def test_get_normalized_data():
    """Test retrieving normalized data."""
    print("=" * 80)
    print("TEST 3: Get Normalized Data API")
    print("=" * 80)

    # Clear and create test data
    clear_storage()

    user_id = "demo_user_789"

    # Create imports
    ingest_document({
        "user_id": user_id,
        "entity_type": "insurance",
        "entity_id": "demo_ins_001",
        "num_line_items": 3
    })

    ingest_document({
        "user_id": user_id,
        "entity_type": "provider",
        "entity_id": "demo_prov_000001",
        "num_line_items": 2
    })

    print(f"✓ Created 2 import jobs for user {user_id}")

    # Get all normalized data
    data_response = get_normalized_data(user_id)

    print(f"✓ Normalized data response:")
    print(f"  Success: {data_response.success}")
    print(f"  User ID: {data_response.user_id}")
    print(f"  Total line items: {data_response.total_line_items}")

    assert data_response.success, "Get data should succeed"
    assert data_response.total_line_items == 5, "Should have 5 total line items (3+2)"
    assert len(data_response.line_items) == 5, "Should return 5 line items"

    # Check metadata
    metadata = data_response.metadata
    print(f"\n  Metadata:")
    print(f"    Total billed: ${metadata['total_billed_amount']:.2f}")
    print(f"    Patient responsibility: ${metadata['total_patient_responsibility']:.2f}")
    print(f"    Unique providers: {metadata['unique_providers']}")
    print(f"    Unique procedures: {metadata['unique_procedure_codes']}")
    print(f"    Date range: {metadata['date_range']['earliest']} to {metadata['date_range']['latest']}")

    assert metadata['total_billed_amount'] > 0, "Should have billed amount"
    assert metadata['unique_providers'] > 0, "Should have providers"
    assert metadata['unique_procedure_codes'] > 0, "Should have procedures"

    # Check line item structure
    print(f"\n  Sample line item:")
    sample = data_response.line_items[0]
    print(f"    Service date: {sample['service_date']}")
    print(f"    Procedure: {sample['procedure_code']} - {sample['procedure_description']}")
    print(f"    Provider: {sample['provider_name']}")
    print(f"    Billed: ${sample['billed_amount']:.2f}")
    print(f"    Patient owes: ${sample['patient_responsibility']:.2f}")

    assert 'service_date' in sample, "Should have service_date"
    assert 'procedure_code' in sample, "Should have procedure_code"
    assert 'billed_amount' in sample, "Should have billed_amount"

    print("\n✓ All assertions passed\n")


def test_get_import_status():
    """Test getting status of specific import job."""
    print("=" * 80)
    print("TEST 4: Get Import Status API")
    print("=" * 80)

    # Clear and create test data
    clear_storage()

    # Create import
    ingest_response = ingest_document({
        "user_id": "demo_user_status",
        "entity_type": "insurance",
        "entity_id": "demo_ins_001",
        "num_line_items": 4
    })

    job_id = ingest_response.job_id
    print(f"✓ Created import job: {job_id}")

    # Get status
    status_response = get_import_status(job_id)

    print(f"✓ Import status response:")
    print(f"  Success: {status_response.success}")
    print(f"  Job ID: {status_response.job_id}")
    print(f"  Status: {status_response.status}")

    assert status_response.success, "Get status should succeed"
    assert status_response.status == "completed", "Status should be completed"
    assert status_response.import_job is not None, "Should have import job data"

    # Check job data
    job_data = status_response.import_job
    print(f"\n  Job details:")
    print(f"    Entity: {job_data['entity_name']}")
    print(f"    Source type: {job_data['source_type']}")
    print(f"    Documents: {job_data['documents_count']}")
    print(f"    Line items: {job_data['line_items_count']}")
    print(f"    Created: {job_data['created_at']}")

    assert job_data['documents_count'] == 1, "Should have 1 document"
    assert job_data['line_items_count'] == 4, "Should have 4 line items"
    assert job_data['source_method'] == 'demo_sample', "Source should be demo_sample"

    print("\n✓ All assertions passed\n")


def test_invalid_requests():
    """Test validation and error handling."""
    print("=" * 80)
    print("TEST 5: Validation & Error Handling")
    print("=" * 80)

    clear_storage()

    # Test 1: Missing required field
    print("Test 5a: Missing required field")
    response = ingest_document({
        "user_id": "test_user",
        "entity_type": "insurance"
        # Missing entity_id
    })

    assert not response.success, "Should fail with missing field"
    assert len(response.errors) > 0, "Should have error messages"
    print(f"✓ Correctly rejected: {response.errors[0]}")

    # Test 2: Invalid entity type
    print("\nTest 5b: Invalid entity type")
    response = ingest_document({
        "user_id": "test_user",
        "entity_type": "invalid_type",
        "entity_id": "demo_ins_001"
    })

    assert not response.success, "Should fail with invalid entity type"
    print(f"✓ Correctly rejected: {response.errors[0]}")

    # Test 3: Entity not found
    print("\nTest 5c: Entity not found")
    response = ingest_document({
        "user_id": "test_user",
        "entity_type": "insurance",
        "entity_id": "nonexistent_entity"
    })

    assert not response.success, "Should fail with entity not found"
    print(f"✓ Correctly rejected: {response.message}")

    # Test 4: Import status not found
    print("\nTest 5d: Import status not found")
    status_response = get_import_status("nonexistent_job_id")

    assert not status_response.success, "Should fail with job not found"
    assert status_response.error_message, "Should have error message"
    print(f"✓ Correctly rejected: {status_response.error_message}")

    print("\n✓ All validation tests passed\n")


def test_storage_isolation():
    """Test that user data is properly isolated."""
    print("=" * 80)
    print("TEST 6: Storage Isolation & Multi-User")
    print("=" * 80)

    clear_storage()

    # Create imports for multiple users
    users = ["user_a", "user_b", "user_c"]

    for user_id in users:
        ingest_document({
            "user_id": user_id,
            "entity_type": "insurance",
            "entity_id": "demo_ins_001",
            "num_line_items": 2
        })

    print(f"✓ Created imports for {len(users)} users")

    # Verify each user sees only their data
    for user_id in users:
        list_response = list_imports(user_id)
        assert list_response.total_imports == 1, f"User {user_id} should have 1 import"

        data_response = get_normalized_data(user_id)
        assert data_response.total_line_items == 2, f"User {user_id} should have 2 line items"

        print(f"✓ User {user_id}: {list_response.total_imports} import(s), {data_response.total_line_items} line item(s)")

    # Check storage stats
    stats = get_storage_stats()
    print(f"\n✓ Storage statistics:")
    print(f"  Total users: {stats['total_users']}")
    print(f"  Total jobs: {stats['total_import_jobs']}")
    print(f"  Users: {', '.join(stats['users'])}")

    assert stats['total_users'] == 3, "Should have 3 users"
    assert stats['total_import_jobs'] == 3, "Should have 3 jobs"

    print("\n✓ All isolation tests passed\n")


def test_filtered_queries():
    """Test filtered queries (by job_id)."""
    print("=" * 80)
    print("TEST 7: Filtered Queries")
    print("=" * 80)

    clear_storage()

    user_id = "demo_user_filter"

    # Create multiple imports
    job1_response = ingest_document({
        "user_id": user_id,
        "entity_type": "insurance",
        "entity_id": "demo_ins_001",
        "num_line_items": 3
    })

    job2_response = ingest_document({
        "user_id": user_id,
        "entity_type": "insurance",
        "entity_id": "demo_ins_002",
        "num_line_items": 5
    })

    job1_id = job1_response.job_id
    job2_id = job2_response.job_id

    print(f"✓ Created 2 import jobs")
    print(f"  Job 1: {job1_id} (3 items)")
    print(f"  Job 2: {job2_id} (5 items)")

    # Get all data
    all_data = get_normalized_data(user_id)
    print(f"\n✓ All data: {all_data.total_line_items} line items")
    assert all_data.total_line_items == 8, "Should have 8 total line items"

    # Get filtered data
    job1_data = get_normalized_data(user_id, job_id=job1_id)
    print(f"✓ Job 1 data: {job1_data.total_line_items} line items")
    assert job1_data.total_line_items == 3, "Should have 3 line items for job 1"

    job2_data = get_normalized_data(user_id, job_id=job2_id)
    print(f"✓ Job 2 data: {job2_data.total_line_items} line items")
    assert job2_data.total_line_items == 5, "Should have 5 line items for job 2"

    # Verify all items in filtered response belong to correct job
    for item in job1_data.line_items:
        assert item['import_job_id'] == job1_id, "Item should belong to job 1"

    print("\n✓ All filtered query tests passed\n")


def run_all_tests():
    """Run all test functions."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 25 + "INGESTION API TEST SUITE" + " " * 29 + "║")
    print("╚" + "=" * 78 + "╝")
    print()

    tests = [
        test_ingest_document,
        test_list_imports,
        test_get_normalized_data,
        test_get_import_status,
        test_invalid_requests,
        test_storage_isolation,
        test_filtered_queries,
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
            import traceback
            traceback.print_exc()
            failed += 1

    print("=" * 80)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 80)

    if failed == 0:
        print("\n🎉 ALL TESTS PASSED ✓\n")
        print("API is ready for use!")
        print("\nNext steps:")
        print("  1. Use these functions in your application")
        print("  2. Add FastAPI wrapper for REST API deployment")
        print("  3. Replace in-memory storage with database")
        print("  4. Add authentication and rate limiting")
        return 0
    else:
        print(f"\n❌ {failed} TESTS FAILED\n")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)

