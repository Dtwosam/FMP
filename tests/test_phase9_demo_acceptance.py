from __future__ import annotations

import hashlib
import json
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

from fmp.phase8b.design import MT5_BRIDGE_PROTOCOL, MT5_PROVIDER, MT5_TRANSPORT
from fmp.phase9.acceptance import (
    MAX_MEDIAN_ADVERSE_SLIPPAGE_PIPS,
    MAX_P95_ADVERSE_SLIPPAGE_PIPS,
    MIN_COMPLETED_TRADES,
    MIN_DEMO_SESSION_DATES,
    MIN_ELAPSED_WEEKS,
    MIN_REPRESENTED_FAMILIES,
    MIN_REPRESENTED_PAIRS,
    PHASE9_DEMO_NEED_MORE_DATA,
    PHASE9_DEMO_PASS_ELIGIBLE_FOR_DEPLOYMENT_REVIEW,
    PHASE9_DEMO_REJECT_EXECUTION_COST_MISMATCH,
    PHASE9_DEMO_REJECT_OPERATIONAL_MISMATCH,
    PHASE9_DEMO_REJECT_SAFETY_FAILURE,
    build_phase9_demo_campaign_evidence,
    compile_phase9_demo_acceptance,
    validate_phase9_demo_acceptance,
    validate_phase9_demo_campaign_evidence,
    write_phase9_demo_acceptance,
)
from fmp.phase9.design import (
    PHASE9_DEMO_DESIGN_FROZEN,
    PHASE9_DEMO_DESIGN_PROTOCOL,
    PHASE9_EXPERIMENT_ID,
    PHASE9_MT5_ORDER_BRIDGE_PROTOCOL,
)
from fmp.risk import RiskConfig


UTC = timezone.utc
START = datetime(2026, 9, 22, 0, 0, tzinfo=UTC)
END = START + timedelta(days=58)
COMMIT = "c" * 40


def _digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()


def _design():
    payload = {
        "protocol": PHASE9_DEMO_DESIGN_PROTOCOL,
        "experiment_id": PHASE9_EXPERIMENT_ID,
        "decision": "DEC-055",
        "outcome": PHASE9_DEMO_DESIGN_FROZEN,
        "demo_design_code_commit": "d" * 40,
        "phase8b_review_id": "3" * 64,
        "phase8b_acceptance_fingerprint": "4" * 64,
        "phase8b_shadow_validation_fingerprint": "5" * 64,
        "capture_preflight_fingerprint": "6" * 64,
        "champion_set_id": "phase9-dec066-test",
        "champion_set_fingerprint": "7" * 64,
        "strategy_fingerprints": ["1" * 64, "2" * 64],
        "strategies": [
            {
                "fingerprint": "1" * 64,
                "identity_json": "{}",
                "family": "family-a",
                "symbol": "EURUSD",
                "timeframe": "5m",
                "code_commit": "a" * 40,
                "lifecycle": "SHADOW_VALIDATED",
            },
            {
                "fingerprint": "2" * 64,
                "identity_json": "{}",
                "family": "family-b",
                "symbol": "GBPUSD",
                "timeframe": "15m",
                "code_commit": "b" * 40,
                "lifecycle": "SHADOW_VALIDATED",
            },
        ],
        "execution_path": {
            "provider": MT5_PROVIDER,
            "accepted_quote_transport": MT5_TRANSPORT,
            "accepted_quote_protocol": MT5_BRIDGE_PROTOCOL,
            "future_order_bridge_protocol": PHASE9_MT5_ORDER_BRIDGE_PROTOCOL,
            "account_mode": "DEMO",
            "account_fingerprint": "8" * 64,
            "server": "FPMarketsSC-Demo",
            "required_symbols": ["EURUSD", "GBPUSD"],
            "symbol_mapping": {
                "EURUSD": "EURUSD",
                "GBPUSD": "GBPUSD",
            },
            "auto_trading_change_authorized": False,
            "provider_change_authorized": False,
        },
        "risk_config": RiskConfig().to_config(),
        "required_controls": {
            "practice_account_assertion_before_order_session": True,
            "mandatory_protective_stop": True,
            "unprotected_position_healthy_state_allowed": False,
            "deterministic_client_order_ids": True,
            "duplicate_client_order_prevention": True,
            "requested_vs_fill_price_logging": True,
            "order_validation_journal": True,
            "order_ack_fill_rejection_journal": True,
            "startup_position_order_reconciliation": True,
            "orphan_unknown_position_fail_closed": True,
            "restart_recovery_required": True,
            "daily_halt_required": True,
            "secrets_in_git_allowed": False,
            "secrets_in_evidence_artifacts_allowed": False,
        },
        "demo_adapter_source_authorized": True,
        "demo_execution_authorized": False,
        "demo_order_authorized": False,
        "live_order_authorized": False,
        "broker_mutation_authorized": False,
        "real_money_authorized": False,
        "phase10_authorized": False,
    }
    return payload | {"demo_design_fingerprint": _digest(payload)}


