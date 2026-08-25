# Independent hostile audit: global Collatz factor-map boundary

Audit `GLOBAL_ATTACK.md` and `sag_collatz/global_attack.py` independently.
Do not treat finite searches, test coverage, or absence of a counterexample as
a proof of the Collatz conjecture.

## Claims that must be rederived, not merely executed

1. For the accelerated odd map
   \(T(n)=(3n+1)/2^{v_2(3n+1)}\), verify
   \(T^j(2^{s+1}-1)=3^j2^{s+1-j}-1>1\) for \(0\le j\le s\).
   Decide whether this really proves that every data map with image size
   \(s\) has a directed cycle in its factor relation.  In particular, check
   the terminal-state issue that invalidates the naive outdegree proof.

2. Check the infinite-graph criterion carefully.  Acyclicity is sufficient
   only for a finite factor graph.  Globally, an ordinal rank exists exactly
   when the factor relation has no infinite directed path.

3. Reprove or refute the boundary theorem: the following are equivalent to the
   Collatz conjecture.

   - Some noninjective regular data map has a well-founded factor relation.
   - Such a map exists with an infinite fiber.
   - Such a map exists as a one-pass finite-state transduction of canonical
     LSB-first binary words.

   For the backward implications audit both explicit maps:

   - merge every binary word `(10)^k1`, `k>=1`, to `101` and copy every other
     word; prove that these inputs are exactly
     \((4^{k+1}-1)/3\), all map directly to 1, the two-tape graph of the data
     map is regular, and the quotient is well-founded iff Collatz is true;
   - \(f(n)=(T(n),[n=1])\); verify that its nonterminal quotient transition
     from \((m,0)\) is uniquely \(f(m)\), that its fiber over \((1,0)\) is
     infinite, and that `accelerated_odd_step_lsb_transducer` really uses only
     a bounded carry plus a finite output-started flag.

4. Check whether any direction silently assumes the conjecture or confuses a
   finite cycle with an infinite acyclic path.  Pay special attention to the
   meaning of “finite-state transducer”; distinguish a regular two-tape graph,
   an MSB-first subsequential function, and the explicitly claimed LSB-first
   subsequential function.

## Exact finite certificates

Independently verify every entry of
`LOCAL_PATTERN_CYCLE_CERTIFICATES` for radii 1 through 6.  Do not import the
project's signature function in the independent check.  For each stored pair
\((a,b)\), verify \(T(a)=b\).  Then count all substrings of the boundary-marked
word `^bin(n)$` of widths at most the radius and confirm that the target
signature of each pair equals the source signature of the next pair,
cyclically.

Confirm the exact scope: a cycle refutes every arbitrary ranking that factors
through that one fixed signature.  Six checked radii do **not** prove the same
claim for every radius.

## Execution

Run:

```bash
python3 -m unittest discover -s tests -v
python3 -m sag_collatz.global_attack
```

Also write at least one independent short checker rather than relying only on
the repository tests.

## Required verdict

Return:

1. the strongest theorem that is actually proved;
2. the smallest counterexample to any false formulation;
3. whether each transducer classification is correct under its stated input
   direction/model;
4. whether all six local-pattern cycles reproduce independently;
5. one of `verified`, `inconclusive`, or `refuted`;
6. an explicit sentence that the result either does or does not solve the
   Collatz conjecture.
