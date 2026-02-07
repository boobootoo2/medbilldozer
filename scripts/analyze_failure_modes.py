#!/usr/bin/env python3
"""Analyze failure modes from a patient benchmark JSON.

Outputs a small JSON summary and prints top missed expected issue types.
"""
import argparse
import json
from pathlib import Path
from collections import Counter, defaultdict


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to patient benchmark JSON")
    parser.add_argument("--output", required=False, default="benchmarks/results/failure_mode_summary_medgemma.json")
    args = parser.parse_args()

    p = Path(args.input)
    if not p.exists():
        print("Input not found:", p)
        raise SystemExit(1)

    data = json.loads(p.read_text(encoding="utf-8"))
    items = data.get("individual_results") or []

    missed_type_counts = Counter()
    missed_savings_by_type = defaultdict(float)
    patient_missed_counts = 0
    total_fn = 0

    for it in items:
        fn = int(it.get("false_negatives") or 0)
        total_fn += fn
        if fn <= 0:
            continue
        patient_missed_counts += 1
        expected = it.get("expected_issues") or []
        detected = it.get("detected_issues") or []
        detected_types = set([d.get("type") or d.get("mapped_type") or "" for d in detected])
        for e in expected:
            et = e.get("type") or e.get("issue_type") or "unknown"
            # If expected type not seen among detected types, count as missed
            if et not in detected_types:
                missed_type_counts[et] += 1
                try:
                    missed_savings_by_type[et] += float(e.get("max_savings") or 0) if isinstance(e.get("max_savings"), (int, float)) else 0.0
                except Exception:
                    # fallback to potential_savings on patient-level
                    missed_savings_by_type[et] += float(it.get("missed_savings") or 0.0)

    summary = {
        "total_patients": len(items),
        "patients_with_fn": patient_missed_counts,
        "total_false_negatives": total_fn,
        "top_missed_types": missed_type_counts.most_common(20),
        "missed_savings_by_type": dict(missed_savings_by_type)
    }

    outp = Path(args.output)
    outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("Wrote failure mode summary to:", outp)
    print("Patients:", summary["total_patients"], "patients with FN:", summary["patients_with_fn"], "total FNs:", summary["total_false_negatives"]) 
    print("Top missed types:")
    for t, c in summary["top_missed_types"]:
        print(f"  {t}: {c} missed")

if __name__ == '__main__':
    main()
