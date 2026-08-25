#!/usr/bin/env python3
"""Build a deterministic manuscript/artifact archive.

The final mode refuses unresolved author/repository placeholders.  ``--draft``
is intended only for internal audit packages.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PREFIX = "collatz-matrix-no-go-1.0.0"

EXACT_FILES = (
    ".github/workflows/tests.yml",
    ".gitignore",
    "ARTIFACT.md",
    "CITATION.cff",
    "LICENSE",
    "Makefile",
    "MATRIX_ATTACK.md",
    "README.md",
    "families-conditions.md",
    "pyproject.toml",
    "scripts/build_release.py",
    "submission/main.tex",
    "submission/references.bib",
    "submission/cover-letter.md",
    "submission/JAR_CHECKLIST.md",
    "submission/AUTHOR_INFO_REQUIRED.md",
    "submission/NOVELTY_CHECK.md",
    "submission/PRE_SUBMISSION_REPORT.md",
)

GLOBS = (
    "sag_collatz/*.py",
    "tests/test_*.py",
    "tools/*.cpp",
)

PLACEHOLDERS = (
    "[INSERT REPOSITORY",
    "[PUBLIC REPOSITORY URL]",
    "[ZENODO DOI]",
)


def selected_files() -> list[Path]:
    files = {ROOT / name for name in EXACT_FILES}
    for pattern in GLOBS:
        files.update(ROOT.glob(pattern))
    missing = sorted(path for path in files if not path.is_file())
    if missing:
        raise SystemExit(f"missing release file(s): {missing}")
    return sorted(files, key=lambda path: path.relative_to(ROOT).as_posix())


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--draft", action="store_true")
    args = parser.parse_args()

    files = selected_files()
    if not args.draft:
        unresolved: list[str] = []
        for path in files:
            if path.suffix not in {".md", ".tex", ".bib", ".toml", ".yml"}:
                continue
            text = path.read_text(encoding="utf-8")
            if any(marker in text for marker in PLACEHOLDERS):
                unresolved.append(path.relative_to(ROOT).as_posix())
        if unresolved:
            raise SystemExit(
                "refusing final archive with unresolved metadata: "
                + ", ".join(unresolved)
            )

    DIST.mkdir(exist_ok=True)
    suffix = "-draft" if args.draft else ""
    archive = DIST / f"{PREFIX}{suffix}.zip"
    manifest_lines: list[str] = []
    with ZipFile(archive, "w", compression=ZIP_DEFLATED, compresslevel=9) as out:
        for path in files:
            relative = path.relative_to(ROOT).as_posix()
            data = path.read_bytes()
            manifest_lines.append(f"{sha256(data)}  {relative}")
            info = ZipInfo(f"{PREFIX}/{relative}", date_time=(2026, 8, 25, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            out.writestr(info, data)
        manifest = ("\n".join(manifest_lines) + "\n").encode()
        info = ZipInfo(
            f"{PREFIX}/MANIFEST.sha256", date_time=(2026, 8, 25, 0, 0, 0)
        )
        info.compress_type = ZIP_DEFLATED
        info.external_attr = 0o100644 << 16
        out.writestr(info, manifest)

    checksum = sha256(archive.read_bytes())
    (DIST / f"{archive.name}.sha256").write_text(
        f"{checksum}  {archive.name}\n", encoding="utf-8"
    )
    print(archive.relative_to(ROOT))
    print(checksum)


if __name__ == "__main__":
    main()
