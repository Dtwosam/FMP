from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2019_dispatch_preflight import (
    build_2019_dispatch_preflight,
    validate_2019_dispatch_preflight,
    validate_2019_dispatch_preflight_sources,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
HEAD = "a" * 40

INSTALL_RECEIPT_JSON = r"""
{
  "annual_segment_label": "2019",
  "annual_workflow_dispatch_authorized": false,
  "broker_mutation_authorized": false,
  "changed_files": [
    "src/fmp/discovery/annual_pattern_catalogue_2019_runtime_authorization.py",
    "src/fmp/discovery/annual_pattern_catalogue_runtime.py"
  ],
  "cross_year_result_production_authorized": false,
  "decision": "DEC-561",
  "demo_order_authorized": false,
  "expected_run_attempt": 1,
  "expected_run_number": 381,
  "historical_artifact_read_authorized": false,
  "historical_catalogue_execution_authorized": false,
  "historical_result_production_authorized": false,
  "install_action_consumed": true,
  "install_action_source_blob_sha": "15cc0c8e3b93453ecaf6ba1dfd635133279acb6c",
  "install_commit_sha": "ea3d63b5181fc592039c0c26d6decb358e43f7cc",
  "install_receipt_fingerprint_sha256": "098d2d24fbce40943ccff16a9ae1374e77facc0804365fedbb15eb128b3ca7be",
  "installed_gate_blob_sha": "d87fe85a5b426fa92caf7d6cc165445590f4097c",
  "installed_runtime_blob_sha": "07ddfe7a968de10cd1d4f8592760cc9eb9e6300e",
  "live_order_authorized": false,
  "next_gate": "READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2019_DISPATCH_PREFLIGHT",
  "next_segment_execution_authorized": false,
  "phase8b_authorized": false,
  "previous_annual_freeze_run_id": 37237817538,
  "promotion_authorized": false,
  "real_money_authorized": false,
  "repository_full_name": "Dtwosam/FMP",
  "runtime_authorization_installed": true,
  "runtime_gate_active": true,
  "source_action_artifact_digest": "sha256:dcd16ee2ddbdf9c5b17acfe6e79b54f1dbf6a38a839362ecc91a896f41520354",
  "source_action_artifact_id": 11341025756,
  "source_action_decision": "DEC-560",
  "source_action_fingerprint_sha256": "c68df812693da1edfc5ab568afef50b2e70797a04b4c44cf22de7c3fc15bea35",
  "source_action_workflow_head_sha": "bacb20c1d1541ac0b46076cef8ca9fe898559339",
  "source_action_workflow_run_id": 37299664787,
  "stage": "ANNUAL_CATALOGUE_2019_RUNTIME_AUTHORIZATION_INSTALLED",
  "strategy_v1_synthesis_authorized": false,
  "trading_authorized": false,
  "version": "fmp-annual-catalogue-2019-runtime-authorization-install-receipt-v1"
}
"""


def _install_receipt() -> dict[str, object]:
    value = json.loads(INSTALL_RECEIPT_JSON)
    assert isinstance(value, dict)
    return value


def _main() -> dict[str, object]:
    return {"name": "main", "commit": {"sha": HEAD}}


def _run(
    *,
    run_id: int,
    number: int,
    head_sha: str,
    conclusion: str,
) -> dict[str, object]:
    return {
        "id": run_id,
        "name": "phase8a-annual-pattern-catalogue",
        "path": ".github/workflows/phase8a-annual-pattern-catalogue.yml",
        "event": "workflow_dispatch",
        "head_branch": "main",
        "head_sha": head_sha,
        "run_number": number,
        "run_attempt": 1,
        "status": "completed",
        "conclusion": conclusion,
    }


def _annual_runs() -> dict[str, object]:
    return {
        "workflow_runs": [
            _run(
                run_id=37237817538,
                number=380,
                head_sha="30971a996f514670a6f836d8e45cf80137197a4f",
                conclusion="success",
            ),
            _run(
                run_id=37227536041,
                number=379,
                head_sha="7b4c1ef8573e280c067443b72f1534d9091d5b7f",
                conclusion="success",
            ),
            _run(
                run_id=37206992367,
                number=378,
                head_sha="2524fde355349581c9440a172d0384c3cbce31ed",
                conclusion="success",
            ),
            _run(
                run_id=37198002653,
                number=377,
                head_sha="a89db974be9a94481e7ed0990476bc661012f1e4",
                conclusion="success",
            ),
            _run(
                run_id=37191637168,
                number=376,
                head_sha="4c14fa7db6eb812b89ecb79201f7e298fa9c04f3",
                conclusion="failure",
            ),
            _run(
                run_id=37126711695,
                number=1,
                head_sha="fd85a886d07234ad584dcca08692b37e6af54b2e",
                conclusion="failure",
            ),
        ]
    }


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-562 requires installed annual workflow and 2019 runtime state",
)
class AnnualPatternCatalogue2019DispatchPreflightTests(unittest.TestCase):
    def test_sources_pin_installed_runtime_and_dec561_receipt(self) -> None:
        value = validate_2019_dispatch_preflight_sources(
            repository_root=REPOSITORY_ROOT,
        )
        self.assertEqual(
            value["install_receipt_source_blob_sha"],
            "5befb123f9d3f01cd4457c992c454c662a9f5b7d",
        )
        self.assertEqual(
            value["active_workflow_blob_sha"],
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        )
        self.assertEqual(
            value["installed_gate_blob_sha"],
            "d87fe85a5b426fa92caf7d6cc165445590f4097c",
        )
        self.assertEqual(
            value["installed_runtime_blob_sha"],
            "07ddfe7a968de10cd1d4f8592760cc9eb9e6300e",
        )

    def test_preflight_freezes_run381_without_authorizing_dispatch(self) -> None:
        value = build_2019_dispatch_preflight(
            _install_receipt(),
            repository_root=REPOSITORY_ROOT,
            main_branch=_main(),
            annual_workflow_runs=_annual_runs(),
            expected_head_sha=HEAD,
        )
        self.assertIs(validate_2019_dispatch_preflight(value), value)
        self.assertEqual(value["decision"], "DEC-562")
        self.assertEqual(value["source_installer_workflow_run_id"], 37304310188)
        self.assertEqual(value["source_install_artifact_id"], 11342593171)
        self.assertEqual(
            value["source_install_receipt_fingerprint_sha256"],
            "098d2d24fbce40943ccff16a9ae1374e77facc0804365fedbb15eb128b3ca7be",
        )
        self.assertEqual(value["expected_run_number"], 381)
        self.assertEqual(value["expected_run_attempt"], 1)
        self.assertEqual(value["previous_annual_freeze_run_id"], 37237817538)
        self.assertEqual(value["annual_workflow_run_count"], 6)
        self.assertEqual(value["successful_2018_run_id"], 37237817538)
        self.assertTrue(value["runtime_authorization_installed"])
        self.assertTrue(value["runtime_gate_active"])
        self.assertTrue(value["preflight_read_only"])
        self.assertFalse(value["dispatch_command_present"])
        self.assertFalse(value["annual_workflow_dispatch_authorized"])
        self.assertFalse(value["historical_catalogue_execution_authorized"])
        self.assertFalse(value["next_segment_execution_authorized"])
        self.assertFalse(value["trading_authorized"])

    def test_run381_already_present_fails_closed(self) -> None:
        runs = _annual_runs()
        rows = runs["workflow_runs"]
        assert isinstance(rows, list)
        rows.insert(
            0,
            _run(
                run_id=999999,
                number=381,
                head_sha="d" * 40,
                conclusion="failure",
            ),
        )
        with self.assertRaisesRegex(ValueError, "exactly six prior"):
            build_2019_dispatch_preflight(
                _install_receipt(),
                repository_root=REPOSITORY_ROOT,
                main_branch=_main(),
                annual_workflow_runs=runs,
                expected_head_sha=HEAD,
            )

    def test_install_receipt_tampering_fails_closed(self) -> None:
        receipt = copy.deepcopy(_install_receipt())
        receipt["annual_workflow_dispatch_authorized"] = True
        with self.assertRaisesRegex(ValueError, "fingerprint mismatch"):
            build_2019_dispatch_preflight(
                receipt,
                repository_root=REPOSITORY_ROOT,
                main_branch=_main(),
                annual_workflow_runs=_annual_runs(),
                expected_head_sha=HEAD,
            )

    def test_main_drift_fails_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "current main head mismatch"):
            build_2019_dispatch_preflight(
                _install_receipt(),
                repository_root=REPOSITORY_ROOT,
                main_branch={"name": "main", "commit": {"sha": "c" * 40}},
                annual_workflow_runs=_annual_runs(),
                expected_head_sha=HEAD,
            )

    def test_cli_is_plan_only(self) -> None:
        text = (
            REPOSITORY_ROOT
            / "scripts/phase8a_annual_pattern_catalogue_2019_dispatch_preflight.py"
        ).read_text(encoding="utf-8")
        self.assertIn('subparsers.add_parser("plan")', text)
        self.assertNotIn("gh workflow run ", text)
        self.assertNotIn('subparsers.add_parser("dispatch")', text)


if __name__ == "__main__":
    unittest.main()
