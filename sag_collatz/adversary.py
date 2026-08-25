"""Small adversarial probes for over-strong accelerated-Collatz claims."""

from __future__ import annotations

import argparse
import json
from typing import Any


def _v2(value: int) -> int:
    return (value & -value).bit_length() - 1


def step(odd_value: int) -> int:
    raw = 3 * odd_value + 1
    return raw >> _v2(raw)


def orbit_prefix(start: int, steps: int) -> list[int]:
    values = [start]
    for _ in range(steps):
        values.append(step(values[-1]))
    return values


def least_counterexample_to_bounded_descent(horizon: int, search_bound: int) -> int | None:
    """Refute 'every odd n>1 descends in <= horizon accelerated steps'."""

    if horizon < 1 or search_bound < 3:
        raise ValueError("invalid search parameters")
    for candidate in range(3, search_bound + 1, 2):
        current = candidate
        for _ in range(horizon):
            current = step(current)
            if current < candidate:
                break
        else:
            return candidate
    return None


def run_probes(search_bound: int = 2_000_000) -> dict[str, Any]:
    horizons = (1, 2, 3, 4, 10, 20, 36)
    counterexamples = {
        str(horizon): least_counterexample_to_bounded_descent(horizon, search_bound)
        for horizon in horizons
    }
    orbit_27 = orbit_prefix(27, 37)
    return {
        "claim_family": "every odd n > 1 descends within L accelerated steps",
        "search_bound": search_bound,
        "least_counterexamples": counterexamples,
        "orbit_27_through_first_descent": orbit_27,
        "first_descent_step_for_27": next(
            index for index, value in enumerate(orbit_27[1:], start=1) if value < 27
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--search-bound", type=int, default=2_000_000)
    args = parser.parse_args()
    print(json.dumps(run_probes(args.search_bound), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

