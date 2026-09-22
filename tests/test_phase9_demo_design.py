from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from fmp.phase8b.acceptance import (
    PHASE8B_ACCEPTANCE_ARTIFACT_PROTOCOL,
    PHASE8B_ACCEPTANCE_CONTRACT_DECISION,
    PHASE8B_ACCEPTANCE_EXPERIMENT_ID,
    PHASE8B_ACCEPTANCE_PROTOCOL,
    PHASE8B_PASS_ELIGIBLE_FOR_DEMO_DESIGN,
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
    PHASE8B_REVIEW_DECISION,
    PHASE8B_REVIEW_EXPERIMENT_ID,
    PHASE8B_REVIEW_MANIFEST_PROTOCOL,
    build_phase8b_shadow_validation,
)
from fmp.phase9.cli import build_parser
from fmp.phase9.design import (
    PHASE9_DEMO_DESIGN_FROZEN,
    PHASE9_DEMO_DESIGN_PROTOCOL,
    PHASE9_MT5_ORDER_BRIDGE_PROTOCOL,
    build_phase9_demo_design,
    build_phase9_demo_design_from_campaign,
    validate_phase9_demo_design,
    write_phase9_demo_design,
)
from fmp.portfolio.contracts import ChampionSet, PHASE8A_EXPERIMENT_ID
from fmp.portfolio.historical_inventory import build_phase4_baseline_inventory
from fmp.risk import RiskConfig


