# _modules/workflow_store.py

import json
from pathlib import Path
from typing import Dict, Any
from dataclasses import is_dataclass, asdict

STORE_PATH = Path("workflow_store.jsonl")


def _json_safe(obj: Any) -> Any:
    """
    Recursively convert dataclasses and other objects
    into JSON-serializable structures.
    """
    if is_dataclass(obj):
        return asdict(obj)

    if isinstance(obj, dict):
        return {k: _json_safe(v) for k, v in obj.items()}

    if isinstance(obj, list):
        return [_json_safe(v) for v in obj]

    return obj


def persist_workflow_log(workflow_log: Dict) -> None:
    safe_log = _json_safe(workflow_log)

    with STORE_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(safe_log) + "\n")
