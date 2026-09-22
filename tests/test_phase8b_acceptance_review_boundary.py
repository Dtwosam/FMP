from __future__ import annotations

import hashlib
import json
import unittest
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

from fmp.contracts import QuoteBar
from fmp.phase8b.acceptance import (
    PHASE8B_NEED_MORE_DATA,
    PHASE8B_PASS_ELIGIBLE_FOR_DEMO_DESIGN,
    PHASE8B_REJECT_SAFETY_FAILURE,
    validate_phase8b_spread_reference,
)
from fmp.phase8b.capture import (
    PHASE8B_CAPTURE_EXPERIMENT_ID,
    PHASE8B_CAPTURE_FOUNDATION_READY,
    PHASE8B_CAPTURE_PREFLIGHT_PROTOCOL,
    READER_START_SEMANTICS,
    validate_phase8b_capture_preflight,
)
from fmp.phase8b.design import (
    BRIDGE_FILE_BY_SYMBOL,
    LIVENESS_TIMEOUT_SECONDS,
    MT5_BRIDGE_PROTOCOL,
    MT5_PROVIDER,
    MT5_TRANSPORT,
    QUOTE_DEADLINE_SECONDS,
    SLIPPAGE_SCENARIOS,
)
from fmp.phase8b.review import (
    PHASE8B_CAMPAIGN_TERMINAL_PROTOCOL,
    PHASE8B_SHADOW_VALIDATION_PROTOCOL,
    build_phase8b_spread_reference,
    review_phase8b_campaign_directory,
    validate_phase8b_shadow_validation,
    write_phase8b_spread_reference,
)
from fmp.portfolio.contracts import ChampionSet, PHASE8A_EXPERIMENT_ID
from fmp.portfolio.historical_inventory import build_phase4_baseline_inventory
from fmp.portfolio.research_data import (
    PHASE8A_RETROSPECTIVE_END_EXCLUSIVE,
    PHASE8A_RETROSPECTIVE_LABEL,
    PHASE8A_RETROSPECTIVE_START,
    LoadedRetrospectiveBars,
)


UTC = timezone.utc
BASE = datetime(2026, 10, 1, 8, 0, tzinfo=UTC)
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


def _stable(value: object) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=True,
            indent=2,
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def _preflight():
    inventory = build_phase4_baseline_inventory()
    chosen = []
    symbols = set()
    for record in inventory:
        if record.strategy.symbol in symbols:
            continue
        chosen.append(record.strategy)
        symbols.add(record.strategy.symbol)
        if len(chosen) == 2:
            break
    strategies = tuple(sorted(chosen, key=lambda item: item.fingerprint))
    champion = ChampionSet(
        champion_set_id="dec054-review-test",
        experiment_id=PHASE8A_EXPERIMENT_ID,
        strategies=strategies,
    )
    rows = [
        {
            "fingerprint": item.fingerprint,
            "identity_json": item.identity_json,
            "family": item.family,
            "symbol": item.symbol,
            "timeframe": item.timeframe,
            "parameters_json": item.parameters_json,
            "code_commit": item.code_commit,
            "lifecycle": "SHADOW_CANDIDATE",
            "evidence_id": "EXP-20260922-016:PHASE8A_ACCEPT_SHADOW_CANDIDATE",
        }
        for item in strategies
    ]
    required_symbols = sorted({item.symbol for item in strategies})
    timeframe_order = {"5m": 0, "15m": 1, "1h": 2}
    required_timeframes = sorted(
        {item.timeframe for item in strategies},
        key=timeframe_order.__getitem__,
    )
    sessions = {
        symbol: f"{index + 1:064x}"
        for index, symbol in enumerate(required_symbols)
    }
    payload = {
        "protocol": PHASE8B_CAPTURE_PREFLIGHT_PROTOCOL,
        "experiment_id": PHASE8B_CAPTURE_EXPERIMENT_ID,
        "outcome": PHASE8B_CAPTURE_FOUNDATION_READY,
        "registration_sha256": "1" * 64,
        "registration_fingerprint": "2" * 64,
        "start_authorization_sha256": "3" * 64,
        "start_authorization_fingerprint": "4" * 64,
        "capture_foundation_code_commit": "1" * 40,
        "prepared_at_utc": "2026-09-22T14:00:00Z",
        "campaign_start_utc": "2026-09-22T13:55:00Z",
        "first_london_date": "2026-09-22",
        "reader_start_semantics": READER_START_SEMANTICS,
        "champion_set_id": champion.champion_set_id,
        "champion_set_fingerprint": champion.fingerprint,
        "strategy_count": len(rows),
        "strategy_fingerprints": [item["fingerprint"] for item in rows],
        "strategies": rows,
        "required_symbols": required_symbols,
        "required_timeframes": required_timeframes,
        "provider": MT5_PROVIDER,
        "transport": MT5_TRANSPORT,
        "connector_protocol": MT5_BRIDGE_PROTOCOL,
        "bridge_file_by_symbol": {
            symbol: BRIDGE_FILE_BY_SYMBOL[symbol]
            for symbol in required_symbols
        },
        "account_fingerprint": "a" * 64,
        "server": "FPMarketsSC-Demo",
        "bridge_session_id_by_symbol": sessions,
        "liveness": {
            "bridge_timeout_seconds": LIVENESS_TIMEOUT_SECONDS,
            "market_quiet_threshold_seconds": LIVENESS_TIMEOUT_SECONDS,
            "quote_deadline_seconds": QUOTE_DEADLINE_SECONDS,
            "per_required_symbol": True,
            "market_quiet_is_bridge_failure": False,
            "backfill_allowed": False,
            "interpolation_allowed": False,
            "alternate_provider_repair_allowed": False,
        },
        "slippage_scenarios": list(SLIPPAGE_SCENARIOS),
        "capture_runtime_ready": True,
        "live_shadow_segment_started": False,
        "acceptance_authorized": False,
        "promotion_authorized": False,
        "demo_order_authorized": False,
        "live_order_authorized": False,
        "broker_mutation_authorized": False,
        "real_money_authorized": False,
        "phase9_authorized": False,
    }
    result = payload | {"capture_preflight_fingerprint": _digest(payload)}
    validate_phase8b_capture_preflight(result)
    return result


