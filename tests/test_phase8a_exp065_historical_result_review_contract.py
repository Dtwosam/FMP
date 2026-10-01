from __future__ import annotations

import unittest
from unittest.mock import patch

from fmp.discovery.exp065_historical_result_review_contract import (
    EXPECTED_ARTIFACT_COUNT,
    EXPECTED_JOB_COUNT,
    RUN_ATTEMPT,
    RUN_HEAD_SHA,
    RUN_ID,
    RUN_NUMBER,
    TOTAL_NOMINAL_HYPOTHESES,
    review_authority_boundary,
    review_success_evidence,
    validate_success_run_shape,
    validate_terminal_run_identity,
)
from fmp.discovery.exp065_pairwise_interaction_protocol import (
    OUTPUT_KIND,
)


def _run(*, conclusion: str = "success") -> dict[str, object]:
    return {
        "id": RUN_ID,
        "name": "phase8a-exp065-pairwise-interaction",
        "path": ".github/workflows/phase8a-exp065-pairwise-interaction.yml",
        "event": "workflow_dispatch",
        "head_branch": "main",
        "head_sha": RUN_HEAD_SHA,
        "run_number": RUN_NUMBER,
        "run_attempt": RUN_ATTEMPT,
        "status": "completed",
        "conclusion": conclusion,
    }


def _jobs() -> dict[str, object]:
    names = [
        "exp065-preflight",
        *[
            f"exp065-cell-{symbol}-{timeframe}-{horizon}m"
            for symbol in ("EURUSD", "GBPUSD", "USDJPY")
            for timeframe in ("5m", "15m", "1h")
            for horizon in (60, 240)
        ],
        "exp065-aggregate",
    ]
    return {
        "jobs": [
            {
                "name": name,
                "status": "completed",
                "conclusion": "success",
            }
            for name in names
        ]
    }


def _artifacts() -> dict[str, object]:
    names = [
        f"phase8a-exp065-preflight-{RUN_HEAD_SHA}",
        *[
            (
                f"phase8a-exp065-cell-{symbol}-{timeframe}-"
                f"{horizon}m-{RUN_HEAD_SHA}"
            )
            for symbol in ("EURUSD", "GBPUSD", "USDJPY")
            for timeframe in ("5m", "15m", "1h")
            for horizon in (60, 240)
        ],
        f"phase8a-exp065-aggregate-{RUN_HEAD_SHA}",
    ]
    return {
        "artifacts": [
            {
                "id": index + 1,
                "name": name,
                "digest": "sha256:" + f"{index + 1:064x}",
                "expired": False,
            }
            for index, name in enumerate(names)
        ]
    }


def _cell(
    symbol: str,
    timeframe: str,
    horizon: int,
    *,
    qualifying: int = 0,
    deduplicated: int = 0,
    frozen: bool = False,
) -> dict[str, object]:
    shortlist = (
        [{"fingerprint": f"{symbol}-{timeframe}-{horizon}".encode().hex().ljust(64, "0")[:64]}]
        if frozen
        else []
    )
    frozen_fingerprints = (
        [shortlist[0]["fingerprint"]]
        if frozen
        else []
    )
    return {
        "code_commit": RUN_HEAD_SHA,
        "evidence_fingerprint": (
            f"{symbol}-{timeframe}-{horizon}".encode().hex().ljust(64, "0")[:64]
        ),
        "cell": {
            "symbol": symbol,
            "timeframe": timeframe,
            "horizon_minutes": horizon,
        },
        "pairwise_interaction": {
            "hypothesis_count": 760,
            "evaluable_hypothesis_count": 700,
            "qualifying_hypothesis_count": qualifying,
            "deduplicated_hypothesis_count": deduplicated,
            "shortlist": shortlist,
            "frozen_hypothesis_fingerprints": frozen_fingerprints,
        },
    }


