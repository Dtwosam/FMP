from __future__ import annotations

"""DEC-638: exclusive leaf-file creation integration, never annual dispatch."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PREFIX = "phase8a_annual_pattern_catalogue_2023_"
AUDITS = (
    "admin_lock_handoff",
    "dispatch_action_preflight",
    "dispatch_authorization",
    "dispatch_immutability_audit",
    "dispatch_preflight",
    "execution_preflight",
    "runtime_authorization_install_action",
    "runtime_authorization_install_preflight",
    "runtime_authorization_install_receipt",
    "runtime_authorization_plan",
)


class LegacyAuditReportExclusiveOutputTests(unittest.TestCase):
    def test_all_ten_wrappers_use_exclusive_report_writer(self):
        self.assertEqual(len(AUDITS), 10)
        for suffix in AUDITS:
            with self.subTest(script=suffix):
                src = (ROOT / "scripts" / f"{PREFIX}{suffix}.py").read_text(encoding="utf-8")
                self.assertIn(
                    "from fmp.discovery.annual_pattern_catalogue_2023_external_report_create "
                    "import write_once_external_report", src,
                )
                self.assertEqual(src.count("write_once_external_report("), 1)
                self.assertNotIn("target.write_text(", src)
                self.assertNotIn("path.write_text(", src)
                self.assertNotIn("destination.write_text(", src)
                self.assertIn("sys.dont_write_bytecode = True", src)
                self.assertIn("if target.is_relative_to(source_checkout):", src)

    def test_nested_writer_callers_check_checkout_before_writing(self):
        # Some wrappers define _write_json before _cmd_* in source text;
        # the actual call is correctly guarded inside _cmd_*, not _write_json.
        for suffix in AUDITS:
            with self.subTest(script=suffix):
                src = (ROOT / "scripts" / f"{PREFIX}{suffix}.py").read_text(encoding="utf-8")
                marker = "if target.is_relative_to(source_checkout):"
                guard = src.index(marker)
                if "def _write_json(" in src:
                    self.assertIn("_write_json(target,", src)
                    self.assertLess(guard, src.rindex("_write_json(target,"))
                else:
                    self.assertLess(guard, src.index("write_once_external_report(target,"))

    def test_shared_helper_remains_leaf_exclusive_and_inert(self):
        helper = (
            ROOT / "src" / "fmp" / "discovery"
            / "annual_pattern_catalogue_2023_external_report_create.py"
        ).read_text(encoding="utf-8")
        self.assertEqual(helper.count('target.open("x", encoding="utf-8")'), 1)
        self.assertIn("except FileExistsError:", helper)
        self.assertNotIn("target.write_text(", helper)
        self.assertNotIn("subprocess", helper)
        self.assertNotIn("requests", helper)


if __name__ == "__main__":
    unittest.main()
