from __future__ import annotations

import unittest
from pathlib import Path


class Phase1RecoveryAccountingSqlTests(unittest.TestCase):
    def test_recovery_accounting_audit_covers_frozen_plan_and_pair_side_breakdown(self) -> None:
        sql = Path("docs/phase1-recovery-accounting-audit.sql").read_text(encoding="utf-8")

        self.assertIn("25500", sql)
        self.assertIn("2015-01-01", sql)
        self.assertIn("2026-08-21", sql)
        self.assertIn("raw_backed_manifests", sql)
        self.assertIn("manifest_only_inferred_not_found", sql)
        self.assertIn("raw_without_manifest", sql)
        self.assertIn("unexpected_manifest_paths", sql)
        self.assertIn("unexpected_raw_paths", sql)
        self.assertIn("pair_side_breakdown", sql)
        self.assertIn("accounting_gate_pass", sql)

    def test_recovery_accounting_documents_manifest_only_inference(self) -> None:
        sql = Path("docs/phase1-recovery-accounting-audit.sql").read_text(encoding="utf-8")

        self.assertIn("raw first, then manifest", sql.lower())
        self.assertIn("not_found", sql)
        self.assertIn("immutable", sql.lower())


if __name__ == "__main__":
    unittest.main()
