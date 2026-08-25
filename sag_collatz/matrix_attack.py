"""Exact no-go certificates for natural affine matrix interpretations.

The mixed binary--ternary rewriting system is the 11-rule system ``T`` from
Yolcu--Aaronson--Heule (arXiv:2105.14697).  This module does not attempt to
prove or disprove termination.  It refutes several direct and relative proof
languages, including the unbounded two-dimensional natural rule-removal
obligation with only the two Collatz rules strict.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from functools import cache
from itertools import product
from typing import Any, Mapping

from .matrix_cubic_templates import (
    RELATIVE_CUBIC_2D_FARKAS_TEMPLATES,
    RELATIVE_CUBIC_EXTENDED_2D_FARKAS_TEMPLATES,
)


Symbol = str
Word = tuple[Symbol, ...]
Rule = tuple[Word, Word]


MIXED_BASE_RULES: dict[str, Rule] = {
    "dynamic-even": (("f", ">"), (">",)),
    "dynamic-odd": (("t", ">"), ("2", ">")),
    "carry-f0": (("f", "0"), ("0", "f")),
    "carry-f1": (("f", "1"), ("0", "t")),
    "carry-f2": (("f", "2"), ("1", "f")),
    "carry-t0": (("t", "0"), ("1", "t")),
    "carry-t1": (("t", "1"), ("2", "f")),
    "carry-t2": (("t", "2"), ("2", "t")),
    "left-0": (("<", "0"), ("<", "t")),
    "left-1": (("<", "1"), ("<", "f", "f")),
    "left-2": (("<", "2"), ("<", "f", "t")),
}


Matrix2 = tuple[int, int, int, int]


# Nonnegative integer combinations of componentwise vector inequalities.  A
# row ``(rule, component, weight)`` uses component 0 (strict, right-hand side
# 1) or component 1 (weak, right-hand side 0) of that rule.  For every
# surviving Boolean matrix assignment, at least one template has a
# nonpositive combined left-hand coefficient vector and a positive combined
# right-hand side, hence certifies 0 >= 1.
BOOLEAN_2D_FARKAS_TEMPLATES: tuple[tuple[tuple[str, int, int], ...], ...] = (
    (("carry-f0", 0, 1),),
    (("dynamic-odd", 0, 1), ("left-2", 0, 1)),
    (("carry-t2", 0, 1),),
    (("dynamic-odd", 0, 1), ("dynamic-odd", 1, 1), ("left-2", 0, 1)),
)


SMALL_2D_FARKAS_TEMPLATES = BOOLEAN_2D_FARKAS_TEMPLATES + (
    (
        ("dynamic-odd", 0, 5), ("dynamic-odd", 1, 6),
        ("carry-f1", 0, 2), ("carry-f1", 1, 2),
        ("carry-f2", 0, 2), ("carry-f2", 1, 2),
        ("left-0", 0, 1), ("left-2", 0, 2),
    ),
    (("dynamic-odd", 0, 1), ("dynamic-odd", 1, 2), ("left-2", 0, 1)),
    (
        ("dynamic-even", 0, 2), ("dynamic-odd", 0, 2),
        ("dynamic-odd", 1, 6), ("carry-f0", 0, 4),
        ("carry-f1", 1, 4), ("carry-t2", 0, 1), ("left-2", 0, 2),
    ),
    (
        ("dynamic-odd", 0, 4), ("dynamic-odd", 1, 8),
        ("carry-f0", 1, 2), ("carry-f1", 0, 2),
        ("carry-f2", 0, 2), ("carry-f2", 1, 2),
        ("carry-t2", 0, 1), ("left-0", 0, 1), ("left-2", 0, 2),
    ),
)


EXTENDED_SMALL_2D_FARKAS_TEMPLATES = SMALL_2D_FARKAS_TEMPLATES + (
    (("dynamic-odd", 1, 1), ("carry-t2", 0, 1)),
    (("carry-f0", 0, 1), ("carry-f0", 1, 1)),
    (("dynamic-odd", 0, 1), ("left-2", 1, 1)),
    (("carry-t2", 0, 1), ("carry-t2", 1, 1)),
    (("dynamic-odd", 1, 2), ("carry-t2", 0, 1)),
    (("carry-f0", 0, 1), ("carry-f0", 1, 2)),
)


DIRECT_EIGHT_RULE_SUBSYSTEM = frozenset(MIXED_BASE_RULES) - frozenset(
    ("carry-t0", "carry-t1", "left-1")
)


# Exact dual certificates for the proof obligation that actually matters for
# Collatz: the two dynamic rules are strict while the nine base-conversion
# rules are merely weak.  The matrices still range over {0,1,2}; the vector
# offsets are arbitrary nonnegative integers.  Floating-point LP was used only
# to discover these rows.  Verification below is entirely integer arithmetic.
RELATIVE_SMALL_2D_FARKAS_TEMPLATES: tuple[
    tuple[tuple[str, int, int], ...], ...
] = (
    (("dynamic-odd", 0, 1), ("left-2", 0, 1)),
    (("dynamic-odd", 0, 1), ("dynamic-odd", 1, 1), ("left-2", 0, 1)),
    (
        ("dynamic-odd", 0, 5), ("dynamic-odd", 1, 6),
        ("carry-f1", 0, 2), ("carry-f1", 1, 2),
        ("carry-f2", 0, 2), ("carry-f2", 1, 2),
        ("left-0", 0, 1), ("left-2", 0, 2),
    ),
    (("dynamic-odd", 0, 1), ("dynamic-odd", 1, 2), ("left-2", 0, 1)),
    (
        ("dynamic-even", 0, 2), ("dynamic-odd", 0, 2),
        ("dynamic-odd", 1, 6), ("carry-f0", 0, 4),
        ("carry-f1", 1, 4), ("carry-t2", 0, 1), ("left-2", 0, 2),
    ),
    (
        ("dynamic-odd", 0, 4), ("dynamic-odd", 1, 8),
        ("carry-f0", 1, 2), ("carry-f1", 0, 2),
        ("carry-f2", 0, 2), ("carry-f2", 1, 2),
        ("carry-t2", 0, 1), ("left-0", 0, 1), ("left-2", 0, 2),
    ),
    (
        ("dynamic-odd", 0, 2), ("dynamic-odd", 1, 3),
        ("carry-f0", 1, 1), ("carry-f1", 0, 1), ("carry-f1", 1, 1),
        ("carry-f2", 1, 2), ("carry-t0", 0, 1), ("left-2", 0, 1),
    ),
    (
        ("dynamic-odd", 0, 2), ("dynamic-odd", 1, 3),
        ("carry-f0", 1, 2), ("carry-f1", 0, 1),
        ("carry-f2", 1, 1), ("carry-t0", 0, 1), ("carry-t0", 1, 1),
        ("left-2", 0, 1),
    ),
    (
        ("dynamic-even", 0, 2), ("dynamic-odd", 0, 3),
        ("dynamic-odd", 1, 1), ("carry-f0", 1, 1),
        ("carry-f1", 0, 1), ("carry-f2", 0, 2), ("carry-f2", 1, 1),
        ("left-0", 0, 1), ("left-1", 0, 1), ("left-2", 0, 1),
    ),
    (
        ("dynamic-even", 0, 3), ("dynamic-even", 1, 2),
        ("dynamic-odd", 0, 3), ("dynamic-odd", 1, 2),
        ("carry-f1", 0, 1), ("carry-f2", 0, 1), ("carry-f2", 1, 1),
        ("carry-t0", 0, 1), ("left-1", 0, 1), ("left-2", 0, 2),
    ),
    (
        ("dynamic-even", 0, 1), ("dynamic-even", 1, 1),
        ("dynamic-odd", 0, 1), ("carry-t2", 1, 1), ("left-2", 0, 1),
    ),
    (
        ("dynamic-even", 0, 4), ("dynamic-odd", 0, 6),
        ("carry-f1", 0, 1), ("carry-f1", 1, 1),
        ("carry-f2", 0, 3), ("carry-f2", 1, 1), ("carry-t2", 1, 1),
        ("left-0", 0, 1), ("left-1", 0, 1), ("left-2", 0, 1),
    ),
    (
        ("dynamic-even", 0, 2), ("dynamic-odd", 0, 3),
        ("dynamic-odd", 1, 2), ("carry-f0", 1, 2),
        ("carry-f1", 0, 1), ("carry-f2", 0, 2), ("carry-f2", 1, 2),
        ("left-0", 0, 1), ("left-1", 0, 1), ("left-2", 0, 1),
    ),
    (
        ("dynamic-even", 0, 3), ("dynamic-even", 1, 4),
        ("dynamic-odd", 0, 3), ("dynamic-odd", 1, 4),
        ("carry-f1", 0, 1), ("carry-f2", 0, 1), ("carry-f2", 1, 2),
        ("carry-t0", 0, 1), ("left-1", 0, 1), ("left-2", 0, 2),
    ),
    (
        ("dynamic-even", 0, 1), ("dynamic-even", 1, 1),
        ("dynamic-odd", 0, 1), ("carry-t2", 1, 2), ("left-2", 0, 1),
    ),
    (
        ("dynamic-even", 0, 1), ("dynamic-even", 1, 2),
        ("dynamic-odd", 0, 1), ("carry-t2", 1, 2), ("left-2", 0, 1),
    ),
    (
        ("dynamic-even", 0, 2), ("dynamic-odd", 0, 2),
        ("dynamic-odd", 1, 2), ("carry-f1", 1, 1), ("left-2", 0, 2),
    ),
    (
        ("dynamic-even", 0, 2), ("dynamic-even", 1, 2),
        ("dynamic-odd", 0, 2), ("dynamic-odd", 1, 1),
        ("carry-t2", 1, 1), ("left-2", 0, 2),
    ),
    (
        ("dynamic-even", 0, 6), ("dynamic-odd", 0, 9),
        ("carry-f1", 0, 1), ("carry-f1", 1, 2),
        ("carry-f2", 0, 4), ("carry-f2", 1, 2), ("carry-t2", 1, 2),
        ("left-0", 0, 1), ("left-1", 0, 1), ("left-2", 0, 1),
    ),
    (
        ("dynamic-even", 0, 6), ("dynamic-odd", 0, 9),
        ("carry-f1", 0, 1), ("carry-f1", 1, 1),
        ("carry-f2", 0, 4), ("carry-f2", 1, 1), ("carry-t2", 1, 1),
        ("left-0", 0, 1), ("left-1", 0, 1), ("left-2", 0, 1),
    ),
    (
        ("dynamic-even", 0, 10), ("dynamic-odd", 0, 15),
        ("carry-f1", 0, 1), ("carry-f1", 1, 2),
        ("carry-f2", 0, 6), ("carry-f2", 1, 2), ("carry-t2", 1, 2),
        ("left-0", 0, 1), ("left-1", 0, 1), ("left-2", 0, 1),
    ),
    (
        ("dynamic-even", 0, 3), ("dynamic-even", 1, 6),
        ("dynamic-odd", 0, 5), ("dynamic-odd", 1, 8),
        ("carry-f1", 0, 1), ("carry-f2", 1, 1),
        ("carry-t0", 0, 1), ("left-2", 0, 4),
    ),
)


# Extends the relative rule-removal theorem from upper-left entry 1 to every
# positive upper-left entry in the same coefficient domain {0,1,2}.  These 20
# additional exact integer dual rows close precisely the newly admitted
# assignments; the first 22 rows above remain unchanged.
RELATIVE_EXTENDED_SMALL_2D_FARKAS_TEMPLATES = (
    RELATIVE_SMALL_2D_FARKAS_TEMPLATES
    + (
        (("dynamic-even", 0, 2), ("dynamic-odd", 0, 2), ("left-2", 0, 1)),
        (
            ("dynamic-even", 0, 4), ("dynamic-odd", 0, 6),
            ("dynamic-odd", 1, 1), ("carry-f0", 1, 1),
            ("carry-f1", 0, 2), ("carry-f2", 0, 4),
            ("carry-f2", 1, 1), ("left-0", 0, 1),
            ("left-1", 0, 1), ("left-2", 0, 1),
        ),
        (
            ("dynamic-even", 0, 4), ("dynamic-odd", 0, 6),
            ("dynamic-odd", 1, 2), ("carry-f0", 1, 2),
            ("carry-f1", 0, 2), ("carry-f2", 0, 4),
            ("carry-f2", 1, 2), ("left-0", 0, 1),
            ("left-1", 0, 1), ("left-2", 0, 1),
        ),
        (
            ("dynamic-even", 0, 10), ("dynamic-even", 1, 4),
            ("dynamic-odd", 0, 10), ("dynamic-odd", 1, 4),
            ("carry-f1", 0, 2), ("carry-f2", 0, 2),
            ("carry-f2", 1, 1), ("carry-t0", 0, 2),
            ("left-1", 0, 1), ("left-2", 0, 4),
        ),
        (
            ("dynamic-even", 0, 6), ("dynamic-even", 1, 4),
            ("dynamic-odd", 0, 8), ("dynamic-odd", 1, 4),
            ("carry-f0", 1, 2), ("carry-f1", 0, 2),
            ("carry-f2", 0, 4), ("carry-f2", 1, 2),
            ("left-0", 0, 1), ("left-1", 0, 1), ("left-2", 0, 2),
        ),
        (
            ("dynamic-even", 0, 2), ("dynamic-even", 1, 2),
            ("dynamic-odd", 0, 2), ("carry-t2", 1, 2), ("left-2", 0, 1),
        ),
        (
            ("dynamic-even", 0, 4), ("dynamic-odd", 0, 4),
            ("dynamic-odd", 1, 2), ("carry-f1", 1, 1), ("left-2", 0, 2),
        ),
        (
            ("dynamic-even", 0, 2), ("dynamic-odd", 0, 2),
            ("dynamic-odd", 1, 1), ("carry-t2", 1, 1), ("left-2", 0, 1),
        ),
        (
            ("dynamic-even", 0, 2), ("dynamic-even", 1, 2),
            ("dynamic-odd", 0, 2), ("dynamic-odd", 1, 1),
            ("carry-t2", 1, 1), ("left-2", 0, 1),
        ),
        (
            ("dynamic-even", 0, 2), ("dynamic-odd", 0, 2),
            ("dynamic-odd", 1, 1), ("left-2", 0, 1),
        ),
        (
            ("dynamic-even", 0, 2), ("dynamic-odd", 0, 2),
            ("dynamic-odd", 1, 2), ("left-2", 0, 1),
        ),
        (
            ("dynamic-even", 0, 6), ("dynamic-odd", 0, 9),
            ("carry-f1", 0, 2), ("carry-f1", 1, 1),
            ("carry-f2", 0, 5), ("carry-f2", 1, 1),
            ("carry-t2", 1, 1), ("left-0", 0, 1),
            ("left-1", 0, 1), ("left-2", 0, 1),
        ),
        (
            ("dynamic-even", 0, 8), ("dynamic-odd", 0, 12),
            ("carry-f1", 0, 2), ("carry-f1", 1, 2),
            ("carry-f2", 0, 6), ("carry-f2", 1, 2),
            ("carry-t2", 1, 2), ("left-0", 0, 1),
            ("left-1", 0, 1), ("left-2", 0, 1),
        ),
        (
            ("dynamic-even", 0, 8), ("dynamic-odd", 0, 12),
            ("carry-f1", 0, 2), ("carry-f1", 1, 1),
            ("carry-f2", 0, 6), ("carry-f2", 1, 1),
            ("carry-t2", 1, 1), ("left-0", 0, 1),
            ("left-1", 0, 1), ("left-2", 0, 1),
        ),
        (
            ("dynamic-even", 0, 12), ("dynamic-odd", 0, 18),
            ("carry-f1", 0, 2), ("carry-f1", 1, 2),
            ("carry-f2", 0, 8), ("carry-f2", 1, 2),
            ("carry-t2", 1, 2), ("left-0", 0, 1),
            ("left-1", 0, 1), ("left-2", 0, 1),
        ),
        (
            ("dynamic-even", 0, 2), ("dynamic-even", 1, 2),
            ("dynamic-odd", 0, 2), ("dynamic-odd", 1, 2),
            ("left-2", 0, 1),
        ),
        (
            ("dynamic-even", 0, 1), ("dynamic-odd", 0, 2),
            ("dynamic-odd", 1, 1), ("left-2", 0, 1),
        ),
        (
            ("dynamic-even", 0, 1), ("dynamic-even", 1, 1),
            ("dynamic-odd", 0, 2), ("dynamic-odd", 1, 1),
            ("left-2", 0, 1),
        ),
        (("dynamic-odd", 0, 2), ("left-2", 0, 1)),
        (("dynamic-odd", 0, 2), ("dynamic-odd", 1, 2), ("left-2", 0, 1)),
    )
)


def _matrix2_multiply(left: Matrix2, right: Matrix2) -> Matrix2:
    a, b, c, d = left
    e, f, g, h = right
    return (
        a * e + b * g,
        a * f + b * h,
        c * e + d * g,
        c * f + d * h,
    )


def _matrix2_dominates(left: Matrix2, right: Matrix2) -> bool:
    return all(a >= b for a, b in zip(left, right))


def _matrix2_word(word: Word, matrices: Mapping[Symbol, Matrix2]) -> Matrix2:
    result: Matrix2 = (1, 0, 0, 1)
    for symbol in word:
        result = _matrix2_multiply(result, matrices[symbol])
    return result


def _offset_coefficients(
    word: Word, matrices: Mapping[Symbol, Matrix2], symbol_index: Mapping[Symbol, int]
) -> tuple[tuple[int, ...], tuple[int, ...]]:
    """Return the two linear forms in all 14 vector-offset coordinates."""

    coefficients = [[0] * 14 for _ in range(2)]
    prefix: Matrix2 = (1, 0, 0, 1)
    for symbol in word:
        column = 2 * symbol_index[symbol]
        coefficients[0][column] += prefix[0]
        coefficients[0][column + 1] += prefix[1]
        coefficients[1][column] += prefix[2]
        coefficients[1][column + 1] += prefix[3]
        prefix = _matrix2_multiply(prefix, matrices[symbol])
    return tuple(coefficients[0]), tuple(coefficients[1])


def _coefficient_assignment_dominates(matrices: Mapping[Symbol, Matrix2]) -> bool:
    for lhs, rhs in MIXED_BASE_RULES.values():
        if not _matrix2_dominates(
            _matrix2_word(lhs, matrices), _matrix2_word(rhs, matrices)
        ):
            return False
    return True


def _farkas_template_for_assignment(
    matrices: Mapping[Symbol, Matrix2],
    templates: tuple[tuple[tuple[str, int, int], ...], ...],
    strict_rules: frozenset[str] | None = None,
) -> int | None:
    if strict_rules is None:
        strict_rules = frozenset(MIXED_BASE_RULES)
    unknown_strict_rules = strict_rules - frozenset(MIXED_BASE_RULES)
    if unknown_strict_rules:
        raise ValueError(f"unknown strict rules: {sorted(unknown_strict_rules)}")
    for template in templates:
        for rule_name, component, weight in template:
            if rule_name not in MIXED_BASE_RULES:
                raise ValueError(f"unknown rule in Farkas template: {rule_name}")
            if component not in (0, 1):
                raise ValueError(f"invalid Farkas component: {component}")
            if not isinstance(weight, int) or isinstance(weight, bool) or weight < 0:
                raise ValueError(
                    f"Farkas weights must be nonnegative integers: {weight!r}"
                )
    symbols = ("f", "t", "0", "1", "2", "<", ">")
    symbol_index = {symbol: index for index, symbol in enumerate(symbols)}
    differences: dict[tuple[str, int], tuple[int, ...]] = {}
    for name, (lhs, rhs) in MIXED_BASE_RULES.items():
        lhs_rows = _offset_coefficients(lhs, matrices, symbol_index)
        rhs_rows = _offset_coefficients(rhs, matrices, symbol_index)
        for component in (0, 1):
            differences[(name, component)] = tuple(
                left - right
                for left, right in zip(lhs_rows[component], rhs_rows[component])
            )
    for template_index, template in enumerate(templates):
        combined = [0] * 14
        strict_right_hand_side = 0
        for rule_name, component, weight in template:
            row = differences[(rule_name, component)]
            for index, coefficient in enumerate(row):
                combined[index] += weight * coefficient
            if component == 0 and rule_name in strict_rules:
                strict_right_hand_side += weight
        if strict_right_hand_side > 0 and all(value <= 0 for value in combined):
            return template_index
    return None


_MATRIX_SYMBOLS = frozenset(("f", "t", "0", "1", "2", "<", ">"))
_RELATIVE_STRICT_RULES = frozenset(("dynamic-even", "dynamic-odd"))


def _validate_natural_matrix_assignment(
    matrices: Mapping[Symbol, Matrix2],
) -> None:
    if frozenset(matrices) != _MATRIX_SYMBOLS:
        raise ValueError("matrix assignment must define exactly the seven symbols")
    for symbol, matrix in matrices.items():
        if (
            len(matrix) != 4
            or any(
                not isinstance(value, int)
                or isinstance(value, bool)
                or value < 0
                for value in matrix
            )
            or matrix[0] < 1
        ):
            raise ValueError(f"invalid natural matrix for symbol {symbol!r}")


def _combined_farkas_row(
    matrices: Mapping[Symbol, Matrix2],
    template: tuple[tuple[str, int, int], ...],
) -> tuple[tuple[int, ...], int]:
    """Return the exact coefficient row and relative strict right-hand side."""

    symbols = ("f", "t", "0", "1", "2", "<", ">")
    symbol_index = {symbol: index for index, symbol in enumerate(symbols)}
    combined = [0] * 14
    strict_right_hand_side = 0
    for rule_name, component, weight in template:
        lhs, rhs = MIXED_BASE_RULES[rule_name]
        lhs_rows = _offset_coefficients(lhs, matrices, symbol_index)
        rhs_rows = _offset_coefficients(rhs, matrices, symbol_index)
        for index, (left, right) in enumerate(
            zip(lhs_rows[component], rhs_rows[component])
        ):
            combined[index] += weight * (left - right)
        if component == 0 and rule_name in _RELATIVE_STRICT_RULES:
            strict_right_hand_side += weight
    return tuple(combined), strict_right_hand_side


def _positive_terms(
    template: tuple[tuple[str, int, int], ...],
) -> tuple[tuple[str, int, int], ...]:
    return tuple(term for term in template if term[2] > 0)


def _smallest_affine_nonpositive_parameter(
    base_row: tuple[int, ...], slope_row: tuple[int, ...]
) -> int | None:
    """Find the least integer ``x >= 1`` with ``base + x*slope <= 0``."""

    if len(base_row) != len(slope_row):
        raise ValueError("affine coefficient rows must have equal length")
    lower = 1
    upper: int | None = None
    for constant, coefficient in zip(base_row, slope_row):
        if coefficient == 0:
            if constant > 0:
                return None
        elif coefficient > 0:
            bound = (-constant) // coefficient
            upper = bound if upper is None else min(upper, bound)
        else:
            bound = -(-constant // (-coefficient))
            lower = max(lower, bound)
    if upper is not None and lower > upper:
        return None
    return lower


def _family_four_parameter(
    matrices: Mapping[Symbol, Matrix2], a: int
) -> int | None:
    """Solve the fourth structural family's integer parameter exactly."""

    base = (
        ("dynamic-even", 0, a),
        ("dynamic-odd", 0, a),
        ("left-2", 0, 1),
    )
    slope = (
        ("dynamic-even", 1, 1),
        ("dynamic-odd", 1, 1),
        ("carry-t2", 1, 1),
    )
    base_row, _ = _combined_farkas_row(matrices, base)
    slope_row, _ = _combined_farkas_row(matrices, slope)
    return _smallest_affine_nonpositive_parameter(base_row, slope_row)


