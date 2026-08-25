from __future__ import annotations

from itertools import product
import unittest

from sag_collatz.matrix_attack import (
    _combined_farkas_row,
    _coefficient_assignment_dominates,
    _smallest_affine_nonpositive_parameter,
    relative_eighth_deficit_template,
    relative_eleventh_deficit_template,
    relative_first_row_growth_template,
    relative_idempotent_completion_template,
    relative_fifth_deficit_template,
    relative_fourth_deficit_template,
    relative_ninth_deficit_template,
    relative_second_deficit_template,
    relative_seventh_deficit_template,
    relative_sixth_deficit_template,
    relative_structural_farkas_template,
    relative_tenth_deficit_template,
    relative_third_deficit_template,
    relative_twelfth_gap_template,
    unbounded_relative_matrix2_no_go_theorem,
)


class UnboundedFirstRowLemmaTests(unittest.TestCase):
    def test_unbounded_relative_dimension_two_theorem_metadata(self) -> None:
        theorem = unbounded_relative_matrix2_no_go_theorem()
        self.assertEqual(theorem["dimension"], 2)
        self.assertEqual(theorem["farkas_families"], 12)
        self.assertFalse(theorem["strict_orientation_possible"])
        self.assertFalse(theorem["collatz_solved"])

    def test_large_idempotent_branches_receive_exact_certificates(self) -> None:
        projection = (1, 0, 0, 0)
        cases = (
            (
                5,
                5,
                {
                    "f": (1, 0, 17, 0),
                    "t": (1, 0, 17, 0),
                    "0": (1, 0, 17, 0),
                    "1": (1, 0, 17, 0),
                    "2": (1, 0, 17, 0),
                    "<": (37, 113, 0, 0),
                    ">": (1, 0, 17, 0),
                },
            ),
            (
                4,
                4,
                {
                    "f": (1, 5, 0, 0),
                    "t": (1, 50, 0, 0),
                    "0": (1, 50, 0, 0),
                    "1": (1, 50, 0, 0),
                    "2": (1, 0, 0, 10),
                    "<": (7, 36, 0, 0),
                    ">": projection,
                },
            ),
            (
                9,
                12,
                {
                    "f": (1, 5, 0, 0),
                    "t": (1, 20, 0, 0),
                    "0": (1, 20, 0, 0),
                    "1": (1, 20, 0, 0),
                    "2": (1, 20, 0, 0),
                    "<": (7, 36, 0, 0),
                    ">": projection,
                },
            ),
            (
                12,
                12,
                {
                    "f": (1, 5, 0, 0),
                    "t": (1, 10, 0, 0),
                    "0": (1, 15, 0, 0),
                    "1": (1, 15, 0, 0),
                    "2": (1, 0, 0, 1),
                    "<": (7, 100, 0, 0),
                    ">": projection,
                },
            ),
        )
        for expected_family, completion_family, matrices in cases:
            with self.subTest(family=expected_family):
                self.assertTrue(_coefficient_assignment_dominates(matrices))
                family, template = relative_structural_farkas_template(matrices) or (0, ())
                self.assertEqual(family, expected_family)
                combined, strict_rhs = _combined_farkas_row(matrices, template)
                self.assertGreater(strict_rhs, 0)
                self.assertTrue(all(value <= 0 for value in combined))
                completion = relative_idempotent_completion_template(matrices)
                self.assertIsNotNone(completion)
                self.assertEqual((completion or (0, ()))[0], completion_family)

    def test_upper_idempotent_scalar_reduction_is_exhaustive_on_small_box(self) -> None:
        projection = (1, 0, 0, 0)
        checked = 0
        for a in (1, 2):
            for p in (1, 2):
                for b in range(a * p + 1, a * p + 3):
                    for s, w, z, k, o, q, d, e in product(range(3), repeat=8):
                        if not (
                            z + p * k >= p
                            and o + p * q >= s + z * w
                            and d + p * e >= p
                            and z + s * k >= s + o * w
                            and o + s * q >= p
                            and d + s * e >= s + d * w
                            and a * z + b * k >= a * s + b * w
                            and a * o + b * q >= a * p
                            and a * d + b * e >= a * (s + p * w)
                            and k * w == 0
                            and q * w == 0
                        ):
                            continue
                        matrices = {
                            "f": (1, p, 0, 0),
                            "t": (1, s, 0, w),
                            "0": (1, z, 0, k),
                            "1": (1, o, 0, q),
                            "2": (1, d, 0, e),
                            "<": (a, b, 0, 0),
                            ">": projection,
                        }
                        self.assertTrue(_coefficient_assignment_dominates(matrices))
                        family, template = relative_idempotent_completion_template(
                            matrices
                        ) or (0, ())
                        self.assertEqual(family, 12 if e <= 1 else 4)
                        combined, strict_rhs = _combined_farkas_row(matrices, template)
                        self.assertGreater(strict_rhs, 0)
                        self.assertTrue(all(value <= 0 for value in combined))
                        checked += 1
        self.assertGreater(checked, 100)

    def test_large_coefficients_receive_an_exact_parametric_certificate(self) -> None:
        identity = (1, 0, 0, 1)
        matrices = {
            "f": identity,
            "t": identity,
            "0": identity,
            "1": identity,
            "2": identity,
            "<": (37, 113, 29, 41),
            ">": (101, 77, 88, 66),
        }
        self.assertTrue(_coefficient_assignment_dominates(matrices))
        self.assertEqual(
            relative_first_row_growth_template(matrices),
            (
                ("dynamic-odd", 0, 37),
                ("dynamic-odd", 1, 113),
                ("left-2", 0, 1),
            ),
        )

    def test_the_lemma_declines_the_strict_first_row_deficit_case(self) -> None:
        projection = (1, 0, 0, 0)
        matrices = {
            "f": projection,
            "t": projection,
            "0": projection,
            "1": projection,
            "2": projection,
            "<": (1, 1, 0, 0),
            ">": projection,
        }
        self.assertTrue(_coefficient_assignment_dominates(matrices))
        self.assertIsNone(relative_first_row_growth_template(matrices))

    def test_malformed_assignments_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "exactly the seven symbols"):
            relative_first_row_growth_template({"f": (1, 0, 0, 1)})

    def test_all_twelve_family_constructor_is_unbounded_and_exact(self) -> None:
        identity = (1, 0, 0, 1)
        matrices = {
            "f": identity,
            "t": identity,
            "0": identity,
            "1": identity,
            "2": identity,
            "<": (37, 113, 29, 41),
            ">": (101, 77, 88, 66),
        }
        family, template = relative_structural_farkas_template(matrices) or (0, ())
        self.assertEqual(family, 1)
        combined, strict_rhs = _combined_farkas_row(matrices, template)
        self.assertGreater(strict_rhs, 0)
        self.assertTrue(all(value <= 0 for value in combined))

    def test_later_parametric_family_closes_a_first_row_deficit(self) -> None:
        projection = (1, 0, 0, 0)
        matrices = {
            "f": projection,
            "t": projection,
            "0": projection,
            "1": projection,
            "2": projection,
            "<": (1, 1, 0, 0),
            ">": projection,
        }
        self.assertIsNone(relative_first_row_growth_template(matrices))
        family, template = relative_structural_farkas_template(matrices) or (0, ())
        self.assertEqual(family, 5)
        self.assertIsNone(relative_fourth_deficit_template(matrices))
        self.assertEqual(relative_fifth_deficit_template(matrices), template)
        self.assertEqual(_combined_farkas_row(matrices, template), ((0,) * 14, 5))

    def test_second_family_closes_an_unbounded_deficit_subclass(self) -> None:
        projection = (1, 0, 0, 0)
        identity = (1, 0, 0, 1)
        matrices = {
            "f": projection,
            "t": projection,
            "0": identity,
            "1": projection,
            "2": projection,
            "<": (37, 113, 29, 41),
            ">": projection,
        }
        self.assertTrue(_coefficient_assignment_dominates(matrices))
        self.assertIsNone(relative_first_row_growth_template(matrices))
        family, template = relative_structural_farkas_template(matrices) or (0, ())
        self.assertEqual(family, 2)
        self.assertEqual(relative_second_deficit_template(matrices), template)
        combined, strict_rhs = _combined_farkas_row(matrices, template)
        self.assertEqual(combined, (0, 0, 0, 0, 0, -113) + (0,) * 8)
        self.assertEqual(strict_rhs, 74)

    def test_second_deficit_lemma_declines_the_family_one_region(self) -> None:
        identity = (1, 0, 0, 1)
        matrices = {symbol: identity for symbol in ("f", "t", "0", "1", "2", "<", ">")}
        self.assertTrue(_coefficient_assignment_dominates(matrices))
        self.assertIsNone(relative_second_deficit_template(matrices))

    def test_third_family_closes_an_unbounded_deficit_subclass(self) -> None:
        projection = (1, 0, 0, 0)
        identity = (1, 0, 0, 1)
        matrices = {
            "f": projection,
            "t": projection,
            "0": projection,
            "1": projection,
            "2": identity,
            "<": (37, 113, 29, 41),
            ">": projection,
        }
        self.assertTrue(_coefficient_assignment_dominates(matrices))
        self.assertIsNone(relative_first_row_growth_template(matrices))
        self.assertIsNone(relative_second_deficit_template(matrices))
        family, template = relative_structural_farkas_template(matrices) or (0, ())
        self.assertEqual(family, 3)
        self.assertEqual(relative_third_deficit_template(matrices), template)
        combined, strict_rhs = _combined_farkas_row(matrices, template)
        self.assertTrue(all(value <= 0 for value in combined))
        self.assertEqual(strict_rhs, 74)

    def test_fourth_family_solves_its_unbounded_integer_interval(self) -> None:
        matrices = {
            "f": (1, 0, 0, 0),
            "t": (1, 0, 0, 1),
            "0": (1, 1, 0, 0),
            "1": (1, 1, 0, 0),
            "2": (1, 0, 0, 2),
            "<": (1, 1, 0, 0),
            ">": (1, 0, 0, 0),
        }
        self.assertTrue(_coefficient_assignment_dominates(matrices))
        self.assertIsNone(relative_first_row_growth_template(matrices))
        self.assertIsNone(relative_second_deficit_template(matrices))
        self.assertIsNone(relative_third_deficit_template(matrices))
        family, template = relative_structural_farkas_template(matrices) or (0, ())
        self.assertEqual(family, 4)
        self.assertEqual(relative_fourth_deficit_template(matrices), template)
        combined, strict_rhs = _combined_farkas_row(matrices, template)
        self.assertTrue(all(value <= 0 for value in combined))
        self.assertEqual(strict_rhs, 2)

    def test_sixth_family_has_an_exact_reduced_branch(self) -> None:
        projection = (1, 0, 0, 0)
        matrices = {
            "f": projection,
            "t": (1, 0, 0, 1),
            "0": (1, 1, 0, 0),
            "1": (1, 1, 0, 0),
            "2": projection,
            "<": (1, 1, 0, 0),
            ">": projection,
        }
        self.assertTrue(_coefficient_assignment_dominates(matrices))
        self.assertIsNone(relative_first_row_growth_template(matrices))
        self.assertIsNone(relative_second_deficit_template(matrices))
        self.assertIsNone(relative_third_deficit_template(matrices))
        self.assertIsNone(relative_fourth_deficit_template(matrices))
        self.assertIsNone(relative_fifth_deficit_template(matrices))
        family, template = relative_structural_farkas_template(matrices) or (0, ())
        self.assertEqual(family, 6)
        self.assertEqual(relative_sixth_deficit_template(matrices), template)
        combined, strict_rhs = _combined_farkas_row(matrices, template)
        self.assertTrue(all(value <= 0 for value in combined))
        self.assertEqual(strict_rhs, 6)

    def test_seventh_family_has_an_exact_reduced_branch(self) -> None:
        projection = (1, 0, 0, 0)
        shoulder = (1, 1, 0, 0)
        matrices = {
            "f": shoulder,
            "t": projection,
            "0": shoulder,
            "1": shoulder,
            "2": shoulder,
            "<": (1, 2, 0, 0),
            ">": projection,
        }
        self.assertTrue(_coefficient_assignment_dominates(matrices))
        self.assertIsNone(relative_first_row_growth_template(matrices))
        self.assertIsNone(relative_second_deficit_template(matrices))
        self.assertIsNone(relative_third_deficit_template(matrices))
        self.assertIsNone(relative_fourth_deficit_template(matrices))
        self.assertIsNone(relative_fifth_deficit_template(matrices))
        self.assertIsNone(relative_sixth_deficit_template(matrices))
        family, template = relative_structural_farkas_template(matrices) or (0, ())
        self.assertEqual(family, 7)
        self.assertEqual(relative_seventh_deficit_template(matrices), template)
        combined, strict_rhs = _combined_farkas_row(matrices, template)
        self.assertTrue(all(value <= 0 for value in combined))
        self.assertEqual(strict_rhs, 2)

    def test_eighth_family_reduced_conditions_are_exact_despite_overlap(self) -> None:
        projection = (1, 0, 0, 0)
        shoulder_two = (1, 2, 0, 0)
        identity = (1, 0, 0, 1)
        matrices = {
            "f": projection,
            "t": identity,
            "0": shoulder_two,
            "1": shoulder_two,
            "2": identity,
            "<": (1, 2, 0, 0),
            ">": projection,
        }
        self.assertTrue(_coefficient_assignment_dominates(matrices))
        self.assertIsNone(relative_first_row_growth_template(matrices))
        template = relative_eighth_deficit_template(matrices)
        self.assertIsNotNone(template)
        combined, strict_rhs = _combined_farkas_row(matrices, template or ())
        self.assertTrue(all(value <= 0 for value in combined))
        self.assertEqual(strict_rhs, 1)

    def test_twelfth_family_closes_the_former_fixed_template_residual(self) -> None:
        matrices = {
            "f": (1, 1, 0, 0),
            "t": (1, 0, 0, 1),
            "0": (1, 2, 0, 0),
            "1": (1, 2, 0, 0),
            "2": (1, 1, 0, 0),
            "<": (1, 2, 0, 0),
            ">": (1, 0, 0, 0),
        }
        self.assertTrue(_coefficient_assignment_dominates(matrices))
        family, template = relative_structural_farkas_template(matrices) or (0, ())
        self.assertEqual(family, 12)
        self.assertEqual(relative_twelfth_gap_template(matrices), template)
        combined, strict_rhs = _combined_farkas_row(matrices, template)
        self.assertGreater(strict_rhs, 0)
        self.assertTrue(all(value <= 0 for value in combined))

    def test_twelfth_family_has_no_coefficient_ceiling(self) -> None:
        matrices = {
            "f": (1, 1, 0, 0),
            "t": (1, 0, 0, 1),
            "0": (1, 4, 0, 0),
            "1": (1, 4, 0, 0),
            "2": (1, 1, 0, 0),
            "<": (37, 113, 0, 0),
            ">": (1, 0, 0, 0),
        }
        self.assertTrue(_coefficient_assignment_dominates(matrices))
        family, template = relative_structural_farkas_template(matrices) or (0, ())
        self.assertEqual(family, 12)
        self.assertEqual(relative_twelfth_gap_template(matrices), template)
        self.assertEqual(
            _combined_farkas_row(matrices, template),
            ((0, 0, 0, -148, 0, 0, 0, 0, -37, 0, 0, 0, 0, -72), 111),
        )

    def test_family_one_has_no_cross_coordinate_compensation(self) -> None:
        matrices = {
            "f": (1, 0, 1, 0),
            "t": (1, 0, 0, 0),
            "0": (1, 0, 0, 0),
            "1": (1, 0, 0, 0),
            "2": (1, 0, 0, 0),
            "<": (1, 2, 0, 0),
            ">": (1, 0, 0, 0),
        }
        family_one = (
            ("dynamic-odd", 0, 1),
            ("dynamic-odd", 1, 2),
            ("left-2", 0, 1),
        )
        combined, strict_rhs = _combined_farkas_row(matrices, family_one)
        self.assertEqual(combined, (-1, -2, -2, 2) + (0,) * 10)
        self.assertEqual(strict_rhs, 1)
        self.assertGreater(combined[3], 0)

    def test_ninth_family_uses_matrix_entries_as_exact_weights(self) -> None:
        matrices = {
            "f": (1, 1, 0, 0),
            "t": (1, 1, 0, 0),
            "0": (1, 0, 0, 1),
            "1": (1, 1, 0, 0),
            "2": (1, 1, 0, 0),
            "<": (1, 2, 0, 0),
            ">": (1, 0, 0, 0),
        }
        family, template = relative_structural_farkas_template(matrices) or (0, ())
        self.assertEqual(family, 9)
        self.assertEqual(relative_ninth_deficit_template(matrices), template)
        combined, strict_rhs = _combined_farkas_row(matrices, template)
        self.assertTrue(all(value <= 0 for value in combined))
        self.assertEqual(strict_rhs, 1)

    def test_tenth_family_reduced_conditions_are_exact_despite_overlap(self) -> None:
        projection = (1, 0, 0, 0)
        matrices = {
            "f": projection,
            "t": projection,
            "0": (1, 0, 0, 2),
            "1": projection,
            "2": projection,
            "<": (1, 2, 0, 0),
            ">": projection,
        }
        self.assertTrue(_coefficient_assignment_dominates(matrices))
        self.assertIsNone(relative_first_row_growth_template(matrices))
        template = relative_tenth_deficit_template(matrices)
        self.assertIsNotNone(template)
        combined, strict_rhs = _combined_farkas_row(matrices, template or ())
        self.assertTrue(all(value <= 0 for value in combined))
        self.assertEqual(strict_rhs, 1)

    def test_eleventh_family_closes_a_second_deficit_shape(self) -> None:
        matrices = {
            "f": (1, 1, 0, 0),
            "t": (1, 2, 0, 0),
            "0": (1, 2, 0, 0),
            "1": (1, 2, 0, 0),
            "2": (1, 2, 0, 0),
            "<": (1, 2, 0, 0),
            ">": (1, 0, 0, 0),
        }
        family, template = relative_structural_farkas_template(matrices) or (0, ())
        self.assertEqual(family, 11)
        self.assertEqual(relative_eleventh_deficit_template(matrices), template)
        combined, strict_rhs = _combined_farkas_row(matrices, template)
        self.assertTrue(all(value <= 0 for value in combined))
        self.assertEqual(strict_rhs, 4)

    def test_unbounded_integer_parameter_interval_has_exact_endpoints(self) -> None:
        self.assertEqual(
            _smallest_affine_nonpositive_parameter((5, -10), (-2, 3)),
            3,
        )
        self.assertIsNone(
            _smallest_affine_nonpositive_parameter((5, -7), (-2, 3))
        )
        self.assertEqual(
            _smallest_affine_nonpositive_parameter((-5, 0), (0, -1)),
            1,
        )
        with self.assertRaisesRegex(ValueError, "equal length"):
            _smallest_affine_nonpositive_parameter((0,), (0, 0))


if __name__ == "__main__":
    unittest.main()
