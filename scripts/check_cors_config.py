#!/usr/bin/env python3
"""
Check CORS configuration for the backend.
Run this from the backend directory to see what origins are allowed.

Usage:
    cd backend
    python ../scripts/check_cors_config.py
"""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

try:
    from app.config import settings

    print("\n🔍 CORS Configuration Check")
    print("=" * 60)
    print(f"Environment:           {settings.environment}")
    print(f"Frontend URL:          {settings.frontend_url or '(not set)'}")
    print(f"Additional Origins:    {settings.backend_cors_origins or '[]'}")
    print(f"Debug Mode:            {settings.debug}")
    print("\n📋 Allowed CORS Origins:")
    print("-" * 60)

    origins = settings.all_cors_origins
    if origins:
        for i, origin in enumerate(origins, 1):
            print(f"  {i}. {origin}")
    else:
        print("  ⚠️  No origins configured!")

    print("\n" + "=" * 60)
    print(f"✓ Total: {len(origins)} origin(s) allowed")
    print()

    # Warnings
    if not origins:
        print("⚠️  WARNING: No CORS origins configured!")

    if settings.environment == "local" and len(origins) < 6:
        print("⚠️  WARNING: Local environment should have 6 localhost origins")

    # Check for production domain (properly validate, not just substring)
    has_prod_domain = any(
        o.endswith("medbilldozer.com") or o.endswith(".medbilldozer.com") for o in origins
    )
    if settings.environment == "production" and not has_prod_domain:
        print("⚠️  WARNING: Production should include medbilldozer.com domains")

except ImportError as e:
    print(f"\n❌ Error: Could not import settings. Make sure to run from backend directory.")
    print(f"   {e}")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ Error: {e}")
    sys.exit(1)
