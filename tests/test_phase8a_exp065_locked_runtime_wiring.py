from __future__ import annotations

from pathlib import Path
import unittest

from fmp.discovery.exp065_runtime_source import (
    ACTIVE_WORKFLOW_PATH,
    DORMANT_WORKFLOW_TEMPLATE_PATH,
    DEC463_MERGE_SHA,
    EXPECTED_ARTIFACT_COUNT,
    EXPECTED_CELL_COUNT,
    EXPECTED_JOB_COUNT,
    FEATURE_EVIDENCE_ARTIFACT,
    FEATURE_RUN,
    HISTORICAL_EXECUTION_AUTHORIZED,
    OUTCOME_EVIDENCE_ARTIFACT,
    OUTCOME_RUN,
    WORKFLOW_DISPATCH_AUTHORIZED,
    expected_artifact_names,
    expected_job_names,
    require_historical_execution_authorized,
    run_contract_payload,
    runtime_source_payload,
    source_artifacts_for_cell,
    validate_installed_runtime_paths,
    validate_runtime_dependencies,
    validate_source_snapshots,
    validate_workflow_text,
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
    for symbol in ("EURUSD", "GBPUSD", "USDJPY"):
        for timeframe in ("5m", "15m", "1h"):
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
    for symbol in ("EURUSD", "GBPUSD", "USDJPY"):
        for timeframe in ("5m", "15m", "1h"):
            raw = source_artifacts_for_cell(symbol, timeframe)
            rows.append(
                {
                    "id": raw["outcome_id"],
                    "name": (
                        f"exp044-market-outcomes-{symbol}-{timeframe}-"
                        f"{OUTCOME_RUN['head_sha']}-from-"
                        f"{FEATURE_RUN['head_sha']}"
                    ),
                    "digest": raw["outcome_digest"],
                    "expired": False,
                }
            )
    return {"artifacts": rows}


class Exp065LockedRuntimeWiringTests(unittest.TestCase):
    def test_run_contract_has_exact_18_cell_20_job_shape(self) -> None:
        payload = run_contract_payload(code_commit=CODE_COMMIT)

        self.assertEqual(EXPECTED_CELL_COUNT, 18)
        self.assertEqual(EXPECTED_JOB_COUNT, 20)
        self.assertEqual(EXPECTED_ARTIFACT_COUNT, 20)
        self.assertEqual(len(expected_job_names()), 20)
        self.assertEqual(len(expected_artifact_names(code_commit=CODE_COMMIT)), 20)
        self.assertEqual(payload["workflow"]["name"], "phase8a-exp065-pairwise-interaction")
        self.assertEqual(
            payload["workflow"]["path"],
            ".github/workflows/phase8a-exp065-pairwise-interaction.yml",
        )
        self.assertEqual(payload["success_shape"]["job_count"], 20)
        self.assertEqual(payload["success_shape"]["artifact_count"], 20)
        self.assertTrue(payload["authorizations"]["workflow_source_authorized"])
        self.assertTrue(payload["authorizations"]["workflow_installed"])
        self.assertFalse(payload["authorizations"]["workflow_dispatch_authorized"])
        self.assertFalse(payload["authorizations"]["historical_execution_authorized"])
        self.assertFalse(payload["authorizations"]["historical_result_authorized"])

    def test_runtime_binds_exact_dec463_merge(self) -> None:
        self.assertEqual(
            DEC463_MERGE_SHA,
            "c8c2c8d2dd5be5ff73655b09730d9eb18f9c3737",
        )

    def test_runtime_dependencies_and_installed_paths_are_exact(self) -> None:
        dependencies = validate_runtime_dependencies(repository_root=Path("."))
        installed = validate_installed_runtime_paths(repository_root=Path("."))

        self.assertEqual(
            dependencies["source_blobs"]["exp062_repaired_adapter"],
            "491ba8c92cb6e6e4c715bfb1ecb934b6949e1596",
        )
        self.assertEqual(
            dependencies["source_blobs"]["dec463_evidence_contract"],
            "ca68622ddfc9866f00569d558b2ab927be23686d",
        )
        self.assertEqual(
            dependencies["source_blobs"]["dec462_pairwise_interaction_miner"],
            "7dac382838d2b8fcc4df5d02c4949ad65c17635b",
        )
        self.assertEqual(
            dependencies["source_blobs"]["dec461_pairwise_interaction_protocol"],
            "b54267d790667659749a96123ad23a491ff50dfa",
        )
        self.assertEqual(
            installed["dormant_template_blob_sha"],
            "75d0e4df56d5c4ced5aff614e236cf0e1bb078e1",
        )
        self.assertEqual(
            installed["active_workflow_blob_sha"],
            installed["dormant_template_blob_sha"],
        )
        self.assertEqual(
            installed["cli_blob_sha"],
            "38e3eb9a5c2733655c845291d6bc3160e5fa0291",
        )

        self.assertEqual(
            Path(DORMANT_WORKFLOW_TEMPLATE_PATH).read_bytes(),
            Path(ACTIVE_WORKFLOW_PATH).read_bytes(),
        )

    def test_exact_exp044_source_snapshots_remain_the_only_runtime_inputs(self) -> None:
        report = validate_source_snapshots(
            feature_run=dict(FEATURE_RUN),
            feature_artifacts=_feature_artifacts_payload(),
            outcome_run=dict(OUTCOME_RUN),
            outcome_artifacts=_outcome_artifacts_payload(),
        )

        self.assertTrue(report["source_ready"])
        self.assertTrue(report["nonfinite_to_null_repair_required"])
        self.assertEqual(report["feature_run_id"], 35867307338)
        self.assertEqual(report["outcome_run_id"], 35876715434)
        self.assertEqual(report["verified_pair_timeframe_source_count"], 9)
        self.assertFalse(report["workflow_dispatch_authorized"])
        self.assertFalse(report["historical_execution_authorized"])
        self.assertFalse(report["historical_result_authorized"])
        self.assertFalse(report["reserved_robustness_access_authorized"])

    def test_cli_gates_cell_and_aggregate_before_historical_reads(self) -> None:
        script = Path("scripts/phase8a_exp065.py").read_text(encoding="utf-8")

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

    def test_active_workflow_gate_precedes_historical_artifact_download(self) -> None:
        text = Path(ACTIVE_WORKFLOW_PATH).read_text(encoding="utf-8")
        gate = text.index("Require separately authorized EXP-065 execution")
        download = text.index(
            "Download exact frozen feature/outcome/evidence artifacts"
        )
        self.assertLess(gate, download)
        self.assertEqual(text.count("          - symbol:"), 18)
        self.assertEqual(text.count("            horizon: 60"), 9)
        self.assertEqual(text.count("            horizon: 240"), 9)

    def test_workflow_validator_rejects_exp064_predecessor_cli(self) -> None:
        text = Path(ACTIVE_WORKFLOW_PATH).read_text(encoding="utf-8")
        tampered = text + "\n# python scripts/phase8a_exp064.py cell\n"

        with self.assertRaisesRegex(
            ValueError,
            "cannot invoke predecessor cell CLI",
        ):
            validate_workflow_text(tampered)

    def test_runtime_payload_exposes_wiring_but_no_execution_authority(self) -> None:
        payload = runtime_source_payload(code_commit=CODE_COMMIT)

        self.assertEqual(payload["experiment_id"], "EXP-20261001-065")
        self.assertEqual(
            payload["dormant_template_path"],
            "docs/superpowers/templates/phase8a-exp065-pairwise-interaction.yml.disabled",
        )
        self.assertEqual(
            payload["active_workflow_path"],
            ".github/workflows/phase8a-exp065-pairwise-interaction.yml",
        )
        self.assertTrue(payload["authorizations"]["workflow_source_authorized"])
        self.assertTrue(payload["authorizations"]["workflow_installed"])
        for field in (
            "workflow_dispatch_authorized",
            "historical_execution_authorized",
            "historical_result_authorized",
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
            self.assertFalse(payload["authorizations"][field], field)

    def test_execution_gate_is_hard_closed(self) -> None:
        self.assertFalse(WORKFLOW_DISPATCH_AUTHORIZED)
        self.assertFalse(HISTORICAL_EXECUTION_AUTHORIZED)
        with self.assertRaisesRegex(
            PermissionError,
            "historical EXP-065 execution remains locked",
        ):
            require_historical_execution_authorized(code_commit=CODE_COMMIT)


if __name__ == "__main__":
    unittest.main()
