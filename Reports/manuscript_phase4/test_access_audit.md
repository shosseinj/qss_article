# Controlled-grid test-access audit — 2026-10-14

**Outcome: source-level risk confirmed; historical use unknown; R6 partially resolved.**

Inspected the pinned, hash-verified `scripts/train_nmnist_controlled_four_models.py` (preserved under results/phase3/recovery/source). Lines 74–79 require a prior test accuracy >=0.95 plus a checkpoint hash for skip, and explicitly request revising the common recipe below that threshold. Lines 143–156 assign PASS based on final test accuracy and request recipe revision if it fails. Lines 108–120 choose the best checkpoint using validation accuracy and validation loss; that does not establish test-independent recipe development. The source preflight also consumes `source["clean_gate_pass"]` from earlier custom-model results; its historical decision provenance is unavailable.

The tracked tree and reports provide no resolved grid training configuration, per-epoch history, test-access ledger or chronological recipe comparisons. A code branch cannot prove it actually triggered, nor prove that it was only a warning. Date-stamped README summaries cover multiple campaigns and do not reconstruct the controlled-grid chronology. No claim of historical leakage or untouched test data is made. The original training script is not modified.

`training_gate.py` is a fresh portable completion/resume policy utility, implemented with a failing low-accuracy regression followed by six passing tests. It never reads a test score. Completion requires the exact config/source/train/validation identity, a validation-selected checkpoint, validity/split-disjoint/frozen-validation-recipe gates and hashes for checkpoint, history and predictions. Corrupt artifacts and absent/failed gates reject resume even with high test accuracy. This only checks receipt evidence; it cannot certify whether a producer fabricated a gate.

**Still required:** integrate this policy into a full fresh training runner, replace the source-result performance gate with validation/provenance gates, freeze the recipe using development evidence before any test evaluation, and recover/inspect the historical run chronology. No fresh grid training was performed. The utility is not presented as an executed repaired training campaign.

If test feedback changed development, another run on the same test does not restore independence. Use untouched evaluation data or a justified external evaluation design; retain the limitation otherwise. Real data and checkpoints are absent and the user deferred dependent work.