def _bar(symbol: str, timestamp: datetime, spread_pips: float) -> QuoteBar:
    pip = 0.01 if symbol == "USDJPY" else 0.0001
    bid = 150.0 if symbol == "USDJPY" else 1.10
    ask = bid + spread_pips * pip
    return QuoteBar(
        timestamp_utc=timestamp,
        symbol=symbol,
        bid_open=bid,
        bid_high=bid,
        bid_low=bid,
        bid_close=bid,
        ask_open=ask,
        ask_high=ask,
        ask_low=ask,
        ask_close=ask,
    )


def _reference(preflight):
    payload = {
        "protocol": "fmp-phase8b-spread-reference-v1",
        "contract_decision": "DEC-051",
        "capture_preflight_fingerprint": preflight[
            "capture_preflight_fingerprint"
        ],
        "champion_set_fingerprint": preflight[
            "champion_set_fingerprint"
        ],
        "required_symbols": sorted(preflight["required_symbols"]),
        "slippage_scenarios": [0.2, 0.5, 1.0],
        "source_label": "RETROSPECTIVE_ALREADY_SEEN",
        "per_symbol": {
            symbol: {
                "entry_sample_count": 100,
                "exit_sample_count": 100,
                "entry_median_pips": 1.5,
                "entry_p95_pips": 2.0,
                "exit_median_pips": 1.5,
                "exit_p95_pips": 2.0,
            }
            for symbol in preflight["required_symbols"]
        },
    }
    return payload | {"spread_reference_fingerprint": _digest(payload)}


