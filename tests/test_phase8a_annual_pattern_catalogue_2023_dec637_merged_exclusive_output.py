from __future__ import annotations

"""DEC-637: verify both merged offline audit CLIs use exclusive leaf creation."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PREFIX = "phase8a_annual_pattern_catalogue_2023_"
AUDITS = ("precheckout_job_if_preview", "review_manifest_identity_separation")


class MergedAuditExclusiveOutputIntegrationTests(unittest.TestCase):
    def test_both_scripts_are_checkout_guarded_and_exclusively_create_reports(self):
        self.assertEqual(len(AUDITS), 2)
        for suffix in AUDITS:
            with self.subTest(suffix=suffix):
                source = (ROOT / "scripts" / f"{PREFIX}{suffix}.py").read_text(encoding="utf-8")
                self.assertIn("source_checkout = Path(__file__).resolve().parents[1]", source)
                self.assertIn("if target.is_relative_to(source_checkout):", source)
                self.assertIn(
                    "from fmp.discovery.annual_pattern_catalogue_2023_external_report_create "
                    "import write_once_external_report", source,
                )
                self.assertEqual(source.count("write_once_external_report(target,"), 1)
                self.assertLess(
                    source.index("if target.is_relative_to(source_checkout):"),
                    source.index("write_once_external_report(target,"),
                )
                self.assertNotIn("target.write_text(", source)
                self.assertIn("sys.dont_write_bytecode = True", source)

    def test_shared_helper_requires_exclusive_mode_and_never_dispatches(self):
        helper = (
            ROOT / "src" / "fmp" / "discovery"
            / "annual_pattern_catalogue_2023_external_report_create.py"
        ).read_text(encoding="utf-8")
        self.assertIn('preview_write_once_external_report(target, content, conflict_message)', helper)
        self.assertIn("except FileExistsError:", (Path(__file__).resolve().parents[1] / "src/fmp/discovery/annual_pattern_catalogue_2023_dirfd_publication_preview.py").read_text(encoding="utf-8"))
        self.assertNotIn("subprocess", helper)
        self.assertNotIn("requests", helper)


if __name__ == "__main__":
    unittest.main()
