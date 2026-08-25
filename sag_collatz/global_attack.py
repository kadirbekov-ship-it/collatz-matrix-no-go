"""Adversarial probes for proposed global Collatz ranking functions.

The finite residue certificates in this project prove many first descents but
cannot prove a uniform bound. This module tests a different idea: a ranking
function on binary structure. It deliberately contains falsifiers, not a
claim of a proof.
"""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from collections.abc import Callable, Hashable
from fractions import Fraction
from typing import Any


def valuation_two(value: int) -> int:
    if value <= 0:
        raise ValueError("valuation_two expects a positive integer")
    return (value & -value).bit_length() - 1


def trailing_ones(value: int) -> int:
    """Return the number of consecutive low-end 1 bits."""

    if value <= 0:
        raise ValueError("trailing_ones expects a positive integer")
    return valuation_two(value + 1)


def binary_run_lengths(value: int) -> tuple[int, ...]:
    """Return lengths of equal-bit runs from most to least significant bit."""

    if value <= 0:
        raise ValueError("binary_run_lengths expects a positive integer")
    bits = f"{value:b}"
    runs: list[int] = []
    current_bit = bits[0]
    current_length = 0
    for bit in bits:
        if bit == current_bit:
            current_length += 1
        else:
            runs.append(current_length)
            current_bit = bit
            current_length = 1
    runs.append(current_length)
    return tuple(runs)


def binary_run_multiset(value: int) -> tuple[int, ...]:
    """Return the run lengths canonically sorted as an unordered multiset."""

    return tuple(sorted(binary_run_lengths(value), reverse=True))


def local_pattern_signature(value: int, radius: int) -> tuple[tuple[str, int], ...]:
    """Count every boundary-aware binary substring of length at most ``radius``."""

    if value <= 0:
        raise ValueError("local_pattern_signature expects a positive integer")
    if radius < 1:
        raise ValueError("radius must be positive")
    word = f"^{value:b}$"
    counts: Counter[str] = Counter()
    for width in range(1, min(radius, len(word)) + 1):
        counts.update(word[index:index + width] for index in range(len(word) - width + 1))
    return tuple(sorted(counts.items()))


# Each pair is a genuine accelerated Collatz edge.  For a fixed radius, the
# target signature of each pair equals the source signature of the next pair,
# cyclically.  These are proof certificates: checking them does not require
# trusting the search that found them.
LOCAL_PATTERN_CYCLE_CERTIFICATES: dict[int, tuple[tuple[int, int], ...]] = {
    1: ((11, 17), (17, 13)),
    2: ((11, 17), (17, 13)),
    3: (
        (59, 89), (89, 67), (67, 101), (105, 79),
        (79, 119), (123, 185), (157, 59),
    ),
    4: (
        (41, 31), (31, 47), (47, 71), (71, 107), (107, 161),
        (161, 121), (121, 91), (91, 137), (145, 109), (109, 41),
    ),
    5: (
        (2791, 4187), (4187, 6281), (6281, 4711), (4903, 7355),
        (7355, 11033), (11033, 8275), (8275, 12413), (12413, 4655),
        (4655, 6983), (6983, 10475), (10475, 15713), (15713, 11785),
        (11785, 8839), (8839, 13259), (13259, 19889),
        (19889, 14917), (14885, 2791),
    ),
    6: (
        (46697, 35023), (35023, 52535), (52535, 78803),
        (81203, 121805), (122477, 45929),
    ),
}


def local_pattern_cycle_obstruction(radius: int) -> dict[str, Any]:
    """Verify an exact cycle for boundary-aware local pattern counts."""

    try:
        witnesses = LOCAL_PATTERN_CYCLE_CERTIFICATES[radius]
    except KeyError as error:
        raise ValueError("no stored certificate for this radius") from error
    states: list[tuple[tuple[str, int], ...]] = []
    for index, (start, successor) in enumerate(witnesses):
        if accelerated_odd_step(start) != successor:
            raise AssertionError("stored pair is not a Collatz edge")
        source_state = local_pattern_signature(start, radius)
        target_state = local_pattern_signature(successor, radius)
        next_source = local_pattern_signature(
            witnesses[(index + 1) % len(witnesses)][0], radius
        )
        if target_state != next_source:
            raise AssertionError("stored witnesses do not close in the factor graph")
        states.append(source_state)
    states.append(states[0])
    return {
        "radius": radius,
        "cycle_length": len(witnesses),
        "cycle_witnesses": witnesses,
        "cycle_states": states,
        "scope": (
            "every ranking that is an arbitrary function of boundary-aware "
            f"binary substring counts of widths at most {radius}"
        ),
    }