def _campaign_evidence(preflight, *, pass_ready: bool, safety: bool = True):
    weeks = 8 if pass_ready else 1
    trades = 50 if pass_ready else 5
    denominator = [
        f"2026-10-{index + 1:02d}"
        if index < 31
        else f"2026-11-{index - 30:02d}"
        for index in range(40 if pass_ready else 5)
    ]
    complete = denominator if pass_ready else denominator[:2]
    end = BASE + timedelta(weeks=weeks)
    symbols = sorted(preflight["required_symbols"])
    payload = {
        "protocol": "fmp-phase8b-campaign-evidence-v1",
        "contract_decision": "DEC-051",
        "prospective_evidence": True,
        "prospective_segment_closed": True,
        "capture_preflight_fingerprint": preflight[
            "capture_preflight_fingerprint"
        ],
        "segment_fingerprint": "3" * 64,
        "replay_fingerprint": "4" * 64,
        "replay_match": True,
        "champion_set_fingerprint": preflight[
            "champion_set_fingerprint"
        ],
        "strategy_fingerprints": list(preflight["strategy_fingerprints"]),
        "required_symbols": symbols,
        "slippage_scenarios": [0.2, 0.5, 1.0],
        "campaign_start_utc": "2026-09-22T13:55:00Z",
        "first_observation_utc": BASE.isoformat().replace("+00:00", "Z"),
        "last_observation_utc": end.isoformat().replace("+00:00", "Z"),
        "denominator_london_dates": denominator,
        "complete_london_dates": complete,
        "completed_trade_count_0_2": trades,
        "same_candidate_sequence_all_scenarios": True,
        "structural_safety": {
            "no_order_surface": safety,
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
            "strategy_families_with_completed_trades": (
                ["family-a", "family-b"] if pass_ready else []
            ),
            "pairs_with_completed_trades": (
                symbols if pass_ready else []
            ),
        },
        "live_spread_by_symbol": {
            symbol: {
                "entry_sample_count": 25 if pass_ready else 0,
                "exit_sample_count": 25 if pass_ready else 0,
                "entry_median_pips": 1.0 if pass_ready else None,
                "entry_p95_pips": 1.5 if pass_ready else None,
                "exit_median_pips": 1.0 if pass_ready else None,
                "exit_p95_pips": 1.5 if pass_ready else None,
            }
            for symbol in symbols
        },
        "demo_order_authorized": False,
        "live_order_authorized": False,
        "broker_mutation_authorized": False,
        "real_money_authorized": False,
        "phase9_execution_authorized": False,
    }
    return payload | {"campaign_evidence_fingerprint": _digest(payload)}


def _campaign_dir(root: Path, preflight, evidence, reference):
    (root / "capture-preflight.json").write_bytes(_stable(preflight))
    (root / "spread-reference.json").write_bytes(_stable(reference))
    closure_id = "9" * 64
    closure = root / "closures" / closure_id
    closure.mkdir(parents=True)
    evidence_bytes = _stable(evidence)
    (closure / "campaign-evidence.json").write_bytes(evidence_bytes)
    manifest = {
        "protocol": "fmp-phase8b-campaign-close-artifacts-v1",
        "experiment_id": "EXP-20260922-024",
        "decision": "DEC-053",
        "closure_id": closure_id,
        "outcome": "PHASE8B_CAMPAIGN_EVIDENCE_SNAPSHOT_READY",
        "campaign_evidence_fingerprint": evidence[
            "campaign_evidence_fingerprint"
        ],
        "segment_fingerprint": evidence["segment_fingerprint"],
        "replay_fingerprint": evidence["replay_fingerprint"],
        "acceptance_authorized": False,
        "promotion_authorized": False,
        "artifacts": [
            {
                "path": "campaign-evidence.json",
                "sha256": hashlib.sha256(evidence_bytes).hexdigest(),
            }
        ],
    }
    (closure / "manifest.json").write_bytes(_stable(manifest))
    return closure_id


