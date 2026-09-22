from __future__ import annotations

import hashlib
import json
import unittest
from datetime import datetime, timedelta, timezone

from fmp.phase8b.acceptance import (
    PHASE8B_ACCEPTANCE_PROTOCOL,
    PHASE8B_NEED_MORE_DATA,
    PHASE8B_PASS_ELIGIBLE_FOR_DEMO_DESIGN,
    PHASE8B_REJECT_FINANCIAL_MISMATCH,
    PHASE8B_REJECT_MARKET_MISMATCH,
    PHASE8B_REJECT_OPERATIONAL_MISMATCH,
    PHASE8B_REJECT_SAFETY_FAILURE,
    compile_phase8b_acceptance,
    validate_phase8b_acceptance,
    validate_phase8b_campaign_evidence,
    validate_phase8b_spread_reference,
)


UTC = timezone.utc
PREFLIGHT = "1" * 64
CHAMPION = "2" * 64
SEGMENT = "3" * 64
REPLAY = "4" * 64
STRATEGIES = ["5" * 64, "6" * 64]
SYMBOLS = ["EURUSD", "USDJPY"]
COMMIT = "a" * 40


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


def _spread_reference():
    payload = {
        "protocol": "fmp-phase8b-spread-reference-v1",
        "contract_decision": "DEC-051",
        "capture_preflight_fingerprint": PREFLIGHT,
        "champion_set_fingerprint": CHAMPION,
        "required_symbols": SYMBOLS,
        "slippage_scenarios": [0.2, 0.5, 1.0],
        "source_label": "RETROSPECTIVE_ALREADY_SEEN",
        "per_symbol": {
            symbol: {
                "entry_sample_count": 100,
                "exit_sample_count": 100,
                "entry_median_pips": 0.7,
                "entry_p95_pips": 1.2,
                "exit_median_pips": 0.8,
                "exit_p95_pips": 1.3,
            }
            for symbol in SYMBOLS
        },
    }
    value = payload | {"spread_reference_fingerprint": _digest(payload)}
    validate_phase8b_spread_reference(value)
    return value


def _campaign_evidence(
    *,
    weeks: int = 8,
    complete_dates: int = 40,
    denominator_dates: int = 40,
    trades: int = 50,
):
    start = datetime(2026, 10, 1, 8, 0, tzinfo=UTC)
    end = start + timedelta(weeks=weeks)
    denominator = [
        f"2026-10-{index + 1:02d}"
        if index < 31
        else f"2026-11-{index - 30:02d}"
        for index in range(denominator_dates)
    ]
    complete = denominator[:complete_dates]
    payload = {
        "protocol": "fmp-phase8b-campaign-evidence-v1",
        "contract_decision": "DEC-051",
        "prospective_evidence": True,
        "prospective_segment_closed": True,
        "capture_preflight_fingerprint": PREFLIGHT,
        "segment_fingerprint": SEGMENT,
        "replay_fingerprint": REPLAY,
        "replay_match": True,
        "champion_set_fingerprint": CHAMPION,
        "strategy_fingerprints": STRATEGIES,
        "required_symbols": SYMBOLS,
        "slippage_scenarios": [0.2, 0.5, 1.0],
        "campaign_start_utc": start.isoformat().replace("+00:00", "Z"),
        "first_observation_utc": start.isoformat().replace("+00:00", "Z"),
        "last_observation_utc": end.isoformat().replace("+00:00", "Z"),
        "denominator_london_dates": denominator,
        "complete_london_dates": complete,
        "completed_trade_count_0_2": trades,
        "same_candidate_sequence_all_scenarios": True,
        "structural_safety": {
            "no_order_surface": True,
            "quote_only_bridge": True,
            "zero_demo_orders": True,
            "zero_live_orders": True,
            "zero_broker_mutations": True,
            "zero_real_money_actions": True,
        },
        "integrity": {
            "malformed_silently_accepted_count": 0,
            "stale_gap_trades_in_financial_metrics_count": 0,
            "all_operational_events_logged": True,
        },
        "timing": {
            "p99_processing_latency_ms": 100.0,
            "entry_deadline_violation_count": 0,
            "scheduled_exit_deadline_violation_count": 0,
        },
        "scenarios": {
            "0.2": {
                "trade_count": trades,
                "net_return": 0.08,
                "expectancy_usd": 20.0,
                "profit_factor": 1.3,
                "max_drawdown_fraction": 0.03,
            },
            "0.5": {
                "trade_count": trades,
                "net_return": 0.04,
                "expectancy_usd": 10.0,
                "profit_factor": 1.15,
                "max_drawdown_fraction": 0.04,
            },
            "1.0": {
                "trade_count": trades,
                "net_return": -0.01,
                "expectancy_usd": -2.0,
                "profit_factor": 0.95,
                "max_drawdown_fraction": 0.05,
            },
        },
        "representation": {
            "strategy_families_with_completed_trades": [
                "session_breakout",
                "volatility_breakout",
            ],
            "pairs_with_completed_trades": SYMBOLS,
        },
        "live_spread_by_symbol": {
            symbol: {
                "entry_sample_count": 25,
                "exit_sample_count": 25,
                "entry_median_pips": 0.8,
                "entry_p95_pips": 1.4,
                "exit_median_pips": 0.9,
                "exit_p95_pips": 1.5,
            }
            for symbol in SYMBOLS
        },
        "demo_order_authorized": False,
        "live_order_authorized": False,
        "broker_mutation_authorized": False,
        "real_money_authorized": False,
        "phase9_execution_authorized": False,
    }
    value = payload | {"campaign_evidence_fingerprint": _digest(payload)}
    validate_phase8b_campaign_evidence(value)
    return value


