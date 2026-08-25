from __future__ import annotations

import json
import hashlib
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

from sag_collatz.adversary import least_counterexample_to_bounded_descent
from sag_collatz.barrier import closed_form_iterate, delayed_descent_witness, verify_barrier
from sag_collatz.frontier import refine_frontier
from sag_collatz.frontier_verifier import reconstruct_open_frontier
from sag_collatz.global_attack import (
    accelerated_odd_step,
    accelerated_odd_step_lsb_transducer,
    binary_run_lengths,
    binary_run_multiset,
    bounded_correction_required_oscillation,
    finite_factor_graph_analysis,
    finite_image_barrier,
    finite_state_noninjectivity_boundary,
    fixed_residue_obstruction,
    integer_from_binary_run_lengths,
    infinite_fiber_finite_state_boundary,
    linear_trailing_ones_asymptotic_bound,
    linear_trailing_ones_block_obstruction,
    linear_trailing_ones_obstruction,
    linear_trailing_ones_upper_bound,
    local_pattern_cycle_obstruction,
    local_pattern_signature,
    merge_all_nonterminal_predecessors_of_one,
    merge_five_and_twenty_one,
    marked_one_step_factor,
    mersenne_predecessor,
    mersenne_prefix_endpoint,
    odd_run_block,
    ordinal_run_length_obstruction,
    one_bit_erasure_obstruction,
    regular_infinite_merge_boundary,
    symbolic_energy_counterexample,
    trailing_ones,
)
from sag_collatz.generator import (
    TRUNCATED_FLAG,
    accelerated_collatz,
    build_certificate_bytes,
    certificate_code,
    valuation_two,
    write_certificate_bundle,
)
from sag_collatz.verifier import VerificationError, audit_bundle


