from __future__ import annotations

import hashlib
import json
import unittest
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

from fmp.phase8b.bridge import (
    Phase8BBridgeFileTail,
    Phase8BBridgeHeartbeatRecord,
    Phase8BBridgeProtocolError,
    Phase8BBridgeTickRecord,
)
from fmp.phase8b.campaign_start import (
    build_phase8b_campaign_start_authorization,
)
from fmp.phase8b.capture import (
    CAPTURE_RECORD_PROTOCOL,
    PHASE8B_CAPTURE_FOUNDATION_READY,
    PHASE8B_CAPTURE_PREFLIGHT_PROTOCOL,
    Phase8BCaptureFeedEnvelope,
    build_phase8b_capture_preflight,
    validate_phase8b_capture_preflight,
    validate_phase8b_capture_record_envelope,
    write_phase8b_capture_preflight,
)
from fmp.phase8b.design import build_phase8b_design
from fmp.phase8b.qualification import (
    FeedQualificationOutcome,
    FeedQualificationResult,
    summarize_phase8b_qualification,
)
from fmp.phase8b.registration import build_phase8b_registration
from fmp.portfolio.challenger_discovery import build_exp015_challengers
from fmp.portfolio.contracts import StrategyLifecycle, StrategyRecord
from fmp.portfolio.historical_inventory import build_phase4_baseline_inventory
from fmp.portfolio.registry import freeze_shadow_champion_set, transition_strategy


UTC = timezone.utc
REGISTERED_AT = datetime(2026, 9, 22, 14, 0, tzinfo=UTC)
STARTED_AT = datetime(2026, 9, 22, 14, 30, tzinfo=UTC)
PREPARED_AT = datetime(2026, 9, 22, 14, 45, tzinfo=UTC)
ACCOUNT = "a" * 64
SERVER = "FPMarketsSC-Demo"
DESIGN_COMMIT = "d" * 40
QUAL_COMMIT = "e" * 40
REG_COMMIT = "f" * 40
START_COMMIT = "1" * 40
CAPTURE_COMMIT = "2" * 40


def _acceptance():
    baseline = next(
        item
        for item in build_phase4_baseline_inventory()
        if item.lifecycle is StrategyLifecycle.HISTORICAL_QUALIFIED
    )
    source = next(
        item
        for item in build_exp015_challengers(code_commit="c" * 40)
        if item.strategy.symbol != baseline.strategy.symbol
    )
    challenger = StrategyRecord(
        strategy=source.strategy,
        lifecycle=StrategyLifecycle.HISTORICAL_QUALIFIED,
        evidence_id="EXP-20260922-015:FINAL_SHORTLIST",
    )
    before = (baseline, challenger)
    after = tuple(
        transition_strategy(
            item,
            StrategyLifecycle.SHADOW_CANDIDATE,
            evidence_id="EXP-20260922-016:PHASE8A_ACCEPT_SHADOW_CANDIDATE",
        )
        for item in before
    )
    champion = freeze_shadow_champion_set(
        after,
        champion_set_id="phase8a-exp016-capture-test",
    )
    before_by_fp = {item.strategy.fingerprint: item for item in before}
    rows = []
    for item in sorted(after, key=lambda value: value.strategy.fingerprint):
        prior = before_by_fp[item.strategy.fingerprint]
        rows.append(
            {
                "fingerprint": item.strategy.fingerprint,
                "identity_json": item.strategy.identity_json,
                "family": item.strategy.family,
                "symbol": item.strategy.symbol,
                "timeframe": item.strategy.timeframe,
                "parameters_json": item.strategy.parameters_json,
                "code_commit": item.strategy.code_commit,
                "prior_lifecycle": prior.lifecycle.value,
                "prior_evidence_id": prior.evidence_id,
                "lifecycle": item.lifecycle.value,
                "evidence_id": item.evidence_id,
            }
        )
    return {
        "protocol": "fmp-phase8a-acceptance-v1",
        "experiment_id": "EXP-20260922-016",
        "outcome": "PHASE8A_SHADOW_CANDIDATE_ACCEPTED",
        "acceptance_code_commit": "b" * 40,
        "shadow_candidate_authorized": True,
        "phase8b_design_authorized": True,
        "promotion_authorized": False,
        "demo_order_authorized": False,
        "live_order_authorized": False,
        "broker_mutation_authorized": False,
        "real_money_authorized": False,
        "phase9_authorized": False,
        "shadow_candidate": {
            "champion_set_id": champion.champion_set_id,
            "champion_set_experiment_id": champion.experiment_id,
            "champion_set_fingerprint": champion.fingerprint,
            "strategy_fingerprints": [
                item.fingerprint for item in champion.strategies
            ],
            "strategies": rows,
        },
    }


