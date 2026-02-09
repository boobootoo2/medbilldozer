#!/usr/bin/env python3
"""Test HuggingFace API connectivity and diagnose 400 errors."""

import os
import sys
import json
import requests
from dotenv import load_dotenv

load_dotenv()

HF_API_TOKEN = os.getenv("HF_API_TOKEN")
HF_MODEL_ID = os.getenv("HF_MODEL_ID", "google/medgemma-4b-it")
HF_MODEL_URL = os.getenv("HF_MODEL_URL", "https://router.huggingface.co/v1/chat/completions")

print("=" * 70)
print("HuggingFace API Diagnostic Test")
print("=" * 70)

# Check token
if not HF_API_TOKEN:
    print("\n❌ ERROR: HF_API_TOKEN not set in environment")
    print("   Please set it in your .env file or environment variables")
    sys.exit(1)

print(f"\n✅ HF_API_TOKEN: {HF_API_TOKEN[:10]}...{HF_API_TOKEN[-10:]}")
print(f"✅ Model ID: {HF_MODEL_ID}")
print(f"✅ API URL: {HF_MODEL_URL}")

# Test request
print("\n" + "=" * 70)
print("Testing API Request...")
print("=" * 70)

headers = {
    "Authorization": f"Bearer {HF_API_TOKEN}",
    "Content-Type": "application/json",
}

payload = {
    "model": HF_MODEL_ID,
    "messages": [{"role": "user", "content": "Hello, test message"}],
    "temperature": 0.0,
    "max_tokens": 50,
}

print("\n📤 Request payload:")
print(json.dumps(payload, indent=2))

try:
    response = requests.post(
        HF_MODEL_URL,
        headers=headers,
        json=payload,
        timeout=60,
    )
    
    print(f"\n📥 Response status: {response.status_code}")
    print(f"📥 Response headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        print("\n✅ SUCCESS!")
        data = response.json()
        print("\n📄 Response data:")
        print(json.dumps(data, indent=2))
    else:
        print(f"\n❌ ERROR: {response.status_code} {response.reason}")
        print("\n📄 Response body:")
        print(response.text)
        
        # Try to parse error details
        try:
            error_data = response.json()
            print("\n📋 Parsed error:")
            print(json.dumps(error_data, indent=2))
        except Exception as e:
            print(f"\n⚠️  Could not parse error response: {e}")
            
except requests.exceptions.RequestException as e:
    print(f"\n❌ Request failed: {e}")
    sys.exit(1)

print("\n" + "=" * 70)
