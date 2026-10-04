from __future__ import annotations

import copy
import importlib
import os
from pathlib import Path
import unittest
from unittest.mock import patch

from fmp.discovery import annual_pattern_catalogue_2016_post_install_runtime_repair as repair_module
from fmp.discovery.annual_pattern_catalogue_2016_post_install_runtime_repair import (
    build_2016_post_install_runtime_repair,
    validate_2016_post_install_runtime_repair,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
PREINSTALL_SNAPSHOT = os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1"
REPAIR_HEAD = "a" * 40


def _run() -> dict[str, object]:
    return {
        "id": 37205170186,
        "name": "phase8a-annual-catalogue-2016-runtime-install-executor",
        "path": (
            ".github/workflows/"
            "phase8a-annual-catalogue-2016-runtime-install-executor.yml"
        ),
        "event": "workflow_dispatch",
        "head_branch": "main",
        "head_sha": "481e3127415e0b676c590a6edf7e30c0bc10760f",
        "run_number": 2,
        "run_attempt": 1,
        "status": "completed",
        "conclusion": "failure",
    }


def _jobs() -> dict[str, object]:
    names = [
        ("Set up job", "success"),
        ("Apply exact two-file runtime authorization install", "success"),
        ("Commit exact DEC-518 install", "success"),
        ("Push only the exact install commit to main", "success"),
        ("Build concrete DEC-508 install receipt", "failure"),
    ]
    return {
        "jobs": [
            {
                "id": 111444750917,
                "name": "install-runtime-authorization",
                "status": "completed",
                "conclusion": "failure",
                "steps": [
                    {
                        "name": name,
                        "status": "completed",
                        "conclusion": conclusion,
                    }
                    for name, conclusion in names
                ],
            }
        ]
    }


@unittest.skipIf(
    PREINSTALL_SNAPSHOT,
    "post-install repair requires active annual runtime state",
)
class AnnualCatalogue2016PostInstallRuntimeRepairTests(unittest.TestCase):
    def test_repaired_runtime_imports_without_cycle(self) -> None:
        module = importlib.import_module(
            "fmp.discovery.annual_pattern_catalogue_runtime"
        )
        self.assertTrue(
            callable(module.require_historical_catalogue_execution_authorized)
        )

    def test_sources_keep_historical_repaired_runtime_pins(self) -> None:
        self.assertEqual(
            repair_module.EXPECTED_ACTIVE_GATE_BLOB_SHA,
            "5b034fba697c3de0c0f8b6140d6f84771f1ae54b",
        )
        self.assertEqual(
            repair_module.EXPECTED_RUNTIME_BLOB_SHA,
            "b564f5a26fdef146fc6080962e7c4762b0b5949a",
        )
        self.assertEqual(
            repair_module.EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA,
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        )

    def _historical_sources(self) -> dict[str, str]:
        return {
            "active_gate_blob_sha": repair_module.EXPECTED_ACTIVE_GATE_BLOB_SHA,
            "runtime_blob_sha": repair_module.EXPECTED_RUNTIME_BLOB_SHA,
            "active_workflow_blob_sha": (
                repair_module.EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA
            ),
        }

    def test_exact_failed_installer_yields_dispatch_locked_repair(self) -> None:
        with patch.object(
            repair_module,
            "validate_2016_post_install_runtime_repair_sources",
            return_value=self._historical_sources(),
        ):
            value = build_2016_post_install_runtime_repair(
                repository_root=REPOSITORY_ROOT,
                installer_run=_run(),
                installer_jobs=_jobs(),
                repair_head_sha=REPAIR_HEAD,
            )
        self.assertIs(validate_2016_post_install_runtime_repair(value), value)
        self.assertEqual(value["decision"], "DEC-531")
        self.assertEqual(
            value["install_commit_sha"],
            "525386dd68955e9f02909f9692987968ab15e516",
        )
        self.assertTrue(value["install_mutation_pushed"])
        self.assertTrue(value["install_receipt_failed_after_push"])
        self.assertTrue(value["runtime_import_cycle_repaired"])
        self.assertFalse(value["annual_workflow_dispatch_authorized"])
        self.assertFalse(value["run_378_authorized"])
        self.assertFalse(value["run_379_or_later_authorized"])
        self.assertFalse(value["trading_authorized"])

    def test_missing_successful_push_step_is_rejected(self) -> None:
        jobs = copy.deepcopy(_jobs())
        steps = jobs["jobs"][0]["steps"]
        assert isinstance(steps, list)
        for row in steps:
            if row["name"] == "Push only the exact install commit to main":
                row["conclusion"] = "failure"
        with patch.object(
            repair_module,
            "validate_2016_post_install_runtime_repair_sources",
            return_value=self._historical_sources(),
        ):
            with self.assertRaisesRegex(
                ValueError,
                "required successful installer step",
            ):
                build_2016_post_install_runtime_repair(
                    repository_root=REPOSITORY_ROOT,
                    installer_run=_run(),
                    installer_jobs=jobs,
                    repair_head_sha=REPAIR_HEAD,
                )


if __name__ == "__main__":
    unittest.main()
