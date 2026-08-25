# Artifact for the two-dimensional natural-matrix no-go theorem

This artifact accompanies the manuscript in `submission/main.tex`. It checks exact certificate algebra and performs bounded regression searches. The universal quantifier over all natural matrix entries is proved in the manuscript and in `MATRIX_ATTACK.md`; it is not replaced by enumeration.

## Requirements

- Python 3.11 or later; no third-party Python packages.
- A C++17 compiler for the exhaustive bounded verifier.
- LaTeX for the manuscript PDF.

The code uses only the Python standard library. Tested locally with Python 3.12.13 and Apple Clang.

## Fast deterministic verification

From the repository root:

```bash
python3 -m unittest tests.test_certificates tests.test_matrix_structural -v
```

This verifies the arithmetic support lemmas, the exact parameterized Farkas rows, malformed-input rejection, adversarial certificate mutations, the unbounded integer interval used by family 4, and large-coefficient witnesses for the structural branches.

To inspect the theorem metadata and the finite Boolean certificate:

```bash
python3 -m sag_collatz.matrix_attack > /tmp/matrix-attack.json
python3 -c 'import json; x=json.load(open("/tmp/matrix-attack.json")); print(x["unbounded_relative_matrix2_theorem"])'
```

The printed object must contain `strict_orientation_possible: False` and `collatz_solved: False`.

## Exhaustive bounded verifier

```bash
clang++ -O3 -std=c++17 tools/verify_relative_cubic.cpp -o /tmp/verify-relative-cubic
/tmp/verify-relative-cubic
/tmp/verify-relative-cubic --upper-left-two
/tmp/verify-relative-cubic --upper-left-three
```

These runs exhaust finite coefficient boxes and validate exact integer dual certificates. They are regression evidence for discovery; they are not the proof of unbounded coverage. Larger optional stress runs are documented in `MATRIX_ATTACK.md`.

## Test tiers

Fast manuscript-facing tests:

```bash
make test-fast
```

All Python tests, including expensive bounded enumerations:

```bash
make test-full
```

The full suite is intentionally not the default CI job because several tests enumerate very large finite spaces. No timeout or partial run should be reported as a mathematical failure.

## Mapping manuscript claims to code

| Manuscript item | Executable location |
|---|---|
| Eleven mixed-base rules | `sag_collatz/matrix_attack.py:MIXED_BASE_RULES` |
| Farkas row reconstruction | `_combined_farkas_row`, `_farkas_template_for_assignment` |
| Families 1–12 | `relative_*_deficit_template`, `relative_twelfth_gap_template` |
| Exact free parameter in family 4 | `_smallest_affine_nonpositive_parameter` |
| Structural selector | `relative_structural_farkas_template` |
| Three residual idempotent branches | `relative_idempotent_completion_template` |
| Unbounded theorem scope metadata | `unbounded_relative_matrix2_no_go_theorem` |
| Structural regression tests | `tests/test_matrix_structural.py` |
| Bounded independent enumerator | `tools/verify_relative_cubic.cpp` |

## Trust boundary

The checker establishes: given matrices and a proposed certificate, the original rule inequalities imply an exact contradiction in integer arithmetic.

The paper establishes: every unbounded two-dimensional coefficient assignment either violates a coefficient obligation or belongs to one of the certified structural branches.

The artifact is therefore **computer-assisted and independently checkable**, but it is not a Lean/Coq formalization and does not eliminate the need to review the symbolic coverage proof.

## Releasing the artifact

Before submission:

1. Replace the repository and DOI placeholders in `CITATION.cff`.
2. Create a public Git release tagged `v1.0.0`.
3. Archive that exact tag in Zenodo or an equivalent repository.
4. Put the repository URL and DOI into the manuscript and cover letter.
5. Record SHA-256 checksums of the source archive and PDF.