COMMIT = "c" * 40
REVIEW_ID = "9" * 64


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
    if len(chosen) != 2:
        raise AssertionError("fixture requires two distinct symbols")
    strategies = tuple(sorted(chosen, key=lambda item: item.fingerprint))
    champion = ChampionSet(
        champion_set_id="phase9-dec055-test",
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
        "bridge_session_id_by_symbol": {
            symbol: f"{index + 1:064x}"
            for index, symbol in enumerate(required_symbols)
        },
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


def _acceptance(preflight):
    payload = {
        "protocol": PHASE8B_ACCEPTANCE_PROTOCOL,
        "experiment_id": PHASE8B_ACCEPTANCE_EXPERIMENT_ID,
        "contract_decision": PHASE8B_ACCEPTANCE_CONTRACT_DECISION,
        "acceptance_code_commit": "b" * 40,
        "campaign_evidence_fingerprint": "5" * 64,
        "spread_reference_fingerprint": "6" * 64,
        "capture_preflight_fingerprint": preflight[
            "capture_preflight_fingerprint"
        ],
        "segment_fingerprint": "7" * 64,
        "replay_fingerprint": "8" * 64,
        "champion_set_fingerprint": preflight[
            "champion_set_fingerprint"
        ],
        "strategy_fingerprints": list(preflight["strategy_fingerprints"]),
        "required_symbols": list(preflight["required_symbols"]),
        "outcome": PHASE8B_PASS_ELIGIBLE_FOR_DEMO_DESIGN,
        "minimum_evidence": {},
        "operational_gate": {},
        "spread_gate": {},
        "financial_gate": {},
        "shadow_validation_authorized": True,
        "lifecycle_transition_authorized": True,
        "lifecycle_transitions": [
            {
                "strategy_fingerprint": fingerprint,
                "from": "SHADOW_CANDIDATE",
                "to": "SHADOW_VALIDATED",
            }
            for fingerprint in preflight["strategy_fingerprints"]
        ],
        "demo_design_eligible": True,
        "demo_order_authorized": False,
        "live_order_authorized": False,
        "broker_mutation_authorized": False,
        "real_money_authorized": False,
        "phase9_execution_authorized": False,
    }
    return payload | {"acceptance_fingerprint": _digest(payload)}


def _review_inputs():
    preflight = _preflight()
    acceptance = _acceptance(preflight)
    shadow = build_phase8b_shadow_validation(
        preflight=preflight,
        acceptance=acceptance,
        review_id=REVIEW_ID,
    )
    manifest = {
        "protocol": PHASE8B_REVIEW_MANIFEST_PROTOCOL,
        "experiment_id": PHASE8B_REVIEW_EXPERIMENT_ID,
        "decision": PHASE8B_REVIEW_DECISION,
        "review_id": REVIEW_ID,
        "closure_id": "d" * 64,
        "outcome": PHASE8B_PASS_ELIGIBLE_FOR_DEMO_DESIGN,
        "acceptance_fingerprint": acceptance["acceptance_fingerprint"],
        "spread_reference_fingerprint": acceptance[
            "spread_reference_fingerprint"
        ],
        "shadow_validation_fingerprint": shadow[
            "shadow_validation_fingerprint"
        ],
        "terminal": True,
        "capture_may_continue": False,
        "demo_order_authorized": False,
        "live_order_authorized": False,
        "broker_mutation_authorized": False,
        "real_money_authorized": False,
        "phase9_execution_authorized": False,
        "artifacts": [],
        "acceptance_manifest_protocol": PHASE8B_ACCEPTANCE_ARTIFACT_PROTOCOL,
    }
    terminal_payload = {
        "protocol": PHASE8B_CAMPAIGN_TERMINAL_PROTOCOL,
        "experiment_id": PHASE8B_REVIEW_EXPERIMENT_ID,
        "decision": PHASE8B_REVIEW_DECISION,
        "review_id": REVIEW_ID,
        "acceptance_fingerprint": acceptance["acceptance_fingerprint"],
        "outcome": PHASE8B_PASS_ELIGIBLE_FOR_DEMO_DESIGN,
        "champion_set_fingerprint": preflight[
            "champion_set_fingerprint"
        ],
        "terminal": True,
        "demo_design_eligible": True,
        "demo_order_authorized": False,
        "live_order_authorized": False,
        "broker_mutation_authorized": False,
        "real_money_authorized": False,
        "phase9_execution_authorized": False,
    }
    terminal = terminal_payload | {
        "campaign_terminal_fingerprint": _digest(terminal_payload)
    }
    return preflight, acceptance, shadow, manifest, terminal


class Phase9DemoDesignTests(unittest.TestCase):
    def test_design_preserves_phase8b_identity_and_phase3_risk(self) -> None:
        preflight, acceptance, shadow, manifest, terminal = _review_inputs()
        result = build_phase9_demo_design(
            preflight=preflight,
            review_id=REVIEW_ID,
            review_manifest=manifest,
            acceptance=acceptance,
            shadow_validation=shadow,
            terminal=terminal,
            code_commit=COMMIT,
        )
        self.assertEqual(result["protocol"], PHASE9_DEMO_DESIGN_PROTOCOL)
        self.assertEqual(result["outcome"], PHASE9_DEMO_DESIGN_FROZEN)
        self.assertEqual(
            result["champion_set_fingerprint"],
            preflight["champion_set_fingerprint"],
        )
        self.assertEqual(
            result["execution_path"]["account_fingerprint"],
            preflight["account_fingerprint"],
        )
        self.assertEqual(
            result["execution_path"]["server"],
            preflight["server"],
        )
        self.assertEqual(
            result["execution_path"]["future_order_bridge_protocol"],
            PHASE9_MT5_ORDER_BRIDGE_PROTOCOL,
        )
        self.assertEqual(result["risk_config"], RiskConfig().to_config())
        self.assertTrue(result["demo_adapter_source_authorized"])
        self.assertFalse(result["demo_execution_authorized"])
        self.assertFalse(result["demo_order_authorized"])
        self.assertFalse(result["broker_mutation_authorized"])
        self.assertFalse(result["real_money_authorized"])
        self.assertFalse(result["phase10_authorized"])
        validate_phase9_demo_design(result)

    def test_nonpass_or_tampered_identity_fails_closed(self) -> None:
        preflight, acceptance, shadow, manifest, terminal = _review_inputs()
        tampered = dict(acceptance)
        tampered["outcome"] = "PHASE8B_NEED_MORE_DATA"
        tampered["shadow_validation_authorized"] = False
        tampered["lifecycle_transition_authorized"] = False
        tampered["lifecycle_transitions"] = []
        tampered["demo_design_eligible"] = False
        payload = dict(tampered)
        payload.pop("acceptance_fingerprint", None)
        tampered["acceptance_fingerprint"] = _digest(payload)
        with self.assertRaisesRegex(ValueError, "PASS|eligible"):
            build_phase9_demo_design(
                preflight=preflight,
                review_id=REVIEW_ID,
                review_manifest=manifest,
                acceptance=tampered,
                shadow_validation=shadow,
                terminal=terminal,
                code_commit=COMMIT,
            )

        changed = dict(preflight)
        changed["server"] = "FPMarketsSC-Demo2"
        payload = dict(changed)
        payload.pop("capture_preflight_fingerprint", None)
        changed["capture_preflight_fingerprint"] = _digest(payload)
        with self.assertRaisesRegex(ValueError, "identity|preflight"):
            build_phase9_demo_design(
                preflight=changed,
                review_id=REVIEW_ID,
                review_manifest=manifest,
                acceptance=acceptance,
                shadow_validation=shadow,
                terminal=terminal,
                code_commit=COMMIT,
            )

    def test_design_tamper_and_write_are_fail_closed(self) -> None:
        preflight, acceptance, shadow, manifest, terminal = _review_inputs()
        result = build_phase9_demo_design(
            preflight=preflight,
            review_id=REVIEW_ID,
            review_manifest=manifest,
            acceptance=acceptance,
            shadow_validation=shadow,
            terminal=terminal,
            code_commit=COMMIT,
        )
        tampered = dict(result)
        tampered["demo_execution_authorized"] = True
        with self.assertRaises(ValueError):
            validate_phase9_demo_design(tampered)

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_phase9_demo_design(result, root)
            self.assertTrue((root / "design.json").is_file())
            self.assertTrue((root / "manifest.json").is_file())
            with self.assertRaises(FileExistsError):
                write_phase9_demo_design(result, root)

    def test_campaign_loader_requires_exact_pass_artifacts(self) -> None:
        preflight, acceptance, shadow, manifest, terminal = _review_inputs()
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            review_dir = root / "reviews" / REVIEW_ID
            (review_dir / "acceptance").mkdir(parents=True)
            (root / "capture-preflight.json").write_bytes(_stable(preflight))
            acceptance_bytes = _stable(acceptance)
            shadow_bytes = _stable(shadow)
            bound_manifest = dict(manifest)
            bound_manifest["artifacts"] = [
                {
                    "path": "acceptance/acceptance.json",
                    "sha256": hashlib.sha256(acceptance_bytes).hexdigest(),
                },
                {
                    "path": "shadow-validation.json",
                    "sha256": hashlib.sha256(shadow_bytes).hexdigest(),
                },
            ]
            (review_dir / "manifest.json").write_bytes(_stable(bound_manifest))
            (review_dir / "acceptance" / "acceptance.json").write_bytes(
                acceptance_bytes
            )
            (review_dir / "shadow-validation.json").write_bytes(shadow_bytes)
            (root / "campaign-terminal.json").write_bytes(_stable(terminal))
            result = build_phase9_demo_design_from_campaign(
                campaign_dir=root,
                review_id=REVIEW_ID,
                code_commit=COMMIT,
            )
            self.assertEqual(
                result["phase8b_review_id"],
                REVIEW_ID,
            )

    def test_phase9_cli_exposes_design_only(self) -> None:
        parser = build_parser()
        self.assertEqual(
            parser.parse_args(
                [
                    "design-demo",
                    "--campaign-dir",
                    "campaign",
                    "--review-id",
                    REVIEW_ID,
                ]
            ).command,
            "design-demo",
        )
        for forbidden in ("run-demo", "order", "trade", "run", "start"):
            with self.subTest(command=forbidden):
                with self.assertRaises(SystemExit):
                    parser.parse_args([forbidden])


if __name__ == "__main__":
    unittest.main()
