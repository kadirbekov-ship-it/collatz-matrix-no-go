"""Independent exhaustive verifier for an unresolved-frontier bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any


class FrontierVerificationError(RuntimeError):
    pass


def _order_two(number: int) -> int:
    order = 0
    while number % 2 == 0:
        number //= 2
        order += 1
    return order


def _critic_code(residue: int, k: int, limit: int) -> int:
    value = residue
    used = 0
    three_power = 1
    for step in range(1, limit + 1):
        numerator = 3 * value + 1
        local = _order_two(numerator)
        three_power *= 3
        remaining = k - used
        if local < remaining:
            value = numerator // (1 << local)
            used += local
            if value < residue and three_power < (1 << used):
                return step
        else:
            upper = numerator // (1 << remaining)
            if upper < residue and three_power < (1 << k):
                return 128 + step
            return 0
    return 0


def reconstruct_open_frontier(target_k: int, limit: int) -> tuple[list[int], list[dict[str, Any]]]:
    frontier = [1]
    history: list[dict[str, Any]] = [
        {
            "k": 1,
            "total_classes": 1,
            "certified_classes": 0,
            "open_classes": 1,
            "coverage_ratio": "0/1",
        }
    ]
    for depth in range(2, target_k + 1):
        added_bit = 1 << (depth - 1)
        children = []
        for parent in frontier:
            first = parent
            second = parent + added_bit
            if _critic_code(first, depth, limit) == 0:
                children.append(first)
            if _critic_code(second, depth, limit) == 0:
                children.append(second)
        frontier = children
        total = 1 << (depth - 1)
        certified = total - len(frontier)
        history.append(
            {
                "k": depth,
                "total_classes": total,
                "certified_classes": certified,
                "open_classes": len(frontier),
                "coverage_ratio": f"{certified}/{total}",
            }
        )
    frontier.sort()
    return frontier, history


def audit_frontier(binary_path: Path, metadata_path: Path) -> dict[str, Any]:
    payload = binary_path.read_bytes()
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if metadata.get("format") != "sag-collatz-open-frontier-v1":
        raise FrontierVerificationError("unknown frontier format")
    if len(payload) % 4:
        raise FrontierVerificationError("frontier payload is not uint32-aligned")
    if hashlib.sha256(payload).hexdigest() != metadata.get("frontier_sha256"):
        raise FrontierVerificationError("frontier SHA-256 mismatch")

    stored = [item[0] for item in struct.iter_unpack("<I", payload)]
    expected, history = reconstruct_open_frontier(metadata["k"], metadata["step_limit"])
    if stored != expected:
        mismatch = next(
            (index for index, pair in enumerate(zip(stored, expected)) if pair[0] != pair[1]),
            min(len(stored), len(expected)),
        )
        raise FrontierVerificationError(f"frontier mismatch at index {mismatch}")
    if metadata.get("history") != history:
        raise FrontierVerificationError("frontier history mismatch")

    total = 1 << (metadata["k"] - 1)
    result = {
        "verified": True,
        "k": metadata["k"],
        "total_classes": total,
        "certified_classes": total - len(expected),
        "open_classes": len(expected),
        "frontier_sha256": metadata["frontier_sha256"],
    }
    for field in ("total_classes", "certified_classes", "open_classes"):
        if metadata.get(field) != result[field]:
            raise FrontierVerificationError(f"metadata mismatch in {field}")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("binary", type=Path)
    parser.add_argument("metadata", type=Path)
    args = parser.parse_args()
    print(json.dumps(audit_frontier(args.binary, args.metadata), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

