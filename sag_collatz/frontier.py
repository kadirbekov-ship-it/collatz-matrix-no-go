"""Refine only the unresolved leaves of the residue-class proof graph."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any

from .generator import certificate_code


FRONTIER_FORMAT = "sag-collatz-open-frontier-v1"


def refine_frontier(target_k: int, step_limit: int = 63) -> tuple[list[int], list[dict[str, Any]]]:
    """Return unresolved odd residues at depth ``target_k``.

    A certified parent is never expanded: its proof is inherited by both
    children.  Thus work is proportional to the unresolved frontier rather
    than to all ``2**(k-1)`` odd classes.
    """

    if not 1 <= target_k <= 31:
        raise ValueError("target_k must be in 1..31")
    if not 1 <= step_limit <= 63:
        raise ValueError("step_limit must be in 1..63")

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

    for k in range(2, target_k + 1):
        high_bit = 1 << (k - 1)
        next_frontier: list[int] = []
        for residue in frontier:
            low_child = residue
            high_child = residue + high_bit
            if certificate_code(low_child, k, step_limit) == 0:
                next_frontier.append(low_child)
            if certificate_code(high_child, k, step_limit) == 0:
                next_frontier.append(high_child)
        frontier = next_frontier
        total = 1 << (k - 1)
        certified = total - len(frontier)
        history.append(
            {
                "k": k,
                "total_classes": total,
                "certified_classes": certified,
                "open_classes": len(frontier),
                "coverage_ratio": f"{certified}/{total}",
            }
        )

    frontier.sort()
    return frontier, history


def encode_frontier(residues: list[int]) -> bytes:
    """Encode sorted residues as deterministic little-endian uint32 values."""

    payload = bytearray(4 * len(residues))
    for index, residue in enumerate(residues):
        struct.pack_into("<I", payload, 4 * index, residue)
    return bytes(payload)


def write_frontier_bundle(target_k: int, step_limit: int, output_dir: Path) -> tuple[Path, Path]:
    frontier, history = refine_frontier(target_k, step_limit)
    payload = encode_frontier(frontier)
    total = 1 << (target_k - 1)
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = f"open-frontier-k{target_k}-l{step_limit}"
    binary_path = output_dir / f"{stem}.bin"
    metadata_path = output_dir / f"{stem}.json"
    metadata = {
        "format": FRONTIER_FORMAT,
        "k": target_k,
        "step_limit": step_limit,
        "integer_encoding": "little-endian uint32",
        "total_classes": total,
        "certified_classes": total - len(frontier),
        "open_classes": len(frontier),
        "coverage_ratio": f"{total - len(frontier)}/{total}",
        "frontier_sha256": hashlib.sha256(payload).hexdigest(),
        "history": history,
    }
    binary_path.write_bytes(payload)
    metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return binary_path, metadata_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--k", type=int, default=26)
    parser.add_argument("--limit", type=int, default=63)
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts"))
    args = parser.parse_args()
    binary, metadata = write_frontier_bundle(args.k, args.limit, args.output_dir)
    print(binary)
    print(metadata)


if __name__ == "__main__":
    main()