def _refingerprint(value, field):
    payload = dict(value)
    payload.pop(field, None)
    payload[field] = _digest(payload)
    return payload


class Phase8BAcceptanceCompilerTests(unittest.TestCase):
    def test_full_pass_authorizes_only_shadow_validation_and_demo_design(self) -> None:
        result = compile_phase8b_acceptance(
            campaign_evidence=_campaign_evidence(),
            spread_reference=_spread_reference(),
            code_commit=COMMIT,
        )
        self.assertEqual(result["protocol"], PHASE8B_ACCEPTANCE_PROTOCOL)
        self.assertEqual(
            result["outcome"],
            PHASE8B_PASS_ELIGIBLE_FOR_DEMO_DESIGN,
        )
        self.assertTrue(result["shadow_validation_authorized"])
        self.assertTrue(result["lifecycle_transition_authorized"])
        self.assertTrue(result["demo_design_eligible"])
        self.assertFalse(result["demo_order_authorized"])
        self.assertFalse(result["live_order_authorized"])
        self.assertFalse(result["broker_mutation_authorized"])
        self.assertFalse(result["real_money_authorized"])
        self.assertFalse(result["phase9_execution_authorized"])
        validate_phase8b_acceptance(result)

    def test_sample_shortfall_is_need_more_data_not_rejection(self) -> None:
        result = compile_phase8b_acceptance(
            campaign_evidence=_campaign_evidence(weeks=7, trades=39),
            spread_reference=_spread_reference(),
            code_commit=COMMIT,
        )
        self.assertEqual(result["outcome"], PHASE8B_NEED_MORE_DATA)
        self.assertFalse(result["lifecycle_transition_authorized"])

    def test_safety_failure_precedes_need_more_data(self) -> None:
        evidence = _campaign_evidence(weeks=1, trades=5)
        evidence["structural_safety"]["no_order_surface"] = False
        evidence = _refingerprint(evidence, "campaign_evidence_fingerprint")
        result = compile_phase8b_acceptance(
            campaign_evidence=evidence,
            spread_reference=_spread_reference(),
            code_commit=COMMIT,
        )
        self.assertEqual(result["outcome"], PHASE8B_REJECT_SAFETY_FAILURE)

    def test_replay_or_coverage_failure_is_operational_mismatch(self) -> None:
        evidence = _campaign_evidence(complete_dates=35, denominator_dates=40)
        evidence["replay_match"] = False
        evidence = _refingerprint(evidence, "campaign_evidence_fingerprint")
        result = compile_phase8b_acceptance(
            campaign_evidence=evidence,
            spread_reference=_spread_reference(),
            code_commit=COMMIT,
        )
        self.assertEqual(
            result["outcome"],
            PHASE8B_REJECT_OPERATIONAL_MISMATCH,
        )

        evidence = _campaign_evidence(complete_dates=35, denominator_dates=40)
        result = compile_phase8b_acceptance(
            campaign_evidence=evidence,
            spread_reference=_spread_reference(),
            code_commit=COMMIT,
        )
        self.assertEqual(
            result["outcome"],
            PHASE8B_REJECT_OPERATIONAL_MISMATCH,
        )

    def test_spread_parity_failure_is_market_mismatch(self) -> None:
        evidence = _campaign_evidence()
        evidence["live_spread_by_symbol"]["EURUSD"]["entry_p95_pips"] = 1.8
        evidence = _refingerprint(evidence, "campaign_evidence_fingerprint")
        result = compile_phase8b_acceptance(
            campaign_evidence=evidence,
            spread_reference=_spread_reference(),
            code_commit=COMMIT,
        )
        self.assertEqual(result["outcome"], PHASE8B_REJECT_MARKET_MISMATCH)

    def test_financial_failure_is_financial_mismatch(self) -> None:
        evidence = _campaign_evidence()
        evidence["scenarios"]["0.5"]["net_return"] = -0.001
        evidence = _refingerprint(evidence, "campaign_evidence_fingerprint")
        result = compile_phase8b_acceptance(
            campaign_evidence=evidence,
            spread_reference=_spread_reference(),
            code_commit=COMMIT,
        )
        self.assertEqual(
            result["outcome"],
            PHASE8B_REJECT_FINANCIAL_MISMATCH,
        )

    def test_tampered_campaign_fingerprint_fails_closed(self) -> None:
        evidence = _campaign_evidence()
        evidence["completed_trade_count_0_2"] = 999
        with self.assertRaisesRegex(ValueError, "fingerprint"):
            validate_phase8b_campaign_evidence(evidence)


if __name__ == "__main__":
    unittest.main()
