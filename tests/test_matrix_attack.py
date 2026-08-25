from __future__ import annotations

import unittest
from itertools import product

from sag_collatz.matrix_attack import (
    Affine1D,
    BOOLEAN_2D_FARKAS_TEMPLATES,
    DIRECT_EIGHT_RULE_SUBSYSTEM,
    EXTENDED_SMALL_2D_FARKAS_TEMPLATES,
    MIXED_BASE_RULES,
    RELATIVE_EXTENDED_SMALL_2D_FARKAS_TEMPLATES,
    RELATIVE_SMALL_2D_FARKAS_TEMPLATES,
    _farkas_template_for_assignment,
    boolean_matrix2_no_go_certificate,
    bounded_scalar_search,
    extended_small_matrix2_no_go_certificate,
    interpret_word,
    relative_extended_small_matrix2_no_go_certificate,
    relative_small_matrix2_no_go_certificate,
    scalar_affine_no_go_certificate,
    scalar_relative_no_go_certificate,
    small_matrix2_no_go_certificate,
    strictly_orients_rule,
    weakened_eight_rule_matrix2_no_go_certificate,
)


class ScalarNaturalMatrixAttackTests(unittest.TestCase):
    def test_word_interpretation_uses_the_published_composition_order(self) -> None:
        interpretation = {
            "f": Affine1D(2, 3),
            "0": Affine1D(5, 7),
        }
        # f(0(x)) = 2*(5*x+7)+3 = 10*x+17.
        self.assertEqual(interpret_word(("f", "0"), interpretation), Affine1D(10, 17))

    def test_selected_slope_constraints_force_the_claimed_unit_slopes(self) -> None:
        satisfying = []
        for a_f, a_t, a_0, a_1, a_2 in product(range(1, 6), repeat=5):
            constraints = (
                a_2 >= a_f * a_t
                and a_t >= a_2
                and a_f * a_1 >= a_0 * a_t
                and a_f * a_2 >= a_1 * a_f
                and a_t * a_0 >= a_1 * a_t
            )
            if constraints:
                satisfying.append((a_f, a_t, a_0, a_1, a_2))
        self.assertEqual(satisfying, [(1, 1, 1, 1, 1)])

    def test_forced_slopes_make_carry_f0_identical_on_both_sides(self) -> None:
        for b_f, b_0 in product(range(8), repeat=2):
            interpretation = {
                "f": Affine1D(1, b_f),
                "0": Affine1D(1, b_0),
            }
            lhs = interpret_word(MIXED_BASE_RULES["carry-f0"][0], interpretation)
            rhs = interpret_word(MIXED_BASE_RULES["carry-f0"][1], interpretation)
            self.assertEqual(lhs, rhs)
            self.assertFalse(
                strictly_orients_rule(MIXED_BASE_RULES["carry-f0"], interpretation)
            )

    def test_symbolic_certificate_states_the_exact_scope(self) -> None:
        certificate = scalar_affine_no_go_certificate()
        self.assertFalse(certificate["strict_orientation_possible"])
        self.assertEqual(certificate["contradictory_rule"], "carry-f0")
        self.assertIn("first", certificate["first_rule_removal_consequence"])
        self.assertIn("higher dimensions", certificate["scope"])

    def test_tiny_exhaustive_search_agrees_but_is_not_the_proof(self) -> None:
        result = bounded_scalar_search(max_slope=1, max_offset=1)
        self.assertEqual(result["checked"], 2 ** 7)
        self.assertFalse(result["found"])

    def test_scalar_relative_certificate_targets_the_actual_rule_removal_goal(self) -> None:
        certificate = scalar_relative_no_go_certificate()
        self.assertEqual(certificate["strict_constraint"]["rule"], "dynamic-odd")
        self.assertEqual(certificate["weak_constraint"]["rule"], "left-2")
        self.assertFalse(certificate["strict_orientation_possible"])

    def test_boolean_two_dimensional_certificate_is_exact_and_exhaustive(self) -> None:
        certificate = boolean_matrix2_no_go_certificate()
        self.assertEqual(certificate["total_matrix_assignments"], 8 ** 7)
        self.assertEqual(certificate["core_coefficient_survivors"], 266)
        self.assertEqual(certificate["full_coefficient_survivors"], 3510)
        self.assertEqual(certificate["farkas_templates"], 4)
        self.assertEqual(
            sum(certificate["template_coverage"]),
            certificate["full_coefficient_survivors"],
        )
        self.assertEqual(len(BOOLEAN_2D_FARKAS_TEMPLATES), 4)
        self.assertTrue(certificate["unbounded_offset_vectors"])
        self.assertFalse(certificate["strict_orientation_possible"])

    def test_small_two_dimensional_matrices_have_exact_dual_certificates(self) -> None:
        certificate = small_matrix2_no_go_certificate()
        self.assertEqual(certificate["matrix_entry_domain"], [0, 1, 2])
        self.assertEqual(certificate["total_matrix_assignments"], 27 ** 7)
        self.assertEqual(certificate["core_coefficient_survivors"], 4917)
        self.assertEqual(certificate["full_coefficient_survivors"], 299_883)
        self.assertEqual(certificate["farkas_templates"], 8)
        self.assertEqual(
            certificate["template_coverage"],
            [189_783, 24_543, 29_457, 26_682, 16_419, 12_495, 432, 72],
        )
        self.assertTrue(certificate["unbounded_offset_vectors"])
        self.assertFalse(certificate["strict_orientation_possible"])

    def test_positive_upper_left_entries_through_two_are_fully_closed(self) -> None:
        certificate = extended_small_matrix2_no_go_certificate()
        self.assertEqual(certificate["upper_left_entries"], [1, 2])
        self.assertEqual(certificate["total_matrix_assignments"], 54 ** 7)
        self.assertEqual(certificate["core_coefficient_survivors"], 19_380)
        self.assertEqual(certificate["full_coefficient_survivors"], 1_169_880)
        self.assertEqual(certificate["farkas_templates"], 14)
        self.assertEqual(
            certificate["template_coverage"],
            [
                756_564, 49_086, 147_210, 53_364, 32_838, 24_990, 864, 144,
                64_728, 22_854, 486, 4_176, 7_920, 4_656,
            ],
        )
        self.assertEqual(len(EXTENDED_SMALL_2D_FARKAS_TEMPLATES), 14)
        self.assertEqual(certificate["inactive_rules"], [])

    def test_same_eight_templates_refute_the_weakened_eight_rule_system(self) -> None:
        certificate = weakened_eight_rule_matrix2_no_go_certificate()
        self.assertEqual(certificate["core_coefficient_survivors"], 24_353)
        self.assertEqual(certificate["full_coefficient_survivors"], 712_866)
        self.assertEqual(certificate["farkas_templates"], 8)
        self.assertEqual(
            certificate["template_coverage"],
            [418_485, 83_718, 105_453, 50_961, 17_052, 36_693, 432, 72],
        )
        self.assertEqual(
            certificate["inactive_rules"], ["carry-t0", "carry-t1", "left-1"]
        )
        self.assertEqual(len(DIRECT_EIGHT_RULE_SUBSYSTEM), 8)

    def test_relative_small_matrices_cannot_make_both_collatz_rules_strict(self) -> None:
        certificate = relative_small_matrix2_no_go_certificate()
        self.assertEqual(certificate["matrix_entry_domain"], [0, 1, 2])
        self.assertEqual(certificate["full_coefficient_survivors"], 299_883)
        self.assertEqual(certificate["farkas_templates"], 22)
        self.assertEqual(
            certificate["template_coverage"],
            [
                145_827, 44_529, 61_884, 16_647, 3_645, 72, 6_792, 1_617,
                11_661, 39, 762, 108, 5_406, 21, 138, 156, 18, 54, 108,
                189, 189, 21,
            ],
        )
        self.assertEqual(
            certificate["strict_rules"], ["dynamic-even", "dynamic-odd"]
        )
        self.assertEqual(len(certificate["weak_rules"]), 9)
        self.assertEqual(len(RELATIVE_SMALL_2D_FARKAS_TEMPLATES), 22)
        self.assertTrue(certificate["unbounded_offset_vectors"])
        self.assertFalse(certificate["strict_orientation_possible"])

    def test_relative_positive_upper_left_entries_through_two_are_closed(self) -> None:
        certificate = relative_extended_small_matrix2_no_go_certificate()
        self.assertEqual(certificate["upper_left_entries"], [1, 2])
        self.assertEqual(certificate["total_matrix_assignments"], 54 ** 7)
        self.assertEqual(certificate["core_coefficient_survivors"], 19_380)
        self.assertEqual(certificate["full_coefficient_survivors"], 1_169_880)
        self.assertEqual(certificate["farkas_templates"], 42)
        self.assertEqual(
            certificate["template_coverage"],
            [
                292_338, 89_058, 123_768, 33_294, 7_290, 144, 222_936,
                45_522, 23_322, 78, 1_524, 270, 10_812, 42, 276, 312,
                36, 108, 270, 378, 378, 42, 230_088, 27_984, 21_360,
                78, 4_062, 9_324, 7_062, 1_482, 480, 4_386, 5_856,
                270, 270, 378, 378, 708, 444, 960, 1_674, 438,
            ],
        )
        self.assertEqual(len(RELATIVE_EXTENDED_SMALL_2D_FARKAS_TEMPLATES), 42)
        self.assertEqual(
            certificate["strict_rules"], ["dynamic-even", "dynamic-odd"]
        )
        self.assertEqual(len(certificate["weak_rules"]), 9)
        self.assertTrue(certificate["unbounded_offset_vectors"])
        self.assertFalse(certificate["strict_orientation_possible"])

    def test_weak_auxiliary_first_coordinate_cannot_supply_dual_strictness(self) -> None:
        identity = (1, 0, 0, 1)
        assignment = {symbol: identity for symbol in ("f", "t", "0", "1", "2", "<", ">")}
        auxiliary_only = (("carry-f0", 0, 1),)
        self.assertIsNone(
            _farkas_template_for_assignment(
                assignment,
                (auxiliary_only,),
                frozenset(("dynamic-even", "dynamic-odd")),
            )
        )
        self.assertEqual(
            _farkas_template_for_assignment(assignment, (auxiliary_only,)), 0
        )

    def test_negative_farkas_weight_is_rejected_before_arithmetic(self) -> None:
        identity = (1, 0, 0, 1)
        assignment = {symbol: identity for symbol in ("f", "t", "0", "1", "2", "<", ">")}
        with self.assertRaisesRegex(ValueError, "nonnegative integers"):
            _farkas_template_for_assignment(
                assignment,
                ((("dynamic-odd", 0, -1),),),
            )


if __name__ == "__main__":
    unittest.main()
