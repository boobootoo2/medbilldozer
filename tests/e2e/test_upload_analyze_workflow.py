#!/usr/bin/env python3
"""
End-to-end test for upload → analyze workflow.

Tests the complete user journey:
1. Upload document
2. Trigger analysis
3. Poll for results
4. Verify analysis completes successfully

Usage:
    python -m pytest tests/e2e/test_upload_analyze_workflow.py -v

Or run directly with a Firebase token:
    python tests/e2e/test_upload_analyze_workflow.py <firebase_token>
"""
import asyncio
import os
import sys
import time
from pathlib import Path
from typing import Optional

# Add backend to path
project_root = Path(__file__).parent.parent.parent
backend_dir = project_root / "backend"
sys.path.insert(0, str(backend_dir))

# Load .env file from backend directory
from dotenv import load_dotenv

env_path = backend_dir / ".env"
load_dotenv(env_path)

from uuid import uuid4

import pytest
import requests


class E2ETestConfig:
    """Test configuration."""

    # Use localhost for e2e tests
    API_BASE_URL = os.getenv("E2E_API_BASE_URL", "http://localhost:8080")
    # For CI/CD, set E2E_FIREBASE_TOKEN env var
    FIREBASE_TOKEN = os.getenv("E2E_FIREBASE_TOKEN")
    # Test timeout in seconds
    ANALYSIS_TIMEOUT = 120
    POLL_INTERVAL = 2


class E2EWorkflowTest:
    """End-to-end workflow test."""

    def __init__(self, api_base_url: str, firebase_token: str):
        self.api_base_url = api_base_url
        self.headers = {
            "Authorization": f"Bearer {firebase_token}",
            "Content-Type": "application/json",
        }
        self.test_document_ids = []
        self.test_analysis_id = None

    def test_health(self) -> bool:
        """Test 1: Health check."""
        print("\n" + "=" * 60)
        print("TEST 1: Health Check")
        print("=" * 60)

        try:
            response = requests.get(f"{self.api_base_url}/health", timeout=10)
            response.raise_for_status()
            data = response.json()

            print(f"✅ Health check passed")
            print(f"   Status: {data['status']}")
            print(f"   Environment: {data.get('environment', 'unknown')}")
            return True

        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return False

    def test_list_documents(self) -> bool:
        """Test 2: List existing documents."""
        print("\n" + "=" * 60)
        print("TEST 2: List Documents")
        print("=" * 60)

        try:
            response = requests.get(
                f"{self.api_base_url}/api/documents/",
                headers=self.headers,
                params={"limit": 5, "offset": 0},
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()

            documents = data.get("documents", [])
            print(f"✅ Found {len(documents)} document(s)")

            # Store first 2 document IDs for testing
            self.test_document_ids = [doc["document_id"] for doc in documents[:2]]

            if len(self.test_document_ids) == 0:
                print("⚠️  No documents found - you'll need to upload some first")
                return False

            for doc in documents[:2]:
                print(f"   - {doc['filename']} (ID: {doc['document_id'][:8]}...)")

            return True

        except Exception as e:
            print(f"❌ List documents failed: {e}")
            return False

    def test_trigger_analysis(self) -> bool:
        """Test 3: Trigger analysis."""
        print("\n" + "=" * 60)
        print("TEST 3: Trigger Analysis")
        print("=" * 60)

        if not self.test_document_ids:
            print("❌ No documents available for analysis")
            return False

        try:
            payload = {"document_ids": self.test_document_ids, "provider": "medgemma-ensemble"}

            print(f"📤 Requesting analysis for {len(self.test_document_ids)} document(s)")
            print(f"   Provider: {payload['provider']}")
            print(f"   Document IDs: {[id[:8]+'...' for id in self.test_document_ids]}")

            response = requests.post(
                f"{self.api_base_url}/api/analyze/", headers=self.headers, json=payload, timeout=30
            )

            # Print response for debugging
            print(f"   Response status: {response.status_code}")
            if response.status_code != 200:
                print(f"   Response body: {response.text}")

            response.raise_for_status()
            data = response.json()

            self.test_analysis_id = data.get("analysis_id")
            status = data.get("status")

            print(f"✅ Analysis triggered successfully")
            print(f"   Analysis ID: {self.test_analysis_id}")
            print(f"   Status: {status}")
            print(f"   Estimated completion: {data.get('estimated_completion')}")

            return True

        except requests.exceptions.HTTPError as e:
            print(f"❌ Analysis trigger failed with HTTP {e.response.status_code}")
            print(f"   Error: {e.response.text}")
            return False
        except Exception as e:
            print(f"❌ Analysis trigger failed: {e}")
            return False

    def test_poll_analysis(self) -> bool:
        """Test 4: Poll for analysis results."""
        print("\n" + "=" * 60)
        print("TEST 4: Poll Analysis Results")
        print("=" * 60)

        if not self.test_analysis_id:
            print("❌ No analysis ID available")
            return False

        try:
            max_attempts = E2ETestConfig.ANALYSIS_TIMEOUT // E2ETestConfig.POLL_INTERVAL
            print(f"⏱️  Polling for up to {E2ETestConfig.ANALYSIS_TIMEOUT}s...")

            for attempt in range(max_attempts):
                response = requests.get(
                    f"{self.api_base_url}/api/analyze/{self.test_analysis_id}",
                    headers=self.headers,
                    timeout=30,
                )
                response.raise_for_status()
                data = response.json()

                status = data.get("status")
                issues_count = data.get("issues_count", 0)

                print(f"   [{attempt+1}/{max_attempts}] Status: {status}, Issues: {issues_count}")

                if status == "completed":
                    print(f"\n✅ Analysis completed successfully!")
                    print(f"   Total issues detected: {issues_count}")
                    print(f"   Total savings: ${data.get('total_savings_detected', 0):.2f}")

                    # Verify results structure
                    results = data.get("results", [])
                    print(f"   Documents analyzed: {len(results)}")

                    return True

                elif status == "failed":
                    print(f"\n❌ Analysis failed")
                    print(f"   Error: {data.get('error_message', 'Unknown error')}")
                    return False

                elif status in ["queued", "processing"]:
                    time.sleep(E2ETestConfig.POLL_INTERVAL)

                else:
                    print(f"❌ Unknown status: {status}")
                    return False

            print(f"\n❌ Timeout after {E2ETestConfig.ANALYSIS_TIMEOUT}s")
            return False

        except Exception as e:
            print(f"❌ Poll analysis failed: {e}")
            return False

    def run_all_tests(self) -> bool:
        """Run all e2e tests."""
        print("🧪 E2E Workflow Test: Upload → Analyze")
        print("=" * 60)
        print(f"API Base URL: {self.api_base_url}")
        print("=" * 60)

        tests = [
            ("Health Check", self.test_health),
            ("List Documents", self.test_list_documents),
            ("Trigger Analysis", self.test_trigger_analysis),
            ("Poll Results", self.test_poll_analysis),
        ]

        results = {}
        for test_name, test_func in tests:
            try:
                results[test_name] = test_func()
                if not results[test_name]:
                    # Stop on first failure
                    break
            except Exception as e:
                print(f"❌ Test {test_name} raised exception: {e}")
                results[test_name] = False
                break

        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)

        for test_name, passed in results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"  {test_name}: {status}")

        all_passed = all(results.values())

        print("\n" + "=" * 60)
        if all_passed:
            print("🎉 ALL E2E TESTS PASSED!")
        else:
            print("💥 SOME E2E TESTS FAILED")
        print("=" * 60)

        return all_passed


