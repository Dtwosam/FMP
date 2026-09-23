from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from fmp.market_learning.evidence import EXPECTED_CELLS
from fmp.market_learning.execution_status import (
    FEATURE_WORKFLOW_NAME,
    FEATURE_WORKFLOW_PATH,
    OUTCOME_WORKFLOW_NAME,
    OUTCOME_WORKFLOW_PATH,
    STATUS_VERSION,
    build_execution_status,
    load_workflow_run,
)
from fmp.market_learning.readiness import (
    build_training_readiness,
    load_training_readiness,
    write_training_readiness,
)


FEATURE_SHA = "a" * 40
OUTCOME_SHA = "b" * 40


def _run(
    *,
    run_id: int,
    name: str,
    path: str,
    head_sha: str,
    status: str = "completed",
    conclusion: str | None = "success",
) -> dict[str, object]:
    return {
        "id": run_id,
        "name": name,
        "path": path,
        "event": "workflow_dispatch",
        "head_branch": "main",
        "head_sha": head_sha,
        "status": status,
        "conclusion": conclusion,
    }


def _feature_evidence() -> dict[str, object]:
    cells = []
    for index, (symbol, timeframe) in enumerate(EXPECTED_CELLS, start=1):
        cells.append(
            {
                "symbol": symbol,
                "timeframe": timeframe,
                "manifest_sha256": f"{index:064x}",
                "processed_manifest_sha256": f"{100 + index:064x}",
                "row_count": 1000 + index,
            }
        )
    return {
        "experiment_id": "EXP-20260923-044",
        "feature_set_version": "fmp-market-feature-v1",
        "evidence_label": "RETROSPECTIVE_ALREADY_SEEN",
        "code_commit": FEATURE_SHA,
        "evidence_fingerprint": "c" * 64,
        "feature_evidence_complete": True,
        "cells": cells,
    }


def _outcome_evidence(feature: dict[str, object]) -> dict[str, object]:
    cells = []
    for index, source in enumerate(feature["cells"], start=1):
        cells.append(
            {
                "symbol": source["symbol"],
                "timeframe": source["timeframe"],
                "manifest_sha256": f"{200 + index:064x}",
                "feature_manifest_sha256": source["manifest_sha256"],
                "processed_manifest_sha256": source["processed_manifest_sha256"],
                "source_feature_rows": source["row_count"],
                "labeled_rows": 2 * int(source["row_count"]) - 1,
            }
        )
    return {
        "experiment_id": "EXP-20260923-044",
        "outcome_set_version": "fmp-market-outcome-grid-v1",
        "feature_set_version": "fmp-market-feature-v1",
        "evidence_label": "RETROSPECTIVE_ALREADY_SEEN",
        "code_commit": OUTCOME_SHA,
        "feature_evidence_fingerprint": feature["evidence_fingerprint"],
        "evidence_fingerprint": "d" * 64,
        "outcome_evidence_complete": True,
        "cells": cells,
    }