def integer_from_binary_run_lengths(run_lengths: tuple[int, ...]) -> int:
    """Reconstruct the unique integer whose leading bit is 1 and runs are given."""

    if not run_lengths or any(
        not isinstance(length, int) or isinstance(length, bool) or length <= 0
        for length in run_lengths
    ):
        raise ValueError("run lengths must be a nonempty tuple of positive integers")
    value = 0
    bit = 1
    for length in run_lengths:
        for _ in range(length):
            value = (value << 1) | bit
        bit ^= 1
    return value


def _factor_graph(
    data_map: Callable[[int], Hashable], max_odd: int
) -> tuple[
    dict[Hashable, list[Hashable]],
    dict[tuple[Hashable, Hashable], tuple[int, int]],
]:
    """Build the finite relation induced by odd starts up to ``max_odd``."""

    if max_odd < 3:
        raise ValueError("max_odd must be at least three")
    adjacency: dict[Hashable, list[Hashable]] = {}
    edge_witnesses: dict[tuple[Hashable, Hashable], tuple[int, int]] = {}
    for start in range(3, max_odd + 1, 2):
        successor = accelerated_odd_step(start)
        source = data_map(start)
        target = data_map(successor)
        try:
            hash(source)
            hash(target)
        except TypeError as error:
            raise TypeError("data_map must return hashable values") from error
        adjacency.setdefault(source, [])
        adjacency.setdefault(target, [])
        edge = (source, target)
        if edge not in edge_witnesses:
            adjacency[source].append(target)
            edge_witnesses[edge] = (start, successor)
    return adjacency, edge_witnesses


def _directed_cycle(
    adjacency: dict[Hashable, list[Hashable]],
) -> list[Hashable] | None:
    """Return a closed directed walk witnessing a cycle, if one exists."""

    color: dict[Hashable, int] = {}
    parent: dict[Hashable, Hashable] = {}
    for root in adjacency:
        if color.get(root, 0) != 0:
            continue
        color[root] = 1
        stack: list[tuple[Hashable, Any]] = [(root, iter(adjacency[root]))]
        while stack:
            source, targets = stack[-1]
            try:
                target = next(targets)
            except StopIteration:
                color[source] = 2
                stack.pop()
                continue
            target_color = color.get(target, 0)
            if target_color == 0:
                parent[target] = source
                color[target] = 1
                stack.append((target, iter(adjacency[target])))
            elif target_color == 1:
                reverse_path = [source]
                while reverse_path[-1] != target:
                    reverse_path.append(parent[reverse_path[-1]])
                cycle = list(reversed(reverse_path))
                cycle.append(target)
                return cycle
    return None


