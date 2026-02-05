#!/usr/bin/env python3
"""
Verify Benchmark Snapshot Automation

Quick script to check if snapshots are being created in Supabase
from GitHub Actions benchmark runs.
"""

import os
import sys
from datetime import datetime, timedelta

try:
    from supabase import create_client
    from dotenv import load_dotenv
except ImportError:
    print("❌ Error: Required packages not installed")
    print("   Run: pip install supabase python-dotenv")
    sys.exit(1)

load_dotenv()

def verify_automation():
    """Check if snapshots are being created automatically."""
    
    print("╔═══════════════════════════════════════════════════════════════╗")
    print("║       Benchmark Snapshot Automation Verification              ║")
    print("╚═══════════════════════════════════════════════════════════════╝")
    print()
    
    # Check environment variables
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ Supabase credentials not found")
        print()
        print("Please set environment variables:")
        print("  SUPABASE_URL=https://xxx.supabase.co")
        print("  SUPABASE_SERVICE_ROLE_KEY=eyJhbG...")
        print()
        print("Or add to .env file")
        return False
    
    print("✓ Supabase credentials found")
    print(f"  URL: {supabase_url}")
    print(f"  Key: {supabase_key[:20]}...")
    print()
    
    try:
        # Connect to Supabase
        client = create_client(supabase_url, supabase_key)
        print("✓ Connected to Supabase")
        print()
        
        # Check recent transactions
        print("─" * 65)
        print("Recent Benchmark Transactions (last 24 hours)")
        print("─" * 65)
        
        yesterday = (datetime.now() - timedelta(days=1)).isoformat()
        
        transactions = client.table('benchmark_transactions') \
            .select('*') \
            .gte('created_at', yesterday) \
            .order('created_at', desc=True) \
            .limit(10) \
            .execute()
        
        if transactions.data:
            print(f"\nFound {len(transactions.data)} transaction(s) in last 24 hours:\n")
            
            for tx in transactions.data:
                created = tx['created_at'][:19]
                model = tx['model_version']
                env = tx['environment']
                f1 = tx['metrics'].get('f1', 'N/A')
                triggered = tx.get('triggered_by', 'unknown')
                
                print(f"  • {created} | {model:15} | {env:15} | F1: {f1:.3f} | By: {triggered}")
            
            print("\n✅ Transactions are being created!\n")
        else:
            print("\n⚠️  No transactions found in last 24 hours")
            print("   This might be normal if:")
            print("   - Benchmarks haven't run recently (scheduled daily)")
            print("   - GitHub Actions is not configured")
            print("   - Secrets are not set up\n")
        
        # Check recent snapshots
        print("─" * 65)
        print("Recent Benchmark Snapshots")
        print("─" * 65)
        
        snapshots = client.table('benchmark_snapshots') \
            .select('*') \
            .order('created_at', desc=True) \
            .limit(10) \
            .execute()
        
        if snapshots.data:
            print(f"\nFound {len(snapshots.data)} snapshot(s):\n")
            
            print(f"{'Model':<15} {'Version':<8} {'F1':<8} {'Current':<8} {'Environment':<15} {'Created'}")
            print("─" * 80)
            
            for snap in snapshots.data:
                model = snap['model_version']
                version = snap['snapshot_version']
                f1 = snap.get('f1_score') or 0
                is_current = '✓' if snap.get('is_current') else ''
                env = snap['environment']
                created = snap['created_at'][:10]
                
                print(f"{model:<15} {version:<8} {f1:<8.3f} {is_current:<8} {env:<15} {created}")
            
            print("\n✅ Snapshots are being created!\n")
            
            # Check for GitHub Actions snapshots specifically
            gh_snapshots = [s for s in snapshots.data if s['environment'] == 'github-actions']
            
            if gh_snapshots:
                print(f"✅ Found {len(gh_snapshots)} GitHub Actions snapshot(s)")
                print("   Automation is working correctly!\n")
            else:
                print("⚠️  No GitHub Actions snapshots found")
                print("   Snapshots may be created locally only")
                print()
                print("To enable GitHub Actions automation:")
                print("  1. Go to: Repository → Settings → Secrets → Actions")
                print("  2. Add: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY")
                print("  3. Wait for next scheduled benchmark run (daily at 2am UTC)")
                print("  4. Or manually trigger: Actions → Run Benchmarks → Run workflow\n")
        else:
            print("\n⚠️  No snapshots found in database")
            print("   Database may be empty or not initialized")
            print()
            print("To create test snapshots:")
            print("  python scripts/populate_test_snapshots.py\n")
        
        # Summary
        print("─" * 65)
        print("Summary")
        print("─" * 65)
        print()
        
        if transactions.data and gh_snapshots:
            print("✅ AUTOMATION WORKING")
            print("   Benchmarks are running and snapshots are being created")
            print("   in GitHub Actions automatically.")
        elif transactions.data:
            print("⚠️  PARTIAL SETUP")
            print("   Transactions exist but no GitHub Actions snapshots found.")
            print("   Check GitHub secrets configuration.")
        else:
            print("⚠️  NO AUTOMATION DETECTED")
            print("   No recent transactions found.")
            print("   Check GitHub Actions configuration and secrets.")
        
        print()
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print()
        return False

if __name__ == "__main__":
    success = verify_automation()
    sys.exit(0 if success else 1)