def relative_structural_farkas_template(
    matrices: Mapping[Symbol, Matrix2],
) -> tuple[int, tuple[tuple[str, int, int], ...]] | None:
    """Find one of twelve exact parametric relative no-go certificates.

    Unlike the finite cube enumerator, this constructor has no coefficient
    ceiling.  A returned pair is ``(family_number, template)`` with family
    numbers 1 through 12.  The structural theorem in ``MATRIX_ATTACK.md``
    proves that these rows cover every natural 2D assignment satisfying all
    eleven coefficient inequalities.  ``None`` is reserved for assignments
    that already fail a coefficient inequality.
    """

    _validate_natural_matrix_assignment(matrices)
    if not _coefficient_assignment_dominates(matrices):
        return None

    a, b = matrices["<"][:2]
    f10 = matrices["f"][2]
    candidates: list[tuple[int, tuple[tuple[str, int, int], ...]]] = [
        (1, _positive_terms((
            ("dynamic-odd", 0, a),
            ("dynamic-odd", 1, b),
            ("left-2", 0, 1),
        ))),
        (2, _positive_terms((
            ("dynamic-even", 0, a),
            ("dynamic-odd", 0, a),
            ("dynamic-odd", 1, b),
            ("carry-f1", 1, b),
            ("left-2", 0, 1),
        ))),
        (3, _positive_terms((
            ("dynamic-even", 0, a),
            ("dynamic-even", 1, b),
            ("dynamic-odd", 0, a),
            ("carry-t2", 1, b),
            ("left-2", 0, 1),
        ))),
    ]
    parameter = _family_four_parameter(matrices, a)
    if parameter is not None:
        candidates.append((4, _positive_terms((
            ("dynamic-even", 0, a),
            ("dynamic-even", 1, parameter),
            ("dynamic-odd", 0, a),
            ("dynamic-odd", 1, parameter),
            ("carry-t2", 1, parameter),
            ("left-2", 0, 1),
        ))))
    scale = a + b * f10
    deficit = max(0, b - a)
    eighth_scale = (deficit + 3) // 4
    candidates.extend((
        (5, _positive_terms((
            ("dynamic-even", 0, 2 * scale),
            ("dynamic-odd", 0, 3 * scale),
            ("carry-f1", 0, a),
            ("carry-f1", 1, b),
            ("carry-f2", 0, 2 * a + b * f10),
            ("carry-f2", 1, b),
            ("carry-t2", 1, b),
            ("left-0", 0, 1),
            ("left-1", 0, 1),
            ("left-2", 0, 1),
        ))),
        (6, _positive_terms((
            ("dynamic-even", 0, 3 * a),
            ("dynamic-odd", 0, 3 * a),
            ("carry-f1", 0, a),
            ("carry-f2", 0, a),
            ("carry-f2", 1, 3 * b),
            ("carry-t0", 0, a),
            ("carry-t1", 1, 2 * b),
            ("left-1", 0, 1),
            ("left-2", 0, 2),
        ))),
        (7, _positive_terms((
            ("dynamic-even", 0, a),
            ("dynamic-odd", 0, a),
            ("dynamic-odd", 1, b),
            ("carry-t2", 0, deficit),
            ("left-2", 0, 1),
        ))),
        (8, _positive_terms((
            ("dynamic-odd", 0, a),
            ("dynamic-odd", 1, b),
            ("carry-f1", 0, eighth_scale),
            ("carry-f2", 1, eighth_scale),
            ("carry-t0", 0, eighth_scale),
            ("left-2", 0, 1),
        ))),
    ))
    f01 = matrices["f"][1]
    t01 = matrices["t"][1]
    fallback_scale = max(1, b - 1)
    candidates.extend((
        (9, _positive_terms((
            ("dynamic-odd", 0, a),
            ("dynamic-odd", 1, b),
            ("carry-f0", 1, t01),
            ("carry-f1", 0, 1),
            ("carry-f2", 1, f01),
            ("carry-t0", 0, 1),
            ("left-2", 0, 1),
        ))),
        (10, _positive_terms((
            ("dynamic-odd", 0, fallback_scale),
            ("dynamic-odd", 1, b),
            ("carry-f0", 1, 1),
            ("carry-f1", 0, 1),
            ("carry-f1", 1, 1),
            ("carry-f2", 1, fallback_scale),
            ("carry-t0", 0, 1),
            ("left-2", 0, 1),
        ))),
        (11, _positive_terms((
            ("dynamic-odd", 0, b * (a + 1)),
            ("dynamic-odd", 1, b * (f01 + b)),
            ("carry-f1", 0, b),
            ("carry-f1", 1, b),
            ("carry-f2", 0, b),
            ("carry-f2", 1, b * f01),
            ("left-0", 0, 1),
            ("left-2", 0, b),
        ))),
    ))
    # The twelfth family is obtained by fixing one dual support and eliminating
    # its free weights algebraically.  It targets the triangular first-row
    # deficit left after families 1--11.  All weights are functions of matrix
    # entries, with no coefficient ceiling.
    z, z11 = matrices["0"][1], matrices["0"][3]
    o, o11 = matrices["1"][1], matrices["1"][3]
    d11 = matrices["2"][3]
    twelfth_weights = (
        ("dynamic-even", 1, a * (o - f01 * (1 - o11))),
        ("dynamic-odd", 0, 3 * a),
        ("dynamic-odd", 1, b + a * f01 + d11 * (a * z + b * z11)),
        ("carry-f1", 0, a),
        ("carry-f1", 1, b),
        ("carry-f2", 0, a),
        ("carry-f2", 1, a * f01),
        ("left-0", 0, 1),
        ("left-2", 0, 1),
    )
    if all(weight >= 0 for _, _, weight in twelfth_weights):
        candidates.append((12, _positive_terms(twelfth_weights)))
    for family, template in candidates:
        if _farkas_template_for_assignment(
            matrices, (template,), _RELATIVE_STRICT_RULES
        ) == 0:
            return family, template
    raise AssertionError(
        "unbounded 2D structural coverage theorem violated by assignment"
    )