def finite_factor_graph_analysis(
    data_map: Callable[[int], Hashable], max_odd: int
) -> dict[str, Any]:
    """Analyze a finite factor graph for a ranking of the form ``g(data_map(n))``.

    On this finite relation, a strictly decreasing natural-valued ``g`` exists
    exactly when the graph is acyclic.  This finite equivalence must not be
    extrapolated to the infinite graph: globally an ordinal ranking requires
    the stronger condition that there is no infinite directed path.
    """

    adjacency, edge_witnesses = _factor_graph(data_map, max_odd)
    cycle = _directed_cycle(adjacency)
    cycle_witnesses = None
    ranks = None
    if cycle is not None:
        cycle_witnesses = [
            edge_witnesses[(source, target)]
            for source, target in zip(cycle, cycle[1:])
        ]
    else:
        # DFS completion order is target-before-source for this acyclic graph.
        visited: set[Hashable] = set()
        completion_order: list[Hashable] = []
        for root in adjacency:
            if root in visited:
                continue
            visited.add(root)
            stack: list[tuple[Hashable, Any]] = [(root, iter(adjacency[root]))]
            while stack:
                source, targets = stack[-1]
                try:
                    target = next(targets)
                except StopIteration:
                    completion_order.append(source)
                    stack.pop()
                    continue
                if target not in visited:
                    visited.add(target)
                    stack.append((target, iter(adjacency[target])))
        ranks = {}
        for source in completion_order:
            ranks[source] = max(
                (ranks[target] + 1 for target in adjacency[source]), default=0
            )
    return {
        "checked_odd_starts": len(range(3, max_odd + 1, 2)),
        "distinct_states": len(adjacency),
        "distinct_edges": len(edge_witnesses),
        "acyclic": cycle is None,
        "cycle_states": cycle,
        "cycle_witnesses": cycle_witnesses,
        "finite_natural_ranks": ranks,
    }


def fixed_residue_obstruction(exponent: int) -> dict[str, int]:
    """Give a self-loop for every map that remembers only ``n mod 2**k``."""

    if exponent < 1:
        raise ValueError("exponent must be positive")
    modulus = 1 << exponent
    start = (1 << (exponent + 1)) - 1
    successor = accelerated_odd_step(start)
    expected_successor = 3 * (1 << exponent) - 1
    if successor != expected_successor:
        raise AssertionError("invalid Mersenne residue witness")
    if start % modulus != successor % modulus:
        raise AssertionError("witness does not form a residue self-loop")
    return {
        "exponent": exponent,
        "modulus": modulus,
        "start": start,
        "successor": successor,
        "shared_residue": start % modulus,
    }


def finite_image_barrier(image_size: int) -> dict[str, Any]:
    """Force a cycle in every factor map whose entire image has this size.

    A finite factor graph may have a genuine terminal state, so the tempting
    claim that every vertex has an outgoing edge is false.  Instead we use a
    Collatz orbit prefix with ``image_size`` edges and no visit to 1.  Its
    ``image_size + 1`` factor states must repeat.
    """

    if image_size < 1:
        raise ValueError("image_size must be positive")
    exponent = image_size + 1
    start = (1 << exponent) - 1
    orbit = [start]
    for _ in range(image_size):
        orbit.append(accelerated_odd_step(orbit[-1]))
    expected = [pow(3, step) * (1 << (exponent - step)) - 1
                for step in range(image_size + 1)]
    if orbit != expected or any(value <= 1 for value in orbit):
        raise AssertionError("invalid finite-image barrier orbit")
    return {
        "image_size": image_size,
        "start": start,
        "edge_count": image_size,
        "orbit": orbit,
        "reason": (
            "image_size+1 nonterminal factor states lie in an image of size "
            "image_size, so two repeat and the intervening edges form a cycle"
        ),
    }


def erase_one_informative_bit(value: int) -> int:
    """Delete the two low bits of an odd input, one of which is always fixed."""

    if value <= 0 or value % 2 == 0:
        raise ValueError("erase_one_informative_bit expects a positive odd integer")
    return value >> 2


def one_bit_erasure_obstruction() -> dict[str, Any]:
    """Return the 0 -> 1 -> 0 factor cycle forced by 3 -> 5 -> 1."""

    analysis = finite_factor_graph_analysis(erase_one_informative_bit, 5)
    if analysis["acyclic"]:
        raise AssertionError("missing one-bit erasure cycle")
    return {
        "map": "floor(n/4) on odd positive integers",
        "cycle_states": analysis["cycle_states"],
        "cycle_witnesses": analysis["cycle_witnesses"],
    }


def merge_five_and_twenty_one(value: int) -> int:
    """A noninjective finite-state map that merges terminal siblings only."""

    if value <= 0 or value % 2 == 0:
        raise ValueError("merge_five_and_twenty_one expects a positive odd integer")
    return 5 if value == 21 else value


