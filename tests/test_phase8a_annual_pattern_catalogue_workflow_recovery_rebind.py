from __future__ import annotations

import hashlib
import os
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2015_replacement_execution_authorization import (
    EXPECTED_REPLACEMENT_RUN_NUMBER,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
PREINSTALL_SNAPSHOT = os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1"
WORKFLOW = (
    REPOSITORY_ROOT
    / ".github/workflows/phase8a-annual-pattern-catalogue.yml"
)
RUNTIME = (
    REPOSITORY_ROOT
    / "src/fmp/discovery/annual_pattern_catalogue_runtime.py"
)
GATE_TEMPLATE = (
    REPOSITORY_ROOT
    / "docs/superpowers/templates/"
    "annual_pattern_catalogue_2016_runtime_authorization.py.disabled"
)
RUNTIME_TEMPLATE = (
    REPOSITORY_ROOT
    / "docs/superpowers/templates/"
    "annual_pattern_catalogue_runtime_with_2016_authorization.py.disabled"
)


def _git_blob_sha(path: Path) -> str:
    payload = path.read_bytes()
    return hashlib.sha1(
        f"blob {len(payload)}\0".encode("ascii") + payload
    ).hexdigest()


class AnnualCatalogueWorkflowRecoveryRebindTests(unittest.TestCase):
    @unittest.skipIf(
        PREINSTALL_SNAPSHOT,
        "historical preinstall snapshot intentionally hides annual workflow",
    )
    def test_live_workflow_is_corrected_blob(self) -> None:
        self.assertEqual(
            _git_blob_sha(WORKFLOW),
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        )

    @unittest.skipIf(
        PREINSTALL_SNAPSHOT,
        "historical preinstall snapshot intentionally hides annual workflow",
    )
    def test_each_upload_block_has_one_hidden_file_flag(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        marker = "uses: actions/upload-artifact@v6"
        blocks = [marker + suffix for suffix in text.split(marker)[1:]]
        self.assertEqual(len(blocks), 3)
        for name, path in (
            ("phase8a-annual-catalogue-preflight-", "path: .preflight"),
            ("phase8a-annual-catalogue-cell-", "path: .result"),
            (
                "phase8a-annual-catalogue-freeze-",
                "path: .annual-freeze/annual-freeze.json",
            ),
        ):
            with self.subTest(name=name):
                matches = [block for block in blocks if name in block]
                self.assertEqual(len(matches), 1)
                self.assertIn(path, matches[0])
                self.assertEqual(
                    matches[0].count("include-hidden-files: true"),
                    1,
                )

    def test_replacement_runtime_identity_is_exact_run_378(self) -> None:
        self.assertEqual(EXPECTED_REPLACEMENT_RUN_NUMBER, 377)
        runtime = RUNTIME.read_text(encoding="utf-8")
        self.assertIn("if effective_run_number == 377:", runtime)
        self.assertNotIn("if effective_run_number == 2:", runtime)

    def test_dormant_2016_identity_is_exact_run_378(self) -> None:
        gate = GATE_TEMPLATE.read_text(encoding="utf-8")
        runtime = RUNTIME_TEMPLATE.read_text(encoding="utf-8")
        self.assertIn("EXPECTED_RUN_NUMBER = 378", gate)
        self.assertIn(
            'segment == "2016" and effective_run_number == 378',
            runtime,
        )
        self.assertIn("if effective_run_number == 377:", runtime)
        self.assertNotIn("EXPECTED_RUN_NUMBER = 3", gate.splitlines())


if __name__ == "__main__":
    unittest.main()