def relative_first_row_growth_template(
    matrices: Mapping[Symbol, Matrix2],
) -> tuple[tuple[str, int, int], ...] | None:
    """Return an unbounded relative no-go row when the first row grows by ``f``.

    Write ``ell`` for the first row of the left-marker matrix.  If all eleven
    coefficient inequalities hold and ``ell M_f >= ell`` componentwise, then
    the coefficient inequality for ``left-2`` gives

        ell M_2 >= ell M_f M_t >= ell M_t.

    Consequently ``ell[0]`` copies of component zero of ``dynamic-odd``,
    ``ell[1]`` copies of component one, and one copy of component zero of
    ``left-2`` have a positive strict right-hand side and a nonpositive
    combined coefficient vector.  The argument has no coefficient bound.
    """

    _validate_natural_matrix_assignment(matrices)
    if not _coefficient_assignment_dominates(matrices):
        return None

    left = matrices["<"]
    left_f = _matrix2_multiply(left, matrices["f"])
    if left_f[0] < left[0] or left_f[1] < left[1]:
        return None

    template = (
        ("dynamic-odd", 0, left[0]),
        ("dynamic-odd", 1, left[1]),
        ("left-2", 0, 1),
    )
    if _farkas_template_for_assignment(
        matrices,
        (template,),
        _RELATIVE_STRICT_RULES,
    ) != 0:
        raise AssertionError("derived first-row certificate failed exact verification")
    return template


