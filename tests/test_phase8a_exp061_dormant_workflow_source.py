from __future__ import annotations

import copy
from pathlib import Path
import unittest

from fmp.discovery.run_contract import expected_job_names
from fmp.discovery.workflow_source import (
    DORMANT_WORKFLOW_TEMPLATE_PATH,
    FEATURE_EVIDENCE_ARTIFACT,
    FEATURE_RUN,
    HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED,
    OUTCOME_EVIDENCE_ARTIFACT,
    OUTCOME_RUN,
    RESERVED_ACTIVE_WORKFLOW_PATH,
    WORKFLOW_DISPATCH_AUTHORIZED,
    WORKFLOW_TEMPLATE_INSTALL_AUTHORIZED,
    require_historical_execution_authorized,
    source_artifacts_for_cell,
    validate_dormant_workflow_template,
    validate_source_snapshots,
    workflow_source_payload,
)


CODE_COMMIT = "a" * 40


def _artifact_row(expected: dict[str, object]) -> dict[str, object]:
    return {
        "id": expected["id"],
        "name": expected["name"],
        "digest": expected["digest"],
        "expired": False,
    }


def _feature_artifacts_payload() -> dict[str, object]:
    rows = [_artifact_row(FEATURE_EVIDENCE_ARTIFACT)]
    for symbol, timeframe in (
        ("EURUSD", "5m"),
        ("EURUSD", "15m"),
        ("EURUSD", "1h"),
        ("GBPUSD", "5m"),
        ("GBPUSD", "15m"),
        ("GBPUSD", "1h"),
        ("USDJPY", "5m"),
        ("USDJPY", "15m"),
        ("USDJPY", "1h"),
    ):
        raw = source_artifacts_for_cell(symbol, timeframe)
        rows.append(
            {
                "id": raw["feature_id"],
                "name": (
                    f"exp044-market-features-{symbol}-{timeframe}-"
                    f"{FEATURE_RUN['head_sha']}"
                ),
                "digest": raw["feature_digest"],
                "expired": False,
            }
        )
    return {"artifacts": rows}


def _outcome_artifacts_payload() -> dict[str, object]:
    rows = [_artifact_row(OUTCOME_EVIDENCE_ARTIFACT)]
    for symbol, timeframe in (
        ("EURUSD", "5m"),
        ("EURUSD", "15m"),
        ("EURUSD", "1h"),
        ("GBPUSD", "5m"),
        ("GBPUSD", "15m"),
        ("GBPUSD", "1h"),
        ("USDJPY", "5m"),
        ("USDJPY", "15m"),
        ("USDJPY", "1h"),
    ):
        raw = source_artifacts_for_cell(symbol, timeframe)
        rows.append(
            {
                "id": raw["outcome_id"],
                "name": (
                    f"exp044-market-outcomes-{symbol}-{timeframe}-"
                    f"{OUTCOME_RUN['head_sha']}-from-{FEATURE_RUN['head_sha']}"
                ),
                "digest": raw["outcome_digest"],
                "expired": False,
            }
        )
    return {"artifacts": rows}


