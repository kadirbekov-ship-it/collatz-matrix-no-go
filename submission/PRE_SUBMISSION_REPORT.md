# Pre-submission report — 2026-08-25

## Result and scope

The manuscript proves a no-go theorem for one-stage relative natural affine matrix interpretations of the Yolcu–Aaronson–Heule mixed-base Collatz rewrite system in dimensions 1 and 2. In dimension 2, matrix entries and affine offsets range over all nonnegative integers, with the standard positive upper-left monotonicity condition.

The theorem does **not** solve Collatz and does not cover dimension 3+, arctic/tropical interpretations, dependency pairs, or general multi-stage rule removal.

## Novelty check

No exact published duplicate was found. The closest source, Yolcu–Aaronson–Heule (JAR 67, article 15, 2023), leaves the broad mixed-base matrix/arctic obstruction question open. It proves a separate all-dimensional obstruction for a unary encoding, which the manuscript now explicitly distinguishes.

Novelty wording is deliberately qualified with “to the best of our knowledge.”

## Verification performed

- Python version: 3.12.13.
- 66 certificate, scalar, bounded-matrix, and structural tests: PASS.
- 2 cubic-template/C++ exhaustive tests: PASS.
- Total: **68/68 PASS** in two deterministic invocations.
- Python byte compilation: PASS.
- C++17 verifier compilation: PASS.
- Bounded C++ enumerations for all three configured cubic domains: PASS as part of `tests.test_matrix_cubic`.
- Deterministic draft ZIP integrity and SHA-256 verification: PASS.

## Verification not claimed

- No Lean, Coq, Isabelle, or proof-producing SMT formalization exists.
- The full symbolic universal proof has not been independently peer reviewed.
- Earlier Claude review checked central lemmas and classification but was neither independent nor line-by-line.
- The manuscript was compiled with Tectonic, all 11 pages were visually inspected, links were checked, and no undefined citations, references, or overfull boxes remain.

## Files ready

- `main.tex`: English manuscript.
- `references.bib`: editable bibliography mirror; `main.tex` also embeds the reliable `thebibliography` form.
- `cover-letter.md`: JAR cover letter.
- `JAR_CHECKLIST.md`: journal compliance checklist.
- `NOVELTY_CHECK.md`: search record and safe claim wording.
- `ARTIFACT.md`: exact reproduction and trust boundary.
- `output/pdf/collatz-matrix-no-go-manuscript.pdf`: visually verified submission PDF.
- `output/submission/collatz-matrix-no-go-source.zip`: independently unpacked and recompiled source package.
- `dist/collatz-matrix-no-go-1.0.1.zip`: deterministic archival artifact package.

## Blocking items before actual upload

1. Human authorization at the journal portal for publisher declarations and the final submit action.