def merge_all_nonterminal_predecessors_of_one(value: int) -> int:
    """Merge the regular family 5, 21, 85, ... and copy every other input."""

    if value <= 0 or value % 2 == 0:
        raise ValueError(
            "merge_all_nonterminal_predecessors_of_one expects a positive odd integer"
        )
    bits = f"{value:b}"
    is_family = (
        len(bits) >= 3
        and len(bits) % 2 == 1
        and all(left != right for left, right in zip(bits, bits[1:]))
    )
    return 5 if is_family else value


def finite_state_noninjectivity_boundary() -> dict[str, Any]:
    """Show why noninjective finite-state data maps are not a weaker problem.

    The map is identity except that 21 is sent to 5.  Since both 5 and 21 map
    to 1 under the accelerated Collatz step, the merger creates no new cycle or
    infinite path.  Its quotient is well-founded exactly when the original
    Collatz graph is well-founded.
    """

    if merge_five_and_twenty_one(5) != merge_five_and_twenty_one(21):
        raise AssertionError("map must be noninjective")
    if accelerated_odd_step(5) != 1 or accelerated_odd_step(21) != 1:
        raise AssertionError("merged values must have the same terminal successor")
    return {
        "merged_inputs": [5, 21],
        "shared_data_value": 5,
        "shared_successor": 1,
        "finite_state": True,
        "factor_well_founded_iff_collatz": True,
        "reason": (
            "the merged state points only to the unique terminal state; every "
            "infinite quotient path avoids it and lifts uniquely to a Collatz path"
        ),
    }