def _registration():
    design = build_phase8b_design(
        acceptance=_acceptance(),
        acceptance_sha256="2" * 64,
        code_commit=DESIGN_COMMIT,
    )
    results = {}
    for index, symbol in enumerate(design["required_symbols"]):
        results[symbol] = FeedQualificationResult(
            symbol=symbol,
            outcome=FeedQualificationOutcome.PASS,
            account_fingerprint=ACCOUNT,
            bridge_session_id=f"{index + 1:064x}",
            server=SERVER,
            started_at_utc=REGISTERED_AT,
            ended_at_utc=REGISTERED_AT,
            elapsed_seconds=1.0,
            price_count=100,
            heartbeat_count=6,
            max_bridge_liveness_gap_seconds=1.0,
            max_market_liveness_gap_seconds=1.0,
            rejection_codes=(),
        )
    qualification = summarize_phase8b_qualification(
        design=design,
        design_sha256="3" * 64,
        code_commit=QUAL_COMMIT,
        feed_results=results,
    )
    return build_phase8b_registration(
        design=design,
        design_sha256="3" * 64,
        qualification=qualification,
        qualification_sha256="4" * 64,
        code_commit=REG_COMMIT,
        registered_at_utc=REGISTERED_AT,
    )


def _start_line(registration, symbol: str) -> bytes:
    value = {
        "record_type": "BRIDGE_START",
        "protocol": registration["connector_protocol"],
        "bridge_session_id": registration["bridge_session_id_by_symbol"][symbol],
        "symbol": symbol,
        "server": registration["server"],
        "account_fingerprint": registration["account_fingerprint"],
        "account_mode": "DEMO",
        "bridge_start_time_msc": int(REGISTERED_AT.timestamp() * 1000),
    }
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")


def _tick_line(registration, symbol: str) -> bytes:
    value = {
        "record_type": "TICK",
        "protocol": registration["connector_protocol"],
        "bridge_session_id": registration["bridge_session_id_by_symbol"][symbol],
        "symbol": symbol,
        "server": registration["server"],
        "account_fingerprint": registration["account_fingerprint"],
        "source_time_msc": int(REGISTERED_AT.timestamp() * 1000) + 1,
        "bid": 1.10 if symbol != "USDJPY" else 150.0,
        "ask": 1.1002 if symbol != "USDJPY" else 150.02,
        "flags": 6,
    }
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")


def _tails(registration, root: Path):
    result = {}
    for symbol in registration["required_symbols"]:
        path = root / f"{symbol}.jsonl"
        path.write_bytes(
            _start_line(registration, symbol)
            + _tick_line(registration, symbol)
        )
        result[symbol] = Phase8BBridgeFileTail(
            path,
            expected_symbol=symbol,
        )
    return result


def _authorization(registration, root: Path):
    tails = _tails(registration, root)
    return build_phase8b_campaign_start_authorization(
        registration=registration,
        registration_sha256="5" * 64,
        bridge_tails=tails,
        code_commit=START_COMMIT,
        started_at_utc=STARTED_AT,
    )


