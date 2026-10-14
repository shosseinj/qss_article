# Phase 3 executable checks and artifact-gated runner

This package is a **new implementation**, separate from the preserved historical runners. It does not supply missing checkpoints, datasets, historical manifests or measured model results. Real experiments have been deferred at the user's request because those artifacts are not on this computer.

The current CPU correctness environment uses Python 3.12, NumPy 1.26.4 and PyTorch 2.5.1+cpu. The environment is separate from historical runs. Recreate it from `configs/phase3/requirements-cpu.txt` in a virtual environment; the session's temporary interpreter is `/tmp/qsnn-phase3-venv/bin/python`.

```bash
/tmp/qsnn-phase3-venv/bin/python -m unittest discover -s tests -v
/tmp/qsnn-phase3-venv/bin/python -m scripts.phase3.runner inventory
/tmp/qsnn-phase3-venv/bin/python -m scripts.phase3.runner pilot --config configs/phase3/pilot.yaml
```

The last command currently exits **2 / blocked_resource**, recording null metrics in `Reports/phase3/pilot.json`. An unavailable experiment is never counted as a survivor or zero ASR. No ETA is inferred from toy test speed.

## Before using real artifacts

1. Set checkpoint path and SHA-256, metadata sidecar path and SHA-256, and the raw-event manifest path and SHA-256 in a copy of the pilot config. Use a new run ID for each protocol/source/environment change. The metadata template is in `configs/phase3/checkpoint-metadata.template.json`.
2. A checkpoint must contain `model_state` and the actual saved `seed`. The loader uses `torch.load(..., weights_only=True)` and strict state-dict matching; a file extension or seed alone is insufficient. Metadata must establish variant, pretraining provenance and preprocessing.
3. Create a **separately frozen pilot manifest**; do not point a 1000-example campaign at a runner that secretly truncates it. The runner requires the configured length.
4. Run a real pilot first, inspect clean reconstruction, selection/audit logs, gradients, memory and timings. Only then run development searches. The staged development YAML is a proposal, not a completed or selected attack protocol.

Manifest CSV columns:

```text
example_id,label,dataset_split,events_path,events_sha256
```

Each event NPZ must contain one-dimensional `ids,x,y,p,t` arrays plus scalar `label`. IDs must be unique, timestamps finite/nondecreasing, coordinates within 34×34 and polarity binary. The exporter must preserve original event order/identities and retain verifiable dataset/split provenance. Dataset export and original official split recovery remain future work; the runner does not fabricate them or download data automatically.

## Commands after prerequisites exist

```bash
python -m scripts.phase3.runner attack --config <resolved-validation-config.yaml>
python -m scripts.phase3.runner clean-eval --config <frozen-official-clean-config.yaml>
```

Use a separate immutable config for each attack, radius, seed and model. `attack` supports PGD CE/margin, clean start plus additional uniform starts, and the literal TEMP schedules. TEMP only supports margin; asking it to report CE is rejected. Query scaling reports actual proposals after rounding. Chunk sizes and actual batched calls are logged separately from individual forward equivalents. There is **no automatic development sweep, time-calibration campaign, training campaign or final-test unlocking**: their validated artifacts and frozen settings must be supplied during the future work.

`clean-eval` refuses to call a partial official-test manifest a full clean test: it requires all 10,000 examples. Final-test commands require `Reports/phase3/preregistration.yaml` to be genuinely frozen and its exact config/source hashes to match. The shipped file is deliberately draft. Hash locking is an execution safeguard; it is not a public registration or evidence that validation tuning happened.

## Selection, storage and resume

- Search and all-candidate hard verification are counted and timed separately. No forward reuse is hidden in the literal PGD search cost.
- Both maximum-loss/margin legacy selection and success-priority selection use the **same verified logits on the same candidate trajectory**. The search-selected output is retained separately, and reevaluation changes are recorded. Unexpected argmax changes during verification fail the example rather than becoming a selection claim.
- Ties use the first class index, matching `torch.argmax`; success is actual valid argmax misclassification, not the sign of margin alone.
- Each example writes an atomic receipt, candidate loss/prediction/validity metadata and selected raw arrays. All candidates' timestamps are temporarily disk-backed; full raw trajectories are retained for predeclared IDs and selection-discordant examples. Others retain selected arrays and candidate metadata.
- Failed, missing or clean-incorrect manifest rows make the cell incomplete with `asr: null`. No difficult example is silently dropped. Model/attack seeds are not pooled as independent samples.
- Run identity binds config, source and stable environment fingerprints. Resuming a changed implementation/device/library environment requires a new run ID. Artifacts are hashed before a completed receipt is reused.
- State metrics use normalized pure vectors after the common learned basis, squared fidelity, trace distance and measurement TV. The per-competitor bound is checked for failures and survivors alike. Classical heads have no quantum-state metrics.

Current tests use explicitly synthetic inputs and untrained models. They validate software contracts and are **not an empirical selection audit or a QSNN test result**. The fixed-frontend variants are constructors, not trained ablations; the no-entangler probability readout is nonlinear.