def _session_dates():
    return [
        (START + timedelta(days=i * 2)).date().isoformat()
        for i in range(30)
    ]


def _build_evidence(**overrides):
    design = _design()
    kwargs = {
        "design": design,
        "first_observation_utc": START,
        "last_observation_utc": END,
        "demo_session_dates": _session_dates(),
        "completed_trade_count": 40,
        "represented_strategy_families": ["family-a", "family-b"],
        "represented_pairs": ["EURUSD", "GBPUSD"],
        "order_attempt_count": 42,
        "completed_send_count": 40,
        "broker_noncompleted_send_count": 2,
        "ambiguous_send_count": 0,
        "retry_after_send_attempt_count": 0,
        "duplicate_client_order_count": 0,
        "completed_send_without_protective_stop_count": 0,
        "startup_reconciliation_failure_count": 0,
        "post_send_reconciliation_failure_count": 0,
        "practice_account_assertion_failure_count": 0,
        "daily_halt_violation_count": 0,
        "journal_integrity_failure_count": 0,
        "unauthorized_broker_mutation_count": 0,
        "live_order_count": 0,
        "real_money_access_count": 0,
        "restart_recovery_drill_count": 1,
        "restart_recovery_failure_count": 0,
        "requested_vs_fill_missing_count": 0,
        "slippage_by_pair": {
            "EURUSD": {
                "sample_count": 20,
                "median_adverse_entry_slippage_pips": 0.3,
                "p95_adverse_entry_slippage_pips": 0.8,
            },
            "GBPUSD": {
                "sample_count": 20,
                "median_adverse_entry_slippage_pips": 0.4,
                "p95_adverse_entry_slippage_pips": 0.9,
            },
        },
        "financial_metrics": {
            "demo_net_return": -0.012,
            "expectancy_per_completed_trade": -3.5,
            "profit_factor": 0.92,
            "maximum_drawdown_fraction": 0.031,
            "win_rate": 0.45,
        },
        "equity_series_fingerprint": "9" * 64,
        "code_commit": COMMIT,
    }
    kwargs.update(overrides)
    evidence = build_phase9_demo_campaign_evidence(**kwargs)
    return design, evidence