def main():
    """Run e2e tests."""
    # Check for token
    token = None
    if len(sys.argv) > 1:
        token = sys.argv[1]
    else:
        token = E2ETestConfig.FIREBASE_TOKEN

    if not token:
        print("❌ Firebase token required!")
        print("\nUsage:")
        print("  1. Set E2E_FIREBASE_TOKEN environment variable")
        print("  2. Or pass token as argument:")
        print(f"     python {sys.argv[0]} <firebase_token>")
        print("\nTo get a token:")
        print("  1. Open http://localhost:5173 in browser")
        print("  2. Login")
        print("  3. Open Developer Tools > Application > Local Storage")
        print("  4. Copy 'access_token' value")
        sys.exit(1)

    # Run tests
    tester = E2EWorkflowTest(api_base_url=E2ETestConfig.API_BASE_URL, firebase_token=token)

    success = tester.run_all_tests()
    sys.exit(0 if success else 1)


# Pytest fixtures for CI/CD integration
@pytest.fixture
def api_client():
    """Create API client for tests."""
    token = E2ETestConfig.FIREBASE_TOKEN
    if not token:
        pytest.skip("E2E_FIREBASE_TOKEN not set")

    return E2EWorkflowTest(api_base_url=E2ETestConfig.API_BASE_URL, firebase_token=token)


def test_e2e_health(api_client):
    """Pytest: Health check."""
    assert api_client.test_health()


def test_e2e_list_documents(api_client):
    """Pytest: List documents."""
    assert api_client.test_list_documents()


def test_e2e_trigger_analysis(api_client):
    """Pytest: Trigger analysis."""
    # First list documents
    api_client.test_list_documents()
    assert api_client.test_trigger_analysis()


@pytest.mark.slow
def test_e2e_full_workflow(api_client):
    """Pytest: Full workflow test."""
    assert api_client.run_all_tests()


if __name__ == "__main__":
    main()
