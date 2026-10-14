# Temporal Retiming Attacks on Hybrid Quantum Spiking Classifiers

LaTeX manuscript, supplementary material, figures, and preserved supporting evidence.

## Build

Requires a TeX distribution with pdfLaTeX, BibTeX, and latexmk.

```bash
latexmk -pdf -outdir=build main.tex
latexmk -pdf -outdir=build supplement.tex
```

Compiled documents: [paper](build/main.pdf) and [supplement](build/supplement.pdf).

The manuscript sections are in `sections/`, references in `references.bib`, and figures in `figures/`. Supporting tables and preserved implementation/report excerpts are in `data/`. The latest enrichment change report and diff are in `build/review/`.

The reported results derive from preserved evidence; manuscript preparation did not rerun training or attacks. Missing original artifacts and evaluation limitations are documented in the paper and supplement.
# qss_article


## Phase 2 revision and figure sources

The current rewrite, static code audit and outstanding experiments are documented in `Reports/phase2-report.txt`. Machine checks are in `Reports/phase2-verification.json`. The original evidence and CSV files in `data/` are unchanged. The older `data/figure_source_data.json` and figure-export checks describe the earlier artwork; current figure provenance is in `Reports/phase2-figure-provenance.json`.

Figures 2 and 3 can be regenerated with Python 3 and Matplotlib:

```bash
python3 scripts/render_phase2_figures.py
```

Figure 1 is a TikZ circuit/pipeline diagram. With TikZ, standalone and the required fonts installed:

```bash
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=build figures/fig01_overview.tex
cp build/fig01_overview.pdf figures/fig01_overview.pdf
pdftocairo -svg figures/fig01_overview.pdf figures/fig01_overview.svg
pdftoppm -r 300 -singlefile -png figures/fig01_overview.pdf figures/fig01_overview
```

After building both documents, run `python3 scripts/verify_phase2.py` to check the aggregate counts, paired p-values, derived intervals, citations/references, build logs and vector exports. This check does not run training or attacks.


## Phase 3 status

The artifact inventory, CPU correctness tests, recovered source and versioned runner are documented in [Reports/phase3/report.md](Reports/phase3/report.md). Real checkpoint/data-dependent experiments are deferred; see [the future-work checklist](Reports/phase3/future-work.md). No Phase 3 empirical results have been added to the paper. Runner instructions: [scripts/phase3/README.md](scripts/phase3/README.md).
