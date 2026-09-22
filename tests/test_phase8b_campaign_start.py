from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import hashlib
import json
import unittest

from fmp.phase8b.bridge import Phase8BBridgeFileTail
from fmp.phase8b.campaign_start import (
    PHASE8B_CAMPAIGN_START_AUTHORIZED,
    PHASE8B_CAMPAIGN_START_PROTOCOL,
    build_phase8b_campaign_start_authorization,
    validate_phase8b_campaign_start_authorization,
    write_phase8b_campaign_start_authorization,
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
STARTED_AT = datetime(2026, 9, 21, 23, 30, tzinfo=UTC)
ACCOUNT = "a" * 64
SERVER = "FPMarketsSC-Demo"
DESIGN_COMMIT = "d" * 40
QUAL_COMMIT = "e" * 40
REG_COMMIT = "f" * 40
START_COMMIT = "1" * 40


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
        champion_set_id="phase8a-exp016-start-test",
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


class Phase8BCampaignStartTests(unittest.TestCase):
    def test_start_authorization_revalidates_sessions_and_freezes_boundary(self) -> None:
        registration = _registration()
        with TemporaryDirectory() as tmp:
            tails = _tails(registration, Path(tmp))
            result = build_phase8b_campaign_start_authorization(
                registration=registration,
                registration_sha256="5" * 64,
                bridge_tails=tails,
                code_commit=START_COMMIT,
                started_at_utc=STARTED_AT,
            )
            self.assertEqual(
                result["protocol"],
                PHASE8B_CAMPAIGN_START_PROTOCOL,
            )
            self.assertEqual(
                result["outcome"],
                PHASE8B_CAMPAIGN_START_AUTHORIZED,
            )
            self.assertEqual(result["campaign_start_utc"], "2026-09-21T23:30:00Z")
            self.assertEqual(result["first_london_date"], "2026-09-22")
            self.assertEqual(
                result["bridge_session_id_by_symbol"],
                registration["bridge_session_id_by_symbol"],
            )
            self.assertEqual(
                result["reader_start_semantics"],
                "TAIL_AT_EOF_NO_BACKFILL",
            )
            self.assertTrue(result["campaign_start_authorized"])
            self.assertTrue(result["prospective_capture_authorized"])
            self.assertFalse(result["promotion_authorized"])
            self.assertFalse(result["demo_order_authorized"])
            self.assertFalse(result["live_order_authorized"])
            self.assertFalse(result["broker_mutation_authorized"])
            self.assertFalse(result["real_money_authorized"])
            self.assertFalse(result["phase9_authorized"])
            validate_phase8b_campaign_start_authorization(result)
            self.assertTrue(
                all(tail.read_available() == () for tail in tails.values())
            )

    def test_start_authorization_rejects_session_change_before_authorization(self) -> None:
        registration = _registration()
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            tails = _tails(registration, root)
            symbol = registration["required_symbols"][0]
            path = tails[symbol].path
            bad = dict(json.loads(_start_line(registration, symbol)))
            bad["bridge_session_id"] = "9" * 64
            path.write_bytes(
                (json.dumps(bad, separators=(",", ":")) + "\n").encode()
            )
            tails[symbol] = Phase8BBridgeFileTail(
                path,
                expected_symbol=symbol,
            )
            with self.assertRaisesRegex(ValueError, "session"):
                build_phase8b_campaign_start_authorization(
                    registration=registration,
                    registration_sha256="5" * 64,
                    bridge_tails=tails,
                    code_commit=START_COMMIT,
                    started_at_utc=STARTED_AT,
                )

    def test_start_authorization_rejects_wrong_account_or_server(self) -> None:
        registration = _registration()
        with TemporaryDirectory() as tmp:
            tails = _tails(registration, Path(tmp))
            symbol = registration["required_symbols"][0]
            start = tails[symbol].start_record
            replacement = type(start)(
                protocol=start.protocol,
                bridge_session_id=start.bridge_session_id,
                symbol=start.symbol,
                server=start.server,
                account_fingerprint="9" * 64,
                account_mode=start.account_mode,
                bridge_start_time_msc=start.bridge_start_time_msc,
            )

            class FakeTail:
                start_record = replacement

            tampered = dict(tails)
            tampered[symbol] = FakeTail()
            with self.assertRaisesRegex(ValueError, "account"):
                build_phase8b_campaign_start_authorization(
                    registration=registration,
                    registration_sha256="5" * 64,
                    bridge_tails=tampered,
                    code_commit=START_COMMIT,
                    started_at_utc=STARTED_AT,
                )

    def test_start_authorization_rejects_tampered_registration_and_non_utc_time(self) -> None:
        registration = _registration()
        tampered = dict(registration)
        tampered["server"] = "FPMarketsSC-Demo2"
        with TemporaryDirectory() as tmp:
            tails = _tails(registration, Path(tmp))
            with self.assertRaises(ValueError):
                build_phase8b_campaign_start_authorization(
                    registration=tampered,
                    registration_sha256="5" * 64,
                    bridge_tails=tails,
                    code_commit=START_COMMIT,
                    started_at_utc=STARTED_AT,
                )
            with self.assertRaisesRegex(ValueError, "UTC"):
                build_phase8b_campaign_start_authorization(
                    registration=registration,
                    registration_sha256="5" * 64,
                    bridge_tails=tails,
                    code_commit=START_COMMIT,
                    started_at_utc=STARTED_AT.replace(tzinfo=None),
                )

    def test_start_authorization_fingerprint_detects_mutation(self) -> None:
        registration = _registration()
        with TemporaryDirectory() as tmp:
            result = build_phase8b_campaign_start_authorization(
                registration=registration,
                registration_sha256="5" * 64,
                bridge_tails=_tails(registration, Path(tmp)),
                code_commit=START_COMMIT,
                started_at_utc=STARTED_AT,
            )
            tampered = dict(result)
            tampered["first_london_date"] = "2026-09-21"
            with self.assertRaisesRegex(ValueError, "fingerprint"):
                validate_phase8b_campaign_start_authorization(tampered)

    def test_start_authorization_write_is_exactly_once_and_deterministic(self) -> None:
        registration = _registration()
        with TemporaryDirectory() as tails_tmp, TemporaryDirectory() as campaign_tmp:
            result = build_phase8b_campaign_start_authorization(
                registration=registration,
                registration_sha256="5" * 64,
                bridge_tails=_tails(registration, Path(tails_tmp)),
                code_commit=START_COMMIT,
                started_at_utc=STARTED_AT,
            )
            root = Path(campaign_tmp)
            manifest = write_phase8b_campaign_start_authorization(
                result,
                root,
            )
            stored = json.loads(
                (root / "start-authorization.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(stored, result)
            self.assertEqual(
                manifest["protocol"],
                "fmp-phase8b-campaign-start-artifacts-v1",
            )
            with self.assertRaisesRegex(FileExistsError, "already exists"):
                write_phase8b_campaign_start_authorization(result, root)

            first = hashlib.sha256(
                (root / "start-authorization.json").read_bytes()
            ).hexdigest()
            self.assertEqual(
                first,
                manifest["artifacts"][0]["sha256"],
            )


if __name__ == "__main__":
    unittest.main()