class Phase8BReviewBoundaryTests(unittest.TestCase):
    def test_spread_reference_uses_fixed_full_retrospective_1m_method(self) -> None:
        preflight = _preflight()
        calls = []

        def loader(**kwargs):
            calls.append(kwargs)
            symbol = kwargs["symbol"]
            bars = (
                _bar(symbol, datetime(2020, 1, 1, 0, 0, tzinfo=UTC), 1.0),
                _bar(symbol, datetime(2020, 1, 1, 0, 1, tzinfo=UTC), 2.0),
                _bar(symbol, datetime(2020, 1, 1, 0, 2, tzinfo=UTC), 3.0),
            )
            return LoadedRetrospectiveBars(
                bars=bars,
                excluded_incomplete_count=0,
                eligible_utc_dates=(date(2020, 1, 1),),
                evidence_label=PHASE8A_RETROSPECTIVE_LABEL,
                start=PHASE8A_RETROSPECTIVE_START,
                end_exclusive=PHASE8A_RETROSPECTIVE_END_EXCLUSIVE,
                processed_manifest_sha256=(
                    "e" * 64 if symbol == "EURUSD" else "d" * 64
                ),
                opened_artifact_months=("2020-01",),
            )

        result = build_phase8b_spread_reference(
            preflight=preflight,
            dataset_root=Path("/dataset"),
            code_commit=COMMIT,
            bar_loader=loader,
        )
        validate_phase8b_spread_reference(result)
        self.assertEqual(len(calls), len(preflight["required_symbols"]))
        self.assertTrue(all(call["timeframe"] == "1m" for call in calls))
        self.assertTrue(
            all(
                call["research_range"].start
                == PHASE8A_RETROSPECTIVE_START
                and call["research_range"].end_exclusive
                == PHASE8A_RETROSPECTIVE_END_EXCLUSIVE
                for call in calls
            )
        )
        for symbol in preflight["required_symbols"]:
            row = result["per_symbol"][symbol]
            self.assertEqual(row["entry_sample_count"], 3)
            self.assertAlmostEqual(row["entry_median_pips"], 2.0)
            self.assertAlmostEqual(row["entry_p95_pips"], 3.0)

    def test_spread_reference_write_is_create_only(self) -> None:
        preflight = _preflight()
        reference = _reference(preflight)
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_phase8b_spread_reference(reference, root)
            with self.assertRaises(FileExistsError):
                write_phase8b_spread_reference(reference, root)

    def test_need_more_data_writes_review_without_terminal_marker(self) -> None:
        preflight = _preflight()
        reference = _reference(preflight)
        evidence = _campaign_evidence(preflight, pass_ready=False)
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            closure_id = _campaign_dir(root, preflight, evidence, reference)
            result = review_phase8b_campaign_directory(
                campaign_dir=root,
                closure_id=closure_id,
                code_commit=COMMIT,
            )
            self.assertEqual(
                result["acceptance"]["outcome"],
                PHASE8B_NEED_MORE_DATA,
            )
            self.assertIsNone(result["shadow_validation"])
            self.assertIsNone(result["terminal_marker"])
            self.assertFalse((root / "campaign-terminal.json").exists())

    def test_safety_rejection_is_terminal_without_lifecycle_transition(self) -> None:
        preflight = _preflight()
        reference = _reference(preflight)
        evidence = _campaign_evidence(
            preflight,
            pass_ready=False,
            safety=False,
        )
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            closure_id = _campaign_dir(root, preflight, evidence, reference)
            result = review_phase8b_campaign_directory(
                campaign_dir=root,
                closure_id=closure_id,
                code_commit=COMMIT,
            )
            self.assertEqual(
                result["acceptance"]["outcome"],
                PHASE8B_REJECT_SAFETY_FAILURE,
            )
            self.assertIsNone(result["shadow_validation"])
            terminal = json.loads(
                (root / "campaign-terminal.json").read_text()
            )
            self.assertEqual(
                terminal["protocol"],
                PHASE8B_CAMPAIGN_TERMINAL_PROTOCOL,
            )
            with self.assertRaisesRegex(ValueError, "terminal"):
                review_phase8b_campaign_directory(
                    campaign_dir=root,
                    closure_id=closure_id,
                    code_commit=COMMIT,
                )

    def test_pass_creates_shadow_validated_evidence_and_terminal_marker(self) -> None:
        preflight = _preflight()
        reference = _reference(preflight)
        evidence = _campaign_evidence(preflight, pass_ready=True)
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            closure_id = _campaign_dir(root, preflight, evidence, reference)
            result = review_phase8b_campaign_directory(
                campaign_dir=root,
                closure_id=closure_id,
                code_commit=COMMIT,
            )
            self.assertEqual(
                result["acceptance"]["outcome"],
                PHASE8B_PASS_ELIGIBLE_FOR_DEMO_DESIGN,
            )
            shadow = result["shadow_validation"]
            self.assertIsNotNone(shadow)
            validate_phase8b_shadow_validation(shadow)
            self.assertEqual(
                shadow["protocol"],
                PHASE8B_SHADOW_VALIDATION_PROTOCOL,
            )
            self.assertEqual(
                shadow["champion_set_fingerprint"],
                preflight["champion_set_fingerprint"],
            )
            self.assertTrue(
                all(
                    row["prior_lifecycle"] == "SHADOW_CANDIDATE"
                    and row["lifecycle"] == "SHADOW_VALIDATED"
                    for row in shadow["strategies"]
                )
            )
            self.assertFalse(shadow["demo_order_authorized"])
            self.assertTrue((root / "campaign-terminal.json").is_file())


if __name__ == "__main__":
    unittest.main()
