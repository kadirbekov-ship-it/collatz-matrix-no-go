# Hostile audit: matrix-interpretation no-go certificates

Audit `MATRIX_ATTACK.md`, `sag_collatz/matrix_attack.py`, and
`tests/test_matrix_attack.py`.  Reconstruct the 11 rules of the mixed-base
system from the primary paper rather than assuming that the transcription is
correct.

## Scalar theorem

Independently derive the coefficient inequalities from the five named rules.
Check every cancellation uses a positive natural slope.  Confirm or refute
that they force

```text
a_f = a_t = a_0 = a_1 = a_2 = 1
```

and that `carry-f0` then has identical affine interpretations on both sides.
State whether the proof excludes arbitrary natural offsets or merely bounded
ones.

## Dimension-two finite coefficient theorem

The claim is **not** that all 2D natural matrix interpretations fail.  Its
exact scope is:

- every matrix has upper-left entry 1;
- every other matrix entry is in `{0,1,2}`;
- offset vectors range over all of `N^2` without an upper bound;
- all 11 rules must be oriented strictly in one direct interpretation.

Write an independent enumerator.  Confirm:

```text
raw assignments              27^7 = 10,460,353,203
core coefficient survivors                 4,917
full coefficient survivors                299,883
integer Farkas templates                         8
template coverage              189783, 24543, 29457, 26682,
                                 16419, 12495, 432, 72
```

For every surviving matrix assignment, independently form the 22 linear
offset inequalities (strict first coordinate, weak second coordinate).  Verify
that the selected template is a nonnegative integer combination whose 14
left-hand coefficients are all nonpositive while its strict right-hand side
is positive.  Do not use floating-point feasibility as the final check.
Explicitly inject a negative Farkas weight and confirm that the verifier rejects
it before doing arithmetic.

Mutation test: alter a matrix multiplication order, one rule, and one Farkas
weight separately.  Compare the complete per-template coverage vector, not
only its sum: a later template can otherwise hide a damaged earlier one.

## Extended direct theorem and weakened subsystem

Repeat the direct enumeration with upper-left entries in `{1,2}` and all other
entries in `{0,1,2}`.  Confirm:

```text
raw assignments                           54^7 = 1,338,925,209,984
core coefficient survivors                              19,380
full coefficient survivors                           1,169,880
integer Farkas templates                                    14
template coverage  756564, 49086, 147210, 53364, 32838, 24990,
                   864, 144, 64728, 22854, 486, 4176, 7920, 4656
```

Then remove `carry-t0`, `carry-t1`, and `left-1`, restore upper-left entry 1,
and confirm that the same original eight templates cover 712,866 survivors as

```text
418485, 83718, 105453, 50961, 17052, 36693, 432, 72
```

Finally check the scalar first-removal consequence: with all 11 rules weak,
the slope constraints already make the two sides of `carry-f0` identical, so
that rule cannot be made strict on the first scalar rule-removal stage.

## Relative theorem (the proof obligation relevant to Collatz)

Independently confirm from the primary paper that the nine auxiliary rules
form a terminating subsystem.  Then audit the stronger-in-relevance claim:

- only `dynamic-even` and `dynamic-odd` have strict first-coordinate right
  hand side 1;
- all nine auxiliary rules are weak in both coordinates;
- matrices and offsets have the same scope as above.

First rederive the scalar contradiction `b_t > b_2` versus
`b_2 >= b_f + b_t`.  For dimension two independently confirm:

```text
full coefficient survivors                299,883
integer Farkas templates                        22
template coverage  145827, 44529, 61884, 16647, 3645, 72,
                    6792, 1617, 11661, 39, 762, 108, 5406,
                    21, 138, 156, 18, 54, 108, 189, 189, 21
```

The critical mutation is to count an auxiliary first-coordinate inequality as
strict.  The verifier must not do that: only the two dynamic rules may
contribute a positive dual right-hand side.  Confirm that every one of the
299,883 assignments is still closed by exact integer arithmetic.

