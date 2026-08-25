from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from sag_collatz.matrix_cubic_templates import (
    RELATIVE_CUBIC_2D_FARKAS_TEMPLATES,
    RELATIVE_CUBIC_EXTENDED_2D_FARKAS_TEMPLATES,
    RELATIVE_CUBIC_FULL_2D_FARKAS_TEMPLATES,
    RULE_NAMES,
)


ROOT = Path(__file__).resolve().parents[1]


class RelativeCubicMatrixCertificateTests(unittest.TestCase):
    def test_template_table_is_nonnegative_and_has_the_expected_size(self) -> None:
        self.assertEqual(len(RELATIVE_CUBIC_2D_FARKAS_TEMPLATES), 47)
        self.assertEqual(len(RELATIVE_CUBIC_EXTENDED_2D_FARKAS_TEMPLATES), 96)
        self.assertEqual(len(RELATIVE_CUBIC_FULL_2D_FARKAS_TEMPLATES), 103)
        self.assertEqual(
            RELATIVE_CUBIC_EXTENDED_2D_FARKAS_TEMPLATES[:47],
            RELATIVE_CUBIC_2D_FARKAS_TEMPLATES,
        )
        self.assertEqual(
            RELATIVE_CUBIC_FULL_2D_FARKAS_TEMPLATES[:96],
            RELATIVE_CUBIC_EXTENDED_2D_FARKAS_TEMPLATES,
        )
        for template in RELATIVE_CUBIC_FULL_2D_FARKAS_TEMPLATES:
            self.assertTrue(template)
            self.assertTrue(
                any(rule in ("dynamic-even", "dynamic-odd") and component == 0
                    and weight > 0 for rule, component, weight in template)
            )
            for _, component, weight in template:
                self.assertIn(component, (0, 1))
                self.assertIs(type(weight), int)
                self.assertGreaterEqual(weight, 0)

    def test_optimized_exact_enumerator_reproduces_the_full_coverage(self) -> None:
        compiler = shutil.which("clang++") or shutil.which("g++")
        if compiler is None:
            self.skipTest("no C++17 compiler available")
        source = ROOT / "tools" / "verify_relative_cubic.cpp"
        with tempfile.TemporaryDirectory() as directory:
            executable = Path(directory) / "verify-relative-cubic"
            subprocess.run(
                [compiler, "-O3", "-std=c++17", str(source), "-o", str(executable)],
                check=True,
                capture_output=True,
                text=True,
            )
            completed = subprocess.run(
                [str(executable)], check=True, capture_output=True, text=True
            )
            completed_extended = subprocess.run(
                [str(executable), "--upper-left-two"],
                check=True,
                capture_output=True,
                text=True,
            )
            completed_full = subprocess.run(
                [str(executable), "--upper-left-three"],
                check=True,
                capture_output=True,
                text=True,
            )

        def checksum(templates: tuple) -> int:
            value = 1_469_598_103_934_665_603
            mask = (1 << 64) - 1
            for template in templates:
                value ^= len(template) + 1
                value = (value * 1_099_511_628_211) & mask
                for rule, component, weight in template:
                    for part in (RULE_NAMES.index(rule), component, weight):
                        value ^= part + 1
                        value = (value * 1_099_511_628_211) & mask
            return value

        self.assertEqual(
            json.loads(completed.stdout),
            {
                "raw_assignments": 64 ** 7,
                "core_survivors": 47_378,
                "full_survivors": 8_546_864,
                "templates": 47,
                "template_checksum": checksum(
                    RELATIVE_CUBIC_2D_FARKAS_TEMPLATES
                ),
                "uncovered": 0,
            },
        )
        self.assertEqual(
            json.loads(completed_extended.stdout),
            {
                "raw_assignments": 128 ** 7,
                "core_survivors": 170_450,
                "full_survivors": 33_099_480,
                "templates": 96,
                "template_checksum": checksum(
                    RELATIVE_CUBIC_EXTENDED_2D_FARKAS_TEMPLATES
                ),
                "uncovered": 0,
            },
        )
        self.assertEqual(
            json.loads(completed_full.stdout),
            {
                "raw_assignments": 192 ** 7,
                "core_survivors": 375_570,
                "full_survivors": 72_169_932,
                "templates": 103,
                "template_checksum": checksum(
                    RELATIVE_CUBIC_FULL_2D_FARKAS_TEMPLATES
                ),
                "structural_families": 12,
                "structural_coverage": [
                    52_698_288,
                    14_886_420,
                    3_017_712,
                    255_360,
                    745_632,
                    26_208,
                    71_532,
                    1_152,
                    444_192,
                    12_480,
                    6_132,
                    4_824,
                ],
                "uncovered": 0,
            },
        )


if __name__ == "__main__":
    unittest.main()