def relative_second_deficit_template(
    matrices: Mapping[Symbol, Matrix2],
) -> tuple[tuple[str, int, int], ...] | None:
    """Return family 2 exactly on its part of the family-1 complement.

    Let ``ell=(a,b)`` be the first row of the left marker.  Under all eleven
    coefficient inequalities, failure of ``ell M_f >= ell`` forces
    ``f11=0`` and ``a*f01 < b``.  On that exact complement, family 2 applies
    if and only if

        f10 = 0,
        (M_0)11 >= 1,
        a*(M_2)01 + b*(M_2)11 >= a*(f01 + (M_t)01).

    The returned row is recomputed exactly as a defensive check.  The
    characterization has no coefficient ceiling.
    """

    _validate_natural_matrix_assignment(matrices)
    if not _coefficient_assignment_dominates(matrices):
        return None

    a, b = matrices["<"][:2]
    f00, f01, f10, f11 = matrices["f"]
    if a * f00 + b * f10 >= a and a * f01 + b * f11 >= b:
        return None
    if f11 != 0 or a * f01 >= b:
        raise AssertionError("invalid complement of the first structural family")

    d01, d11 = matrices["2"][1], matrices["2"][3]
    if (
        f10 != 0
        or matrices["0"][3] < 1
        or a * d01 + b * d11 < a * (f01 + matrices["t"][1])
    ):
        return None

    template = _positive_terms((
        ("dynamic-even", 0, a),
        ("dynamic-odd", 0, a),
        ("dynamic-odd", 1, b),
        ("carry-f1", 1, b),
        ("left-2", 0, 1),
    ))
    if _farkas_template_for_assignment(
        matrices,
        (template,),
        _RELATIVE_STRICT_RULES,
    ) != 0:
        raise AssertionError("derived second-family certificate failed verification")
    return template


def relative_third_deficit_template(
    matrices: Mapping[Symbol, Matrix2],
) -> tuple[tuple[str, int, int], ...] | None:
    """Return family 3 exactly on its part of the family-1 complement.

    On ``f11=0`` and ``a*f01 < b``, the third structural family applies if
    and only if

        (M_t)10 = (M_t)11 = 0,
        (M_2)11 >= 1,
        a*(M_2)01 + b >= a*(f01 + (M_t)01).

    As with the first two lemmas, all coefficient inequalities are checked
    before the unbounded parametric certificate is returned.
    """

    _validate_natural_matrix_assignment(matrices)
    if not _coefficient_assignment_dominates(matrices):
        return None

    a, b = matrices["<"][:2]
    f00, f01, f10, f11 = matrices["f"]
    if a * f00 + b * f10 >= a and a * f01 + b * f11 >= b:
        return None
    if f11 != 0 or a * f01 >= b:
        raise AssertionError("invalid complement of the first structural family")

    t01, t10, t11 = matrices["t"][1:]
    d01, d11 = matrices["2"][1], matrices["2"][3]
    if (
        t10 != 0
        or t11 != 0
        or d11 < 1
        or a * d01 + b < a * (f01 + t01)
    ):
        return None

    template = _positive_terms((
        ("dynamic-even", 0, a),
        ("dynamic-even", 1, b),
        ("dynamic-odd", 0, a),
        ("carry-t2", 1, b),
        ("left-2", 0, 1),
    ))
    if _farkas_template_for_assignment(
        matrices,
        (template,),
        _RELATIVE_STRICT_RULES,
    ) != 0:
        raise AssertionError("derived third-family certificate failed verification")
    return template


def relative_fourth_deficit_template(
    matrices: Mapping[Symbol, Matrix2],
) -> tuple[tuple[str, int, int], ...] | None:
    """Return family 4 exactly when its integer parameter interval is nonempty.

    On the exact complement ``f11=0`` and ``a*f01 < b`` of family 1, write
    ``x`` for the common component-one weight.  The fourteen Farkas
    inequalities reduce exactly to ``x >= 1`` and

        x <= b,
        t10 = 0,
        b + x*(t11 - 2) <= 0,
        a*(1-f00) - b*f10 - x*d10 <= 0,
        x*(2-d11) <= a*f01,
        a*(f00+t00-d00-1) + x*(f10-d10) <= 0,
        a*(f01+t01-d01) + x*(t11-d11-1) <= 0.

    ``_family_four_parameter`` solves this same affine system over the
    integers without a search ceiling.  The returned certificate is then
    recomputed from the rewriting rules as a defensive exact check.
    """

    _validate_natural_matrix_assignment(matrices)
    if not _coefficient_assignment_dominates(matrices):
        return None

    a, b = matrices["<"][:2]
    f00, f01, f10, f11 = matrices["f"]
    if a * f00 + b * f10 >= a and a * f01 + b * f11 >= b:
        return None
    if f11 != 0 or a * f01 >= b:
        raise AssertionError("invalid complement of the first structural family")

    parameter = _family_four_parameter(matrices, a)
    if parameter is None:
        return None
    template = _positive_terms((
        ("dynamic-even", 0, a),
        ("dynamic-even", 1, parameter),
        ("dynamic-odd", 0, a),
        ("dynamic-odd", 1, parameter),
        ("carry-t2", 1, parameter),
        ("left-2", 0, 1),
    ))
    if _farkas_template_for_assignment(
        matrices,
        (template,),
        _RELATIVE_STRICT_RULES,
    ) != 0:
        raise AssertionError("derived fourth-family certificate failed verification")
    return template


