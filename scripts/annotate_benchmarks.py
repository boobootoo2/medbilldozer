#!/usr/bin/env python3
"""Script to create and update ground truth annotations for benchmark documents.

This script helps create JSON annotations for medical bills and other documents
by parsing the text and presenting a UI for annotating expected issues.

Usage:
    python scripts/annotate_benchmarks.py --input benchmarks/inputs/patient_001_doc_1_medical_bill.txt
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from _modules.extractors.local_heuristic_extractor import extract_facts_local


def extract_patient_info_from_text(text: str) -> dict:
    """Parse text to extract patient info."""
    facts = extract_facts_local(text)
    
    info = {
        "patient_name": facts.get("patient_name", ""),
        "patient_dob": facts.get("patient_dob"),
        "date_of_service": facts.get("date_of_service"),
        "facility_name": facts.get("facility_name", ""),
        "medical_line_items": facts.get("medical_line_items", [])
    }
    
    return info


def create_annotation_template(text: str, document_type: str = "medical_bill") -> dict:
    """Create annotation template from document text."""
    patient_info = extract_patient_info_from_text(text)
    
    template = {
        "document_type": document_type,
        "expected_facts": patient_info,
        "expected_issues": [],
        "expected_savings": 0.0
    }
    
    return template


def print_document_summary(text: str, template: dict):
    """Print document summary for review."""
    print("\n" + "="*70)
    print("DOCUMENT ANALYSIS")
    print("="*70)
    
    print("\nExtracted Facts:")
    print(f"  Patient: {template['expected_facts'].get('patient_name', 'N/A')}")
    print(f"  DOB: {template['expected_facts'].get('patient_dob', 'N/A')}")
    print(f"  Facility: {template['expected_facts'].get('facility_name', 'N/A')}")
    print(f"  Date of Service: {template['expected_facts'].get('date_of_service', 'N/A')}")
    
    items = template['expected_facts'].get('medical_line_items', [])
    print(f"\nLine Items ({len(items)} items):")
    for i, item in enumerate(items, 1):
        print(f"  {i}. {item.get('cpt_code', 'N/A')}: {item.get('description', 'N/A')}")
        print(f"     Billed: ${item.get('billed_amount', 0):.2f}, "
              f"Patient: ${item.get('patient_responsibility', 0):.2f}")
    
    print("\n" + "="*70)


def interactive_issue_creation(template: dict):
    """Interactively add issues to annotation."""
    print("\n" + "="*70)
    print("ADD EXPECTED ISSUES")
    print("="*70)
    
    issue_types = [
        "duplicate_charge",
        "coding_error",
        "unbundling",
        "facility_fee_error",
        "cross_bill_discrepancy",
        "excessive_charge"
    ]
    
    issues = []
    
    while True:
        print("\nOptions:")
        print("  1. Add issue")
        print("  2. Remove issue")
        print("  3. View issues")
        print("  4. Done")
        
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == "1":
            print("\nIssue Types:")
            for i, itype in enumerate(issue_types, 1):
                print(f"  {i}. {itype}")
            
            type_choice = input("Select type (1-6): ").strip()
            if not type_choice.isdigit() or int(type_choice) < 1 or int(type_choice) > len(issue_types):
                print("Invalid choice")
                continue
            
            issue_type = issue_types[int(type_choice) - 1]
            
            severity = input("Severity (high/medium/low) [high]: ").strip() or "high"
            description = input("Description: ").strip()
            savings = input("Expected savings ($) [0]: ").strip() or "0"
            should_detect = input("Should detect? (y/n) [y]: ").strip().lower() != "n"
            
            try:
                savings = float(savings)
            except ValueError:
                print("Invalid savings amount")
                continue
            
            issue = {
                "type": issue_type,
                "severity": severity,
                "cpt_code": None,
                "line_item_index": None,
                "description": description,
                "expected_savings": savings,
                "should_detect": should_detect
            }
            
            issues.append(issue)
            print("✅ Issue added")
        
        elif choice == "2":
            if not issues:
                print("No issues to remove")
                continue
            
            for i, issue in enumerate(issues, 1):
                print(f"  {i}. {issue['type']}: {issue['description']}")
            
            idx = input("Remove issue (number): ").strip()
            if idx.isdigit() and 1 <= int(idx) <= len(issues):
                issues.pop(int(idx) - 1)
                print("✅ Issue removed")
            else:
                print("Invalid choice")
        
        elif choice == "3":
            if not issues:
                print("No issues added")
            else:
                print("\nCurrent Issues:")
                for i, issue in enumerate(issues, 1):
                    print(f"  {i}. {issue['type']} ({issue['severity']})")
                    print(f"     {issue['description']}")
                    print(f"     Savings: ${issue['expected_savings']:.2f}, "
                          f"Should detect: {issue['should_detect']}")
        
        elif choice == "4":
            break
    
    return issues


def main():
    parser = argparse.ArgumentParser(description="Create ground truth annotations for benchmarks")
    parser.add_argument(
        "--input",
        required=True,
        help="Path to input document to annotate"
    )
    parser.add_argument(
        "--output",
        help="Output JSON file (default: inferred from input)"
    )
    parser.add_argument(
        "--type",
        default="medical_bill",
        choices=["medical_bill", "dental_bill", "pharmacy_receipt", "insurance_eob"],
        help="Document type"
    )
    parser.add_argument(
        "--batch",
        action="store_true",
        help="Batch mode - create minimal annotations for all inputs"
    )
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"❌ Input file not found: {input_path}")
        return 1
    
    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        benchmarks_dir = PROJECT_ROOT / "benchmarks"
        output_path = benchmarks_dir / "expected_outputs" / f"{input_path.stem}.json"
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Read document
    document_text = input_path.read_text(encoding="utf-8")
    
    # Create annotation template
    print(f"📄 Processing: {input_path.name}")
    template = create_annotation_template(document_text, args.type)
    
    if not args.batch:
        # Show summary and allow interactive issue creation
        print_document_summary(document_text, template)
        
        # Interactive issue creation
        issues = interactive_issue_creation(template)
        template["expected_issues"] = issues
        template["expected_savings"] = sum(i["expected_savings"] for i in issues)
    
    # Save annotation
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(template, f, indent=2)
    
    print(f"\n✅ Annotation saved to: {output_path}")
    print(f"   Issues: {len(template['expected_issues'])}")
    print(f"   Expected Savings: ${template['expected_savings']:.2f}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
