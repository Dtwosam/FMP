from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import hashlib
import json
import unittest

from fmp.phase8b.design import build_phase8b_design
from fmp.phase8b.qualification import (
    FeedQualificationOutcome,
    FeedQualificationResult,
    summarize_phase8b_qualification,
)
from fmp.phase8b.registration import (
    PHASE8B_REGISTRATION_PROTOCOL,
    build_phase8b_registration,
    validate_phase8b_registration,
    write_phase8b_registration,
)
from fmp.portfolio.challenger_discovery import build_exp015_challengers
from fmp.portfolio.contracts import StrategyLifecycle, StrategyRecord
from fmp.portfolio.historical_inventory import build_phase4_baseline_inventory
from fmp.portfolio.registry import freeze_shadow_champion_set, transition_strategy


UTC = timezone.utc
NOW = datetime(2026, 9, 22, 14, 0, tzinfo=UTC)
ACCOUNT = "a" * 64
SERVER = "FPMarketsSC-Demo"
DESIGN_COMMIT = "d" * 40
QUAL_COMMIT = "e" * 40
REG_COMMIT = "f" * 40


def _acceptance():
    baseline = next(
        item for item in build_phase4_baseline_inventory()
        if item.lifecycle is StrategyLifecycle.HISTORICAL_QUALIFIED
    )
    source = next(
        item for item in build_exp015_challengers(code_commit="c" * 40)
        if item.strategy.symbol != baseline.strategy.symbol
    )
    challenger = StrategyRecord(
        strategy=source.strategy,
        lifecycle=StrategyLifecycle.HISTORICAL_QUALIFIED,
        evidence_id="EXP-20260922-015:FINAL_SHORTLIST",
    )
    prior = (baseline, challenger)
    after = tuple(
        transition_strategy(
            item,
            StrategyLifecycle.SHADOW_CANDIDATE,
            evidence_id="EXP-20260922-016:PHASE8A_ACCEPT_SHADOW_CANDIDATE",
        )
        for item in prior
    )
    champion = freeze_shadow_champion_set(
        after,
        champion_set_id="phase8a-exp016-registration-test",
    )
    prior_by_fp = {item.strategy.fingerprint: item for item in prior}
    rows = []
    for item in sorted(after, key=lambda x: x.strategy.fingerprint):
        old = prior_by_fp[item.strategy.fingerprint]
        rows.append({
            "fingerprint": item.strategy.fingerprint,
            "identity_json": item.strategy.identity_json,
            "family": item.strategy.family,
            "symbol": item.strategy.symbol,
            "timeframe": item.strategy.timeframe,
            "parameters_json": item.strategy.parameters_json,
            "code_commit": item.strategy.code_commit,
            "prior_lifecycle": old.lifecycle.value,
            "prior_evidence_id": old.evidence_id,
            "lifecycle": item.lifecycle.value,
            "evidence_id": item.evidence_id,
        })
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
            "strategy_fingerprints": [x.fingerprint for x in champion.strategies],
            "strategies": rows,
        },
    }


def _design():
    return build_phase8b_design(
        acceptance=_acceptance(),
        acceptance_sha256="1" * 64,
        code_commit=DESIGN_COMMIT,
    )


def _qualification(design):
    results = {}
    for index, symbol in enumerate(design["required_symbols"]):
        results[symbol] = FeedQualificationResult(
            symbol=symbol,
            outcome=FeedQualificationOutcome.PASS,
            account_fingerprint=ACCOUNT,
            bridge_session_id=f"{index + 1:064x}",
            server=SERVER,
            started_at_utc=NOW,
            ended_at_utc=NOW,
            elapsed_seconds=1.0,
            price_count=100,
            heartbeat_count=6,
            max_bridge_liveness_gap_seconds=1.0,
            max_market_liveness_gap_seconds=1.0,
            rejection_codes=(),
        )
    return summarize_phase8b_qualification(
        design=design,
        design_sha256="2" * 64,
        code_commit=QUAL_COMMIT,
        feed_results=results,
    )


