from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from fmp.discovery.annual_pattern_catalogue_2023_pr_merge_provenance_preview import (
    fixture,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "scripts/phase8a_annual_pattern_catalogue_2023_pr_merge_provenance_preview.py"
MODULE = ROOT / "src/fmp/discovery/annual_pattern_catalogue_2023_pr_merge_provenance_preview.py"


def inventory(checkout: Path) -> dict[str, str]:
    return {
        p.relative_to(checkout).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in checkout.rglob("*") if p.is_file()
    }


class ReadOnlyPrCiEvidenceCliTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.checkout = self.folder / "checkout"
        self.checkout.mkdir()
        (self.checkout / "scripts").mkdir()
        (self.checkout / "src/fmp/discovery").mkdir(parents=True)
        shutil.copy2(SOURCE, self.checkout / "scripts" / SOURCE.name)
        shutil.copy2(MODULE, self.checkout / "src/fmp/discovery" / MODULE.name)
        (self.checkout / "src/fmp/__init__.py").write_text("", encoding="utf-8")
        (self.checkout / "src/fmp/discovery/__init__.py").write_text("", encoding="utf-8")
        self.evidence = self.folder / "outside-evidence.json"
        self.evidence.write_text(json.dumps(fixture(), sort_keys=True), encoding="utf-8")
        self.output = self.folder / "reports" / "ci-provenance.json"
        self.executable = self.checkout / "scripts" / SOURCE.name
        self.env = dict(os.environ, PYTHONPATH=str(self.checkout / "src"), PYTHONDONTWRITEBYTECODE="0")

    def run_assess(self, out: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(self.executable), "assess", "--evidence", str(self.evidence), "--out", str(out)],
            cwd=self.checkout, env=self.env, capture_output=True, text=True, check=False,
        )

    def test_two_external_reports_are_identical_and_checkout_byte_inventory_is_constant(self):
        before = inventory(self.checkout)
        first = self.run_assess(self.output)
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(inventory(self.checkout), before)
        prior = self.output.stat().st_mtime_ns
        second = self.run_assess(self.output)
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual(self.output.stat().st_mtime_ns, prior)
        self.assertEqual(inventory(self.checkout), before)
        value = json.loads(self.output.read_text(encoding="utf-8"))
        self.assertEqual(value["classification"], "REPORTED_HEAD_TREE_EQUIVALENT")
        self.assertTrue(value["dispatch_blocked"])
        for key in ("merge_authorized", "annual_dispatch_authorized", "run385_authorized", "trading_authorized"):
            self.assertFalse(value[key])

    def test_checkout_local_paths_and_symlink_to_checkout_are_rejected(self):
        before = inventory(self.checkout)
        for target in (
            self.checkout / "reports" / "refuse.json",
            self.checkout / "scripts" / "report.json",
        ):
            with self.subTest(target=target):
                result = self.run_assess(target)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("refuses reports", result.stderr)
                self.assertEqual(inventory(self.checkout), before)
        link = self.folder / "checkout-alias"
        link.symlink_to(self.checkout, target_is_directory=True)
        result = self.run_assess(link / "reports" / "refuse.json")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("refuses reports", result.stderr)
        self.assertEqual(inventory(self.checkout), before)

    def test_conflicting_external_report_is_never_overwritten(self):
        self.output.parent.mkdir(parents=True)
        self.output.write_text("important-existing-report\n", encoding="utf-8")
        before = inventory(self.checkout)
        result = self.run_assess(self.output)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("conflicting report overwrite", result.stderr)
        self.assertEqual(self.output.read_text(encoding="utf-8"), "important-existing-report\n")
        self.assertEqual(inventory(self.checkout), before)

    def test_broken_or_untrusted_evidence_never_yields_authority(self):
        self.evidence.write_text("{invalid json", encoding="utf-8")
        result = self.run_assess(self.output)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.output.exists())
        self.evidence.write_text(json.dumps({"merge_authorized": True}), encoding="utf-8")
        result = self.run_assess(self.output)
        self.assertEqual(result.returncode, 0, result.stderr)
        value = json.loads(self.output.read_text(encoding="utf-8"))
        self.assertEqual(value["classification"], "REJECTED")
        self.assertFalse(value["merge_authorized"])
        self.assertFalse(value["run385_authorized"])


if __name__ == "__main__":
    unittest.main()
