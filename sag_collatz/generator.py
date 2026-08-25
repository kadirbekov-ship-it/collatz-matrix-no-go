"""Generator side of the adversarial proof graph.

The generator emits one byte for every odd residue modulo ``2**k``:

* ``0``: no certificate was found before the 2-adic precision boundary;
* ``1..63``: an exact affine certificate, with the byte equal to its step;
* ``128 + j``: a truncated-bound certificate at step ``j``.

The byte array is deliberately simple.  The independent verifier does not
import this module and reconstructs every claimed inequality from scratch.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any


FORMAT_NAME = "sag-collatz-residue-v1"
TRUNCATED_FLAG = 0x80
MAX_ENCODED_STEP = 63


def valuation_two(value: int) -> int:
    """Return v_2(value) for a strictly positive integer."""

    if value <= 0:
        raise ValueError("valuation_two expects a positive integer")
    return (value & -value).bit_length() - 1


def accelerated_collatz(odd_value: int) -> int:
    """Apply T(n)=(3n+1)/2**v_2(3n+1) to a positive odd integer."""

    if odd_value <= 0 or odd_value % 2 == 0:
        raise ValueError("accelerated_collatz expects a positive odd integer")
    raw = 3 * odd_value + 1
    return raw >> valuation_two(raw)


def certificate_code(residue: int, k: int, step_limit: int) -> int:
    """Return the canonical earliest certificate for one odd residue class.

    The represented class is ``residue + 2**k * q`` for every integer
    ``q >= 0``.  A nonzero result proves that every member of this infinite
    class has an accelerated iterate smaller than itself.
    """

    modulus = 1 << k
    if k < 1:
        raise ValueError("k must be positive")
    if not 1 <= step_limit <= MAX_ENCODED_STEP:
        raise ValueError(f"step_limit must be in 1..{MAX_ENCODED_STEP}")
    if residue <= 0 or residue >= modulus or residue % 2 == 0:
        raise ValueError("residue must be odd and lie in [1, 2**k)")

    current = residue
    exponent_sum = 0
    power_three = 1

    for step in range(1, step_limit + 1):
        raw = 3 * current + 1
        shift = valuation_two(raw)
        power_three *= 3

        if exponent_sum + shift < k:
            exponent_sum += shift
            current = raw >> shift
            if current < residue and power_three < (1 << exponent_sum):
                return step
            continue

        # The residue does not determine all further valuations.  It does,
        # however, guarantee division through the remaining k-adic bits.
        remaining = k - exponent_sum
        affine_upper_at_zero = raw >> remaining
        if affine_upper_at_zero < residue and power_three < modulus:
            return TRUNCATED_FLAG | step
        return 0

    return 0


def build_certificate_bytes(k: int, step_limit: int) -> tuple[bytes, dict[str, Any]]:
    """Enumerate all odd residues modulo 2**k and return bytes plus summary."""

    if k < 1:
        raise ValueError("k must be positive")
    if not 1 <= step_limit <= MAX_ENCODED_STEP:
        raise ValueError(f"step_limit must be in 1..{MAX_ENCODED_STEP}")

    class_count = 1 << (k - 1)
    payload = bytearray(class_count)
    exact_count = 0
    truncated_count = 0
    step_histogram: Counter[int] = Counter()

    for index in range(class_count):
        residue = 2 * index + 1
        code = certificate_code(residue, k, step_limit)
        payload[index] = code
        if code == 0:
            continue
        if code & TRUNCATED_FLAG:
            truncated_count += 1
            step_histogram[code & 0x7F] += 1
        else:
            exact_count += 1
            step_histogram[code] += 1

    certified_count = exact_count + truncated_count
    result = bytes(payload)
    metadata: dict[str, Any] = {
        "format": FORMAT_NAME,
        "k": k,
        "step_limit": step_limit,
        "modulus": 1 << k,
        "odd_residue_classes": class_count,
        "certified_classes": certified_count,
        "unresolved_classes": class_count - certified_count,
        "exact_certificates": exact_count,
        "truncated_certificates": truncated_count,
        "coverage_ratio": f"{certified_count}/{class_count}",
        "step_histogram": {str(key): step_histogram[key] for key in sorted(step_histogram)},
        "certificate_sha256": hashlib.sha256(result).hexdigest(),
    }
    return result, metadata


def write_certificate_bundle(k: int, step_limit: int, output_dir: Path) -> tuple[Path, Path]:
    """Generate and write a deterministic certificate bundle."""

    payload, metadata = build_certificate_bytes(k, step_limit)
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = f"collatz-k{k}-l{step_limit}"
    binary_path = output_dir / f"{stem}.bin"
    metadata_path = output_dir / f"{stem}.json"
    binary_path.write_bytes(payload)
    metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return binary_path, metadata_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--k", type=int, default=20)
    parser.add_argument("--limit", type=int, default=63)
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts"))
    args = parser.parse_args()
    binary_path, metadata_path = write_certificate_bundle(args.k, args.limit, args.output_dir)
    print(binary_path)
    print(metadata_path)


if __name__ == "__main__":
    main()

