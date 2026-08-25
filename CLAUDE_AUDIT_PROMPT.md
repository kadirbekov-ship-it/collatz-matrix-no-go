# Independent audit request for Claude

Audit this repository as a hostile mathematical and code reviewer.  Do not
assume that successful computation proves the Collatz conjecture.

1. Read `REPORT.md`, especially the exact and truncated certificate lemmas.
2. Try to falsify either universal affine inequality algebraically.
3. Inspect `sag_collatz/generator.py` and `sag_collatz/verifier.py` for shared
   hidden assumptions, off-by-one errors at cumulative valuation `A=k`, and an
   incorrect transition from a residue representative to all `q>=0`.
4. Run the tests and the independent verifier commands from `README.md`.
5. Mutate at least one nonzero certificate byte, update its SHA-256 in the JSON,
   and confirm that arithmetic verification still rejects it.
6. Check the reported counts and SHA-256 independently, preferably with a new
   short implementation rather than by importing project code.
7. State clearly whether the finite density theorem is valid.  Treat any leap
   from that theorem to the full Collatz conjecture as a fatal error.

Return: (a) the strongest valid theorem, (b) any counterexample or bug with the
smallest residue that triggers it, and (c) a verdict: verified / inconclusive /
refuted.

