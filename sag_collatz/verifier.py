"""Independent critic for Collatz residue-class certificates.

This module intentionally shares no implementation helpers with the generator.
It validates both every nonzero proof byte and the generator's claim that zero
bytes have no certificate under the stated finite search protocol.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any


EXPECTED_FORMAT = "sag-collatz-residue-v1"


class VerificationError(RuntimeError):
    """Raised when a certificate bundle fails exact verification."""


def _two_adic_order(number: int) -> int:
    if number < 1:
        raise VerificationError("nonpositive value in valuation")
    order = 0
    while number % 2 == 0:
        number //= 2
        order += 1
    return order


def _validate_encoded_claim(residue: int, k: int, code: int) -> None:
    """Validate one claimed affine inequality without trusting the generator."""

    if code == 0:
        return
    truncated = bool(code & 128)
    step = code & 127 if truncated else code
    if step < 1 or step > 63 or (not truncated and code >= 64):
        raise VerificationError(f"invalid code {code} for residue {residue}")

    value = residue
    accumulated_order = 0

    # Every earlier accelerated step must be exactly determined by the class.
    for _ in range(1, step):
        numerator = 3 * value + 1
        order = _two_adic_order(numerator)
        if accumulated_order + order >= k:
            raise VerificationError(f"certificate crosses precision early at residue {residue}")
        accumulated_order += order
        value = numerator // (1 << order)

    numerator = 3 * value + 1
    order = _two_adic_order(numerator)

    if not truncated:
        if accumulated_order + order >= k:
            raise VerificationError(f"exact certificate exhausts precision at residue {residue}")
        accumulated_order += order
        endpoint = numerator // (1 << order)
        if endpoint >= residue:
            raise VerificationError(f"exact endpoint does not descend at residue {residue}")
        if pow(3, step) >= (1 << accumulated_order):
            raise VerificationError(f"exact affine slope is not below one at residue {residue}")
        return

    if accumulated_order + order < k:
        raise VerificationError(f"truncated certificate has unused precision at residue {residue}")
    guaranteed_order = k - accumulated_order
    if numerator % (1 << guaranteed_order) != 0:
        raise VerificationError(f"invalid guaranteed division at residue {residue}")
    affine_upper_at_zero = numerator // (1 << guaranteed_order)
    if affine_upper_at_zero >= residue:
        raise VerificationError(f"truncated upper bound does not descend at residue {residue}")
    if pow(3, step) >= (1 << k):
        raise VerificationError(f"truncated affine slope is not below one at residue {residue}")


def _critic_canonical_code(residue: int, k: int, limit: int) -> int:
    """Reconstruct the earliest admissible code using critic-side arithmetic."""

    state = residue
    used_bits = 0
    triple_power = 1
    modulus = pow(2, k)

    for iteration in range(1, limit + 1):
        transformed = 3 * state + 1
        local_order = _two_adic_order(transformed)
        triple_power *= 3
        available = k - used_bits

        if local_order < available:
            state = transformed // pow(2, local_order)
            used_bits += local_order
            if state < residue and triple_power < pow(2, used_bits):
                return iteration
            continue

        conservative_endpoint = transformed // pow(2, available)
        if conservative_endpoint < residue and triple_power < modulus:
            return 128 + iteration
        return 0
    return 0


def audit_bundle(binary_path: Path, metadata_path: Path) -> dict[str, Any]:
    """Exhaustively audit a bundle and return an independently computed summary."""

    payload = binary_path.read_bytes()
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if metadata.get("format") != EXPECTED_FORMAT:
        raise VerificationError("unknown certificate format")

    k = metadata.get("k")
    limit = metadata.get("step_limit")
    if not isinstance(k, int) or k < 1:
        raise VerificationError("invalid k")
    if not isinstance(limit, int) or not 1 <= limit <= 63:
        raise VerificationError("invalid step limit")

    expected_size = pow(2, k - 1)
    if len(payload) != expected_size:
        raise VerificationError(f"wrong payload size: {len(payload)} != {expected_size}")
    digest = hashlib.sha256(payload).hexdigest()
    if digest != metadata.get("certificate_sha256"):
        raise VerificationError("SHA-256 mismatch")

    exact_count = 0
    truncated_count = 0
    histogram: Counter[int] = Counter()

    for index, code in enumerate(payload):
        residue = 2 * index + 1
        _validate_encoded_claim(residue, k, code)
        expected_code = _critic_canonical_code(residue, k, limit)
        if code != expected_code:
            raise VerificationError(
                f"noncanonical or omitted certificate at residue {residue}: {code} != {expected_code}"
            )
        if code == 0:
            continue
        if code & 128:
            truncated_count += 1
            histogram[code & 127] += 1
        else:
            exact_count += 1
            histogram[code] += 1

    certified = exact_count + truncated_count
    independently_computed: dict[str, Any] = {
        "verified": True,
        "k": k,
        "step_limit": limit,
        "odd_residue_classes": expected_size,
        "certified_classes": certified,
        "unresolved_classes": expected_size - certified,
        "exact_certificates": exact_count,
        "truncated_certificates": truncated_count,
        "step_histogram": {str(key): histogram[key] for key in sorted(histogram)},
        "certificate_sha256": digest,
    }

    for field in (
        "odd_residue_classes",
        "certified_classes",
        "unresolved_classes",
        "exact_certificates",
        "truncated_certificates",
        "step_histogram",
    ):
        if metadata.get(field) != independently_computed[field]:
            raise VerificationError(f"metadata mismatch in {field}")

    return independently_computed


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("binary", type=Path)
    parser.add_argument("metadata", type=Path)
    args = parser.parse_args()
    result = audit_bundle(args.binary, args.metadata)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