def relative_fifth_deficit_template(
    matrices: Mapping[Symbol, Matrix2],
) -> tuple[tuple[str, int, int], ...] | None:
    """Return family 5 exactly on its part of the family-1 complement.

    On ``f11=0`` and ``a*f01 < b``, family 5 applies if and only if

        f00 = 1, f01 = 0, t11 = 0, t10 <= f10,
        2*a*(1-o00) + b*f10*(2-o00) - b*o10 <= 0,
        a*(1-z00) + b*(2*f10-d10-z10) <= 0,
        t00 <= d00, t01 <= d01.

    Here ``Z=M_0``, ``O=M_1``, and ``D=M_2``.  These are the exact
    nonautomatic coordinates of the combined Farkas row after restricting
    to the first-family complement; no coefficient bound is used.
    """

    _validate_natural_matrix_assignment(matrices)
    if not _coefficient_assignment_dominates(matrices):
        return None

    a, b = matrices["<"][:2]
    f00, f01, f10, f11 = matrices["f"]
    if a * f00 + b * f10 >= a and a * f01 + b * f11 >= b:
        return None
    if f11 != 0 or a * f01 >= b:
        raise AssertionError("invalid complement of the first structural family")

    t00, t01, t10, t11 = matrices["t"]
    z00, _z01, z10, _z11 = matrices["0"]
    o00, _o01, o10, _o11 = matrices["1"]
    d00, d01, d10, _d11 = matrices["2"]
    if (
        f00 != 1
        or f01 != 0
        or t11 != 0
        or t10 > f10
        or 2 * a * (1 - o00) + b * f10 * (2 - o00) - b * o10 > 0
        or a * (1 - z00) + b * (2 * f10 - d10 - z10) > 0
        or t00 > d00
        or t01 > d01
    ):
        return None

    scale = a + b * f10
    template = _positive_terms((
        ("dynamic-even", 0, 2 * scale),
        ("dynamic-odd", 0, 3 * scale),
        ("carry-f1", 0, a),
        ("carry-f1", 1, b),
        ("carry-f2", 0, 2 * a + b * f10),
        ("carry-f2", 1, b),
        ("carry-t2", 1, b),
        ("left-0", 0, 1),
        ("left-1", 0, 1),
        ("left-2", 0, 1),
    ))
    if _farkas_template_for_assignment(
        matrices,
        (template,),
        _RELATIVE_STRICT_RULES,
    ) != 0:
        raise AssertionError("derived fifth-family certificate failed verification")
    return template


def relative_sixth_deficit_template(
    matrices: Mapping[Symbol, Matrix2],
) -> tuple[tuple[str, int, int], ...] | None:
    """Return family 6 exactly on its part of the family-1 complement.

    The general eleven conditions collapse on ``f11=0`` and ``a*f01<b`` to

        F = [[1, 0], [0, 0]],
        t00 = 1, t01 = t10 = 0, t11 <= 1,
        a*(o01 + z01) >= 2*b.

    All other coordinates of the family-6 Farkas row are then automatically
    nonpositive from naturality and the positive upper-left convention.
    """

    _validate_natural_matrix_assignment(matrices)
    if not _coefficient_assignment_dominates(matrices):
        return None

    a, b = matrices["<"][:2]
    f00, f01, f10, f11 = matrices["f"]
    if a * f00 + b * f10 >= a and a * f01 + b * f11 >= b:
        return None
    if f11 != 0 or a * f01 >= b:
        raise AssertionError("invalid complement of the first structural family")

    t00, t01, t10, t11 = matrices["t"]
    z01 = matrices["0"][1]
    o01 = matrices["1"][1]
    if (
        (f00, f01, f10) != (1, 0, 0)
        or t00 != 1
        or t01 != 0
        or t10 != 0
        or t11 > 1
        or a * (o01 + z01) < 2 * b
    ):
        return None

    template = _positive_terms((
        ("dynamic-even", 0, 3 * a),
        ("dynamic-odd", 0, 3 * a),
        ("carry-f1", 0, a),
        ("carry-f2", 0, a),
        ("carry-f2", 1, 3 * b),
        ("carry-t0", 0, a),
        ("carry-t1", 1, 2 * b),
        ("left-1", 0, 1),
        ("left-2", 0, 2),
    ))
    if _farkas_template_for_assignment(
        matrices,
        (template,),
        _RELATIVE_STRICT_RULES,
    ) != 0:
        raise AssertionError("derived sixth-family certificate failed verification")
    return template


def relative_seventh_deficit_template(
    matrices: Mapping[Symbol, Matrix2],
) -> tuple[tuple[str, int, int], ...] | None:
    """Return family 7 exactly on its part of the family-1 complement.

    Put ``D=b-a``.  Family 7 is impossible on the complement when ``D<=0``;
    for ``D>0`` its exact reduced conditions are

        t00 = 1, t01 = 0,
        D*d01 >= b-a*f01,
        (a,b)*T <= (a,b)*Dmat componentwise.

    ``Dmat`` denotes ``M_2``.  The omitted combined coordinates are
    automatically nonpositive from naturality and ``f00,d00 >= 1``.
    """

    _validate_natural_matrix_assignment(matrices)
    if not _coefficient_assignment_dominates(matrices):
        return None

    a, b = matrices["<"][:2]
    f00, f01, f10, f11 = matrices["f"]
    if a * f00 + b * f10 >= a and a * f01 + b * f11 >= b:
        return None
    if f11 != 0 or a * f01 >= b:
        raise AssertionError("invalid complement of the first structural family")

    deficit = b - a
    if deficit <= 0:
        return None
    t00, t01, t10, t11 = matrices["t"]
    d00, d01, d10, d11 = matrices["2"]
    if (
        t00 != 1
        or t01 != 0
        or deficit * d01 < b - a * f01
        or a * t00 + b * t10 > a * d00 + b * d10
        or a * t01 + b * t11 > a * d01 + b * d11
    ):
        return None

    template = _positive_terms((
        ("dynamic-even", 0, a),
        ("dynamic-odd", 0, a),
        ("dynamic-odd", 1, b),
        ("carry-t2", 0, deficit),
        ("left-2", 0, 1),
    ))
    if _farkas_template_for_assignment(
        matrices,
        (template,),
        _RELATIVE_STRICT_RULES,
    ) != 0:
        raise AssertionError("derived seventh-family certificate failed verification")
    return template


def relative_eighth_deficit_template(
    matrices: Mapping[Symbol, Matrix2],
) -> tuple[tuple[str, int, int], ...] | None:
    """Return family 8 exactly on its part of the family-1 complement."""

    _validate_natural_matrix_assignment(matrices)
    if not _coefficient_assignment_dominates(matrices):
        return None

    a, b = matrices["<"][:2]
    f00, f01, f10, f11 = matrices["f"]
    if a * f00 + b * f10 >= a and a * f01 + b * f11 >= b:
        return None
    if f11 != 0 or a * f01 >= b:
        raise AssertionError("invalid complement of the first structural family")

    deficit = b - a
    if deficit <= 0:
        return None
    scale = (deficit + 3) // 4
    t00, t01, t10, t11 = matrices["t"]
    z01 = matrices["0"][1]
    o01, o10 = matrices["1"][1], matrices["1"][2]
    d00, d01, d10, d11 = matrices["2"]
    if (
        f00 != 1
        or f01 > 1
        or f10 != 0
        or t00 != 1
        or t01 != 0
        or scale * (1 - o10) > a
        or scale * (o01 + z01) < b - a * f01
        or a * t00 + b * t10 > a * d00 + b * d10
        or a * t01 + b * t11 > a * d01 + b * d11
    ):
        return None

    template = _positive_terms((
        ("dynamic-odd", 0, a),
        ("dynamic-odd", 1, b),
        ("carry-f1", 0, scale),
        ("carry-f2", 1, scale),
        ("carry-t0", 0, scale),
        ("left-2", 0, 1),
    ))
    if _farkas_template_for_assignment(
        matrices,
        (template,),
        _RELATIVE_STRICT_RULES,
    ) != 0:
        raise AssertionError("derived eighth-family certificate failed verification")
    return template


def relative_ninth_deficit_template(
    matrices: Mapping[Symbol, Matrix2],
) -> tuple[tuple[str, int, int], ...] | None:
    """Return family 9 exactly on its part of the family-1 complement."""

    _validate_natural_matrix_assignment(matrices)
    if not _coefficient_assignment_dominates(matrices):
        return None

    a, b = matrices["<"][:2]
    f00, f01, f10, f11 = matrices["f"]
    if a * f00 + b * f10 >= a and a * f01 + b * f11 >= b:
        return None
    if f11 != 0 or a * f01 >= b:
        raise AssertionError("invalid complement of the first structural family")

    t00, t01, t10, t11 = matrices["t"]
    z01, z11 = matrices["0"][1], matrices["0"][3]
    o01, o11 = matrices["1"][1], matrices["1"][3]
    d00, d01, d10, d11 = matrices["2"]
    if (
        f00 != 1
        or t00 != 1
        or f10 * t01 != 0
        or f01 * f10 != 0
        or f01 + t01 > b + f01 * o11 + t01 * z11
        or o01 + z01 < b - a * f01
        or a * t00 + b * t10 > a * d00 + b * d10
        or a * t01 + b * t11 > a * d01 + b * d11
    ):
        return None

    template = _positive_terms((
        ("dynamic-odd", 0, a),
        ("dynamic-odd", 1, b),
        ("carry-f0", 1, t01),
        ("carry-f1", 0, 1),
        ("carry-f2", 1, f01),
        ("carry-t0", 0, 1),
        ("left-2", 0, 1),
    ))
    if _farkas_template_for_assignment(
        matrices,
        (template,),
        _RELATIVE_STRICT_RULES,
    ) != 0:
        raise AssertionError("derived ninth-family certificate failed verification")
    return template