def regular_infinite_merge_boundary() -> dict[str, Any]:
    """Merge infinitely many terminal siblings using only a regular language.

    The binary family is ``(10)^k 1`` for ``k >= 1``.  Its graph under the
    merge map is a regular two-tape relation: use the identity relation off
    that regular language and output the fixed word ``101`` on it.  This need
    not be subsequential in a fixed one-way reading convention, which is why
    the exact transducer model must always be stated.
    """

    samples = [((1 << (2 * exponent)) - 1) // 3 for exponent in range(2, 9)]
    if any(accelerated_odd_step(value) != 1 for value in samples):
        raise AssertionError("family member is not a direct predecessor of one")
    if any(merge_all_nonterminal_predecessors_of_one(value) != 5 for value in samples):
        raise AssertionError("regular family did not merge to one state")
    if merge_all_nonterminal_predecessors_of_one(1) != 1:
        raise AssertionError("terminal one must remain separate")
    return {
        "map": "merge (10)^k1, k>=1, to 101; copy the complement",
        "sample_infinite_fiber": samples,
        "shared_data_value": 5,
        "shared_successor": 1,
        "binary_family": "(10)^k1 for k>=1",
        "uses_collatz_iteration_to_evaluate": False,
        "regular_two_tape_graph": True,
        "factor_well_founded_iff_collatz": True,
        "reason": (
            "only direct predecessors of the terminal state are merged; every "
            "infinite quotient path avoids the merged state and lifts uniquely"
        ),
    }


def marked_one_step_factor(value: int) -> tuple[int, bool]:
    """A highly noninjective factor retaining one Collatz step and a terminal tag."""

    if value <= 0 or value % 2 == 0:
        raise ValueError("marked_one_step_factor expects a positive odd integer")
    return accelerated_odd_step(value), value == 1


def accelerated_odd_step_lsb_transducer(input_bits: str) -> str:
    """Compute ``T`` as a subsequential transduction on LSB-first bits.

    The state consists only of a multiplication carry in ``{0, 1, 2}`` and
    a flag saying whether the first nonzero output bit has been seen.  Initial
    zero output bits are suppressed, which divides ``3*n+1`` by its full
    power of two.  The returned word is also least-significant-bit first.
    """

    if (
        not input_bits
        or input_bits[0] != "1"
        or input_bits[-1] != "1"
        or any(bit not in "01" for bit in input_bits)
    ):
        raise ValueError("expected a canonical LSB-first positive odd word")
    carry = 1  # The +1 in 3*n+1.
    output: list[str] = []
    started = False

    def emit(bit: int) -> None:
        nonlocal started
        if bit:
            started = True
        if started:
            output.append(str(bit))

    for character in input_bits:
        total = 3 * int(character) + carry
        emit(total & 1)
        carry = total >> 1
        if carry > 2:
            raise AssertionError("finite carry bound was violated")
    while carry:
        emit(carry & 1)
        carry >>= 1
    if not output or output[0] != "1" or output[-1] != "1":
        raise AssertionError("transducer produced a noncanonical odd word")
    return "".join(output)


def infinite_fiber_finite_state_boundary() -> dict[str, Any]:
    """Give an infinite-fiber finite-state factor equivalent to Collatz itself."""

    samples = [((1 << (2 * exponent)) - 1) // 3 for exponent in range(2, 9)]
    shared = marked_one_step_factor(samples[0])
    if any(marked_one_step_factor(value) != shared for value in samples):
        raise AssertionError("depth-one family must share one factor value")
    if shared != (1, False) or marked_one_step_factor(1) != (1, True):
        raise AssertionError("terminal marker must split 1 from its predecessors")
    transducer_checks = {}
    for value in (1, 3, 5, 7, 9, 27, 31, samples[-1]):
        input_lsb = f"{value:b}"[::-1]
        output_lsb = accelerated_odd_step_lsb_transducer(input_lsb)
        output_value = int(output_lsb[::-1], 2)
        if output_value != accelerated_odd_step(value):
            raise AssertionError("LSB-first transducer disagrees with arithmetic")
        transducer_checks[str(value)] = output_value
    return {
        "map": "f(n)=(T(n), n==1)",
        "sample_infinite_fiber": samples,
        "shared_data_value": shared,
        "terminal_data_value": marked_one_step_factor(1),
        "lsb_first_finite_state": True,
        "transducer_state": "carry in {0,1,2} plus output-started flag",
        "transducer_checks": transducer_checks,
        "factor_well_founded_iff_collatz": True,
        "reason": (
            "the factor transition from (m,false) is f(m), while (1,true) is "
            "terminal, so the quotient is the Collatz graph shifted by one step"
        ),
    }


def reduced_odd_step(odd_value: int) -> int:
    """Apply (3*n+1)/2 once to an odd positive integer."""

    if odd_value <= 0 or odd_value % 2 == 0:
        raise ValueError("reduced_odd_step expects a positive odd integer")
    return (3 * odd_value + 1) // 2


def accelerated_odd_step(odd_value: int) -> int:
    """Apply (3*n+1)/2**v2(3*n+1) once."""

    if odd_value <= 0 or odd_value % 2 == 0:
        raise ValueError("accelerated_odd_step expects a positive odd integer")
    raw = 3 * odd_value + 1
    return raw >> valuation_two(raw)


def odd_run_block(odd_value: int) -> tuple[int, int, int]:
    """Collapse one maximal run of reduced odd steps and following halvings.

    If k is the number of trailing binary ones, exactly k successive reduced
    odd steps are possible before an even value is reached. The returned tuple
    is (next_odd, k, extra_halvings).
    """

    if odd_value <= 1 or odd_value % 2 == 0:
        raise ValueError("odd_run_block expects an odd integer greater than one")
    run = trailing_ones(odd_value)
    current = odd_value
    for _ in range(run):
        current = reduced_odd_step(current)
    extra_halvings = valuation_two(current)
    return current >> extra_halvings, run, extra_halvings


def proposed_symbolic_energy(value: int, initial: int) -> float:
    """Energy used by a representative trailing-bit ranking proposal."""

    if value <= 0 or initial <= 1:
        raise ValueError("invalid energy arguments")
    return (
        math.log2(value) / math.log2(initial)
        + trailing_ones(value)
        - valuation_two(value)
    )


def symbolic_energy_counterexample() -> dict[str, Any]:
    """Return the exact full-block counterexample 9 -> 14 -> 7."""

    initial = 9
    successor, odd_steps, extra_halvings = odd_run_block(initial)
    midpoint = reduced_odd_step(initial)
    before = proposed_symbolic_energy(initial, initial)
    middle = proposed_symbolic_energy(midpoint, initial)
    after = proposed_symbolic_energy(successor, initial)
    return {
        "initial": initial,
        "even_midpoint": midpoint,
        "successor": successor,
        "odd_steps": odd_steps,
        "extra_halvings": extra_halvings,
        "energy_before": before,
        "energy_midpoint": middle,
        "energy_after": after,
        "odd_phase_decrease": middle < before,
        "strict_decrease": after < before,
    }


def linear_trailing_ones_obstruction() -> dict[str, Any]:
    """Contradict per-step decrease of log2(n) + c*trailing_ones(n)."""

    lower = math.log2(Fraction(5, 3))
    sample_exponents = (3, 15, 59)
    upper_bounds = {
        str(exponent): linear_trailing_ones_upper_bound(exponent)
        for exponent in sample_exponents
    }
    return {
        "lower_witness": [3, accelerated_odd_step(3)],
        "required_c_greater_than": lower,
        "upper_witness_family": "n_m=(2^(m+2)-5)/3 for odd m >= 3",
        "upper_bound_examples": upper_bounds,
        "upper_bound_limit": 0.0,
        "feasible": False,
        "exact_reason": (
            "3 -> 5 requires c > log2(5/3), while the exact upper bounds "
            "from n_m -> 2^m-1 tend to zero"
        ),
    }


def mersenne_predecessor(exponent: int) -> int:
    """Return the odd predecessor n_m mapping to 2**m-1 in one odd step."""

    if exponent < 3 or exponent % 2 == 0:
        raise ValueError("exponent must be odd and at least three")
    return ((1 << (exponent + 2)) - 5) // 3


def linear_trailing_ones_upper_bound(exponent: int) -> float:
    """Exact upper bound on c forced by n_m -> 2**m-1.

    For odd m, n_m=(2**(m+2)-5)/3 has one trailing binary one and its
    accelerated odd successor 2**m-1 has m. Strict decrease of
    log2(n)+c*trailing_ones(n) therefore requires the returned upper bound.
    """

    predecessor = mersenne_predecessor(exponent)
    target = (1 << exponent) - 1
    if accelerated_odd_step(predecessor) != target:
        raise AssertionError("invalid Mersenne predecessor identity")
    return math.log2(Fraction(predecessor, target)) / (exponent - 1)


def linear_trailing_ones_asymptotic_bound(exponent: int) -> float:
    """Strict finite-m upper bound asymptotic to the exact c threshold."""

    mersenne_predecessor(exponent)  # Validate the same domain as the exact bound.
    return math.log2(Fraction(4, 3)) / (exponent - 1)


def ordinal_run_length_obstruction() -> dict[str, Any]:
    """Refute rankings based on ordinal sums or multisets of run lengths."""

    factor_cycle = finite_factor_graph_analysis(binary_run_multiset, 9)
    if factor_cycle["acyclic"]:
        raise AssertionError("missing run-multiset factor cycle")
    self_loop_start = 25
    self_loop_end = accelerated_odd_step(self_loop_start)
    shared_multiset = binary_run_multiset(self_loop_start)
    if binary_run_multiset(self_loop_end) != shared_multiset:
        raise AssertionError("invalid run-multiset self-loop")
    sample_exponents = (3, 15, 59)
    family = {}
    for exponent in sample_exponents:
        predecessor = mersenne_predecessor(exponent)
        target = (1 << exponent) - 1
        family[str(exponent)] = {
            "predecessor": predecessor,
            "predecessor_runs": binary_run_lengths(predecessor),
            "target": target,
            "target_runs": binary_run_lengths(target),
        }
    return {
        "unordered_multiset_factor_cycle": {
            "steps": factor_cycle["cycle_witnesses"],
            "states": factor_cycle["cycle_states"],
            "reason": (
                "7 -> 11 and 9 -> 7 induce opposite edges between the same "
                "two run-multiset states"
            ),
        },
        "unordered_multiset_self_loop": {
            "step": [self_loop_start, self_loop_end],
            "binary": [f"{self_loop_start:b}", f"{self_loop_end:b}"],
            "shared_run_multiset": shared_multiset,
        },
        "mersenne_predecessor_family": family,
        "family_reason": (
            "every predecessor run has length at most 2, so any finite sum "
            "of omega^run is below omega^3; the target has value omega^m"
        ),
        "scope": (
            "all functions of the unordered run-length multiset, and the "
            "specific ordinal sum of omega powers even when run order is kept"
        ),
        "ordered_run_boundary": (
            "ordered run lengths reconstruct an odd integer uniquely; an "
            "unrestricted well-founded ranking on them exists exactly when "
            "the Collatz conjecture is true"
        ),
    }


def linear_trailing_ones_block_obstruction() -> dict[str, Any]:
    """Contradict blockwise decrease of the same linear ranking.

    Here 7 -> 13 means the genuine three-step accelerated macro-transition
    7 -> 11 -> 17 -> 13.
    """

    lower = math.log2(Fraction(13, 7)) / 2
    upper = math.log2(Fraction(9, 7)) / 2
    return {
        "expanding_block_orbit": [7, 11, 17, 13],
        "contracting_block_orbit": [9, 7],
        "required_c_greater_than": lower,
        "required_c_less_than": upper,
        "feasible": lower < upper,
        "exact_reason": "13/7 > 9/7",
    }


def mersenne_prefix_endpoint(exponent: int) -> tuple[int, int]:
    """Return start and endpoint after exponent-1 accelerated steps."""

    if exponent < 2:
        raise ValueError("exponent must be at least two")
    return (1 << exponent) - 1, 2 * pow(3, exponent - 1) - 1


def bounded_correction_required_oscillation(exponent: int) -> float:
    """Minimum oscillation a bounded correction must absorb."""

    start, endpoint = mersenne_prefix_endpoint(exponent)
    return math.log2(Fraction(endpoint, start))


def run_audit() -> dict[str, Any]:
    counterexample = symbolic_energy_counterexample()
    linear = linear_trailing_ones_obstruction()
    linear_block = linear_trailing_ones_block_obstruction()
    ordinal_runs = ordinal_run_length_obstruction()
    residue_obstructions = {
        str(exponent): fixed_residue_obstruction(exponent)
        for exponent in (1, 3, 9, 17)
    }
    finite_image_examples = {
        str(size): finite_image_barrier(size) for size in (1, 4, 16)
    }
    local_pattern_examples = {}
    for radius in sorted(LOCAL_PATTERN_CYCLE_CERTIFICATES):
        obstruction = local_pattern_cycle_obstruction(radius)
        local_pattern_examples[str(radius)] = {
            "cycle_length": obstruction["cycle_length"],
            "cycle_witnesses": obstruction["cycle_witnesses"],
            "scope": obstruction["scope"],
        }
    exponents = (8, 16, 32, 64, 128)
    return {
        "claim": "a local binary ranking closes the Collatz proof",
        "verdict": (
            "refuted for bounded-correction, linear trailing-one, and "
            "run-length ordinal potentials, and every fixed 2-adic residue map"
        ),
        "symbolic_energy_counterexample": counterexample,
        "linear_trailing_ones_step_obstruction": linear,
        "linear_trailing_ones_block_obstruction": linear_block,
        "ordinal_run_length_obstruction": ordinal_runs,
        "fixed_residue_obstructions": residue_obstructions,
        "finite_image_barriers": finite_image_examples,
        "one_bit_erasure_obstruction": one_bit_erasure_obstruction(),
        "finite_state_noninjectivity_boundary": finite_state_noninjectivity_boundary(),
        "regular_infinite_merge_boundary": regular_infinite_merge_boundary(),
        "infinite_fiber_finite_state_boundary": infinite_fiber_finite_state_boundary(),
        "local_pattern_cycle_obstructions": local_pattern_examples,
        "bounded_correction_mersenne_gap_bits": {
            str(m): bounded_correction_required_oscillation(m) for m in exponents
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    print(json.dumps(run_audit(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
