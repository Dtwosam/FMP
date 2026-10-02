from __future__ import annotations

import copy
from pathlib import Path
import unittest

from fmp.discovery.annual_pattern_catalogue_evidence import (
    DIRECTIONAL_RECORDS_PER_ANNUAL_CELL,
    ValidatedAnnualCellSummary,
)
from fmp.discovery.annual_pattern_catalogue_segment_evidence import (
    compile_annual_segment_freeze,
)
from fmp.discovery.annual_pattern_catalogue_workflow_source import (
    CLI_PATH,
    DORMANT_WORKFLOW_TEMPLATE_PATH,
    FEATURE_EVIDENCE_ARTIFACT,
    FEATURE_RUN,
    HISTORICAL_ARTIFACT_READ_AUTHORIZED,
    HISTORICAL_CATALOGUE_EXECUTION_AUTHORIZED,
    HISTORICAL_RESULT_PRODUCTION_AUTHORIZED,
    OUTCOME_EVIDENCE_ARTIFACT,
    OUTCOME_RUN,
    RESERVED_ACTIVE_WORKFLOW_PATH,
    WORKFLOW_DISPATCH_AUTHORIZED,
    WORKFLOW_INSTALLED,
    WORKFLOW_TEMPLATE_INSTALL_AUTHORIZED,
    prior_segment_label,
    source_artifacts_for_cell,
    validate_annual_segment_label,
    validate_prior_segment_freeze,
    validate_dormant_source_files,
    validate_dormant_workflow_template,
    validate_source_snapshots,
    workflow_source_payload,
)


CODE_COMMIT = "a" * 40


PRIOR_RUN_ID = 424242


def _summary(
    segment: str,
    symbol: str,
    timeframe: str,
    horizon: int,
    *,
    code_commit: str = CODE_COMMIT,
) -> ValidatedAnnualCellSummary:
    return ValidatedAnnualCellSummary(
        annual_segment_label=segment,
        symbol=symbol,
        timeframe=timeframe,
        horizon_minutes=horizon,
        code_commit=code_commit,
        evidence_fingerprint="b" * 64,
        catalogue_payload_sha256="c" * 64,
        processed_manifest_sha256="d" * 64,
        feature_manifest_sha256="e" * 64,
        outcome_manifest_sha256="f" * 64,
        feature_evidence_fingerprint="1" * 64,
        outcome_evidence_fingerprint="2" * 64,
        directional_record_count=DIRECTIONAL_RECORDS_PER_ANNUAL_CELL,
        evaluable_record_count=1,
        zero_support_record_count=1,
        total_support=1,
    )


def _annual_freeze(
    segment: str,
    *,
    code_commit: str = CODE_COMMIT,
) -> dict[str, object]:
    summaries = [
        _summary(
            segment,
            symbol,
            timeframe,
            horizon,
            code_commit=code_commit,
        )
        for symbol in ("EURUSD", "GBPUSD", "USDJPY")
        for timeframe in ("5m", "15m", "1h")
        for horizon in (60, 240)
    ]
    return compile_annual_segment_freeze(
        summaries,
        annual_segment_label=segment,
        code_commit=code_commit,
    )


def _prior_run(
    *,
    run_id: int = PRIOR_RUN_ID,
    head_sha: str = CODE_COMMIT,
) -> dict[str, object]:
    return {
        "id": run_id,
        "name": "phase8a-annual-pattern-catalogue",
        "path": RESERVED_ACTIVE_WORKFLOW_PATH,
        "event": "workflow_dispatch",
        "head_branch": "main",
        "head_sha": head_sha,
        "run_attempt": 1,
        "status": "completed",
        "conclusion": "success",
    }


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
                        f"{OUTCOME_RUN['head_sha']}-from-{FEATURE_RUN['head_sha']}"
                    ),
                    "digest": raw["outcome_digest"],
                    "expired": False,
                }
            )
    return {"artifacts": rows}