def relative_tenth_deficit_template(
    matrices: Mapping[Symbol, Matrix2],
) -> tuple[tuple[str, int, int], ...] | None:
    """Return family 10 exactly on its part of the family-1 complement."""

    _validate_natural_matrix_assignment(matrices)
    if not _coefficient_assignment_dominates(matrices):
        return None

    a, b = matrices["<"][:2]
    f00, f01, f10, f11 = matrices["f"]
    if a * f00 + b * f10 >= a and a * f01 + b * f11 >= b:
        return None
    if f11 != 0 or a * f01 >= b:
        raise AssertionError("invalid complement of the first structural family")

    scale = max(1, b - 1)
    t00, t01, t10, t11 = matrices["t"]
    z00, z01, z10, z11 = matrices["0"]
    o00, o01, _o10, o11 = matrices["1"]
    d00, d01, d10, d11 = matrices["2"]
    if (
        f00 != 1
        or f10 != 0
        or t00 != 1
        or t01 > 2
        or f01 > scale
        or a > scale
        or scale * (1 - o11) - b - z11 + 2 > 0
        or scale - a - o00 - z00 - z10 + 1 > 0
        or b - a * f01 - o01 - z01 - z11 > 0
        or scale * t00 + b * t10 > scale * d00 + b * d10
        or scale * t01 + b * t11 > scale * d01 + b * d11
    ):
        return None

    template = _positive_terms((
        ("dynamic-odd", 0, scale),
        ("dynamic-odd", 1, b),
        ("carry-f0", 1, 1),
        ("carry-f1", 0, 1),
        ("carry-f1", 1, 1),
        ("carry-f2", 1, scale),
        ("carry-t0", 0, 1),
        ("left-2", 0, 1),
    ))
    if _farkas_template_for_assignment(
        matrices,
        (template,),
        _RELATIVE_STRICT_RULES,
    ) != 0:
        raise AssertionError("derived tenth-family certificate failed verification")
    return template


def relative_eleventh_deficit_template(
    matrices: Mapping[Symbol, Matrix2],
) -> tuple[tuple[str, int, int], ...] | None:
    """Return family 11 exactly on its part of the family-1 complement."""

    _validate_natural_matrix_assignment(matrices)
    if not _coefficient_assignment_dominates(matrices):
        return None

    a, b = matrices["<"][:2]
    f00, f01, f10, f11 = matrices["f"]
    if a * f00 + b * f10 >= a and a * f01 + b * f11 >= b:
        return None
    if f11 != 0 or a * f01 >= b:
        raise AssertionError("invalid complement of the first structural family")

    t00, t01, t10, t11 = matrices["t"]
    z01, z11 = matrices["0"][1], matrices["0"][3]
    o01, o11 = matrices["1"][1], matrices["1"][3]
    d00, d01, d10, d11 = matrices["2"]
    left_weight, right_weight = a + 1, b + f01
    if (
        a > b
        or f00 != 1
        or f10 != 0
        or b + f01 * o11 + o01 < f01 + 1
        or a * f01 + z01 + z11 + 1 < b + f01
        or left_weight * t00 + right_weight * t10
        > left_weight * d00 + right_weight * d10
        or left_weight * t01 + right_weight * t11
        > left_weight * d01 + right_weight * d11
    ):
        return None

    template = _positive_terms((
        ("dynamic-odd", 0, b * (a + 1)),
        ("dynamic-odd", 1, b * (f01 + b)),
        ("carry-f1", 0, b),
        ("carry-f1", 1, b),
        ("carry-f2", 0, b),
        ("carry-f2", 1, b * f01),
        ("left-0", 0, 1),
        ("left-2", 0, b),
    ))
    if _farkas_template_for_assignment(
        matrices,
        (template,),
        _RELATIVE_STRICT_RULES,
    ) != 0:
        raise AssertionError("derived eleventh-family certificate failed verification")
    return template


def relative_twelfth_gap_template(
    matrices: Mapping[Symbol, Matrix2],
) -> tuple[tuple[str, int, int], ...] | None:
    """Return family 12 exactly on the family-1 complement.

    Let ``p=f01``, ``K=a*z01+b*z11``,
    ``q=a*(o01-p*(1-o11))``, and ``H=a*p+d11*K+b``.  After imposing
    ``f11=0`` and ``a*p<b``, the exact reduced conditions are

        f00=1, f10=0, q>=0, (d11-1)*K<=0,
        3*a*(t00-d00)+H*(t10-d10)<=0,
        3*a*(t01-d01)+H*(t11-d11)-q<=0.

    The first inequality makes the only potentially signed Farkas weight
    nonnegative.  The final two are the two right-marker coordinates.
    """

    _validate_natural_matrix_assignment(matrices)
    if not _coefficient_assignment_dominates(matrices):
        return None

    a, b = matrices["<"][:2]
    f00, f01, f10, f11 = matrices["f"]
    if a * f00 + b * f10 >= a and a * f01 + b * f11 >= b:
        return None
    if f11 != 0 or a * f01 >= b:
        raise AssertionError("invalid complement of the first structural family")

    t00, t01, t10, t11 = matrices["t"]
    z01, z11 = matrices["0"][1], matrices["0"][3]
    o01, o11 = matrices["1"][1], matrices["1"][3]
    d00, d01, d10, d11 = matrices["2"]
    k = a * z01 + b * z11
    q = a * (o01 - f01 * (1 - o11))
    h = a * f01 + d11 * k + b
    if (
        f00 != 1
        or f10 != 0
        or q < 0
        or (d11 - 1) * k > 0
        or 3 * a * (t00 - d00) + h * (t10 - d10) > 0
        or 3 * a * (t01 - d01) + h * (t11 - d11) - q > 0
    ):
        return None

    template = _positive_terms((
        ("dynamic-even", 1, q),
        ("dynamic-odd", 0, 3 * a),
        ("dynamic-odd", 1, b + a * f01 + d11 * k),
        ("carry-f1", 0, a),
        ("carry-f1", 1, b),
        ("carry-f2", 0, a),
        ("carry-f2", 1, a * f01),
        ("left-0", 0, 1),
        ("left-2", 0, 1),
    ))
    if _farkas_template_for_assignment(
        matrices,
        (template,),
        _RELATIVE_STRICT_RULES,
    ) != 0:
        raise AssertionError("derived twelfth-family certificate failed verification")
    return template


def relative_idempotent_completion_template(
    matrices: Mapping[Symbol, Matrix2],
) -> tuple[int, tuple[tuple[str, int, int], ...]] | None:
    """Implement the final three branches of the unbounded 2D proof.

    This routine is intentionally narrower than
    :func:`relative_structural_farkas_template`: it applies only on the
    family-1 deficit after the structural lemmas have reduced ``M_f`` to one
    of its three idempotent forms.  A missing expected family is an arithmetic
    regression in the proof implementation.
    """

    _validate_natural_matrix_assignment(matrices)
    if not _coefficient_assignment_dominates(matrices):
        return None

    a, b = matrices["<"][:2]
    f00, f01, f10, f11 = matrices["f"]
    if a * f00 + b * f10 >= a and a * f01 + b * f11 >= b:
        return None
    if f00 != 1 or f11 != 0 or a * f01 >= b or f01 * f10 != 0:
        return None

    if f10 > 0:
        family = 5
        template = relative_fifth_deficit_template(matrices)
    elif f01 == 0:
        z11 = matrices["0"][3]
        t01, t11 = matrices["t"][1], matrices["t"][3]
        d01, d11 = matrices["2"][1], matrices["2"][3]
        if z11 >= 1:
            family = 2
            template = relative_second_deficit_template(matrices)
        elif t11 > 0:
            family = 6
            template = relative_sixth_deficit_template(matrices)
        elif t01 <= d01:
            family = 5
            template = relative_fifth_deficit_template(matrices)
        elif d11 == 1:
            family = 3
            template = relative_third_deficit_template(matrices)
        else:
            family = 4
            template = relative_fourth_deficit_template(matrices)
    else:
        if matrices["2"][3] <= 1:
            family = 12
            template = relative_twelfth_gap_template(matrices)
        else:
            family = 4
            template = relative_fourth_deficit_template(matrices)

    if template is None:
        raise AssertionError(
            f"idempotent completeness branch failed for family {family}"
        )
    return family, template