Then remove the upper-left-entry fixation in this relative theorem.  Let every
matrix entry lie in `{0,1,2}`, with the upper-left entry restricted only to be
positive.  Independently confirm:

```text
raw assignments                           54^7 = 1,338,925,209,984
core coefficient survivors                              19,380
full coefficient survivors                           1,169,880
integer Farkas templates                                    42
template coverage  292338, 89058, 123768, 33294, 7290, 144,
                   222936, 45522, 23322, 78, 1524, 270, 10812,
                   42, 276, 312, 36, 108, 270, 378, 378, 42,
                   230088, 27984, 21360, 78, 4062, 9324, 7062,
                   1482, 480, 4386, 5856, 270, 270, 378, 378,
                   708, 444, 960, 1674, 438
```

Check the full vector, not merely its sum, and verify each selected dual row
with exact integer arithmetic.  In particular, ensure that no direct-proof
template is accidentally accepted by treating a weak auxiliary rule as a
source of strict right-hand side.

Finally audit the separate coefficient-three extension. Compile
`tools/verify_relative_cubic.cpp` and run it without arguments, with
`--upper-left-two`, and with `--upper-left-three`, but also reconstruct enough
of the enumeration
independently to avoid treating that executable as an oracle. Confirm the
base slice:

```text
raw assignments                           64^7 = 4,398,046,511,104
core coefficient survivors                              47,378
full coefficient survivors                           8,546,864
integer Farkas templates                                    47
uncovered assignments                                         0
```

Then confirm the extended slice:

```text
raw assignments                          128^7 = 562,949,953,421,312
core coefficient survivors                             170,450
full coefficient survivors                          33,099,480
integer Farkas templates                                    96
template checksum                         11289329001599812833
uncovered assignments                                         0
```

Finally confirm the complete cube, where every matrix entry is in
`{0,1,2,3}` and the upper-left entry is positive:

```text
raw assignments                        192^7 = 9,618,527,719,784,448
core coefficient survivors                             375,570
full coefficient survivors                          72,169,932
parameterized structural families                           12
structural first-match coverage       52698288, 14886420, 3017712,
                                      255360, 745632, 26208, 71532, 1152,
                                      444192, 12480, 6132, 4824
fixed integer Farkas templates                               103
fixed-template residual coverage                               0
template checksum                         15444582427154671289
uncovered assignments                                         0
```

Check every parameterized row with the same exact 14-coefficient test as a
fixed row.  Independently confirm that the 103-entry fixed-template
first-match vector is now identically zero.  Do not infer the unbounded theorem
from this finite cube: audit the separate structural proof below.
Also reproduce the diagnostic for the original first eight families:
100% on `{0,1}`, 99.4317365884% on `{0,1,2}`, and 99.3520459462% on
`{0,1,2,3}`.  This decreasing trend is the evidence that motivated the four
later formulas; it is not itself an asymptotic theorem.

Compare all three complete coverage descriptions in `MATRIX_ATTACK.md`.
Verify that the C++ checker uses exact integer arithmetic, that its strict
right-hand side can come only from the two dynamic rules, and that all
template checksums agree
with `sag_collatz/matrix_cubic_templates.py`. Explicitly state that the full
coefficient-three cube, including upper-left entry 3, is finite and closed.

Audit the separate unbounded first-row lemma in `MATRIX_ATTACK.md` and
`relative_first_row_growth_template`.  Re-derive the combined offset row for

```text
ell[0] * dynamic-odd[0]
+ ell[1] * dynamic-odd[1]
+ left-2[0]
```

