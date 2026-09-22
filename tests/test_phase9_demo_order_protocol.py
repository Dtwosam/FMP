from __future__ import annotations

import inspect
import json
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

from fmp.contracts import Direction, OrderIntent
from fmp.phase8b.design import (
    MT5_BRIDGE_PROTOCOL,
    MT5_PROVIDER,
    MT5_TRANSPORT,
)
from fmp.phase9.design import (
    PHASE9_DEMO_DESIGN_FROZEN,
    PHASE9_DEMO_DESIGN_PROTOCOL,
    PHASE9_EXPERIMENT_ID,
    PHASE9_MT5_ORDER_BRIDGE_PROTOCOL,
)
from fmp.phase9.protocol import (
    DemoExecutionLockedError,
    LockedDemoOrderAdapter,
    PHASE9_DEMO_DRY_RUN_PROTOCOL,
    PHASE9_DEMO_ORDER_PROTOCOL_READY,
    PHASE9_DEMO_ORDER_REQUEST_PROTOCOL,
    PHASE9_DEMO_RECONCILIATION_PROTOCOL,
    build_phase9_demo_order_protocol_foundation,
    build_phase9_demo_order_request,
    build_phase9_demo_reconciliation,
    validate_phase9_demo_dry_run,
    validate_phase9_demo_order_request,
    validate_phase9_demo_reconciliation,
    write_phase9_demo_dry_run,
)
from fmp.risk import RiskConfig


UTC = timezone.utc
COMMIT = "c" * 40
DECISION_TIME = datetime(2026, 9, 22, 17, 0, tzinfo=UTC)
EARLIEST = DECISION_TIME + timedelta(minutes=1)


