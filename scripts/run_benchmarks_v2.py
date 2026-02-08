#!/usr/bin/env python3
"""
Wrapper script for running patient benchmarks.

This script is a convenience wrapper that calls generate_patient_benchmarks.py
with the same arguments. It exists for backward compatibility.
"""
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import and run the main benchmark script
from scripts.generate_patient_benchmarks import main

if __name__ == "__main__":
    sys.exit(main())
