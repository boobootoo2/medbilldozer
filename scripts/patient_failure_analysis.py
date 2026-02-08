#!/usr/bin/env python3
"""Produce a per-patient failure analysis CSV from a patient benchmark JSON.

Usage: python scripts/patient_failure_analysis.py --input <results.json> --output <csv>

The script expects the benchmark JSON to have an "individual_results" list with fields
like patient_id, patient_name, expected_issues (list), detected_issues (list),
true_positives, false_positives, false_negatives, domain_recall, potential_savings, missed_savings.
"""
import argparse
import json
import csv
from pathlib import Path


def summarize_patient(p):
    pid = p.get("patient_id")
    name = p.get("patient_name")
    expected = p.get("expected_issues") or []
    detected = p.get("detected_issues") or []
    tp = int(p.get("true_positives") or 0)
    fp = int(p.get("false_positives") or 0)
    fn = int(p.get("false_negatives") or 0)
    domain_recall = p.get("domain_recall")
    potential_savings = p.get("potential_savings")
    missed_savings = p.get("missed_savings")

    expected_types = [e.get("type") or e.get("issue_type") or e.get("issue") or "" for e in expected]
    detected_types = [d.get("type") or d.get("mapped_type") or d.get("label") or "" for d in detected]

    # For false negatives, include the expected issue descriptions
    fn_details = []
    if fn > 0:
        # Determine which expected issues appear to be missed by checking types not in detected types
        for e in expected:
            t = e.get("type") or e.get("issue_type") or e.get("issue")
            if t not in detected_types:
                fn_details.append({
                    "type": t,
                    "description": e.get("description"),
                    "cpt_code": e.get("cpt_code") or e.get("code")
                })

    return {
        "patient_id": pid,
        "patient_name": name,
        "expected_count": len(expected),
        "detected_count": len(detected),
        "true_positives": tp,
        "false_positives": fp,
        "false_negatives": fn,
        "domain_recall": domain_recall,
        "potential_savings": potential_savings,
        "missed_savings": missed_savings,
        "expected_types": ";".join(expected_types),
        "detected_types": ";".join(detected_types),
        "fn_details": json.dumps(fn_details, ensure_ascii=False),
        "detected_raw": json.dumps(detected, ensure_ascii=False)
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to patient benchmark JSON")
    parser.add_argument("--output", required=False, default="benchmarks/results/patient_failure_analysis_medgemma.csv", help="Output CSV path")
    args = parser.parse_args()

    input_path = Path(args.input)
    out_path = Path(args.output)

    if not input_path.exists():
        print(f"Input file not found: {input_path}")
        raise SystemExit(1)

    data = json.loads(input_path.read_text(encoding="utf-8"))
    items = data.get("individual_results") or []

    rows = [summarize_patient(p) for p in items]

    # Ensure output dir exists
    out_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "patient_id",
        "patient_name",
        "expected_count",
        "detected_count",
        "true_positives",
        "false_positives",
        "false_negatives",
        "domain_recall",
        "potential_savings",
        "missed_savings",
        "expected_types",
        "detected_types",
        "fn_details",
        "detected_raw",
    ]

    with out_path.open("w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    # Print a brief summary of overall failures
    total_patients = len(rows)
    total_fn = sum(r["false_negatives"] for r in rows)
    total_fp = sum(r["false_positives"] for r in rows)
    total_tp = sum(r["true_positives"] for r in rows)

    print("Per-patient failure analysis written to:", out_path)
    print(f"Patients: {total_patients}  TP: {total_tp}  FP: {total_fp}  FN: {total_fn}")


if __name__ == "__main__":
    main()