def _bounded_matrix2_no_go_certificate(
    max_entry: int,
    templates: tuple[tuple[tuple[str, int, int], ...], ...],
    strict_rules: frozenset[str] | None = None,
    upper_left_entries: tuple[int, ...] = (1,),
    active_rules: frozenset[str] | None = None,
) -> dict[str, Any]:
    if max_entry < 1:
        raise ValueError("max_entry must be positive")
    if not upper_left_entries or any(
        not isinstance(value, int)
        or isinstance(value, bool)
        or not 1 <= value <= max_entry
        for value in upper_left_entries
    ) or len(set(upper_left_entries)) != len(upper_left_entries):
        raise ValueError(
            "upper-left entries must be distinct positive integers within the domain"
        )
    if active_rules is None:
        active_rules = frozenset(MIXED_BASE_RULES)
    unknown_active_rules = active_rules - frozenset(MIXED_BASE_RULES)
    if unknown_active_rules:
        raise ValueError(f"unknown active rules: {sorted(unknown_active_rules)}")
    if strict_rules is None:
        strict_rules = active_rules
    if not strict_rules <= active_rules:
        raise ValueError("strict rules must belong to the active subsystem")
    template_rules = {
        rule_name
        for template in templates
        for rule_name, _component, _weight in template
    }
    if not template_rules <= active_rules:
        raise ValueError("Farkas template uses a rule outside the active subsystem")
    matrices: tuple[Matrix2, ...] = tuple(
        (upper_left, upper_right, lower_left, lower_right)
        for upper_left in upper_left_entries
        for upper_right, lower_left, lower_right
        in product(range(max_entry + 1), repeat=3)
    )
    symbols = ("f", "t", "0", "1", "2", "<", ">")
    count = len(matrices)
    products = [
        [_matrix2_multiply(left, right) for right in matrices]
        for left in matrices
    ]
    core_assignments: list[tuple[int, int, int, int, int]] = []
    for f_index in range(count):
        for t_index in range(count):
            for zero_index in range(count):
                if "carry-f0" in active_rules and not _matrix2_dominates(
                    products[f_index][zero_index], products[zero_index][f_index]
                ):
                    continue
                for one_index in range(count):
                    if "carry-f1" in active_rules and not _matrix2_dominates(
                        products[f_index][one_index], products[zero_index][t_index]
                    ):
                        continue
                    if "carry-t0" in active_rules and not _matrix2_dominates(
                        products[t_index][zero_index], products[one_index][t_index]
                    ):
                        continue
                    for two_index in range(count):
                        if (
                            (
                                "carry-f2" not in active_rules
                                or _matrix2_dominates(
                                    products[f_index][two_index],
                                    products[one_index][f_index],
                                )
                            )
                            and (
                                "carry-t1" not in active_rules
                                or _matrix2_dominates(
                                    products[t_index][one_index],
                                    products[two_index][f_index],
                                )
                            )
                            and (
                                "carry-t2" not in active_rules
                                or _matrix2_dominates(
                                    products[t_index][two_index],
                                    products[two_index][t_index],
                                )
                            )
                        ):
                            core_assignments.append(
                                (f_index, t_index, zero_index, one_index, two_index)
                            )

    surviving = 0
    template_counts = [0] * len(templates)
    for f_index, t_index, zero_index, one_index, two_index in core_assignments:
        for left_index in range(count):
            if (
                (
                    "left-0" in active_rules
                    and not _matrix2_dominates(
                    products[left_index][zero_index], products[left_index][t_index]
                    )
                )
                or (
                    "left-1" in active_rules
                    and not _matrix2_dominates(
                    products[left_index][one_index],
                    _matrix2_multiply(products[left_index][f_index], matrices[f_index]),
                    )
                )
                or (
                    "left-2" in active_rules
                    and not _matrix2_dominates(
                    products[left_index][two_index],
                    _matrix2_multiply(products[left_index][f_index], matrices[t_index]),
                    )
                )
            ):
                continue
            for right_index in range(count):
                if "dynamic-even" in active_rules and not _matrix2_dominates(
                    products[f_index][right_index], matrices[right_index]
                ):
                    continue
                if "dynamic-odd" in active_rules and not _matrix2_dominates(
                    products[t_index][right_index], products[two_index][right_index]
                ):
                    continue
                assignment = dict(
                    zip(
                        symbols,
                        (
                            matrices[f_index], matrices[t_index], matrices[zero_index],
                            matrices[one_index], matrices[two_index],
                            matrices[left_index], matrices[right_index],
                        ),
                    )
                )
                surviving += 1
                template_index = _farkas_template_for_assignment(
                    assignment, templates, strict_rules
                )
                if template_index is None:
                    raise AssertionError(
                        "bounded matrix assignment lacks an exact certificate"
                    )
                template_counts[template_index] += 1
    if surviving == 0 or sum(template_counts) != surviving:
        raise AssertionError("invalid bounded matrix enumeration")
    result = {
        "dimension": 2,
        "matrix_entry_domain": list(range(max_entry + 1)),
        "upper_left_entries": list(upper_left_entries),
        "total_matrix_assignments": len(matrices) ** len(symbols),
        "core_coefficient_survivors": len(core_assignments),
        "full_coefficient_survivors": surviving,
        "farkas_templates": len(templates),
        "template_coverage": template_counts,
        "strict_rules": sorted(strict_rules),
        "weak_rules": sorted(active_rules - strict_rules),
        "inactive_rules": sorted(set(MIXED_BASE_RULES) - active_rules),
        "unbounded_offset_vectors": True,
        "strict_orientation_possible": False,
        "scope": f"direct 2D natural affine interpretations with symbol matrix "
        f"entries at most {max_entry}; larger entries, higher dimensions, and "
        "staged termination proofs are not excluded",
    }
    if len(upper_left_entries) == 1:
        result["upper_left_entry"] = upper_left_entries[0]
    return result


def boolean_matrix2_no_go_certificate() -> dict[str, Any]:
    """Refute Boolean 2D matrices with exact unbounded-offset certificates."""

    return _bounded_matrix2_no_go_certificate(1, BOOLEAN_2D_FARKAS_TEMPLATES)


def unbounded_relative_matrix2_no_go_theorem() -> dict[str, Any]:
    """Describe the proved unbounded relative 2D natural-matrix no-go."""

    return {
        "system": "Yolcu-Aaronson-Heule mixed-base 11-rule SRS T",
        "dimension": 2,
        "matrix_entry_domain": "all nonnegative integers; upper-left positive",
        "offset_vector_domain": "all nonnegative integer vectors",
        "strict_rules": ["dynamic-even", "dynamic-odd"],
        "weak_rules": sorted(set(MIXED_BASE_RULES) - _RELATIVE_STRICT_RULES),
        "farkas_families": 12,
        "structural_reduction": [
            "ell*M_f >= ell: family 1",
            "strict deficit forces f11=0 and a*f01<b",
            "f00>=2: four zero-pattern contradictions",
            "f00=1 and f01*f10>0: Perron rank contradiction",
            "lower idempotent form: family 5",
            "projection: families 2--6",
            "upper idempotent form: families 4 and 12",
        ],
        "strict_orientation_possible": False,
        "scope": (
            "rules out one-stage relative natural affine matrix "
            "interpretations in dimension 2; dimensions at least 3, other "
            "semirings, dependency pairs, and multi-stage proofs remain open"
        ),
        "collatz_solved": False,
    }


def small_matrix2_no_go_certificate() -> dict[str, Any]:
    """Refute 2D matrices over ``{0,1,2}`` with exact certificates."""

    return _bounded_matrix2_no_go_certificate(2, SMALL_2D_FARKAS_TEMPLATES)


@cache
def extended_small_matrix2_no_go_certificate() -> dict[str, Any]:
    """Refute every direct 2D natural matrix with entries at most two."""

    result = _bounded_matrix2_no_go_certificate(
        2,
        EXTENDED_SMALL_2D_FARKAS_TEMPLATES,
        upper_left_entries=(1, 2),
    )
    result["scope"] = (
        "direct 2D natural affine interpretations with every matrix entry "
        "at most 2, positive upper-left entry, and arbitrary natural offset "
        "vectors; larger entries, higher dimensions, relative proofs, and "
        "staged termination proofs are not excluded"
    )
    return result


@cache
def weakened_eight_rule_matrix2_no_go_certificate() -> dict[str, Any]:
    """Refute a strict interpretation of the eight-rule weakening."""

    result = _bounded_matrix2_no_go_certificate(
        2,
        SMALL_2D_FARKAS_TEMPLATES,
        active_rules=DIRECT_EIGHT_RULE_SUBSYSTEM,
    )
    result["scope"] = (
        "direct strict orientation of the eight-rule subsystem obtained by "
        "removing carry-t0, carry-t1, and left-1; upper-left matrix entry 1, "
        "other entries at most 2, and arbitrary natural offset vectors"
    )
    return result


@cache
def relative_small_matrix2_no_go_certificate() -> dict[str, Any]:
    """Refute the direct relative proof with small 2D natural matrices.

    Only the two Collatz rules are required to be strict; all nine auxiliary
    base-conversion rules are weak.  Since the auxiliary subsystem terminates,
    such an interpretation would prove the Collatz conjecture by rule removal.
    """

    result = _bounded_matrix2_no_go_certificate(
        2,
        RELATIVE_SMALL_2D_FARKAS_TEMPLATES,
        frozenset(("dynamic-even", "dynamic-odd")),
    )
    result["scope"] = (
        "relative 2D natural affine interpretations with the two dynamic "
        "rules strict, the nine auxiliary rules weak, symbol matrix entries "
        "at most 2, upper-left entry 1, and arbitrary natural offset vectors; "
        "larger entries, higher dimensions, arctic interpretations, and "
        "multi-stage proofs are not excluded"
    )
    return result


@cache
def relative_extended_small_matrix2_no_go_certificate() -> dict[str, Any]:
    """Refute the relative proof for every 2D matrix entry at most two."""

    result = _bounded_matrix2_no_go_certificate(
        2,
        RELATIVE_EXTENDED_SMALL_2D_FARKAS_TEMPLATES,
        frozenset(("dynamic-even", "dynamic-odd")),
        upper_left_entries=(1, 2),
    )
    result["scope"] = (
        "relative 2D natural affine interpretations with the two dynamic "
        "rules strict, the nine auxiliary rules weak, every symbol matrix "
        "entry at most 2, positive upper-left entry, and arbitrary natural "
        "offset vectors; larger entries, higher dimensions, arctic "
        "interpretations, and multi-stage proofs are not excluded"
    )
    return result


@cache
def relative_cubic_matrix2_no_go_certificate() -> dict[str, Any]:
    """Refute the relative 2D proof through coefficient three at top-left one.

    This pure-Python verifier is intentionally independent of the optimized
    C++ enumerator in ``tools/verify_relative_cubic.cpp``.  It is exhaustive
    but substantially slower and therefore is not run by the default CLI.
    """

    result = _bounded_matrix2_no_go_certificate(
        3,
        RELATIVE_CUBIC_2D_FARKAS_TEMPLATES,
        frozenset(("dynamic-even", "dynamic-odd")),
    )
    result["scope"] = (
        "relative 2D natural affine interpretations with the two dynamic "
        "rules strict, the nine auxiliary rules weak, upper-left matrix "
        "entry 1, every other entry at most 3, and arbitrary natural offset "
        "vectors; upper-left entries above 1 in this coefficient range, "
        "larger entries, higher dimensions, and other proof languages are "
        "not excluded"
    )
    return result