class MarketLearningExecutionStatusTests(unittest.TestCase):
    def test_no_run_requires_feature_dispatch_and_authorizes_nothing(self) -> None:
        status = build_execution_status()
        self.assertEqual(status["status_version"], STATUS_VERSION)
        self.assertEqual(status["stage"], "FEATURE_DISPATCH_REQUIRED")
        self.assertFalse(status["data_preparation_complete"])
        self.assertFalse(status["model_protocol_source_open_authorized"])
        self.assertFalse(status["model_fit_authorized"])
        self.assertFalse(status["promotion_authorized"])

    def test_feature_success_and_evidence_require_outcome_dispatch(self) -> None:
        feature = _feature_evidence()
        run = _run(
            run_id=111,
            name=FEATURE_WORKFLOW_NAME,
            path=FEATURE_WORKFLOW_PATH,
            head_sha=FEATURE_SHA,
        )
        status = build_execution_status(
            feature_run=run,
            feature_evidence=feature,
        )
        self.assertEqual(status["stage"], "OUTCOME_DISPATCH_REQUIRED")
        self.assertIn("feature_run_id=111", status["next_action"])
        self.assertTrue(status["feature_evidence_verified"])
        self.assertFalse(status["model_protocol_source_open_authorized"])

    def test_incomplete_feature_run_cannot_have_downstream_evidence(self) -> None:
        run = _run(
            run_id=111,
            name=FEATURE_WORKFLOW_NAME,
            path=FEATURE_WORKFLOW_PATH,
            head_sha=FEATURE_SHA,
            status="in_progress",
            conclusion=None,
        )
        with self.assertRaisesRegex(ValueError, "cannot precede feature success"):
            build_execution_status(
                feature_run=run,
                feature_evidence=_feature_evidence(),
            )

    def test_outcome_success_without_readiness_reports_readiness_required(self) -> None:
        feature = _feature_evidence()
        outcome = _outcome_evidence(feature)
        status = build_execution_status(
            feature_run=_run(
                run_id=111,
                name=FEATURE_WORKFLOW_NAME,
                path=FEATURE_WORKFLOW_PATH,
                head_sha=FEATURE_SHA,
            ),
            feature_evidence=feature,
            outcome_run=_run(
                run_id=222,
                name=OUTCOME_WORKFLOW_NAME,
                path=OUTCOME_WORKFLOW_PATH,
                head_sha=OUTCOME_SHA,
            ),
            outcome_evidence=outcome,
        )
        self.assertEqual(status["stage"], "READINESS_REQUIRED")
        self.assertTrue(status["outcome_evidence_verified"])
        self.assertFalse(status["data_preparation_complete"])

    def test_valid_readiness_opens_protocol_source_only(self) -> None:
        feature = _feature_evidence()
        outcome = _outcome_evidence(feature)
        readiness = build_training_readiness(
            feature_evidence=feature,
            outcome_evidence=outcome,
        )
        status = build_execution_status(
            feature_run=_run(
                run_id=111,
                name=FEATURE_WORKFLOW_NAME,
                path=FEATURE_WORKFLOW_PATH,
                head_sha=FEATURE_SHA,
            ),
            feature_evidence=feature,
            outcome_run=_run(
                run_id=222,
                name=OUTCOME_WORKFLOW_NAME,
                path=OUTCOME_WORKFLOW_PATH,
                head_sha=OUTCOME_SHA,
            ),
            outcome_evidence=outcome,
            readiness=readiness,
        )
        self.assertEqual(status["stage"], "MODEL_PROTOCOL_SOURCE_OPEN")
        self.assertTrue(status["data_preparation_complete"])
        self.assertTrue(status["model_protocol_source_open_authorized"])
        self.assertFalse(status["model_protocol_result_authorized"])
        self.assertFalse(status["model_fit_authorized"])
        self.assertFalse(status["shadow_authorized"])
        self.assertFalse(status["demo_order_authorized"])
        self.assertFalse(status["broker_mutation_authorized"])
        self.assertFalse(status["live_order_authorized"])
        self.assertFalse(status["real_money_authorized"])

    def test_workflow_run_loader_rejects_non_main_or_non_manual_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "run.json"
            payload = _run(
                run_id=111,
                name=FEATURE_WORKFLOW_NAME,
                path=FEATURE_WORKFLOW_PATH,
                head_sha=FEATURE_SHA,
            )
            payload["event"] = "push"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "workflow_dispatch"):
                load_workflow_run(
                    path,
                    expected_name=FEATURE_WORKFLOW_NAME,
                    expected_path=FEATURE_WORKFLOW_PATH,
                )

    def test_persisted_readiness_tamper_fails_closed(self) -> None:
        feature = _feature_evidence()
        outcome = _outcome_evidence(feature)
        readiness = build_training_readiness(
            feature_evidence=feature,
            outcome_evidence=outcome,
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "readiness.json"
            write_training_readiness(readiness=readiness, path=path)
            loaded = load_training_readiness(path)
            self.assertEqual(
                loaded["readiness_fingerprint"],
                readiness["readiness_fingerprint"],
            )
            tampered = json.loads(path.read_text(encoding="utf-8"))
            tampered["model_fit_authorized"] = True
            path.write_text(json.dumps(tampered, sort_keys=True, indent=2) + "\n")
            with self.assertRaisesRegex(ValueError, "fingerprint mismatch"):
                load_training_readiness(path)


if __name__ == "__main__":
    unittest.main()