def _digest(value: object) -> str:
    import hashlib

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
    fingerprints = ["1" * 64, "2" * 64]
    rows = [
        {
            "fingerprint": fingerprints[0],
            "identity_json": "{}",
            "family": "family-a",
            "symbol": "EURUSD",
            "timeframe": "5m",
            "code_commit": "a" * 40,
            "lifecycle": "SHADOW_VALIDATED",
        },
        {
            "fingerprint": fingerprints[1],
            "identity_json": "{}",
            "family": "family-b",
            "symbol": "USDJPY",
            "timeframe": "15m",
            "code_commit": "b" * 40,
            "lifecycle": "SHADOW_VALIDATED",
        },
    ]
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
        "champion_set_id": "phase9-dec056-test",
        "champion_set_fingerprint": "7" * 64,
        "strategy_fingerprints": fingerprints,
        "strategies": rows,
        "execution_path": {
            "provider": MT5_PROVIDER,
            "accepted_quote_transport": MT5_TRANSPORT,
            "accepted_quote_protocol": MT5_BRIDGE_PROTOCOL,
            "future_order_bridge_protocol": PHASE9_MT5_ORDER_BRIDGE_PROTOCOL,
            "account_mode": "DEMO",
            "account_fingerprint": "8" * 64,
            "server": "FPMarketsSC-Demo",
            "required_symbols": ["EURUSD", "USDJPY"],
            "symbol_mapping": {
                "EURUSD": "EURUSD",
                "USDJPY": "USDJPY",
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


def _intent(
    *,
    direction: Direction = Direction.LONG,
    units: int = 10_000,
    stop: float = 1.095,
    target: float | None = 1.11,
    reserved_risk: float = 100.0,
):
    return OrderIntent(
        decision_id="decision-001",
        symbol="EURUSD",
        direction=direction,
        units=units,
        reserved_risk_usd=reserved_risk,
        stop_price=stop,
        target_price=target,
        decision_timestamp_utc=DECISION_TIME,
        earliest_executable_timestamp_utc=EARLIEST,
    )


class Phase9DemoOrderProtocolTests(unittest.TestCase):
    def test_foundation_authorizes_protocol_only(self) -> None:
        result = build_phase9_demo_order_protocol_foundation(
            design=_design(),
            code_commit=COMMIT,
        )
        self.assertEqual(
            result["outcome"],
            PHASE9_DEMO_ORDER_PROTOCOL_READY,
        )
        self.assertTrue(result["demo_adapter_protocol_ready"])
        for field in (
            "demo_execution_authorized",
            "demo_order_authorized",
            "live_order_authorized",
            "broker_mutation_authorized",
            "real_money_authorized",
            "phase10_authorized",
        ):
            self.assertFalse(result[field])

    def test_request_is_deterministic_and_copies_exact_practice_identity(self) -> None:
        design = _design()
        first = build_phase9_demo_order_request(
            design=design,
            intent=_intent(),
            strategy_fingerprint="1" * 64,
            reference_entry_price=1.10,
        )
        second = build_phase9_demo_order_request(
            design=design,
            intent=_intent(),
            strategy_fingerprint="1" * 64,
            reference_entry_price=1.10,
        )
        self.assertEqual(first, second)
        self.assertEqual(first["protocol"], PHASE9_DEMO_ORDER_REQUEST_PROTOCOL)
        self.assertTrue(first["client_order_id"].startswith("fmp9-"))
        self.assertEqual(len(first["client_order_id"]), 29)
        self.assertEqual(first["provider"], MT5_PROVIDER)
        self.assertEqual(first["account_mode"], "DEMO")
        self.assertEqual(first["account_fingerprint"], "8" * 64)
        self.assertEqual(first["server"], "FPMarketsSC-Demo")
        self.assertEqual(first["broker_symbol"], "EURUSD")
        self.assertEqual(first["units"], 10_000)
        self.assertEqual(first["reserved_risk_usd"], 100.0)
        validate_phase9_demo_order_request(first, design=design)

        parameters = inspect.signature(
            build_phase9_demo_order_request
        ).parameters
        self.assertNotIn("account_fingerprint", parameters)
        self.assertNotIn("server", parameters)
        self.assertNotIn("provider", parameters)
        self.assertNotIn("units", parameters)

    def test_request_rejects_geometry_and_strategy_symbol_drift(self) -> None:
        design = _design()
        with self.assertRaisesRegex(ValueError, "LONG stop"):
            build_phase9_demo_order_request(
                design=design,
                intent=_intent(stop=1.101),
                strategy_fingerprint="1" * 64,
                reference_entry_price=1.10,
            )
        with self.assertRaisesRegex(ValueError, "strategy"):
            build_phase9_demo_order_request(
                design=design,
                intent=_intent(),
                strategy_fingerprint="2" * 64,
                reference_entry_price=1.10,
            )
        with self.assertRaisesRegex(ValueError, "reserved risk"):
            build_phase9_demo_order_request(
                design=design,
                intent=_intent(reserved_risk=0.0),
                strategy_fingerprint="1" * 64,
                reference_entry_price=1.10,
            )

    def test_locked_adapter_can_only_validate_dry_run_and_raise_on_submit(self) -> None:
        design = _design()
        request = build_phase9_demo_order_request(
            design=design,
            intent=_intent(),
            strategy_fingerprint="1" * 64,
            reference_entry_price=1.10,
        )
        adapter = LockedDemoOrderAdapter(design)
        self.assertFalse(hasattr(adapter, "transport"))
        self.assertFalse(hasattr(adapter, "broker"))
        adapter.validate_request(request)
        dry_run = adapter.dry_run(request)
        self.assertEqual(dry_run["protocol"], PHASE9_DEMO_DRY_RUN_PROTOCOL)
        self.assertFalse(dry_run["submission_attempted"])
        self.assertFalse(dry_run["broker_mutation_attempted"])
        self.assertFalse(dry_run["demo_order_submitted"])
        validate_phase9_demo_dry_run(dry_run)
        with self.assertRaises(DemoExecutionLockedError):
            adapter.submit(request)

    def test_dry_run_evidence_is_create_only(self) -> None:
        design = _design()
        request = build_phase9_demo_order_request(
            design=design,
            intent=_intent(),
            strategy_fingerprint="1" * 64,
            reference_entry_price=1.10,
        )
        dry_run = LockedDemoOrderAdapter(design).dry_run(request)
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = write_phase9_demo_dry_run(dry_run, root)
            self.assertTrue((root / "dry-run.json").is_file())
            self.assertTrue((root / "manifest.json").is_file())
            self.assertFalse(manifest["submission_attempted"])
            with self.assertRaises(FileExistsError):
                write_phase9_demo_dry_run(dry_run, root)

    def test_reconciliation_is_deterministic_and_flags_discrepancies(self) -> None:
        design = _design()
        request = build_phase9_demo_order_request(
            design=design,
            intent=_intent(),
            strategy_fingerprint="1" * 64,
            reference_entry_price=1.10,
        )
        client = request["client_order_id"]

        healthy = build_phase9_demo_reconciliation(
            design=design,
            local_requests=[request],
            broker_orders=[
                {
                    "broker_order_id": "order-1",
                    "client_order_id": client,
                    "protective_stop_id": "stop-1",
                }
            ],
            broker_positions=[
                {
                    "broker_position_id": "position-1",
                    "client_order_id": client,
                    "protective_stop_id": "stop-1",
                }
            ],
        )
        self.assertEqual(
            healthy["protocol"],
            PHASE9_DEMO_RECONCILIATION_PROTOCOL,
        )
        self.assertTrue(healthy["healthy"])
        self.assertFalse(healthy["broker_read_performed"])
        validate_phase9_demo_reconciliation(healthy)

        unhealthy = build_phase9_demo_reconciliation(
            design=design,
            local_requests=[request, request],
            broker_orders=[
                {
                    "broker_order_id": "order-unknown",
                    "client_order_id": "fmp9-unknown-client-id",
                    "protective_stop_id": "stop-x",
                },
                {
                    "broker_order_id": "order-known",
                    "client_order_id": client,
                    "protective_stop_id": None,
                },
            ],
            broker_positions=[
                {
                    "broker_position_id": "position-orphan",
                    "client_order_id": "fmp9-orphan-client-id",
                    "protective_stop_id": "stop-y",
                }
            ],
        )
        self.assertFalse(unhealthy["healthy"])
        self.assertEqual(
            unhealthy["duplicate_client_order_ids"],
            [client],
        )
        self.assertEqual(
            unhealthy["unknown_broker_order_ids"],
            ["order-unknown"],
        )
        self.assertEqual(
            unhealthy["orphan_broker_position_ids"],
            ["position-orphan"],
        )
        self.assertEqual(
            unhealthy["missing_expected_protective_stop_ids"],
            [client],
        )
        validate_phase9_demo_reconciliation(unhealthy)

        tampered = dict(unhealthy)
        tampered["duplicate_client_order_ids"] = []
        tampered.pop("reconciliation_fingerprint", None)
        tampered["reconciliation_fingerprint"] = _digest(tampered)
        with self.assertRaisesRegex(ValueError, "does not replay"):
            validate_phase9_demo_reconciliation(tampered)


if __name__ == "__main__":
    unittest.main()