and verify that `ell M_f >= ell` together with the coefficient inequality
`ell M_2 >= ell M_f M_t` makes all 14 coefficients nonpositive while the
strict right-hand side is `ell[0] > 0`.  Check the claimed complement:
failure of `ell M_f >= ell` forces `ell[1] > 0`, the bottom-right entry of
`M_f` to be zero, and `ell[0] (M_f)[0,1] < ell[1]`.  This lemma is only the
first branch; the claimed unbounded conclusion must come from the complete
case analysis in `MATRIX_ATTACK.md`.

Then audit `relative_structural_farkas_template`.  Confirm that all twelve
parameterized rows are accepted only after exact recomputation of the 14
combined coefficients and a positive strict right-hand side.  In family four,
verify the integer interval solver is equivalent to existence of an integer
`x >= 1` satisfying every affine inequality; there must be no hidden `x <= 12`
bound.  Confirm the C++ self-probe whose least feasible value is exactly 13.
Independently derive the second unbounded sufficient condition in
`MATRIX_ATTACK.md` and check its four-parameter projection family.  Also check
the former residual assignment now assigned to family 12. Re-derive its nine
weights and verify the large-coefficient example with `a=37`, `b=113`.

Do not accept a completeness proof that splits only on `f10`, `f01`, and
`b > a`.  Re-derive family 1 in all fourteen offset coordinates.  In the
row-major convention its two `v_t` coefficients are
`a-a*f00-b*f10` and `b-a*f01-b*f11`, and its two right-marker coefficients
are the components of `(a,b)(M_t-M_2)`.  A negative first coefficient cannot
cancel a positive second coefficient.  The unbounded completeness proof must
derive a disjunction of the complete applicability conditions of
families 1--12 from all eleven coefficient-matrix inequalities; finite sparse
and widened runs are evidence only.

Audit the separate diagonal zero-pattern lemma in `MATRIX_ATTACK.md`.  Under
`M_f = diag(u,0)`, `u >= 2`, re-derive from `carry-f0`, `carry-f2`, and
`left-1` that `z10=o10=0`, `d00=o00=x`, and `x>=u^2`.  Check both cases
`z11>0` and `z11=0`, including the strict consequences `g10>0` and
`t01>d01` of `dynamic-odd`.  In the second case verify that the two
upper-right carry inequalities force simultaneously
`u>t11>=d11` and
`d01*(u-t11) >= t01*(x-d11)`, which is impossible.  Also verify the warning
example showing that carry plus left alone do not prove the lemma.

Then audit the upper-triangular extension `M_f=[[u,p],[0,0]]`, `p>0`.
Check equations (C)--(F), especially the strict contradiction obtained from
assuming `t00<u`: `p*d10 >= z01*t10 > p*d10`.  After deriving `t00=u`,
verify that `z01>0` forces `t10=0` and that the two cases `t11=0` and
`t11>0` both reduce to the same `carry-t2` contradiction as the diagonal
branch.  No finite coefficient bound may enter this derivation.

Audit also the completed lower-triangular branch
`M_f=[[u,0],[r,0]]`, `r>0`.  Use determinant rigidity to justify both
equalities in (H), then derive `t10*t01=0` and equation (I).  Check carefully
that the assumption `t01>0` forces `z11>z00` while `carry-f0` gives
`z11<=z00`; hence `t01=0,t00=u`.  Finally re-derive `d00>=u^2` and the
contradiction with the upper coordinate of `dynamic-odd`.  The tempting
stronger statement `rho(T)<=u` is false and must not be used.

Audit the next two exact branches on the complement `f11=0`, `a*f01<b`.
Family 2 must be equivalent there to `f10=0`, `(M_0)11>=1`, and
`a*(M_2)01+b*(M_2)11 >= a*(f01+(M_t)01)`.  Family 3 must be equivalent to
`(M_t)10=(M_t)11=0`, `(M_2)11>=1`, and
`a*(M_2)01+b >= a*(f01+(M_t)01)`.  Derive the forced zero entries from the
matrix inequalities rather than finite data, then recompute both returned
Farkas rows exactly.

