from __future__ import annotations

from pathlib import Path
import unittest

from fmp.portfolio.challenger_discovery import build_exp015_challengers
from fmp.portfolio.challenger_discovery_stage_a import (
    exp015_catalog_identity_sha256,
    exp015_strategy_source_sha256,
)
from fmp.portfolio.exp015_stage_a_terminal_review import (
    EXPECTED_CELLS,
    validate_exp015_stage_a_terminal_review,
)


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "phase8a-exp015-stage-a.yml"
HEAD = "a" * 40


def _jobs(*, conclusion: str = "success") -> dict[str, object]:
    jobs: list[dict[str, object]] = [
        {
            "id": 1,
            "name": "catalog-freeze",
            "status": "completed",
            "conclusion": conclusion,
        }
    ]
    next_id = 2
    for symbol, timeframe in EXPECTED_CELLS:
        jobs.append(
            {
                "id": next_id,
                "name": f"stage-a-cell ({symbol}, {timeframe})",
                "status": "completed",
                "conclusion": conclusion,
            }
        )
        next_id += 1
    jobs.append(
        {
            "id": next_id,
            "name": "stage-a-authorize",
            "status": "completed",
            "conclusion": conclusion,
        }
    )
    return {"jobs": jobs}


def _artifacts() -> dict[str, object]:
    names = [
        f"phase8a-exp015-catalog-{HEAD}",
        *[
            f"phase8a-exp015-stage-a-{symbol}-{timeframe}-{HEAD}"
            for symbol, timeframe in EXPECTED_CELLS
        ],
        f"phase8a-exp015-stage-a-authorization-{HEAD}",
    ]
    return {
        "total_count": len(names),
        "artifacts": [
            {"name": name, "expired": False}
            for name in names
        ],
    }


def _authorization() -> dict[str, object]:
    catalog = build_exp015_challengers(code_commit=HEAD)
    by_cell: dict[tuple[str, str], list[object]] = {}
    for record in catalog:
        key = (record.strategy.symbol, record.strategy.timeframe)
        by_cell.setdefault(key, []).append(record)

    cells = []
    for symbol, timeframe in EXPECTED_CELLS:
        records = sorted(
            by_cell[(symbol, timeframe)],
            key=lambda item: item.strategy.fingerprint,
        )
        fingerprints = [item.strategy.fingerprint for item in records]
        families = sorted({item.strategy.family for item in records})
        cells.append(
            {
                "symbol": symbol,
                "timeframe": timeframe,
                "strategy_fingerprints": fingerprints,
                "survivor_fingerprints": [],
                "family_rankings": {
                    family: {
                        "passing_fingerprints": [],
                        "selected_fingerprints": [],
                    }
                    for family in families
                },
                "strategy_gates": {
                    item.strategy.fingerprint: {
                        "family": item.strategy.family,
                        "parameters_json": item.strategy.parameters_json,
                        "mandatory_gate_pass": False,
                        "annualized_return_02": None,
                        "annualized_return_05": None,
                    }
                    for item in records
                },
            }
        )

    return {
        "protocol": "fmp-phase8a-exp015-stage-a-authorization-v1",
        "experiment_id": "EXP-20260922-015",
        "evidence_label": "RETROSPECTIVE_ALREADY_SEEN",
        "untouched_oos": False,
        "promotion_authorized": False,
        "historical_status_mutation_authorized": False,
        "runner_code_commit": HEAD,
        "catalog_identity_sha256": exp015_catalog_identity_sha256(
            code_commit=HEAD
        ),
        "strategy_source_sha256": exp015_strategy_source_sha256(),
        "cell_count": 9,
        "ranking_cell_count": 54,
        "strategy_identity_count": 567,
        "maximum_stage_a_survivors": 108,
        "survivor_count": 0,
        "survivor_fingerprints": [],
        "stage_b_source_open_authorized": False,
        "cells": cells,
    }


def _run(*, conclusion: str = "success", attempt: int = 1) -> dict[str, object]:
    return {
        "id": 12345,
        "name": "phase8a-exp015-stage-a",
        "path": ".github/workflows/phase8a-exp015-stage-a.yml",
        "event": "workflow_dispatch",
        "head_branch": "main",
        "head_sha": HEAD,
        "run_attempt": attempt,
        "status": "completed",
        "conclusion": conclusion,
    }


