# Temporal Retiming Attacks on Hybrid Quantum Spiking Classifiers

LaTeX manuscript, supplement, vector figures and preserved evidence for `qss_article`.

## Current revision — 14 October 2026

[Manuscript Phase 4 response](Reports/manuscript_phase4/response_to_review.md) tracks R1–R8 and M1–M13. Editorial, reference and source-audit changes are complete; empirical validation remains incomplete. No new trained-model experiment was performed. The user confirmed that data/checkpoints are unavailable and deferred dependent experiments to [future work](Reports/manuscript_phase4/remaining_work.md).

The bibliography contains 32 entries, including 12 additions cited in the main text. Baseline definitions and attack/training source are available; resolved historical configs, trained weights, raw N-MNIST, manifests, per-example outputs and original run-audit artifacts are absent locally. See the [availability matrix](Reports/manuscript_phase4/repository_availability.json) and [source manifest](Reports/manuscript_phase4/source-manifest.json). Source recovery is not replay of historical results.

## Build and manuscript checks

Requires pdfLaTeX, BibTeX and latexmk. The existing TeX backend and numeric citation order are retained; `unsrtlinks.bst` extends standard `unsrt` to print DOI/URL fields. TinyTeX in this workspace provides the required packages. No venue-specific page limit was supplied.

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=build main.tex
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=build supplement.tex
python3 -m scripts.manuscript_phase4.verify
```

Outputs: [paper](build/main.pdf) and [supplement](build/supplement.pdf). The verification command checks hashes, aggregate arithmetic, source-level costs, actual citations, duplicate DOI/title, cross references, TeX logs and vector exports. It does not train a model or execute an attack.

## Figure regeneration

The current figure-2 renderer preserves the CSV counts and separates paired counts from marginal Wilson intervals:

```bash
python3 -m scripts.manuscript_phase4.render_figure2
```

Its figure dependencies are pinned in [requirements-figures.txt](scripts/manuscript_phase4/requirements-figures.txt); exports in this revision used Python 3.14. Figure 3 is unchanged and derives from `data/controlled_four_models.csv`; its short ConvNet label means **spiking SimpleNet_v2**. Figure 1 is a TikZ diagram:

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=build figures/fig01_overview.tex
cp build/fig01_overview.pdf figures/fig01_overview.pdf
pdftocairo -svg figures/fig01_overview.pdf figures/fig01_overview.svg
pdftoppm -r 300 -singlefile -png figures/fig01_overview.pdf figures/fig01_overview
```

Original numerical CSVs, evidence snapshots and prior phase reports remain unchanged. The Phase 2 renderer regenerates older artwork and writes historical reports; its checker expects 20 references. Use the current commands above for the current manuscript. Prior work is recorded in [Phase 2](Reports/phase2-report.txt) and [Phase 3](Reports/phase3/report.md).

## Portable software checks and future real-data execution

Use Python 3.12 with [pinned CPU dependencies](configs/phase3/requirements-cpu.txt). A separate environment is recommended for figure rendering. The CPU environment is a new correctness environment, not a historical runtime reconstruction.

```bash
python3.12 -m venv /tmp/qsnn-cpu
/tmp/qsnn-cpu/bin/python -m pip install -r configs/phase3/requirements-cpu.txt
/tmp/qsnn-cpu/bin/python -W error::ResourceWarning -m unittest discover -v
```

Tests use synthetic inputs and untrained constructors. They validate software contracts, not scientific results. The new [training completion policy](scripts/manuscript_phase4/training_gate.py) ignores test accuracy but retains identity, validation selection, validity/leakage/frozen-recipe gates and artifact hashes. Integration into a full fresh grid training runner remains pending. The [test-access audit](Reports/manuscript_phase4/test_access_audit.md) distinguishes confirmed source risk from unknown historical behavior.

The [Phase 3 runner instructions](scripts/phase3/README.md) specify event NPZ/manifest schemas and checkpoint metadata. For a real pilot, supply an actual checkpoint, metadata, raw-event manifest, all SHA-256 hashes and a new run ID in a copy of `configs/phase3/pilot.yaml`:

```bash
/tmp/qsnn-cpu/bin/python -m scripts.phase3.runner pilot --config /absolute/path/to/resolved-pilot.yaml
```

The shipped config deliberately has null prerequisites and reports `blocked_resource` with null metrics. It does not download data automatically. Obtain N-MNIST through its original distribution or Tonic's `NMNIST` loader (historical source specifies `tonic==1.6.0`), respecting dataset terms; retain archive hashes, official train/test identities and timestamps when exporting. A download or new training run must not be labeled a replay of unavailable historical weights. The original source requirements are preserved in `data/evidence_source_snapshot/requirements.txt`; they are not a complete resolved environment for every campaign.

Development and recipe selection must use validation. The supplied final-test lock remains draft; no final-test evaluation is authorized by an import check or an unset configuration. No new best-so-far curve, real exemplar, final-model ablation or independent official-test QSNN result is included.

Historical research source is pinned to `80d02f5733d4cbe7c3e69b828dff66d50ba5c211`. Additional baseline source matches upstream `f16738f80be94067223f4968c1c318a125b9a321`; full hashes and paths are in the manifests. [Dated README reconciliation](Reports/manuscript_phase4/readme_reconciliation.md) explains stale/contradictory historical status statements without editing the original snapshots.
