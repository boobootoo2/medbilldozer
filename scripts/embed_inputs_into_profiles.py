#!/usr/bin/env python3
"""Utility: Embed input files into patient profile JSON files.

Converts profiles that reference document filenames into profiles that embed
document objects with a `content` field. This migration makes `patient_profiles`
the single canonical source for benchmark inputs.
"""
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
PROFILES = ROOT / "benchmarks" / "patient_profiles"
INPUTS = ROOT / "benchmarks" / "inputs"


def embed_all_profiles():
    if not PROFILES.exists():
        print("No profiles dir found:", PROFILES)
        return

    for p in sorted(PROFILES.glob("*.json")):
        doc = json.loads(p.read_text(encoding="utf-8"))
        changed = False
        docs = doc.get("documents", [])
        new_docs = []
        for d in docs:
            if isinstance(d, str):
                # Load file from inputs
                input_path = INPUTS / d
                if input_path.exists():
                    content = input_path.read_text(encoding="utf-8")
                    new_docs.append({
                        "document_id": input_path.stem,
                        "document_type": "text",
                        "content": content
                    })
                    changed = True
                else:
                    new_docs.append({"document_id": d, "document_type": "missing", "content": ""})
            else:
                new_docs.append(d)

        if changed:
            doc["documents"] = new_docs
            p.write_text(json.dumps(doc, indent=2), encoding="utf-8")
            print("Updated:", p.name)


if __name__ == "__main__":
    embed_all_profiles()