class AnnualPatternCatalogueDormantWorkflowSourceTests(unittest.TestCase):
    def test_exact_exp044_sources_are_reused_with_no_new_data_authority(self) -> None:
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
        self.assertFalse(report["new_data_acquisition_authorized"])
        self.assertFalse(report["workflow_template_install_authorized"])
        self.assertFalse(report["workflow_installed"])
        self.assertFalse(report["workflow_dispatch_authorized"])
        self.assertFalse(report["historical_artifact_read_authorized"])
        self.assertFalse(report["historical_catalogue_execution_authorized"])
        self.assertFalse(report["historical_result_production_authorized"])

    def test_source_snapshot_tampering_fails_closed(self) -> None:
        artifacts = _feature_artifacts_payload()
        rows = artifacts["artifacts"]
        assert isinstance(rows, list)
        rows[0]["digest"] = "sha256:" + ("0" * 64)

        with self.assertRaisesRegex(ValueError, "digest mismatch"):
            validate_source_snapshots(
                feature_run=dict(FEATURE_RUN),
                feature_artifacts=artifacts,
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

    def test_dormant_template_and_cli_exist_but_active_workflow_does_not(self) -> None:
        report = validate_dormant_source_files(repository_root=Path("."))

        self.assertTrue(Path(DORMANT_WORKFLOW_TEMPLATE_PATH).is_file())
        self.assertTrue(Path(CLI_PATH).is_file())
        self.assertFalse(Path(RESERVED_ACTIVE_WORKFLOW_PATH).exists())
        self.assertFalse(report["active_workflow_present"])
        self.assertFalse(report["workflow_template_install_authorized"])
        self.assertFalse(report["workflow_installed"])
        self.assertFalse(report["workflow_dispatch_authorized"])

    def test_template_is_exact_one_segment_18_cell_annual_freeze_shape(self) -> None:
        text = Path(DORMANT_WORKFLOW_TEMPLATE_PATH).read_text(encoding="utf-8")
        validate_dormant_workflow_template(text)

        self.assertEqual(text.count("          - symbol:"), 18)
        self.assertEqual(text.count("            horizon: 60"), 9)
        self.assertEqual(text.count("            horizon: 240"), 9)
        self.assertIn(
            "name: annual-cell-${{ inputs.annual_segment_label }}-"
            "${{ matrix.dataset.symbol }}-${{ matrix.dataset.timeframe }}-"
            "${{ matrix.dataset.horizon }}m",
            text,
        )
        self.assertIn(
            "python scripts/phase8a_annual_pattern_catalogue.py freeze",
            text,
        )
        self.assertIn(
            "pattern: phase8a-annual-catalogue-cell-${{ inputs.annual_segment_label }}-*-*-*m-${{ github.sha }}",
            text,
        )
        self.assertNotIn("phase8a-exp065-cell-", text)
        self.assertNotIn("aggregate-evidence.json", text)
        self.assertNotIn(RESERVED_ACTIVE_WORKFLOW_PATH, text)

    def test_template_rejects_missing_segment_option(self) -> None:
        text = Path(DORMANT_WORKFLOW_TEMPLATE_PATH).read_text(encoding="utf-8")
        tampered = text.replace('          - "2024"\n', "")

        with self.assertRaisesRegex(ValueError, "annual segment options drift"):
            validate_dormant_workflow_template(tampered)

    def test_cli_gates_freeze_before_result_artifact_reads(self) -> None:
        script = Path(CLI_PATH).read_text(encoding="utf-8")
        start = script.index("def _cmd_freeze")
        gate = script.index(
            "require_historical_catalogue_execution_authorized",
            start,
        )
        read = script.index("_load_validated_cell_summaries", start)
        self.assertLess(gate, read)

    def test_annual_segment_label_is_exact(self) -> None:
        self.assertEqual(validate_annual_segment_label("2015"), "2015")
        self.assertEqual(
            validate_annual_segment_label("2026_YTD_TO_2026_08_20"),
            "2026_YTD_TO_2026_08_20",
        )
        with self.assertRaisesRegex(ValueError, "segment label drift"):
            validate_annual_segment_label("2027")

    def test_prior_segment_mapping_is_exact(self) -> None:
        self.assertIsNone(prior_segment_label("2015"))
        self.assertEqual(prior_segment_label("2016"), "2015")
        self.assertEqual(prior_segment_label("2025"), "2024")
        self.assertEqual(
            prior_segment_label("2026_YTD_TO_2026_08_20"),
            "2025",
        )

    def test_2015_requires_no_prior_freeze_and_rejects_one(self) -> None:
        report = validate_prior_segment_freeze(
            annual_segment_label="2015",
            previous_run=None,
            previous_freeze=None,
            expected_previous_run_id=None,
        )
        self.assertFalse(report["prior_segment_required"])
        self.assertIsNone(report["prior_segment_label"])

        with self.assertRaisesRegex(
            ValueError,
            "2015 must not provide prior-segment evidence",
        ):
            validate_prior_segment_freeze(
                annual_segment_label="2015",
                previous_run=_prior_run(),
                previous_freeze=_annual_freeze("2015"),
                expected_previous_run_id=PRIOR_RUN_ID,
            )

    def test_2016_requires_exact_successful_2015_freeze(self) -> None:
        report = validate_prior_segment_freeze(
            annual_segment_label="2016",
            previous_run=_prior_run(),
            previous_freeze=_annual_freeze("2015"),
            expected_previous_run_id=PRIOR_RUN_ID,
        )

        self.assertTrue(report["prior_segment_required"])
        self.assertEqual(report["prior_segment_label"], "2015")
        self.assertEqual(report["prior_run_id"], PRIOR_RUN_ID)
        self.assertEqual(report["prior_run_head_sha"], CODE_COMMIT)
        self.assertEqual(
            report["prior_freeze_evidence_fingerprint"],
            _annual_freeze("2015")["evidence_fingerprint"],
        )

    def test_wrong_prior_year_or_run_identity_fails_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "annual segment mismatch"):
            validate_prior_segment_freeze(
                annual_segment_label="2016",
                previous_run=_prior_run(),
                previous_freeze=_annual_freeze("2016"),
                expected_previous_run_id=PRIOR_RUN_ID,
            )

        with self.assertRaisesRegex(ValueError, "prior run id mismatch"):
            validate_prior_segment_freeze(
                annual_segment_label="2016",
                previous_run=_prior_run(run_id=PRIOR_RUN_ID + 1),
                previous_freeze=_annual_freeze("2015"),
                expected_previous_run_id=PRIOR_RUN_ID,
            )

        retried = _prior_run()
        retried["run_attempt"] = 2
        with self.assertRaisesRegex(ValueError, "prior run run_attempt mismatch"):
            validate_prior_segment_freeze(
                annual_segment_label="2016",
                previous_run=retried,
                previous_freeze=_annual_freeze("2015"),
                expected_previous_run_id=PRIOR_RUN_ID,
            )

        with self.assertRaisesRegex(ValueError, "code commit/run head mismatch"):
            validate_prior_segment_freeze(
                annual_segment_label="2016",
                previous_run=_prior_run(head_sha="9" * 40),
                previous_freeze=_annual_freeze("2015"),
                expected_previous_run_id=PRIOR_RUN_ID,
            )

    def test_template_requires_prior_freeze_before_annual_cells(self) -> None:
        text = Path(DORMANT_WORKFLOW_TEMPLATE_PATH).read_text(encoding="utf-8")
        execution_gate = text.index(
            "phase8a_annual_pattern_catalogue.py require-execution"
        )
        prior_download = text.index("Fetch exact prior annual freeze evidence")
        prior_validation = text.index(
            "phase8a_annual_pattern_catalogue.py require-prior-freeze"
        )
        cell_job = text.index("  annual_cell:")

        self.assertLess(execution_gate, prior_download)
        self.assertLess(prior_download, prior_validation)
        self.assertLess(prior_validation, cell_job)
        self.assertIn("previous_annual_freeze_run_id:", text)
        self.assertIn(
            'subparsers.add_parser("require-prior-freeze")',
            Path(CLI_PATH).read_text(encoding="utf-8"),
        )
        self.assertIn('          - "2015"', text)
        self.assertIn('          - "2026_YTD_TO_2026_08_20"', text)

    def test_source_payload_remains_dormant_and_non_executing(self) -> None:
        payload = workflow_source_payload(code_commit=CODE_COMMIT)

        self.assertEqual(payload["decision"], "DEC-478")
        self.assertEqual(payload["source_segment_freeze_decision"], "DEC-477")
        self.assertEqual(payload["annual_segment_labels"][0], "2015")
        self.assertEqual(
            payload["annual_segment_labels"][-1],
            "2026_YTD_TO_2026_08_20",
        )
        self.assertEqual(payload["cells_per_segment"], 18)
        self.assertEqual(payload["jobs_per_segment"], 20)
        self.assertEqual(payload["artifacts_per_segment"], 20)
        self.assertTrue(payload["prior_freeze_required_after_first_segment"])
        self.assertEqual(
            payload["prior_segment_dependencies"][0],
            {
                "annual_segment_label": "2015",
                "prior_segment_label": None,
            },
        )
        self.assertEqual(
            payload["prior_segment_dependencies"][-1],
            {
                "annual_segment_label": "2026_YTD_TO_2026_08_20",
                "prior_segment_label": "2025",
            },
        )
        self.assertEqual(
            payload["next_gate"],
            "SOURCE_ONLY_ANNUAL_PATTERN_CATALOGUE_WORKFLOW_INSTALL_CONTRACT",
        )
        for field in (
            "workflow_template_install_authorized",
            "workflow_installed",
            "workflow_dispatch_authorized",
            "historical_artifact_read_authorized",
            "historical_catalogue_execution_authorized",
            "historical_result_production_authorized",
            "next_segment_execution_authorized",
            "cross_year_result_production_authorized",
            "strategy_v1_synthesis_authorized",
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

    def test_module_level_authorities_are_all_closed(self) -> None:
        self.assertFalse(WORKFLOW_TEMPLATE_INSTALL_AUTHORIZED)
        self.assertFalse(WORKFLOW_INSTALLED)
        self.assertFalse(WORKFLOW_DISPATCH_AUTHORIZED)
        self.assertFalse(HISTORICAL_ARTIFACT_READ_AUTHORIZED)
        self.assertFalse(HISTORICAL_CATALOGUE_EXECUTION_AUTHORIZED)
        self.assertFalse(HISTORICAL_RESULT_PRODUCTION_AUTHORIZED)


if __name__ == "__main__":
    unittest.main()
