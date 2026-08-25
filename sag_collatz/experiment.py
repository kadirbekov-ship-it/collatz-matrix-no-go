"""Run the complete finite Collatz proof-graph experiment."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from .adversary import run_probes
from .generator import build_certificate_bytes, write_certificate_bundle
from .stress import stress_bundle
from .verifier import audit_bundle


def run(output_dir: Path, target_k: int = 20, step_limit: int = 63) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)

    coverage_rows: list[dict[str, int | str]] = []
    starting_k = 8 if target_k >= 8 else target_k
    sampled_depths = list(range(starting_k, target_k + 1, 2))
    if target_k not in sampled_depths:
        sampled_depths.append(target_k)

    for k in sampled_depths:
        _, summary = build_certificate_bytes(k, step_limit)
        coverage_rows.append(
            {
                "k": k,
                "certified": summary["certified_classes"],
                "unresolved": summary["unresolved_classes"],
                "total": summary["odd_residue_classes"],
                "coverage_ratio": summary["coverage_ratio"],
            }
        )

    coverage_path = output_dir / "coverage-by-depth.csv"
    with coverage_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(coverage_rows[0]))
        writer.writeheader()
        writer.writerows(coverage_rows)

    binary_path, metadata_path = write_certificate_bundle(target_k, step_limit, output_dir)
    audit = audit_bundle(binary_path, metadata_path)
    audit_path = output_dir / "independent-audit.json"
    audit_path.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    stress = stress_bundle(binary_path, metadata_path)
    stress_path = output_dir / "bigint-stress.json"
    stress_path.write_text(json.dumps(stress, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    probes = run_probes()
    probes_path = output_dir / "adversarial-counterexamples.json"
    probes_path.write_text(json.dumps(probes, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    return {
        "certificate": str(binary_path),
        "metadata": str(metadata_path),
        "audit": str(audit_path),
        "coverage": str(coverage_path),
        "counterexamples": str(probes_path),
        "stress": str(stress_path),
        "verified": audit["verified"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts"))
    parser.add_argument("--k", type=int, default=20)
    parser.add_argument("--limit", type=int, default=63)
    args = parser.parse_args()
    result = run(args.output_dir, args.k, args.limit)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
