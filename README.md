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