class ArithmeticTests(unittest.TestCase):
    def test_two_adic_valuation(self) -> None:
        self.assertEqual(valuation_two(1), 0)
        self.assertEqual(valuation_two(40), 3)
        self.assertEqual(valuation_two(1024), 10)

    def test_accelerated_map(self) -> None:
        self.assertEqual(accelerated_collatz(3), 5)
        self.assertEqual(accelerated_collatz(7), 11)
        self.assertEqual(accelerated_collatz(27), 41)

    def test_known_exact_certificates(self) -> None:
        self.assertEqual(certificate_code(5, 5, 10), 1)
        self.assertEqual(certificate_code(3, 6, 10), 2)
        self.assertEqual(certificate_code(7, 10, 10), 4)

    def test_bounded_claims_are_refuted(self) -> None:
        self.assertEqual(least_counterexample_to_bounded_descent(1, 100), 3)
        self.assertEqual(least_counterexample_to_bounded_descent(2, 100), 7)
        self.assertEqual(least_counterexample_to_bounded_descent(20, 100), 27)

    def test_arbitrarily_delayed_descent_witness(self) -> None:
        for horizon in range(1, 65):
            start = delayed_descent_witness(horizon)
            self.assertTrue(verify_barrier(horizon))
            current = start
            for iteration in range(1, horizon + 1):
                current = accelerated_collatz(current)
                self.assertEqual(current, closed_form_iterate(horizon, iteration))
                self.assertGreater(current, start)

    def test_symbolic_energy_is_refuted_by_nine(self) -> None:
        self.assertEqual(odd_run_block(9), (7, 1, 1))
        counterexample = symbolic_energy_counterexample()
        self.assertFalse(counterexample["strict_decrease"])
        self.assertGreater(counterexample["energy_after"], counterexample["energy_before"])

    def test_no_linear_trailing_ones_weight_orients_every_step(self) -> None:
        self.assertEqual(accelerated_odd_step(3), 5)
        obstruction = linear_trailing_ones_obstruction()
        self.assertFalse(obstruction["feasible"])
        self.assertAlmostEqual(
            obstruction["required_c_greater_than"],
            0.7369655941662062,
        )
        self.assertEqual(obstruction["upper_bound_limit"], 0.0)

    def test_mersenne_predecessor_family_forces_c_to_zero(self) -> None:
        for exponent in range(3, 100, 2):
            predecessor = mersenne_predecessor(exponent)
            target = (1 << exponent) - 1
            self.assertEqual(3 * predecessor + 1, 4 * target)
            self.assertEqual(accelerated_odd_step(predecessor), target)
            self.assertEqual(trailing_ones(predecessor), 1)
            self.assertEqual(trailing_ones(target), exponent)
            self.assertEqual(
                3 * ((1 << (exponent + 2)) - 5)
                - 4 * (3 * (1 << exponent) - 3),
                -3,
            )
            self.assertLess(Fraction(predecessor, target), Fraction(4, 3))

        bounds = [linear_trailing_ones_upper_bound(m) for m in (3, 15, 59)]
        self.assertAlmostEqual(bounds[0], 0.18128503969235415)
        self.assertAlmostEqual(bounds[1], 0.029644749429377438)
        self.assertAlmostEqual(bounds[2], 0.007155818953083513)
        self.assertGreater(bounds[0], bounds[1])
        self.assertGreater(bounds[1], bounds[2])
        self.assertLess(bounds[1], linear_trailing_ones_asymptotic_bound(15))
        self.assertLess(linear_trailing_ones_upper_bound(999), 0.001)

    def test_ordinal_run_family_rises_to_mersenne_target(self) -> None:
        for exponent in (*range(3, 100, 2), 999):
            predecessor = mersenne_predecessor(exponent)
            target = (1 << exponent) - 1
            expected_bits = "10" * ((exponent - 3) // 2) + "1001"
            self.assertEqual(f"{predecessor:b}", expected_bits)
            self.assertLessEqual(max(binary_run_lengths(predecessor)), 2)
            self.assertEqual(binary_run_lengths(target), (exponent,))

        obstruction = ordinal_run_length_obstruction()
        self.assertIn("omega^3", obstruction["family_reason"])
        self.assertEqual(
            obstruction["unordered_multiset_factor_cycle"]["steps"],
            [(7, 11), (9, 7)],
        )

    def test_no_ranking_of_unordered_run_multisets_can_strictly_descend(self) -> None:
        self.assertEqual(accelerated_odd_step(25), 19)
        self.assertEqual(binary_run_lengths(25), (2, 2, 1))
        self.assertEqual(binary_run_lengths(19), (1, 2, 2))
        self.assertEqual(binary_run_multiset(25), binary_run_multiset(19))
        for odd_value in range(3, 25, 2):
            self.assertNotEqual(
                binary_run_multiset(odd_value),
                binary_run_multiset(accelerated_odd_step(odd_value)),
            )

    def test_ordered_run_lengths_reconstruct_every_checked_odd_integer(self) -> None:
        for odd_value in range(1, 200_002, 2):
            runs = binary_run_lengths(odd_value)
            self.assertEqual(len(runs) % 2, 1)
            self.assertEqual(integer_from_binary_run_lengths(runs), odd_value)

    def test_factor_graph_finds_run_multiset_cycle_before_first_self_loop(self) -> None:
        analysis = finite_factor_graph_analysis(binary_run_multiset, 9)
        self.assertFalse(analysis["acyclic"])
        self.assertEqual(analysis["cycle_witnesses"], [(7, 11), (9, 7)])
        self.assertIsNone(analysis["finite_natural_ranks"])

    def test_finite_injective_factor_graph_gets_a_valid_rank(self) -> None:
        analysis = finite_factor_graph_analysis(binary_run_lengths, 20_001)
        self.assertTrue(analysis["acyclic"])
        ranks = analysis["finite_natural_ranks"]
        self.assertIsNotNone(ranks)
        for start in range(3, 20_002, 2):
            successor = accelerated_odd_step(start)
            self.assertGreater(
                ranks[binary_run_lengths(start)],
                ranks[binary_run_lengths(successor)],
            )

    def test_every_fixed_power_of_two_residue_map_has_a_self_loop(self) -> None:
        for exponent in range(1, 65):
            witness = fixed_residue_obstruction(exponent)
            modulus = 1 << exponent
            start = witness["start"]
            successor = witness["successor"]
            self.assertEqual(start, (1 << (exponent + 1)) - 1)
            self.assertEqual(successor, 3 * (1 << exponent) - 1)
            self.assertEqual(accelerated_odd_step(start), successor)
            self.assertEqual(start % modulus, successor % modulus)

    def test_every_finite_image_is_forced_to_contain_a_factor_cycle(self) -> None:
        for image_size in range(1, 65):
            barrier = finite_image_barrier(image_size)
            self.assertEqual(len(barrier["orbit"]), image_size + 1)
            self.assertTrue(all(value > 1 for value in barrier["orbit"]))
            for current, successor in zip(barrier["orbit"], barrier["orbit"][1:]):
                self.assertEqual(accelerated_odd_step(current), successor)

    def test_erasing_one_nonconstant_low_bit_already_creates_a_cycle(self) -> None:
        obstruction = one_bit_erasure_obstruction()
        self.assertEqual(obstruction["cycle_states"], [0, 1, 0])
        self.assertEqual(obstruction["cycle_witnesses"], [(3, 5), (5, 1)])

    def test_noninjective_finite_state_map_can_preserve_the_whole_problem(self) -> None:
        boundary = finite_state_noninjectivity_boundary()
        self.assertEqual(merge_five_and_twenty_one(5), merge_five_and_twenty_one(21))
        self.assertEqual(accelerated_odd_step(5), accelerated_odd_step(21))
        self.assertTrue(boundary["factor_well_founded_iff_collatz"])

    def test_even_infinite_fibers_can_preserve_the_whole_problem(self) -> None:
        boundary = infinite_fiber_finite_state_boundary()
        for exponent in range(2, 65):
            value = ((1 << (2 * exponent)) - 1) // 3
            self.assertEqual(accelerated_odd_step(value), 1)
            self.assertEqual(marked_one_step_factor(value), (1, False))
        self.assertEqual(marked_one_step_factor(1), (1, True))
        self.assertTrue(boundary["factor_well_founded_iff_collatz"])

    def test_regular_infinite_merge_needs_no_collatz_step_to_evaluate(self) -> None:
        boundary = regular_infinite_merge_boundary()
        for exponent in range(2, 65):
            value = ((1 << (2 * exponent)) - 1) // 3
            self.assertEqual(f"{value:b}", "10" * (exponent - 1) + "1")
            self.assertEqual(accelerated_odd_step(value), 1)
            self.assertEqual(merge_all_nonterminal_predecessors_of_one(value), 5)
        self.assertEqual(merge_all_nonterminal_predecessors_of_one(1), 1)
        self.assertEqual(merge_all_nonterminal_predecessors_of_one(27), 27)
        self.assertFalse(boundary["uses_collatz_iteration_to_evaluate"])
        self.assertTrue(boundary["factor_well_founded_iff_collatz"])

    def test_lsb_first_transducer_exactly_computes_accelerated_step(self) -> None:
        for value in range(1, 200_002, 2):
            input_bits = f"{value:b}"[::-1]
            output_bits = accelerated_odd_step_lsb_transducer(input_bits)
            self.assertEqual(int(output_bits[::-1], 2), accelerated_odd_step(value))
        for exponent in (64, 257, 1024):
            value = (1 << exponent) - 1
            output_bits = accelerated_odd_step_lsb_transducer(f"{value:b}"[::-1])
            self.assertEqual(int(output_bits[::-1], 2), accelerated_odd_step(value))

    def test_local_pattern_signatures_have_small_factor_cycles(self) -> None:
        expected = {
            1: [(11, 17), (17, 13)],
            2: [(11, 17), (17, 13)],
            3: [(59, 89), (89, 67), (67, 101), (105, 79), (79, 119),
                (123, 185), (157, 59)],
        }
        limits = {1: 17, 2: 17, 3: 157}
        for radius, witnesses in expected.items():
            analysis = finite_factor_graph_analysis(
                lambda value, r=radius: local_pattern_signature(value, r),
                limits[radius],
            )
            self.assertEqual(analysis["cycle_witnesses"], witnesses)

    def test_stored_local_pattern_cycles_are_exact_certificates(self) -> None:
        expected_lengths = {1: 2, 2: 2, 3: 7, 4: 10, 5: 17, 6: 5}
        for radius, expected_length in expected_lengths.items():
            obstruction = local_pattern_cycle_obstruction(radius)
            self.assertEqual(obstruction["cycle_length"], expected_length)
            self.assertEqual(
                obstruction["cycle_states"][0],
                obstruction["cycle_states"][-1],
            )

    def test_no_linear_trailing_ones_weight_orients_every_block(self) -> None:
        self.assertEqual(odd_run_block(7), (13, 3, 1))
        obstruction = linear_trailing_ones_block_obstruction()
        self.assertFalse(obstruction["feasible"])
        self.assertGreater(
            obstruction["required_c_greater_than"],
            obstruction["required_c_less_than"],
        )

    def test_bounded_correction_faces_unbounded_mersenne_growth(self) -> None:
        self.assertEqual(mersenne_prefix_endpoint(5), (31, 161))
        gaps = [bounded_correction_required_oscillation(m) for m in (8, 16, 32, 64)]
        self.assertEqual(gaps, sorted(gaps))
        self.assertGreater(gaps[-1], 30.0)


class BundleTests(unittest.TestCase):
    def test_recursive_frontier_matches_independent_critic(self) -> None:
        generated, generated_history = refine_frontier(12, 20)
        audited, audited_history = reconstruct_open_frontier(12, 20)
        self.assertEqual(generated, audited)
        self.assertEqual(generated_history, audited_history)
        self.assertEqual(len(generated), 227)

    def test_small_bundle_is_exhaustively_verified(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            binary, metadata = write_certificate_bundle(10, 20, Path(directory))
            audit = audit_bundle(binary, metadata)
            self.assertTrue(audit["verified"])
            self.assertEqual(audit["certified_classes"], 447)
            self.assertEqual(audit["unresolved_classes"], 65)

    def test_every_small_claim_survives_concrete_substitution(self) -> None:
        k = 8
        payload, _ = build_certificate_bytes(k, 20)
        modulus = 1 << k
        for index, code in enumerate(payload):
            if code == 0:
                continue
            residue = 2 * index + 1
            step_count = code & 0x7F if code & TRUNCATED_FLAG else code
            for quotient in (0, 1, 2, 17, 101):
                start = residue + modulus * quotient
                current = start
                for _ in range(step_count):
                    current = accelerated_collatz(current)
                self.assertLess(current, start, (residue, code, quotient))

    def test_hash_detects_tampering(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            binary, metadata = write_certificate_bundle(8, 20, Path(directory))
            payload = bytearray(binary.read_bytes())
            payload[0] ^= 1
            binary.write_bytes(payload)
            with self.assertRaisesRegex(VerificationError, "SHA-256 mismatch"):
                audit_bundle(binary, metadata)

    def test_arithmetic_detects_tampering_even_with_updated_hash(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            binary, metadata = write_certificate_bundle(8, 20, Path(directory))
            payload = bytearray(binary.read_bytes())
            payload[0] = 1  # False claim: residue 1 descends in one exact step.
            binary.write_bytes(payload)
            content = json.loads(metadata.read_text(encoding="utf-8"))
            content["certificate_sha256"] = hashlib.sha256(payload).hexdigest()
            metadata.write_text(json.dumps(content), encoding="utf-8")
            with self.assertRaisesRegex(VerificationError, "does not descend"):
                audit_bundle(binary, metadata)

    def test_metadata_detects_count_tampering_after_valid_hash(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            binary, metadata = write_certificate_bundle(8, 20, Path(directory))
            content = json.loads(metadata.read_text(encoding="utf-8"))
            content["certified_classes"] += 1
            metadata.write_text(json.dumps(content), encoding="utf-8")
            with self.assertRaisesRegex(VerificationError, "metadata mismatch"):
                audit_bundle(binary, metadata)


if __name__ == "__main__":
    unittest.main()