class Phase8BRegistrationTests(unittest.TestCase):
    def test_registration_freezes_exact_design_and_qualified_identity(self) -> None:
        design = _design()
        qualification = _qualification(design)
        registration = build_phase8b_registration(
            design=design,
            design_sha256="2" * 64,
            qualification=qualification,
            qualification_sha256="3" * 64,
            code_commit=REG_COMMIT,
            registered_at_utc=NOW,
        )
        self.assertEqual(
            registration["protocol"],
            PHASE8B_REGISTRATION_PROTOCOL,
        )
        self.assertEqual(registration["design_fingerprint"], design["design_fingerprint"])
        self.assertEqual(registration["account_fingerprint"], ACCOUNT)
        self.assertEqual(registration["server"], SERVER)
        self.assertEqual(
            set(registration["bridge_session_id_by_symbol"]),
            set(design["required_symbols"]),
        )
        self.assertFalse(registration["campaign_start_authorized"])
        self.assertFalse(registration["promotion_authorized"])
        self.assertFalse(registration["demo_order_authorized"])
        self.assertFalse(registration["live_order_authorized"])
        validate_phase8b_registration(registration)

    def test_registration_rejects_nonpass_or_wrong_design_qualification(self) -> None:
        design = _design()
        qualification = _qualification(design)

        bad_outcome = dict(qualification)
        bad_outcome["outcome"] = "INCONCLUSIVE"
        bad_outcome["campaign_registration_authorized"] = False
        with self.assertRaisesRegex(ValueError, "qualified connector"):
            build_phase8b_registration(
                design=design,
                design_sha256="2" * 64,
                qualification=bad_outcome,
                qualification_sha256="3" * 64,
                code_commit=REG_COMMIT,
                registered_at_utc=NOW,
            )

        bad_design = dict(qualification)
        bad_design["design_sha256"] = "9" * 64
        with self.assertRaisesRegex(ValueError, "design digest"):
            build_phase8b_registration(
                design=design,
                design_sha256="2" * 64,
                qualification=bad_design,
                qualification_sha256="3" * 64,
                code_commit=REG_COMMIT,
                registered_at_utc=NOW,
            )

    def test_registration_fingerprint_detects_mutation(self) -> None:
        design = _design()
        registration = build_phase8b_registration(
            design=design,
            design_sha256="2" * 64,
            qualification=_qualification(design),
            qualification_sha256="3" * 64,
            code_commit=REG_COMMIT,
            registered_at_utc=NOW,
        )
        tampered = dict(registration)
        tampered["campaign_start_authorized"] = True
        with self.assertRaises(ValueError):
            validate_phase8b_registration(tampered)

    def test_registration_write_is_exactly_once_and_deterministic(self) -> None:
        design = _design()
        registration = build_phase8b_registration(
            design=design,
            design_sha256="2" * 64,
            qualification=_qualification(design),
            qualification_sha256="3" * 64,
            code_commit=REG_COMMIT,
            registered_at_utc=NOW,
        )
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = write_phase8b_registration(registration, root)
            stored = json.loads(
                (root / "registration.json").read_text(encoding="utf-8")
            )
            self.assertEqual(stored, registration)
            self.assertEqual(
                manifest["protocol"],
                "fmp-phase8b-campaign-registration-artifacts-v1",
            )
            with self.assertRaisesRegex(FileExistsError, "already exists"):
                write_phase8b_registration(registration, root)

        left = json.dumps(
            registration,
            sort_keys=True,
            separators=(",", ":"),
        ).encode()
        repeated = build_phase8b_registration(
            design=design,
            design_sha256="2" * 64,
            qualification=_qualification(design),
            qualification_sha256="3" * 64,
            code_commit=REG_COMMIT,
            registered_at_utc=NOW,
        )
        right = json.dumps(
            repeated,
            sort_keys=True,
            separators=(",", ":"),
        ).encode()
        self.assertEqual(hashlib.sha256(left).hexdigest(), hashlib.sha256(right).hexdigest())


if __name__ == "__main__":
    unittest.main()
