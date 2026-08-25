# Draft letter to Emre Yolcu and Marijn Heule

**Subject:** A two-dimensional natural-matrix no-go theorem for the mixed-base Collatz SRS

Dear Dr. Yolcu and Prof. Heule,

I have been studying the mixed binary--ternary string-rewriting system
\(\mathcal T\) from your paper *An Automated Approach to the Collatz
Conjecture*. I obtained a no-go result for one specific termination-proof
language used in that setting, and I would be grateful to know whether you
are aware of an existing result that subsumes it.

The statement is the following. For the 11-rule system \(\mathcal T\), there
is no one-stage relative natural affine matrix interpretation of dimension
two in which the two dynamic rules

```text
f> -> >
t> -> 2>
```

are strict and the other nine rules are weak. The result has no bound on the
natural matrix entries or on the natural offset vectors. It does not address
dimensions three and above, other semirings, dependency pairs, or multistage
rule removal, and it does not prove or disprove the Collatz conjecture.

The proof first separates coefficient feasibility from the offset-vector
constraints. In the feasible coefficient region, twelve parametric
nonnegative Farkas certificates cover all cases. Completeness is proved
structurally rather than by bounded enumeration: a first-row growth branch is
closed directly; the complementary branch is reduced using carry equalities
and a Perron--Frobenius rigidity argument; the remaining coefficient matrix
is then one of three idempotent forms, each covered by explicit certificate
families. An exact Python checker reconstructs every Farkas row using integer
arithmetic. Adversarial checks have re-derived the principal rigidity and
classification lemmas, and large finite stress tests have found
no uncovered assignment; these computations are supporting checks, not the
source of the unbounded conclusion.

Before preparing a journal submission, I would particularly value your view
on two questions:

1. Is this dimension-two impossibility result already known, or implied by a
   more general limitation of natural matrix interpretations?
2. If it appears new, would a short technical manuscript with the complete
   proof and reproducible checker be of interest to the rewriting and
   automated-reasoning community?

I can send a concise statement-and-proof summary and the complete artifact.
I would also welcome any correction to the formulation of the relative
termination obligation for \(\mathcal T\).

Thank you for your time and for making the original system and implementation
available.

Best regards,

[Name]\
[Affiliation, if any]\
[Contact information]

---

Original paper: Emre Yolcu, Scott Aaronson, and Marijn J. H. Heule,
*An Automated Approach to the Collatz Conjecture*, Journal of Automated
Reasoning 67, 15 (2023), DOI: 10.1007/s10817-022-09658-8.