class Exp061DormantWorkflowSourceTests(unittest.TestCase):
    def test_source_snapshots_are_exact_and_all_downstream_authority_is_false(self) -> None:
        report = validate_source_snapshots(
            feature_run=dict(FEATURE_RUN),
            feature_artifacts=_feature_artifacts_payload(),
            outcome_run=dict(OUTCOME_RUN),
            outcome_artifacts=_outcome_artifacts_payload(),
        )
        self.assertTrue(report["source_ready"])
        self.assertEqual(report["feature_run_id"], 35867307338)
        self.assertEqual(report["outcome_run_id"], 35876715434)
        self.assertEqual(report["verified_pair_timeframe_source_count"], 9)
        for field in (
            "historical_discovery_execution_authorized",
            "discovery_result_authorized",
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
            self.assertFalse(report[field], field)

    def test_source_snapshot_tampering_fails_closed(self) -> None:
        feature_artifacts = _feature_artifacts_payload()
        rows = feature_artifacts["artifacts"]
        assert isinstance(rows, list)
        rows[0]["digest"] = "sha256:" + ("0" * 64)
        with self.assertRaisesRegex(ValueError, "digest mismatch"):
            validate_source_snapshots(
                feature_run=dict(FEATURE_RUN),
                feature_artifacts=feature_artifacts,
                outcome_run=dict(OUTCOME_RUN),
                outcome_artifacts=_outcome_artifacts_payload(),
            )

        feature_run = copy.deepcopy(FEATURE_RUN)
        feature_run["run_attempt"] = 2
        with self.assertRaisesRegex(ValueError, "run_attempt mismatch"):
            validate_source_snapshots(
                feature_run=feature_run,
                feature_artifacts=_feature_artifacts_payload(),
                outcome_run=dict(OUTCOME_RUN),
                outcome_artifacts=_outcome_artifacts_payload(),
            )

    def test_workflow_source_payload_is_dormant_and_exact(self) -> None:
        payload = workflow_source_payload(code_commit=CODE_COMMIT)
        self.assertEqual(
            payload["dormant_template_path"],
            DORMANT_WORKFLOW_TEMPLATE_PATH,
        )
        self.assertEqual(
            payload["reserved_active_workflow_path"],
            RESERVED_ACTIVE_WORKFLOW_PATH,
        )
        self.assertEqual(
            tuple(payload["expected_job_names"]),
            expected_job_names(),
        )
        self.assertFalse(payload["template_install_authorized"])
        self.assertFalse(payload["workflow_dispatch_authorized"])
        self.assertFalse(payload["historical_discovery_execution_authorized"])
        for value in payload["authorizations"].values():
            self.assertFalse(value)

    def test_dormant_template_is_not_an_active_github_workflow(self) -> None:
        template = Path(DORMANT_WORKFLOW_TEMPLATE_PATH)
        active = Path(RESERVED_ACTIVE_WORKFLOW_PATH)
        self.assertTrue(template.is_file())
        self.assertFalse(active.exists())

        text = template.read_text(encoding="utf-8")
        validate_dormant_workflow_template(text)
        self.assertEqual(text.count("          - symbol:"), 18)
        self.assertEqual(text.count("            horizon: 60"), 9)
        self.assertEqual(text.count("            horizon: 240"), 9)
        self.assertEqual(
            text.count(
                "name: exp061-cell-${{ matrix.dataset.symbol }}-"
                "${{ matrix.dataset.timeframe }}-"
                "${{ matrix.dataset.horizon }}m"
            ),
            1,
        )
        self.assertNotIn("name: exp061-cell (", text)

    def test_cli_gates_historical_paths_before_any_loader_or_result_read(self) -> None:
        script = Path("scripts/phase8a_exp061.py").read_text(encoding="utf-8")
        cell_start = script.index("def _cmd_cell")
        aggregate_start = script.index("def _cmd_aggregate")

        cell_gate = script.index(
            "require_historical_execution_authorized",
            cell_start,
        )
        cell_loader = script.index(
            "load_verified_exp061_cell_from_indexes",
            cell_start,
        )
        self.assertLess(cell_gate, cell_loader)

        aggregate_gate = script.index(
            "require_historical_execution_authorized",
            aggregate_start,
        )
        aggregate_read = script.index(
            "_load_cell_evidence",
            aggregate_start,
        )
        self.assertLess(aggregate_gate, aggregate_read)

    def test_execution_gate_remains_closed(self) -> None:
        self.assertFalse(WORKFLOW_TEMPLATE_INSTALL_AUTHORIZED)
        self.assertFalse(WORKFLOW_DISPATCH_AUTHORIZED)
        self.assertFalse(HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED)
        with self.assertRaisesRegex(PermissionError, "execution remains locked"):
            require_historical_execution_authorized(
                code_commit=CODE_COMMIT,
            )


if __name__ == "__main__":
    unittest.main()