Audit family 4 on the same complement.  Its exact certificate uses a common
integer weight `x>=1` on `dynamic-even[1]`, `dynamic-odd[1]`, and
`carry-t2[1]`.  Re-derive all affine coefficient rows and verify that they are
equivalent to the seven displayed constraints in `MATRIX_ATTACK.md`, including
`x<=b` and `t10=0`.  Check that the interval solver returns the least feasible
integer and that the concrete example is rejected by families 1--3 but accepted
by family 4 with `x=1`.

Audit the carry-diagonal lemma.  Use trace cyclicity to show that `carry-f0`
and `carry-t2` have equality on both diagonal coordinates, and that the four
rules `carry-f1`, `carry-t0`, `carry-t1`, `carry-f2` form a closed trace chain,
forcing their diagonal coordinates to be equal as well.  Do not accept the
empirical claim `f00=1` on the family-1 complement unless it is derived from
these equalities and the left-marker inequalities without a coefficient bound.

Also audit the determinant-rigidity strengthening.  Once the carry products
have equal diagonals, componentwise dominance reverses determinant order.
Check that the four-rule determinant chain closes and that `carry-f0` and
`carry-t2` have equal determinants by cyclicity.  Verify the conclusion that
strict off-diagonal slack can occur only when at least one corresponding
off-diagonal coordinate is zero.

Audit the fully off-diagonal Perron branch independently.  First verify the
identity

```text
sum(carry slacks) = (F+T)(Z+O+D) - (Z+O+D)(F+T)
```

and use positive left and right Perron vectors of the irreducible matrix
`F+T` to prove that every carry slack is zero.  In rank one of `D`, check the
outer-product argument through `TFD=D F^2`, the derivation `F c=lambda c`,
and the final `left-2`/`dynamic-odd` contradiction.  In rank two, verify both
similarities in (M), the common characteristic polynomial of `F,T`, and the
eigenbasis argument excluding the lower-left entry of `T`.  Re-derive the
incompatible bounds `delta>=lambda^2` and `delta<=lambda`.  This branch is
claimed for every `u,p,r>=1`, not merely a finite cube.

Before accepting the final case split, audit its exhaustiveness explicitly.
On the family-1 complement derive `f11=0`; use strict monotonicity to retain
`f00>=1`; use the four zero-pattern lemmas to obtain `f00=1`; and use the
fully off-diagonal lemma to obtain `f01*f10=0`.  Then multiply
`F=[[1,p],[r,0]]` by itself and verify that `pr=0` gives `F^2=F` and exactly
the three cases `(p,r)=(0,0)`, `p>0,r=0`, and `p=0,r>0`.  Treat any fourth
remaining form as fatal.

Finally audit the three idempotent forms.  For `F=[[1,0],[r,0]]`, derive every
condition of family 5.  For `F=diag(1,0)`, verify the split `z11>=1` versus
`z11=0` and the exhaustive subcases leading to families 2--6.  For
`F=[[1,p],[0,0]]`, prove `t10=0` first, re-derive all scalar inequalities (N),
and check the six cases `w=0 or >0` crossed with `e=0,1,>=2`; they must lead
to families 4 or 12 with no coefficient bound.  Treat any missing sign
condition or uncovered subcase as fatal to the unbounded theorem.

## Required verdict

Return:

1. strongest theorem actually established;
2. any transcription, composition-order, or off-by-one error;
3. independent survivor and coverage counts;
4. whether unbounded vectors are genuinely covered;
5. explicit scope not covered: dimensions above 2, arctic/tropical
   interpretations, dependency pairs, and relative/staged proofs outside the
   exact one-stage class above; do not list entries above 3 if the structural
   proof verifies;
6. `verified`, `inconclusive`, or `refuted`;
7. an explicit statement that this is or is not a proof of Collatz.

Primary source:
https://doi.org/10.1007/s10817-022-09658-8