def _aggregate(cells: list[dict[str, object]]) -> dict[str, object]:
    rows: list[dict[str, object]] = []
    shortlist_total = 0
    frozen_total = 0
    for cell in cells:
        identity = cell["cell"]
        section = cell["pairwise_interaction"]
        shortlist = section["shortlist"]
        frozen = section["frozen_hypothesis_fingerprints"]
        shortlist_fingerprints = [item["fingerprint"] for item in shortlist]
        shortlist_total += len(shortlist)
        frozen_total += len(frozen)
        rows.append(
            {
                "symbol": identity["symbol"],
                "timeframe": identity["timeframe"],
                "horizon_minutes": identity["horizon_minutes"],
                "cell_evidence_fingerprint": cell["evidence_fingerprint"],
                "hypothesis_count": section["hypothesis_count"],
                "evaluable_hypothesis_count": section[
                    "evaluable_hypothesis_count"
                ],
                "qualifying_hypothesis_count": section[
                    "qualifying_hypothesis_count"
                ],
                "deduplicated_hypothesis_count": section[
                    "deduplicated_hypothesis_count"
                ],
                "pairwise_interaction_shortlist_count": len(shortlist),
                "pairwise_interaction_frozen_count": len(frozen),
                "pairwise_interaction_shortlist_fingerprints": (
                    shortlist_fingerprints
                ),
                "pairwise_interaction_frozen_fingerprints": list(frozen),
                "output_kind": OUTPUT_KIND,
            }
        )
    return {
        "code_commit": RUN_HEAD_SHA,
        "evidence_label": "RETROSPECTIVE_ALREADY_SEEN",
        "untouched_oos": False,
        "reserved_robustness_opened": False,
        "output_kind": OUTPUT_KIND,
        "evidence_fingerprint": "a" * 64,
        "protocol_fingerprint": "b" * 64,
        "feature_evidence_fingerprint": "c" * 64,
        "outcome_evidence_fingerprint": "d" * 64,
        "pairwise_interaction_shortlist_count": shortlist_total,
        "pairwise_interaction_frozen_count": frozen_total,
        "cells": rows,
    }


def _cells() -> list[dict[str, object]]:
    return [
        _cell(symbol, timeframe, horizon)
        for symbol in ("EURUSD", "GBPUSD", "USDJPY")
        for timeframe in ("5m", "15m", "1h")
        for horizon in (60, 240)
    ]


