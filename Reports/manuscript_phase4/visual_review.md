# PDF and grayscale review — 2026-10-14

Both final PDFs were rendered with Poppler for local inspection. All main9 and supplement18 page layouts were inspected in contact sheets; main pages3,5–9 and supplement pages14–16/18 were inspected at higher resolution. Three scientific figures were also inspected in grayscale, including actual-size main page7. Temporary review rasters are under /tmp/phase4-visual; final vector originals remain in figures/.

- Figure1: readable gate labels and wire indices; new legend distinguishes input-dependent angles from trained parameters fixed at inference. Pipeline is a computation diagram, not a real attack exemplar.
- Figure2: paired-count columns and PGD/TEMP marker shapes remain distinguishable in gray. Redundant text below the axes was removed; caption gives the candidate/forward grouping once. Historical counts are unchanged.
- Figure3: existing inset labels are separated and readable; circle/square budget markers distinguish conditions without color. Caption explicitly defines ConvNet as spiking SimpleNet_v2 and preserves historical/contextual scope.
- Cost/notation/model/availability tables fit the page and columns. Verified source counts and unverified reference counts are visibly distinguished.
- Bibliography: standard DOI/URL fields render with line breaks. An initial split of entry15 across pages8–9 was found and fixed by keeping individual entries together. Final entry26 includes independently verified QCE pages1571–1582. Both bibliography layouts have no overflow or broken reference.

The main document is9 pages (formerly8); supplement is18 pages. No venue limit was provided, and fonts were not reduced to force a page count. TeX reports four harmless underfull boxes in main and one pre-existing amsmath/atopwithdelims package warning in supplement; no overfull boxes, undefined citations/references or build errors.

Grayscale/raster outputs are review aids; PDF/SVG scientific figures contain no embedded raster images. Visual review supplies no new model evidence.
