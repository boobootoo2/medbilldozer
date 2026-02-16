#!/usr/bin/env python3
"""
Verify Supabase API keys are correct type (service_role vs anon)
"""

import os
import sys
import base64
import json

def decode_jwt_payload(token: str) -> dict:
    """Decode JWT payload without verification (just to inspect claims)."""
    try:
        # JWT structure: header.payload.signature
        parts = token.split('.')
        if len(parts) != 3:
            return {"error": "Invalid JWT structure"}
        
        # Decode payload (add padding if needed)
        payload = parts[1]
        padding = 4 - len(payload) % 4
        if padding != 4:
            payload += '=' * padding
        
        decoded = base64.urlsafe_b64decode(payload)
        return json.loads(decoded)
    except Exception as e:
        return {"error": str(e)}

def check_key(key_name: str, key_value: str | None):
    """Check if a key is service_role or anon."""
    print(f"\n{'='*60}")
    print(f"Checking {key_name}")
    print(f"{'='*60}")
    
    if not key_value:
        print(f"❌ {key_name} not set in environment")
        return False
    
    # Check if it looks like a JWT
    if not key_value.startswith('eyJ'):
        print(f"❌ {key_name} doesn't look like a JWT token")
        return False
    
    # Decode and check role
    payload = decode_jwt_payload(key_value)
    
    if "error" in payload:
        print(f"❌ Error decoding JWT: {payload['error']}")
        return False
    
    role = payload.get('role', 'unknown')
    print(f"Token role: {role}")
    print(f"Issuer: {payload.get('iss', 'unknown')}")
    print(f"Issued at: {payload.get('iat', 'unknown')}")
    
    if role == 'service_role':
        print(f"✅ {key_name} is a SERVICE ROLE key (correct for sync)")
        return True
    elif role == 'anon':
        print(f"⚠️  {key_name} is an ANON key (WRONG for sync!)")
        print(f"    You need to use the service_role key for data sync")
        return False
    else:
        print(f"❓ {key_name} has unknown role: {role}")
        return False

def main():
    print("🔍 Supabase Key Verification Tool")
    print("=" * 60)
    
    # Check main Supabase key
    main_key = os.getenv('SUPABASE_KEY')
    main_ok = check_key('SUPABASE_KEY', main_key)
    
    # Check beta Supabase key
    beta_key = os.getenv('SUPABASE_BETA_KEY')
    beta_ok = check_key('SUPABASE_BETA_KEY', beta_key)
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    if main_ok and beta_ok:
        print("✅ Both keys are service_role keys - sync should work!")
        return 0
    else:
        print("❌ One or more keys are incorrect")
        print("\nTo fix:")
        print("1. Go to Supabase project settings")
        print("2. Navigate to API section")
        print("3. Copy the 'service_role' key (NOT the anon key)")
        print("4. Update your environment variables:")
        if not main_ok:
            print("   export SUPABASE_KEY='service_role_key_here'")
        if not beta_ok:
            print("   export SUPABASE_BETA_KEY='service_role_key_here'")
        return 1

if __name__ == "__main__":
    sys.exit(main())