class Exp065HistoricalResultReviewContractTests(unittest.TestCase):
    def test_exact_terminal_run_identity_is_bound_to_consumed_slot(self) -> None:
        report = validate_terminal_run_identity(_run())

        self.assertTrue(report["run_identity_verified"])
        self.assertEqual(report["run_id"], 36905224184)
        self.assertEqual(
            report["run_head_sha"],
            "5faa733572576aa5a1c56176ac27c415eaaf6416",
        )
        self.assertEqual(report["run_number"], 1)
        self.assertEqual(report["run_attempt"], 1)

    def test_terminal_identity_rejects_head_or_attempt_drift(self) -> None:
        bad_head = _run()
        bad_head["head_sha"] = "a" * 40
        with self.assertRaisesRegex(ValueError, "head_sha mismatch"):
            validate_terminal_run_identity(bad_head)

        bad_attempt = _run()
        bad_attempt["run_attempt"] = 2
        with self.assertRaisesRegex(ValueError, "run_attempt mismatch"):
            validate_terminal_run_identity(bad_attempt)

    def test_success_shape_requires_exact_20_jobs_and_artifacts(self) -> None:
        report = validate_success_run_shape(_run(), _jobs(), _artifacts())

        self.assertTrue(report["success_shape_verified"])
        self.assertEqual(report["job_count"], EXPECTED_JOB_COUNT)
        self.assertEqual(report["artifact_count"], EXPECTED_ARTIFACT_COUNT)
        self.assertEqual(
            report["aggregate_artifact_name"],
            f"phase8a-exp065-aggregate-{RUN_HEAD_SHA}",
        )

    def test_success_shape_cannot_reinterpret_terminal_failure(self) -> None:
        with self.assertRaisesRegex(ValueError, "requires run success"):
            validate_success_run_shape(
                _run(conclusion="failure"),
                _jobs(),
                _artifacts(),
            )

    def test_zero_qualifier_evidence_summary_is_deterministic(self) -> None:
        cells = _cells()
        aggregate = _aggregate(cells)
        with (
            patch(
                "fmp.discovery.exp065_historical_result_review_contract."
                "validate_dec463_aggregate_evidence",
                side_effect=lambda value: value,
            ),
            patch(
                "fmp.discovery.exp065_historical_result_review_contract."
                "validate_dec463_cell_evidence",
                side_effect=lambda value: value,
            ),
        ):
            report = review_success_evidence(
                aggregate=aggregate,
                cell_evidence=cells,
            )

        self.assertTrue(report["evidence_verified"])
        self.assertEqual(
            report["result_state"],
            "ZERO_PAIRWISE_INTERACTION_QUALIFIERS",
        )
        self.assertEqual(report["verified_cell_count"], 18)
        self.assertEqual(report["total_hypotheses"], 13680)
        self.assertEqual(report["total_evaluable_hypotheses"], 12600)
        self.assertEqual(report["total_qualifying_hypotheses"], 0)
        self.assertEqual(report["pairwise_interaction_frozen_count"], 0)

    def test_frozen_carry_forward_is_retrospective_only_summary(self) -> None:
        cells = _cells()
        cells[0] = _cell(
            "EURUSD",
            "5m",
            60,
            qualifying=2,
            deduplicated=1,
            frozen=True,
        )
        aggregate = _aggregate(cells)
        with (
            patch(
                "fmp.discovery.exp065_historical_result_review_contract."
                "validate_dec463_aggregate_evidence",
                side_effect=lambda value: value,
            ),
            patch(
                "fmp.discovery.exp065_historical_result_review_contract."
                "validate_dec463_cell_evidence",
                side_effect=lambda value: value,
            ),
        ):
            report = review_success_evidence(
                aggregate=aggregate,
                cell_evidence=cells,
            )

        self.assertEqual(
            report["result_state"],
            "PAIRWISE_INTERACTION_FROZEN_CARRY_FORWARD_PRESENT",
        )
        self.assertEqual(report["total_qualifying_hypotheses"], 2)
        self.assertEqual(report["total_deduplicated_hypotheses"], 1)
        self.assertEqual(report["pairwise_interaction_shortlist_count"], 1)
        self.assertEqual(report["pairwise_interaction_frozen_count"], 1)
        self.assertEqual(report["evidence_label"], "RETROSPECTIVE_ALREADY_SEEN")
        self.assertFalse(report["untouched_oos"])
        self.assertFalse(report["reserved_robustness_opened"])

    def test_review_contract_keeps_every_downstream_authority_closed(self) -> None:
        payload = review_authority_boundary()

        self.assertEqual(
            payload["stage"],
            "EXP065_HISTORICAL_RESULT_REVIEW_CONTRACT_PREDECLARED",
        )
        self.assertEqual(payload["run_id"], RUN_ID)
        self.assertEqual(payload["run_number"], 1)
        self.assertEqual(payload["run_attempt"], 1)
        self.assertEqual(
            payload["total_nominal_hypotheses"],
            TOTAL_NOMINAL_HYPOTHESES,
        )
        for field in (
            "rerun_authorized",
            "retry_authorized",
            "replacement_run_authorized",
            "reserved_robustness_access_authorized",
            "candidate_compilation_authorized",
            "promotion_authorized",
            "phase8b_authorized",
            "demo_order_authorized",
            "broker_mutation_authorized",
            "live_order_authorized",
            "real_money_authorized",
            "trading_authorized",
        ):
            self.assertFalse(payload[field], field)


if __name__ == "__main__":
    unittest.main()