@cache
def relative_cubic_extended_matrix2_no_go_certificate() -> dict[str, Any]:
    """Refute coefficient-three matrices with upper-left entry one or two.

    The optimized exact verifier in ``tools/verify_relative_cubic.cpp`` is
    the practical reproduction path.  This pure-Python version expresses the
    same finite theorem directly and is deliberately left outside the normal
    test suite because it traverses more than 33 million survivors.
    """

    result = _bounded_matrix2_no_go_certificate(
        3,
        RELATIVE_CUBIC_EXTENDED_2D_FARKAS_TEMPLATES,
        frozenset(("dynamic-even", "dynamic-odd")),
        upper_left_entries=(1, 2),
    )
    result["scope"] = (
        "relative 2D natural affine interpretations with the two dynamic "
        "rules strict, the nine auxiliary rules weak, upper-left matrix "
        "entry 1 or 2, every other entry at most 3, and arbitrary natural "
        "offset vectors; upper-left entry 3, larger entries, higher "
        "dimensions, and other proof languages are not excluded"
    )
    return result


@dataclass(frozen=True)
class Affine1D:
    """The natural affine function ``x -> slope*x + offset``."""

    slope: int
    offset: int

    def __post_init__(self) -> None:
        if self.slope < 1 or self.offset < 0:
            raise ValueError("natural strictly monotone affine maps need slope>=1, offset>=0")

    def after(self, inner: "Affine1D") -> "Affine1D":
        """Return ``self(inner(x))``."""

        return Affine1D(
            self.slope * inner.slope,
            self.offset + self.slope * inner.offset,
        )


def interpret_word(word: Word, interpretation: Mapping[Symbol, Affine1D]) -> Affine1D:
    """Compose symbol interpretations from left to right as outer functions."""

    result = Affine1D(1, 0)
    for symbol in reversed(word):
        result = interpretation[symbol].after(result)
    return result


def strictly_orients_rule(rule: Rule, interpretation: Mapping[Symbol, Affine1D]) -> bool:
    """Check ``[lhs](x)>[rhs](x)`` for every natural ``x`` exactly."""

    lhs = interpret_word(rule[0], interpretation)
    rhs = interpret_word(rule[1], interpretation)
    return lhs.slope >= rhs.slope and lhs.offset > rhs.offset


def directly_orients_all_rules(interp: Mapping[Symbol, Affine1D]) -> bool:
    return all(strictly_orients_rule(rule, interp) for rule in MIXED_BASE_RULES.values())


def scalar_affine_no_go_certificate() -> dict[str, Any]:
    """Return a symbolic contradiction forced by five coefficient inequalities.

    Write ``a_s`` for the positive integer slope of symbol ``s``.  Coefficient
    domination for ``left-2`` and ``dynamic-odd`` gives

        a_2 >= a_f*a_t  and  a_t >= a_2.

    Positivity forces ``a_f=1`` and ``a_2=a_t``.  The rules ``carry-f1``,
    ``carry-f2``, and ``carry-t0`` then give

        a_1 >= a_0*a_2,  a_2 >= a_1,  a_0 >= a_1,

    so ``a_1 >= a_1**2`` and every one of ``a_0,a_1,a_2,a_t`` is 1.  The
    two sides of ``carry-f0`` are therefore the identical affine function
    ``x -> x + b_f + b_0``, contradicting strict orientation.
    """

    return {
        "system": "Yolcu-Aaronson-Heule mixed-base 11-rule SRS T",
        "interpretation_class": "one-dimensional natural affine, all rules strict",
        "selected_coefficient_constraints": [
            {"rule": "left-2", "inequality": "a_2 >= a_f*a_t"},
            {"rule": "dynamic-odd", "inequality": "a_t >= a_2"},
            {"rule": "carry-f1", "inequality": "a_f*a_1 >= a_0*a_t"},
            {"rule": "carry-f2", "inequality": "a_f*a_2 >= a_1*a_f"},
            {"rule": "carry-t0", "inequality": "a_t*a_0 >= a_1*a_t"},
        ],
        "forced_slopes": {"a_f": 1, "a_0": 1, "a_1": 1, "a_2": 1, "a_t": 1},
        "contradictory_rule": "carry-f0",
        "left_interpretation": "x + b_f + b_0",
        "right_interpretation": "x + b_0 + b_f",
        "first_rule_removal_consequence": (
            "if all 11 rules are weak, carry-f0 cannot be one of the first "
            "rules made strict by a scalar natural affine interpretation"
        ),
        "strict_orientation_possible": False,
        "scope": (
            "rules out only a direct scalar natural affine interpretation; "
            "it does not rule out higher dimensions, arctic interpretations, "
            "dependency pairs, or staged rule removal"
        ),
    }


def scalar_relative_no_go_certificate() -> dict[str, Any]:
    """Refute the scalar rule-removal proof that would settle Collatz.

    The coefficient constraints are identical for strict and weak rule
    orientation, so the five inequalities used by
    :func:`scalar_affine_no_go_certificate` still force the five digit slopes
    to one.  Strictness of ``dynamic-odd`` then gives ``b_t > b_2``.  Weak
    orientation of ``left-2`` gives ``b_2 >= b_f + b_t`` after cancelling the
    positive left-marker slope.  Nonnegativity of ``b_f`` is already enough
    for a contradiction.
    """

    return {
        "system": "Yolcu-Aaronson-Heule mixed-base 11-rule SRS T",
        "interpretation_class": (
            "one-dimensional natural affine; dynamic rules strict, "
            "auxiliary rules weak"
        ),
        "forced_slopes": {"a_f": 1, "a_0": 1, "a_1": 1, "a_2": 1, "a_t": 1},
        "strict_constraint": {
            "rule": "dynamic-odd",
            "inequality": "b_t > b_2",
        },
        "weak_constraint": {
            "rule": "left-2",
            "inequality": "b_2 >= b_f + b_t",
        },
        "nonnegativity": "b_f >= 0",
        "strict_orientation_possible": False,
        "scope": (
            "rules out the direct scalar relative interpretation that would "
            "make the two dynamic rules strict and the terminating auxiliary "
            "subsystem weak; higher dimensions and other interpretation "
            "semirings remain open"
        ),
    }


def bounded_scalar_search(max_slope: int, max_offset: int) -> dict[str, Any]:
    """Adversarial finite check; useful for tests, never the theorem's proof."""

    if max_slope < 1 or max_offset < 0:
        raise ValueError("invalid finite search bounds")
    symbols = ("f", "t", "0", "1", "2", "<", ">")
    functions = [
        Affine1D(slope, offset)
        for slope in range(1, max_slope + 1)
        for offset in range(max_offset + 1)
    ]
    checked = 0
    for choices in product(functions, repeat=len(symbols)):
        checked += 1
        interpretation = dict(zip(symbols, choices))
        if directly_orients_all_rules(interpretation):
            return {"checked": checked, "found": True, "interpretation": interpretation}
    return {"checked": checked, "found": False, "interpretation": None}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--search-slope", type=int)
    parser.add_argument("--search-offset", type=int)
    parser.add_argument("--matrix-entry-max", type=int, choices=(1, 2), default=1)
    parser.add_argument("--upper-left-max", type=int, choices=(1, 2), default=1)
    parser.add_argument(
        "--relative",
        action="store_true",
        help="also verify the exact relative {0,1,2} matrix no-go certificate",
    )
    parser.add_argument(
        "--relative-cubic",
        action="store_true",
        help=(
            "run the slow pure-Python relative 2D certificate through entry "
            "3, using --upper-left-max to select its upper-left range"
        ),
    )
    parser.add_argument(
        "--weakened-eight-rules",
        action="store_true",
        help="also verify the strict no-go certificate for the eight-rule subsystem",
    )
    args = parser.parse_args()
    if args.upper_left_max == 2:
        if args.matrix_entry_max != 2:
            parser.error("--upper-left-max 2 requires --matrix-entry-max 2")
        matrix_certificate = extended_small_matrix2_no_go_certificate()
    else:
        matrix_certificate = (
            boolean_matrix2_no_go_certificate()
            if args.matrix_entry_max == 1
            else small_matrix2_no_go_certificate()
        )
    report: dict[str, Any] = {
        "scalar_certificate": scalar_affine_no_go_certificate(),
        "scalar_relative_certificate": scalar_relative_no_go_certificate(),
        "matrix2_certificate": matrix_certificate,
        "unbounded_relative_matrix2_theorem": (
            unbounded_relative_matrix2_no_go_theorem()
        ),
    }
    if args.relative:
        report["relative_matrix2_certificate"] = (
            relative_extended_small_matrix2_no_go_certificate()
            if args.upper_left_max == 2
            else relative_small_matrix2_no_go_certificate()
        )
    if args.relative_cubic:
        report["relative_cubic_matrix2_certificate"] = (
            relative_cubic_extended_matrix2_no_go_certificate()
            if args.upper_left_max == 2
            else relative_cubic_matrix2_no_go_certificate()
        )
    if args.weakened_eight_rules:
        report["weakened_eight_rule_matrix2_certificate"] = (
            weakened_eight_rule_matrix2_no_go_certificate()
        )
    if args.search_slope is not None or args.search_offset is not None:
        if args.search_slope is None or args.search_offset is None:
            parser.error("both finite search bounds are required")
        report["bounded_search"] = bounded_scalar_search(
            args.search_slope, args.search_offset
        )
    print(json.dumps(report, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