class Exp015StageAFirstRunGovernanceTests(unittest.TestCase):
    def test_guard_preserves_first_authoritative_manual_main_attempt_only(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "Reject any prior authoritative manual-main EXP-015 Stage A attempt",
            text,
        )
        self.assertIn('current["name"] == "phase8a-exp015-stage-a"', text)
        self.assertIn(
            'current["path"] == ".github/workflows/phase8a-exp015-stage-a.yml"',
            text,
        )
        self.assertIn('current["event"] == "workflow_dispatch"', text)
        self.assertIn('current["head_branch"] == "main"', text)
        self.assertIn('current["run_attempt"] == 1', text)
        self.assertIn('main["commit"]["sha"] == run_sha', text)
        self.assertIn("branch=main&event=workflow_dispatch&per_page=100", text)
        self.assertNotIn("gh workflow run", text)
        self.assertNotIn("gh run rerun", text)

    def test_success_review_revalidates_exact_stage_a_authorization(self) -> None:
        report = validate_exp015_stage_a_terminal_review(
            run=_run(),
            jobs_payload=_jobs(),
            artifacts_payload=_artifacts(),
            authorization_evidence=_authorization(),
        )
        self.assertTrue(report["exp015_stage_a_terminal_reviewed"])
        self.assertTrue(report["exp015_stage_a_authorization_evidence_verified"])
        self.assertEqual(report["verified_cell_count"], 9)
        self.assertEqual(report["verified_ranking_cell_count"], 54)
        self.assertEqual(report["verified_strategy_identity_count"], 567)
        self.assertEqual(report["verified_maximum_stage_a_survivors"], 108)
        self.assertEqual(report["verified_survivor_count"], 0)
        self.assertFalse(report["verified_stage_b_source_open"])
        self.assertFalse(report["stage_a_retry_authorized"])
        self.assertFalse(report["stage_a_replacement_authorized"])
        self.assertFalse(report["stage_b_execution_authorized"])
        self.assertFalse(report["stage_c_execution_authorized"])
        self.assertFalse(report["portfolio_selection_authorized"])
        self.assertFalse(report["phase8a_acceptance_authorized"])
        self.assertFalse(report["phase8b_authorized"])
        self.assertFalse(report["demo_order_authorized"])
        self.assertFalse(report["broker_mutation_authorized"])
        self.assertFalse(report["live_order_authorized"])
        self.assertFalse(report["real_money_authorized"])
        self.assertFalse(report["trading_authorized"])

    def test_rerun_attempt_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "forbids rerun attempts"):
            validate_exp015_stage_a_terminal_review(
                run=_run(attempt=2),
                jobs_payload=_jobs(),
                artifacts_payload=_artifacts(),
                authorization_evidence=_authorization(),
            )

    def test_non_success_cannot_claim_final_authorization(self) -> None:
        failed_artifacts = _artifacts()
        failed_artifacts["artifacts"] = [
            item
            for item in failed_artifacts["artifacts"]
            if "authorization" not in str(item["name"])
        ]
        failed_artifacts["total_count"] = len(failed_artifacts["artifacts"])
        with self.assertRaisesRegex(
            ValueError,
            "cannot claim authorization evidence",
        ):
            validate_exp015_stage_a_terminal_review(
                run=_run(conclusion="failure"),
                jobs_payload=_jobs(conclusion="failure"),
                artifacts_payload=failed_artifacts,
                authorization_evidence=_authorization(),
            )

    def test_non_success_preserves_only_expected_partial_artifacts(self) -> None:
        failed_jobs = _jobs(conclusion="failure")
        failed_artifacts = {
            "total_count": 2,
            "artifacts": [
                {"name": f"phase8a-exp015-catalog-{HEAD}", "expired": False},
                {
                    "name": f"phase8a-exp015-stage-a-EURUSD-5m-{HEAD}",
                    "expired": False,
                },
            ],
        }
        report = validate_exp015_stage_a_terminal_review(
            run=_run(conclusion="failure"),
            jobs_payload=failed_jobs,
            artifacts_payload=failed_artifacts,
            authorization_evidence=None,
        )
        self.assertEqual(
            report["stage"],
            "EXP015_STAGE_A_RUN_FAILURE_REVIEW_REQUIRED",
        )
        self.assertEqual(report["persisted_cell_artifact_count"], 1)
        self.assertTrue(report["catalog_artifact_present"])
        self.assertFalse(report["authorization_artifact_present"])
        self.assertFalse(report["stage_a_retry_authorized"])
        self.assertFalse(report["stage_a_replacement_authorized"])


if __name__ == "__main__":
    unittest.main()
