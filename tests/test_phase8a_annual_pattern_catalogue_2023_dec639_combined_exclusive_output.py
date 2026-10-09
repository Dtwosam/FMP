from __future__ import annotations

"""DEC-639 rehearsal-only cross-branch audit of the 23 external report CLIs."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PREFIX = "phase8a_annual_pattern_catalogue_2023_"
WRITER = (
    "from fmp.discovery.annual_pattern_catalogue_2023_external_report_create "
    "import write_once_external_report"
)


class CombinedExclusiveOutputRehearsalTests(unittest.TestCase):
    def test_all_23_clis_have_checkout_guards_and_exclusive_report_writer(self):
        scripts = sorted((ROOT / "scripts").glob(f"{PREFIX}*.py"))
        self.assertEqual(len(scripts), 23, "Reevaluate the full audit CLI inventory")
        for script in scripts:
            with self.subTest(script=script.name):
                content = script.read_text(encoding="utf-8")
                self.assertIn("sys.dont_write_bytecode = True", content)
                self.assertIn(WRITER, content)
                self.assertIn("write_once_external_report(", content)
                self.assertIn("target.is_relative_to(", content)
                self.assertNotIn("target.write_text(", content)
                self.assertNotIn("args.out.write_text(", content)
                self.assertNotIn("destination.write_text(", content)
                self.assertLess(content.index("sys.dont_write_bytecode = True"), content.index("from fmp"))

    def test_single_shared_writer_uses_exclusive_leaf_create(self):
        module = ROOT / "src/fmp/discovery/annual_pattern_catalogue_2023_external_report_create.py"
        content = module.read_text(encoding="utf-8")
        self.assertEqual(content.count('os.link(staged, target)'), 1)
        self.assertIn("except FileExistsError:", content)
        self.assertNotIn("target.write_text(", content)


if __name__ == "__main__":
    unittest.main()
