"""Catch test-dependent completion, provenance bypass and missing audit gates."""
import copy
import hashlib
from pathlib import Path
import tempfile
import unittest

from scripts.manuscript_phase4.training_gate import completion_status


class CompletionTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.identity = {key: hashlib.sha256(key.encode()).hexdigest() for key in
                         ("config_sha256", "source_sha256", "train_manifest_sha256",
                          "validation_manifest_sha256")}
        self.artifacts = {}
        for name in ("checkpoint", "history", "predictions"):
            path = self.root / name
            path.write_bytes(name.encode())
            self.artifacts[name] = {"path": name,
                                    "sha256": hashlib.sha256(name.encode()).hexdigest()}
        self.record = {"status": "completed", "identity": self.identity,
                       "checkpoint_selection_split": "validation",
                       "gates": {"validity": True, "split_disjoint": True,
                                 "validation_recipe_frozen": True},
                       "artifacts": self.artifacts, "test": {"accuracy": 0.01}}

    def test_low_test_accuracy_is_a_completed_run(self):
        self.assertTrue(completion_status(self.record, self.identity, self.root))
        self.record["test"]["accuracy"] = 0.99
        self.assertTrue(completion_status(self.record, self.identity, self.root))
        del self.record["test"]
        self.assertTrue(completion_status(self.record, self.identity, self.root))

    def test_hash_damage_rejects_resume_even_with_high_accuracy(self):
        self.record["test"]["accuracy"] = 1.0
        (self.root / "checkpoint").write_bytes(b"damaged")
        self.assertFalse(completion_status(self.record, self.identity, self.root))

    def test_recipe_change_cannot_reuse_completed_run(self):
        changed = copy.deepcopy(self.identity)
        changed["config_sha256"] = "f" * 64
        self.assertFalse(completion_status(self.record, changed, self.root))

    def test_missing_or_failed_scientific_gates_reject_completion(self):
        for name in ("validity", "split_disjoint", "validation_recipe_frozen"):
            record = copy.deepcopy(self.record)
            record["gates"][name] = False
            self.assertFalse(completion_status(record, self.identity, self.root))
            del record["gates"][name]
            self.assertFalse(completion_status(record, self.identity, self.root))

    def test_test_selected_checkpoint_cannot_complete(self):
        self.record["checkpoint_selection_split"] = "official_test"
        self.assertFalse(completion_status(self.record, self.identity, self.root))

    def test_incomplete_missing_artifacts_and_invalid_identity_reject(self):
        record = copy.deepcopy(self.record)
        record["status"] = "running"
        self.assertFalse(completion_status(record, self.identity, self.root))
        for name in ("checkpoint", "history", "predictions"):
            record = copy.deepcopy(self.record)
            del record["artifacts"][name]
            self.assertFalse(completion_status(record, self.identity, self.root))
        self.assertFalse(completion_status(self.record, {}, self.root))


if __name__ == "__main__":
    unittest.main()