class Phase8BCaptureFoundationTests(unittest.TestCase):
    def test_preflight_binds_exact_upstream_and_revalidates_fresh_tails(self) -> None:
        registration = _registration()
        with TemporaryDirectory() as auth_tmp, TemporaryDirectory() as preflight_tmp:
            authorization = _authorization(registration, Path(auth_tmp))
            fresh_tails = _tails(registration, Path(preflight_tmp))
            result = build_phase8b_capture_preflight(
                registration=registration,
                registration_sha256="5" * 64,
                authorization=authorization,
                authorization_sha256="6" * 64,
                bridge_tails=fresh_tails,
                code_commit=CAPTURE_COMMIT,
                prepared_at_utc=PREPARED_AT,
            )
            self.assertEqual(result["protocol"], PHASE8B_CAPTURE_PREFLIGHT_PROTOCOL)
            self.assertEqual(result["outcome"], PHASE8B_CAPTURE_FOUNDATION_READY)
            self.assertEqual(result["registration_sha256"], "5" * 64)
            self.assertEqual(result["start_authorization_sha256"], "6" * 64)
            self.assertEqual(
                result["start_authorization_fingerprint"],
                authorization["start_authorization_fingerprint"],
            )
            self.assertEqual(
                result["bridge_session_id_by_symbol"],
                registration["bridge_session_id_by_symbol"],
            )
            self.assertEqual(
                result["reader_start_semantics"],
                "TAIL_AT_EOF_NO_BACKFILL",
            )
            self.assertTrue(result["capture_runtime_ready"])
            self.assertFalse(result["live_shadow_segment_started"])
            self.assertFalse(result["acceptance_authorized"])
            self.assertFalse(result["promotion_authorized"])
            validate_phase8b_capture_preflight(result)
            self.assertTrue(
                all(tail.read_available() == () for tail in fresh_tails.values())
            )

    def test_preflight_rejects_registration_digest_mismatch(self) -> None:
        registration = _registration()
        with TemporaryDirectory() as auth_tmp, TemporaryDirectory() as fresh_tmp:
            authorization = _authorization(registration, Path(auth_tmp))
            with self.assertRaisesRegex(ValueError, "registration digest"):
                build_phase8b_capture_preflight(
                    registration=registration,
                    registration_sha256="9" * 64,
                    authorization=authorization,
                    authorization_sha256="6" * 64,
                    bridge_tails=_tails(registration, Path(fresh_tmp)),
                    code_commit=CAPTURE_COMMIT,
                    prepared_at_utc=PREPARED_AT,
                )

    def test_preflight_rejects_changed_current_bridge_session(self) -> None:
        registration = _registration()
        with TemporaryDirectory() as auth_tmp, TemporaryDirectory() as fresh_tmp:
            authorization = _authorization(registration, Path(auth_tmp))
            fresh_tails = _tails(registration, Path(fresh_tmp))
            symbol = registration["required_symbols"][0]
            start = fresh_tails[symbol].start_record
            replacement = type(start)(
                protocol=start.protocol,
                bridge_session_id="9" * 64,
                symbol=start.symbol,
                server=start.server,
                account_fingerprint=start.account_fingerprint,
                account_mode=start.account_mode,
                bridge_start_time_msc=start.bridge_start_time_msc,
            )

            class FakeTail:
                start_record = replacement

                def read_available(self):
                    return ()

            changed = dict(fresh_tails)
            changed[symbol] = FakeTail()
            with self.assertRaisesRegex(ValueError, "session"):
                build_phase8b_capture_preflight(
                    registration=registration,
                    registration_sha256="5" * 64,
                    authorization=authorization,
                    authorization_sha256="6" * 64,
                    bridge_tails=changed,
                    code_commit=CAPTURE_COMMIT,
                    prepared_at_utc=PREPARED_AT,
                )

    def test_preflight_write_is_exactly_once_and_tamper_evident(self) -> None:
        registration = _registration()
        with TemporaryDirectory() as auth_tmp, TemporaryDirectory() as fresh_tmp, TemporaryDirectory() as out_tmp:
            authorization = _authorization(registration, Path(auth_tmp))
            result = build_phase8b_capture_preflight(
                registration=registration,
                registration_sha256="5" * 64,
                authorization=authorization,
                authorization_sha256="6" * 64,
                bridge_tails=_tails(registration, Path(fresh_tmp)),
                code_commit=CAPTURE_COMMIT,
                prepared_at_utc=PREPARED_AT,
            )
            root = Path(out_tmp)
            manifest = write_phase8b_capture_preflight(result, root)
            self.assertEqual(
                hashlib.sha256(
                    (root / "capture-preflight.json").read_bytes()
                ).hexdigest(),
                manifest["artifacts"][0]["sha256"],
            )
            with self.assertRaises(FileExistsError):
                write_phase8b_capture_preflight(result, root)
            tampered = dict(result)
            tampered["server"] = "FPMarketsSC-Demo2"
            with self.assertRaisesRegex(ValueError, "fingerprint"):
                validate_phase8b_capture_preflight(tampered)

    def test_capture_record_envelope_is_deterministic_and_deduplicates_ticks(self) -> None:
        registration = _registration()
        with TemporaryDirectory() as auth_tmp, TemporaryDirectory() as fresh_tmp:
            authorization = _authorization(registration, Path(auth_tmp))
            fresh_tails = _tails(registration, Path(fresh_tmp))
            preflight = build_phase8b_capture_preflight(
                registration=registration,
                registration_sha256="5" * 64,
                authorization=authorization,
                authorization_sha256="6" * 64,
                bridge_tails=fresh_tails,
                code_commit=CAPTURE_COMMIT,
                prepared_at_utc=PREPARED_AT,
            )
            symbol = registration["required_symbols"][0]
            start = fresh_tails[symbol].start_record
            feed = Phase8BCaptureFeedEnvelope(
                preflight=preflight,
                start_record=start,
            )
            heartbeat = Phase8BBridgeHeartbeatRecord(
                protocol=start.protocol,
                bridge_session_id=start.bridge_session_id,
                symbol=symbol,
                server=start.server,
                account_fingerprint=start.account_fingerprint,
                bridge_emitted_time_msc=int(PREPARED_AT.timestamp() * 1000),
                last_tick_time_msc=None,
            )
            heartbeat_result = feed.accept(
                heartbeat,
                received_at_utc=PREPARED_AT,
                receive_monotonic_ns=10,
            )
            self.assertIsNotNone(heartbeat_result)
            heartbeat_envelope, heartbeat_quote = heartbeat_result
            self.assertIsNone(heartbeat_quote)
            self.assertEqual(
                heartbeat_envelope["protocol"],
                CAPTURE_RECORD_PROTOCOL,
            )
            validate_phase8b_capture_record_envelope(
                heartbeat_envelope,
                preflight=preflight,
            )

            tick = Phase8BBridgeTickRecord(
                protocol=start.protocol,
                bridge_session_id=start.bridge_session_id,
                symbol=symbol,
                server=start.server,
                account_fingerprint=start.account_fingerprint,
                source_time_msc=int(PREPARED_AT.timestamp() * 1000) + 1,
                bid=1.1000 if symbol != "USDJPY" else 150.0,
                ask=1.1002 if symbol != "USDJPY" else 150.02,
                flags=6,
            )
            tick_result = feed.accept(
                tick,
                received_at_utc=PREPARED_AT,
                receive_monotonic_ns=11,
            )
            self.assertIsNotNone(tick_result)
            tick_envelope, tick_quote = tick_result
            self.assertIsNotNone(tick_quote)
            self.assertEqual(tick_quote.symbol, symbol)
            validate_phase8b_capture_record_envelope(
                tick_envelope,
                preflight=preflight,
            )
            self.assertIsNone(
                feed.accept(
                    tick,
                    received_at_utc=PREPARED_AT,
                    receive_monotonic_ns=12,
                )
            )

            mutated = dict(tick_envelope)
            mutated["receive_monotonic_ns"] = 99
            with self.assertRaisesRegex(ValueError, "fingerprint"):
                validate_phase8b_capture_record_envelope(
                    mutated,
                    preflight=preflight,
                )

    def test_capture_feed_rejects_identity_change(self) -> None:
        registration = _registration()
        with TemporaryDirectory() as auth_tmp, TemporaryDirectory() as fresh_tmp:
            authorization = _authorization(registration, Path(auth_tmp))
            fresh_tails = _tails(registration, Path(fresh_tmp))
            preflight = build_phase8b_capture_preflight(
                registration=registration,
                registration_sha256="5" * 64,
                authorization=authorization,
                authorization_sha256="6" * 64,
                bridge_tails=fresh_tails,
                code_commit=CAPTURE_COMMIT,
                prepared_at_utc=PREPARED_AT,
            )
            symbol = registration["required_symbols"][0]
            start = fresh_tails[symbol].start_record
            feed = Phase8BCaptureFeedEnvelope(
                preflight=preflight,
                start_record=start,
            )
            changed = Phase8BBridgeHeartbeatRecord(
                protocol=start.protocol,
                bridge_session_id="9" * 64,
                symbol=symbol,
                server=start.server,
                account_fingerprint=start.account_fingerprint,
                bridge_emitted_time_msc=int(PREPARED_AT.timestamp() * 1000),
                last_tick_time_msc=None,
            )
            with self.assertRaises(Phase8BBridgeProtocolError):
                feed.accept(
                    changed,
                    received_at_utc=PREPARED_AT,
                    receive_monotonic_ns=10,
                )


if __name__ == "__main__":
    unittest.main()
