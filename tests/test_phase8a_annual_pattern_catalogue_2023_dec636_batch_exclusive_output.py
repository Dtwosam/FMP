from __future__ import annotations

"""DEC-636: ensure all seven staged offline audit scripts use the same safe writer."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PREFIX = "phase8a_annual_pattern_catalogue_2023_"
AUDITS = (
    "ambiguous_dispatch_hold_model",
    "disarmed_tag_amendment_preview",
    "lock_witness_coverage",
    "preaccess_identity_gate_topology_audit",
    "ref_race_interleaving_model",
    "runtime_tag_sha_binding_preview",
    "three_layer_admission_model",
)


class BatchExclusiveOutputIntegrationTests(unittest.TestCase):
    def test_seven_scripts_call_shared_exclusive_writer_and_keep_source_denial(self):
        self.assertEqual(len(AUDITS), 7)
        for suffix in AUDITS:
            with self.subTest(script=suffix):
                script = ROOT / "scripts" / f"{PREFIX}{suffix}.py"
                source = script.read_text(encoding="utf-8")
                self.assertIn(
                    "from fmp.discovery.annual_pattern_catalogue_2023_external_report_create "
                    "import write_once_external_report", source,
                )
                self.assertEqual(source.count("write_once_external_report(target,"), 1)
                self.assertIn("target.is_relative_to(source_checkout)", source)
                self.assertIn("sys.dont_write_bytecode = True", source)
                self.assertNotIn("target.write_text(", source)
                self.assertNotIn("target.parent.mkdir(", source)
                self.assertLess(
                    source.index("if target.is_relative_to(source_checkout):"),
                    source.index("write_once_external_report(target,"),
                )

    def test_no_live_dispatch_or_authority_added_to_any_script(self):
        # This regression controls only added output-writer functionality;
        # source-level checks are not a substitute for independent review.
        for suffix in AUDITS:
            with self.subTest(script=suffix):
                source = (ROOT / "scripts" / f"{PREFIX}{suffix}.py").read_text(encoding="utf-8")
                self.assertNotIn("import requests", source)
                self.assertNotIn("import subprocess", source)
                self.assertNotIn("gh workflow run", source)
                self.assertNotIn("workflow_dispatch(", source)
                self.assertNotIn("place_order(", source)

    def test_shared_helper_matches_expected_exclusive_create_boundary(self):
        helper = (
            ROOT / "src" / "fmp" / "discovery"
            / "annual_pattern_catalogue_2023_external_report_create.py"
        ).read_text(encoding="utf-8")
        self.assertEqual(helper.count('target.open("x", encoding="utf-8")'), 1)
        self.assertIn("except FileExistsError:", helper)
        self.assertNotIn("target.write_text(", helper)


if __name__ == "__main__":
    unittest.main()