class Phase9DemoAcceptanceTests(unittest.TestCase):
    def test_thresholds_are_frozen_to_pre_result_values(self) -> None:
        self.assertEqual(MIN_COMPLETED_TRADES, 40)
        self.assertEqual(MIN_ELAPSED_WEEKS, 8)
        self.assertEqual(MIN_DEMO_SESSION_DATES, 30)
        self.assertEqual(MIN_REPRESENTED_FAMILIES, 2)
        self.assertEqual(MIN_REPRESENTED_PAIRS, 2)
        self.assertEqual(MAX_MEDIAN_ADVERSE_SLIPPAGE_PIPS, 0.5)
        self.assertEqual(MAX_P95_ADVERSE_SLIPPAGE_PIPS, 1.0)

    def test_clean_operational_evidence_passes_even_with_negative_demo_pnl(self) -> None:
        design, evidence = _build_evidence()
        validate_phase9_demo_campaign_evidence(evidence, design=design)
        result = compile_phase9_demo_acceptance(
            evidence=evidence,
            design=design,
            code_commit=COMMIT,
        )
        self.assertEqual(
            result["outcome"],
            PHASE9_DEMO_PASS_ELIGIBLE_FOR_DEPLOYMENT_REVIEW,
        )
        self.assertTrue(result["phase10_deployment_review_eligible"])
        self.assertEqual(
            result["financial_metrics_diagnostic"]["demo_net_return"],
            -0.012,
        )
        self.assertFalse(result["live_order_authorized"])
        self.assertFalse(result["real_money_authorized"])
        self.assertFalse(result["phase11_authorized"])
        validate_phase9_demo_acceptance(
            result,
            evidence=evidence,
            design=design,
        )

    def test_minimum_evidence_is_need_more_data_and_nonterminal(self) -> None:
        design, evidence = _build_evidence(completed_trade_count=39)
        result = compile_phase9_demo_acceptance(
            evidence=evidence,
            design=design,
            code_commit=COMMIT,
        )
        self.assertEqual(result["outcome"], PHASE9_DEMO_NEED_MORE_DATA)
        self.assertFalse(result["phase10_deployment_review_eligible"])
        self.assertFalse(
            result["minimum_evidence_checks"]["completed_trades_pass"]
        )

    def test_safety_failure_precedes_need_more_data(self) -> None:
        design, evidence = _build_evidence(
            completed_trade_count=10,
            live_order_count=1,
        )
        result = compile_phase9_demo_acceptance(
            evidence=evidence,
            design=design,
            code_commit=COMMIT,
        )
        self.assertEqual(
            result["outcome"],
            PHASE9_DEMO_REJECT_SAFETY_FAILURE,
        )
        self.assertFalse(result["safety_checks"]["live_order_pass"])

    def test_operational_failure_rejects_after_minimums(self) -> None:
        design, evidence = _build_evidence(restart_recovery_drill_count=0)
        result = compile_phase9_demo_acceptance(
            evidence=evidence,
            design=design,
            code_commit=COMMIT,
        )
        self.assertEqual(
            result["outcome"],
            PHASE9_DEMO_REJECT_OPERATIONAL_MISMATCH,
        )
        self.assertFalse(
            result["operational_checks"]["restart_recovery_drill_present"]
        )

    def test_execution_cost_mismatch_rejects_per_pair(self) -> None:
        design, evidence = _build_evidence(
            slippage_by_pair={
                "EURUSD": {
                    "sample_count": 20,
                    "median_adverse_entry_slippage_pips": 0.3,
                    "p95_adverse_entry_slippage_pips": 1.1,
                },
                "GBPUSD": {
                    "sample_count": 20,
                    "median_adverse_entry_slippage_pips": 0.4,
                    "p95_adverse_entry_slippage_pips": 0.9,
                },
            }
        )
        result = compile_phase9_demo_acceptance(
            evidence=evidence,
            design=design,
            code_commit=COMMIT,
        )
        self.assertEqual(
            result["outcome"],
            PHASE9_DEMO_REJECT_EXECUTION_COST_MISMATCH,
        )
        self.assertFalse(
            result["execution_cost_checks"]["pair_checks"]["EURUSD"]["p95_pass"]
        )

    def test_slippage_samples_must_account_for_all_completed_sends(self) -> None:
        design, evidence = _build_evidence(
            slippage_by_pair={
                "EURUSD": {
                    "sample_count": 19,
                    "median_adverse_entry_slippage_pips": 0.3,
                    "p95_adverse_entry_slippage_pips": 0.8,
                },
                "GBPUSD": {
                    "sample_count": 20,
                    "median_adverse_entry_slippage_pips": 0.4,
                    "p95_adverse_entry_slippage_pips": 0.9,
                },
            }
        )
        result = compile_phase9_demo_acceptance(
            evidence=evidence,
            design=design,
            code_commit=COMMIT,
        )
        self.assertEqual(
            result["outcome"],
            PHASE9_DEMO_REJECT_OPERATIONAL_MISMATCH,
        )
        self.assertFalse(
            result["operational_checks"]["slippage_sample_accounting_pass"]
        )

    def test_campaign_identity_tamper_fails_even_if_refingerprinted(self) -> None:
        design, evidence = _build_evidence()
        changed = dict(evidence)
        changed["account_fingerprint"] = "f" * 64
        changed.pop("demo_campaign_evidence_fingerprint")
        changed["demo_campaign_evidence_fingerprint"] = _digest(changed)
        with self.assertRaisesRegex(ValueError, "account_fingerprint mismatch"):
            validate_phase9_demo_campaign_evidence(changed, design=design)

    def test_session_date_outside_campaign_range_fails(self) -> None:
        with self.assertRaisesRegex(ValueError, "outside observation range"):
            _build_evidence(
                demo_session_dates=_session_dates()
                + [(END + timedelta(days=1)).date().isoformat()]
            )

    def test_acceptance_writer_is_create_only(self) -> None:
        design, evidence = _build_evidence()
        result = compile_phase9_demo_acceptance(
            evidence=evidence,
            design=design,
            code_commit=COMMIT,
        )
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = write_phase9_demo_acceptance(
                result,
                out_dir=root,
                evidence=evidence,
                design=design,
            )
            self.assertTrue((root / "acceptance.json").is_file())
            self.assertTrue((root / "manifest.json").is_file())
            self.assertTrue(manifest["phase10_deployment_review_eligible"])
            self.assertFalse(manifest["live_order_authorized"])
            with self.assertRaises(FileExistsError):
                write_phase9_demo_acceptance(
                    result,
                    out_dir=root,
                    evidence=evidence,
                    design=design,
                )


if __name__ == "__main__":
    unittest.main()
