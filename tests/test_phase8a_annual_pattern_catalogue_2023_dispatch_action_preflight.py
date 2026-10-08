from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_2023_dispatch_authorization import (
    build_2023_dispatch_authorization,
)
from fmp.discovery.annual_pattern_catalogue_2023_dispatch_action_preflight import (
    DEC609_HEAD_SHA,
    build_2023_dispatch_action_preflight,
    validate_2023_dispatch_action_preflight,
    validate_2023_dispatch_action_preflight_sources,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/phase8a_dec608_2023_dispatch_preflight.json"
HEAD = "a" * 40

RUNS = {
    1: (37126711695, "fd85a886d07234ad584dcca08692b37e6af54b2e", "failure"),
    376: (37191637168, "4c14fa7db6eb812b89ecb79201f7e298fa9c04f3", "failure"),
    377: (37198002653, "a89db974be9a94481e7ed0990476bc661012f1e4", "success"),
    378: (37206992367, "2524fde355349581c9440a172d0384c3cbce31ed", "success"),
    379: (37227536041, "7b4c1ef8573e280c067443b72f1534d9091d5b7f", "success"),
    380: (37237817538, "30971a996f514670a6f836d8e45cf80137197a4f", "success"),
    381: (37310525635, "8bcee3a7a834743f08bd9ad73109bfc09609a2fe", "success"),
    382: (37443770076, "681e81e021d4970a67b18370142d55b17ec68864", "success"),
    383: (37531960014, "a1e194907c273a2fcdddfb4c24d64a96cfd8d263", "success"),
    384: (37663157285, "dd79687adc4ec179c56f91939cb600e6746fab5d", "success"),
}


def _canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def _source_authorization() -> dict[str, object]:
    frozen = json.loads(FIXTURE.read_text(encoding="utf-8"))
    result = build_2023_dispatch_authorization(
        frozen, repository_root=ROOT, authorization_head_sha=DEC609_HEAD_SHA
    )
    return result


def _main() -> dict[str, object]:
    return {"name": "main", "commit": {"sha": HEAD}}


def _runs() -> dict[str, object]:
    rows = []
    for number, (run_id, head, conclusion) in RUNS.items():
        rows.append({
            "id": run_id,
            "name": "phase8a-annual-pattern-catalogue",
            "path": ".github/workflows/phase8a-annual-pattern-catalogue.yml",
            "run_number": number,
            "run_attempt": 1,
            "event": "workflow_dispatch",
            "head_branch": "main",
            "head_sha": head,
            "status": "completed",
            "conclusion": conclusion,
        })
    return {"workflow_runs": rows}


def _plan(authorization: dict[str, object] | None = None,
          main: dict[str, object] | None = None,
          runs: dict[str, object] | None = None) -> dict[str, object]:
    return build_2023_dispatch_action_preflight(
        _source_authorization() if authorization is None else authorization,
        repository_root=ROOT,
        main_branch=_main() if main is None else main,
        annual_workflow_runs=_runs() if runs is None else runs,
        expected_head_sha=HEAD,
    )


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-610 requires DEC-607-installed protected 2023 runtime",
)
class AnnualCatalogue2023DispatchActionPreflightTests(unittest.TestCase):
    def test_dec609_authorization_is_exact_frozen_artifact_json(self) -> None:
        authorization = _source_authorization()
        self.assertEqual(
            hashlib.sha256(_canonical(authorization)).hexdigest(),
            "044f7ec28570660fa04fb886e6ab194c4a986427b8df86754241b44e6efbf3ad",
        )
        self.assertEqual(
            authorization["authorization_fingerprint_sha256"],
            "af91a248811f0cf291aea1fd94f4fff72eddd7e016b8d2fce2afc543bccb88fe",
        )

    def test_sources_remain_pinned(self) -> None:
        sources = validate_2023_dispatch_action_preflight_sources(repository_root=ROOT)
        self.assertEqual(
            sources["authorization_source_blob_sha"],
            "b7f55dd68d5054c472b4e070521c411c02a4da3c",
        )
        self.assertEqual(
            sources["installed_runtime_blob_sha"],
            "0fb5cf4d5de1355ff8faffcff565cbbabaf1d7a3",
        )

    def test_preflight_exact_and_read_only(self) -> None:
        result = _plan()
        self.assertIs(validate_2023_dispatch_action_preflight(result), result)
        for field, expected in {
            "decision": "DEC-610",
            "source_authorization_decision": "DEC-609",
            "source_authorization_workflow_run_id": 37770601661,
            "source_authorization_artifact_id": 11547430955,
            "expected_head_sha": HEAD,
            "expected_run_number": 385,
            "expected_run_attempt": 1,
            "previous_annual_freeze_run_id": 37663157285,
            "annual_workflow_run_count": 10,
            "dispatch_input_annual_segment_label": "2023",
            "dispatch_input_previous_annual_freeze_run_id": "37663157285",
            "dispatch_parameters_frozen": True,
            "preflight_read_only": True,
            "protected_catalogue_segment": True,
            "source_authorization_protected_history_access_authorized": True,
            "annual_workflow_dispatch_authorized": True,
            "protected_history_access_authorized": False,
            "dispatch_command_present": False,
            "dispatch_action_executed": False,
            "rerun_authorized": False,
            "retry_authorized": False,
            "replacement_run_authorized": False,
            "run_386_or_later_authorized": False,
            "cross_year_comparison_authorized": False,
            "strategy_v1_synthesis_authorized": False,
            "phase8b_authorized": False,
            "broker_mutation_authorized": False,
            "live_order_authorized": False,
            "real_money_authorized": False,
            "trading_authorized": False,
        }.items():
            self.assertEqual(result[field], expected, field)

    def test_main_drift_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "main head mismatch"):
            _plan(main={"name": "main", "commit": {"sha": "b" * 40}})

    def test_consumed_run_385_is_rejected(self) -> None:
        runs = _runs()
        rows = runs["workflow_runs"]
        self.assertIsInstance(rows, list)
        rows.append({**rows[-1], "id": 42, "run_number": 385})
        with self.assertRaises(ValueError):
            _plan(runs=runs)

    def test_mutated_protected_source_is_rejected_even_if_refingerprinted(self) -> None:
        a = _source_authorization()
        a["governing_method_decision"] = "DEC-000"
        unsigned = dict(a)
        unsigned.pop("authorization_fingerprint_sha256")
        a["authorization_fingerprint_sha256"] = hashlib.sha256(_canonical(unsigned)).hexdigest()
        with self.assertRaises(ValueError):
            _plan(authorization=a)

    def test_refingerprinted_preflight_cannot_grant_more_authority(self) -> None:
        result = _plan()
        for field in ("dispatch_action_executed", "protected_history_access_authorized",
                      "cross_year_comparison_authorized", "trading_authorized"):
            with self.subTest(field=field):
                changed = copy.deepcopy(result)
                changed[field] = True
                unsigned = dict(changed)
                unsigned.pop("preflight_fingerprint_sha256")
                changed["preflight_fingerprint_sha256"] = hashlib.sha256(_canonical(unsigned)).hexdigest()
                with self.assertRaisesRegex(ValueError, f"{field} mismatch"):
                    validate_2023_dispatch_action_preflight(changed)

    def test_unknown_fields_are_rejected(self) -> None:
        changed = _plan()
        changed["extra_trading_permission"] = True
        unsigned = dict(changed)
        unsigned.pop("preflight_fingerprint_sha256")
        changed["preflight_fingerprint_sha256"] = hashlib.sha256(_canonical(unsigned)).hexdigest()
        with self.assertRaisesRegex(ValueError, "unauthorized extra fields"):
            validate_2023_dispatch_action_preflight(changed)

    def test_cli_is_plan_only(self) -> None:
        script = (
            ROOT / "scripts/phase8a_annual_pattern_catalogue_2023_dispatch_action_preflight.py"
        ).read_text(encoding="utf-8")
        self.assertIn('sub.add_parser("plan")', script)
        for forbidden in ('sub.add_parser("dispatch")', 'sub.add_parser("execute")',
                          "gh workflow run ", "git push", "git commit"):
            self.assertNotIn(forbidden, script)


if __name__ == "__main__":
    unittest.main()
