"""Deterministic big-integer substitution tests for certified classes.

This is a bug-finding layer, not a proof layer.  Exact acceptance remains the
responsibility of :mod:`sag_collatz.verifier`.
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Any


def _accelerated(value: int) -> int:
    raw = 3 * value + 1
    shift = 0
    while raw % 2 == 0:
        raw //= 2
        shift += 1
    if shift == 0:
        raise AssertionError("3n+1 must be even for odd n")
    return raw


def stress_bundle(
    binary_path: Path,
    metadata_path: Path,
    samples: int = 10_000,
    seed: int = 0xC011A72,
) -> dict[str, Any]:
    payload = binary_path.read_bytes()
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    k = int(metadata["k"])
    modulus = 1 << k
    certified_indices = [index for index, code in enumerate(payload) if code]
    if not certified_indices:
        raise AssertionError("bundle contains no certificates")

    rng = random.Random(seed)
    concrete_checks = 0
    quotient_bit_lengths = (0, 1, 64, 256, 1024)

    for _ in range(samples):
        index = certified_indices[rng.randrange(len(certified_indices))]
        code = payload[index]
        proof_step = code & 0x7F if code & 0x80 else code
        residue = 2 * index + 1

        for bit_length in quotient_bit_lengths:
            if bit_length == 0:
                quotient = 0
            elif bit_length == 1:
                quotient = 1
            else:
                quotient = (1 << (bit_length - 1)) | rng.getrandbits(bit_length - 1)
            start = residue + modulus * quotient
            endpoint = start
            for _ in range(proof_step):
                endpoint = _accelerated(endpoint)
            if endpoint >= start:
                raise AssertionError(
                    f"concrete counterexample: r={residue}, q={quotient}, code={code}"
                )
            concrete_checks += 1

    return {
        "passed": True,
        "seed": seed,
        "sampled_certificates": samples,
        "quotient_bit_lengths": list(quotient_bit_lengths),
        "concrete_checks": concrete_checks,
        "largest_quotient_bits": max(quotient_bit_lengths),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("binary", type=Path)
    parser.add_argument("metadata", type=Path)
    parser.add_argument("--samples", type=int, default=10_000)
    args = parser.parse_args()
    print(json.dumps(stress_bundle(args.binary, args.metadata, args.samples), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

