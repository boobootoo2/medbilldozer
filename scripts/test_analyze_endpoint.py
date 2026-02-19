#!/usr/bin/env python3
"""Test analyze endpoint to identify failure point."""
import requests
import time
import json
import sys

# Configuration - Updated after deployment revision medbilldozer-api-00021-8p9
API_BASE_URL = "https://medbilldozer-api-360553024921.us-central1.run.app"
# Get token from command line or use existing one
# You can get this from your browser's Network tab after logging in

def test_step(step_name, func):
    """Run a test step and report results."""
    print(f"\n{'='*60}")
    print(f"STEP: {step_name}")
    print('='*60)
    try:
        result = func()
        print(f"✅ PASSED")
        return True, result
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False, None


def main():
    if len(sys.argv) < 2:
        print("Usage: python test_analyze_endpoint.py <your_jwt_token>")
        print("\nGet your token from:")
        print("1. Open https://medbilldozer.vercel.app/ in browser")
        print("2. Login")
        print("3. Open Developer Tools > Network tab")
        print("4. Look at any API request's Authorization header")
        print("5. Copy the token after 'Bearer '")
        sys.exit(1)

    token = sys.argv[1]
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Step 1: List documents (known to work)
    def test_list_documents():
        response = requests.get(
            f"{API_BASE_URL}/api/documents/?limit=50&offset=0",
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        print(f"Found {data['total']} documents")
        if data['total'] == 0:
            raise Exception("No documents found - upload some first!")
        return data['documents']

    success, documents = test_step("List Documents (Baseline)", test_list_documents)
    if not success or not documents:
        print("\n❌ Cannot proceed - no documents available")
        sys.exit(1)

    # Use first 2 documents for testing
    doc_ids = [doc['document_id'] for doc in documents[:2]]
    print(f"\nUsing documents: {doc_ids}")

    # Step 2: Submit analyze request
    def test_submit_analyze():
        payload = {
            "document_ids": doc_ids,
            "provider": "medgemma-ensemble"
        }
        print(f"Payload: {json.dumps(payload, indent=2)}")
        response = requests.post(
            f"{API_BASE_URL}/api/analyze/",  # Trailing slash required (redirect_slashes=False)
            headers=headers,
            json=payload,
            timeout=30
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        response.raise_for_status()
        data = response.json()
        print(f"Analysis ID: {data.get('analysis_id')}")
        return data

    success, analyze_response = test_step("Submit Analyze Request", test_submit_analyze)
    if not success:
        print("\n❌ Analyze submission failed")
        sys.exit(1)

    analysis_id = analyze_response.get('analysis_id')

    # Step 3: Poll for analysis result
    def test_poll_analysis():
        max_attempts = 30
        for attempt in range(max_attempts):
            print(f"Poll attempt {attempt + 1}/{max_attempts}...", end=' ')
            response = requests.get(
                f"{API_BASE_URL}/api/analyze/{analysis_id}",  # Fixed: analyze not analysis
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            status = data.get('status')
            print(f"Status: {status}")

            if status == 'completed':
                print(f"✅ Analysis completed!")
                print(f"Results preview: {json.dumps(data, indent=2)[:500]}")
                return data
            elif status == 'failed':
                error = data.get('error_message', 'Unknown error')
                raise Exception(f"Analysis failed: {error}")
            elif status in ['queued', 'processing']:
                time.sleep(2)
            else:
                raise Exception(f"Unknown status: {status}")

        raise Exception(f"Timeout after {max_attempts * 2} seconds")

    success, result = test_step("Poll Analysis Result", test_poll_analysis)

    if success:
        print("\n" + "="*60)
        print("🎉 ALL TESTS PASSED!")
        print("="*60)
        print("\nAnalysis completed successfully. The analyze endpoint is working!")
    else:
        print("\n" + "="*60)
        print("⚠️  ANALYSIS INCOMPLETE")
        print("="*60)
        print("\nThe analyze request was submitted but did not complete.")
        print("Check Cloud Run logs for backend errors:")
        print(f"https://console.cloud.google.com/run/detail/us-central1/medbilldozer-api/logs")


if __name__ == "__main__":
    main()
