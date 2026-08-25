"""Exact obstruction to every bounded-horizon first-descent proof."""

from __future__ import annotations


def delayed_descent_witness(horizon: int) -> int:
    """Return an odd integer that stays above its start for ``horizon`` steps."""

    if horizon < 1:
        raise ValueError("horizon must be positive")
    return (1 << (horizon + 1)) - 1


def closed_form_iterate(horizon: int, step: int) -> int:
    """Closed form for T**step(2**(horizon+1)-1), for 0 <= step <= horizon."""

    if horizon < 1 or not 0 <= step <= horizon:
        raise ValueError("invalid horizon or step")
    return pow(3, step) * (1 << (horizon + 1 - step)) - 1


def verify_barrier(horizon: int) -> bool:
    start = delayed_descent_witness(horizon)
    for step in range(1, horizon + 1):
        if closed_form_iterate(horizon, step) <= start:
            return False
    return True

