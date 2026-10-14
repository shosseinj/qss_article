"""Completion policy for future runs; no test-accuracy quality threshold.

This validates receipt evidence, not the truth of an upstream leakage audit.
Historical training code is preserved. Integration into a real fresh training
campaign is pending; a successful receipt check is not a new experiment.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re


def completion_status(record, identity, root):
    required = {"config_sha256", "source_sha256", "train_manifest_sha256",
                "validation_manifest_sha256"}
    if not required <= identity.keys() or not all(
        isinstance(identity[k], str) and re.fullmatch(r"[0-9a-f]{64}", identity[k])
        for k in required
    ):
        return False
    if record.get("status") != "completed" or record.get("identity") != identity:
        return False
    if record.get("checkpoint_selection_split") != "validation":
        return False
    gates = record.get("gates", {})
    if any(gates.get(k) is not True for k in
           ("validity", "split_disjoint", "validation_recipe_frozen")):
        return False
    artifacts = record.get("artifacts", {})
    if not {"checkpoint", "history", "predictions"} <= artifacts.keys():
        return False
    for item in artifacts.values():
        if not isinstance(item, dict) or not item.get("path") or not item.get("sha256"):
            return False
        path = Path(root) / item["path"]
        try:
            with path.open("rb") as stream:
                actual = hashlib.file_digest(stream, "sha256").hexdigest()
        except OSError:
            return False
        if actual != item["sha256"]:
            return False
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", required=True, type=Path)
    parser.add_argument("--identity", required=True, type=Path)
    parser.add_argument("--artifact-root", required=True, type=Path)
    args = parser.parse_args()
    result = completion_status(json.loads(args.receipt.read_text()),
                               json.loads(args.identity.read_text()), args.artifact_root)
    print(json.dumps({"can_resume_completed": result, "test_accuracy_used": False}))
    raise SystemExit(0 if result else 1)
