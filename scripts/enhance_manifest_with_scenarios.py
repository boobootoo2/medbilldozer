#!/usr/bin/env python3
"""
Enhance Manifest with Clinical Scenarios
=========================================

Adds clinical scenario data to the manifest.json file so that the dashboard
can display detailed scenario information when viewing images.

This script:
1. Reads the existing manifest.json
2. Reads the CLINICAL_SCENARIOS from run_clinical_validation_benchmarks.py
3. Matches scenarios to images by filename
4. Adds scenario data to each image entry
5. Writes updated manifest.json

Usage:
    python3 scripts/enhance_manifest_with_scenarios.py

Author: Senior MLOps Engineer
Date: 2026-02-15
"""

import json
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / 'scripts'))

# Import CLINICAL_SCENARIOS from benchmark script
from run_clinical_validation_benchmarks import CLINICAL_SCENARIOS


def enhance_manifest():
    """Add clinical scenario data to manifest.json."""
    
    manifest_path = PROJECT_ROOT / 'benchmarks/clinical_images/kaggle_datasets/selected/manifest.json'
    
    if not manifest_path.exists():
        print(f"❌ Manifest not found at: {manifest_path}")
        print("Run download_kaggle_medical_images.py first to create the manifest.")
        return False
    
    # Read existing manifest
    print(f"📖 Reading manifest from: {manifest_path}")
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
    
    print(f"Found {len(manifest.get('images', []))} images in manifest")
    
    # Build mapping of image_file to scenarios
    image_to_scenarios = {}
    for scenario_key, scenario_data in CLINICAL_SCENARIOS.items():
        image_file = scenario_data.get('image_file')
        if image_file:
            if image_file not in image_to_scenarios:
                image_to_scenarios[image_file] = []
            
            # Create clean scenario data for manifest
            scenario_info = {
                'scenario_id': scenario_key,
                'validation_type': scenario_data.get('validation_type'),
                'modality': scenario_data.get('modality'),
                'image_type': scenario_data.get('image_type'),
                'patient_context': scenario_data.get('patient_context', {}),
                'clinical_finding': scenario_data.get('clinical_finding'),
                'prescribed_treatment': scenario_data.get('prescribed_treatment'),
                'expected_determination': scenario_data.get('expected_determination'),
                'error_type': scenario_data.get('error_type'),
                'severity': scenario_data.get('severity'),
                'cost_impact': scenario_data.get('cost_impact', 0)
            }
            
            # Add ICD-specific fields if present
            if 'diagnosis' in scenario_data:
                scenario_info['diagnosis'] = scenario_data.get('diagnosis')
            if 'icd_code' in scenario_data:
                scenario_info['icd_code'] = scenario_data.get('icd_code')
                scenario_info['icd_description'] = scenario_data.get('icd_description')
            if 'provided_icd_code' in scenario_data:
                scenario_info['provided_icd_code'] = scenario_data.get('provided_icd_code')
            if 'correct_code' in scenario_data:
                scenario_info['correct_code'] = scenario_data.get('correct_code')
            if 'correct_icd_codes' in scenario_data:
                scenario_info['correct_icd_codes'] = scenario_data.get('correct_icd_codes')
            
            image_to_scenarios[image_file].append(scenario_info)
    
    print(f"\n📊 Scenario Mapping:")
    print(f"  {len(image_to_scenarios)} unique images have scenarios")
    print(f"  {sum(len(scenarios) for scenarios in image_to_scenarios.values())} total scenarios")
    
    # Enhance manifest images with scenario data
    enhanced_count = 0
    for img_entry in manifest.get('images', []):
        filename = img_entry.get('filename')
        if filename in image_to_scenarios:
            img_entry['scenarios'] = image_to_scenarios[filename]
            enhanced_count += 1
            print(f"  ✅ {filename}: {len(image_to_scenarios[filename])} scenario(s)")
        else:
            img_entry['scenarios'] = []
    
    # Write updated manifest
    print(f"\n💾 Writing enhanced manifest...")
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"\n✅ Successfully enhanced manifest!")
    print(f"  Enhanced: {enhanced_count}/{len(manifest.get('images', []))} images")
    print(f"  Location: {manifest_path}")
    print(f"\n🎯 Dashboard will now display clinical scenarios in 'View Full' panel")
    
    return True


def main():
    """Main entry point."""
    print("=" * 70)
    print("Enhance Manifest with Clinical Scenarios")
    print("=" * 70)
    
    success = enhance_manifest()
    
    if success:
        print("\n🚀 Next steps:")
        print("  1. Refresh your Streamlit dashboard")
        print("  2. Navigate to: Production Stability → Clinical Validation (BETA)")
        print("  3. Expand: '📚 Clinical Data Sets'")
        print("  4. Click: '🔍 View Full' on any image")
        print("  5. See: '📋 Associated Clinical Scenarios' sub-accordions")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
