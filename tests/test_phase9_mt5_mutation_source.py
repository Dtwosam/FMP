from __future__ import annotations

import hashlib
import inspect
import json
import unittest
from collections import namedtuple
from datetime import datetime, timedelta, timezone

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
from fmp.phase9.mt5_mutation import (
    DEMO_EXECUTION_SOURCE_ARMED,
    GatedMT5DemoMutationAdapter,
    MetaTrader5PythonDemoBackend,
    PHASE9_MT5_MUTATION_SOURCE_READY,
    TRADE_RETCODE_DONE,
    build_phase9_mt5_mutation_source_foundation,
    build_phase9_mt5_send_result,
    validate_phase9_mt5_send_result,
)
from fmp.phase9.protocol import (
    DemoExecutionLockedError,
    build_phase9_demo_order_request,
)
from fmp.risk import RiskConfig


UTC = timezone.utc
NOW = datetime(2026, 9, 22, 18, 30, tzinfo=UTC)
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
        "phase8b_review_id": "2" * 64,
        "phase8b_acceptance_fingerprint": "3" * 64,
        "phase8b_shadow_validation_fingerprint": "4" * 64,
        "capture_preflight_fingerprint": "5" * 64,
        "champion_set_id": "phase9-dec058-test",
        "champion_set_fingerprint": "6" * 64,
        "strategy_fingerprints": ["1" * 64],
        "strategies": [
            {
                "fingerprint": "1" * 64,
                "identity_json": "{}",
                "family": "family-a",
                "symbol": "EURUSD",
                "timeframe": "5m",
                "code_commit": "a" * 40,
                "lifecycle": "SHADOW_VALIDATED",
            }
        ],
        "execution_path": {
            "provider": MT5_PROVIDER,
            "accepted_quote_transport": MT5_TRANSPORT,
            "accepted_quote_protocol": MT5_BRIDGE_PROTOCOL,
            "future_order_bridge_protocol": PHASE9_MT5_ORDER_BRIDGE_PROTOCOL,
            "account_mode": "DEMO",
            "account_fingerprint": hashlib.sha256(b"12345678").hexdigest(),
            "server": "FPMarketsSC-Demo",
            "required_symbols": ["EURUSD"],
            "symbol_mapping": {"EURUSD": "EURUSD"},
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


def _request():
    design = _design()
    intent = OrderIntent(
        decision_id="decision-058",
        symbol="EURUSD",
        direction=Direction.LONG,
        units=10_000,
        reserved_risk_usd=100.0,
        stop_price=1.095,
        target_price=1.11,
        decision_timestamp_utc=NOW,
        earliest_executable_timestamp_utc=NOW + timedelta(minutes=1),
    )
    return design, build_phase9_demo_order_request(
        design=design,
        intent=intent,
        strategy_fingerprint="1" * 64,
        reference_entry_price=1.10,
    )


class FakeMT5:
    ACCOUNT_TRADE_MODE_DEMO = 1
    SYMBOL_TRADE_EXECUTION_MARKET = 2
    SYMBOL_FILLING_FOK = 1
    SYMBOL_FILLING_IOC = 2
    SYMBOL_TRADE_MODE_DISABLED = 0

    TRADE_ACTION_DEAL = 10
    ORDER_TYPE_BUY = 20
    ORDER_TYPE_SELL = 21
    ORDER_TIME_GTC = 30
    ORDER_FILLING_RETURN = 40
    ORDER_FILLING_FOK = 41
    ORDER_FILLING_IOC = 42

    Account = namedtuple(
        "Account",
        "login trade_mode server trade_allowed trade_expert",
    )
    Symbol = namedtuple(
        "Symbol",
        (
            "trade_contract_size volume_min volume_step volume_max digits "
            "point trade_stops_level filling_mode trade_exemode trade_mode"
        ),
    )
    Tick = namedtuple("Tick", "time_msc bid ask")
    Check = namedtuple(
        "Check",
        "retcode balance equity profit margin margin_free margin_level comment",
    )
    Send = namedtuple(
        "Send",
        (
            "retcode deal order volume price bid ask comment request_id "
            "retcode_external"
        ),
    )
    BrokerOrder = namedtuple("BrokerOrder", "ticket comment sl")
    Position = namedtuple("Position", "ticket comment sl")

    def __init__(self):
        self.checked = []
        self.sent = []

    def account_info(self):
        return self.Account(
            12345678,
            self.ACCOUNT_TRADE_MODE_DEMO,
            "FPMarketsSC-Demo",
            True,
            True,
        )

    def symbol_info(self, symbol):
        assert symbol == "EURUSD"
        return self.Symbol(
            100_000.0,
            0.01,
            0.01,
            100.0,
            5,
            0.00001,
            20,
            self.SYMBOL_FILLING_FOK | self.SYMBOL_FILLING_IOC,
            self.SYMBOL_TRADE_EXECUTION_MARKET,
            4,
        )

    def symbol_info_tick(self, symbol):
        assert symbol == "EURUSD"
        return self.Tick(
            int(NOW.timestamp() * 1000),
            1.0998,
            1.1000,
        )

    def order_check(self, request):
        self.checked.append(dict(request))
        return self.Check(
            0,
            100000.0,
            100000.0,
            0.0,
            100.0,
            99900.0,
            1000.0,
            "Done",
        )

    def order_send(self, request):
        self.sent.append(dict(request))
        return self.Send(
            TRADE_RETCODE_DONE,
            111,
            222,
            0.1,
            1.1000,
            1.0998,
            1.1000,
            "Request executed",
            7,
            0,
        )

    def orders_get(self):
        return (
            self.BrokerOrder(333, "fmp9-order-a", 1.095),
        )

    def positions_get(self):
        return (
            self.Position(444, "fmp9-order-a", 1.095),
        )


class CountingBackend:
    def __init__(self):
        self.calls = []

    def __getattr__(self, name):
        def method(*args, **kwargs):
            self.calls.append(name)
            raise AssertionError(f"backend should not be called: {name}")

        return method


class Phase9MT5MutationSourceTests(unittest.TestCase):
    def test_source_foundation_keeps_execution_unarmed(self) -> None:
        self.assertIs(DEMO_EXECUTION_SOURCE_ARMED, False)
        result = build_phase9_mt5_mutation_source_foundation(
            design=_design(),
            code_commit=COMMIT,
        )
        self.assertEqual(
            result["outcome"],
            PHASE9_MT5_MUTATION_SOURCE_READY,
        )
        self.assertTrue(result["mt5_mutation_source_ready"])
        self.assertFalse(result["demo_execution_source_armed"])
        for field in (
            "demo_execution_authorized",
            "demo_order_authorized",
            "live_order_authorized",
            "broker_mutation_authorized",
            "real_money_authorized",
            "phase10_authorized",
        ):
            self.assertFalse(result[field])

    def test_backend_derives_existing_bridge_account_fingerprint(self) -> None:
        module = FakeMT5()
        backend = MetaTrader5PythonDemoBackend(module)
        account = backend.account_snapshot()
        self.assertEqual(account["account_mode"], "DEMO")
        self.assertEqual(
            account["account_fingerprint"],
            hashlib.sha256(b"12345678").hexdigest(),
        )
        self.assertEqual(account["server"], "FPMarketsSC-Demo")
        self.assertTrue(account["trade_allowed"])

        parameters = inspect.signature(
            MetaTrader5PythonDemoBackend
        ).parameters
        self.assertEqual(list(parameters), ["mt5_module"])

    def test_backend_resolves_market_execution_fill_and_constants(self) -> None:
        module = FakeMT5()
        backend = MetaTrader5PythonDemoBackend(module)
        symbol = backend.symbol_snapshot("EURUSD")
        self.assertEqual(symbol["filling_mode"], "FOK")

        symbolic = {
            "action": "TRADE_ACTION_DEAL",
            "symbol": "EURUSD",
            "volume": 0.1,
            "type": "ORDER_TYPE_BUY",
            "price": 1.1,
            "sl": 1.095,
            "tp": 1.11,
            "deviation": 0,
            "type_time": "ORDER_TIME_GTC",
            "type_filling": "ORDER_FILLING_FOK",
            "comment": "fmp9-test",
        }
        check = backend.order_check(symbolic)
        self.assertEqual(check["retcode"], 0)
        self.assertEqual(len(module.checked), 1)
        translated = module.checked[0]
        self.assertEqual(translated["action"], module.TRADE_ACTION_DEAL)
        self.assertEqual(translated["type"], module.ORDER_TYPE_BUY)
        self.assertEqual(translated["type_time"], module.ORDER_TIME_GTC)
        self.assertEqual(
            translated["type_filling"],
            module.ORDER_FILLING_FOK,
        )

        raw_send = backend.order_send(symbolic)
        self.assertEqual(raw_send["retcode"], TRADE_RETCODE_DONE)
        self.assertEqual(len(module.sent), 1)
        self.assertEqual(module.sent[0], translated)

    def test_broker_reads_normalize_protective_stop_presence(self) -> None:
        backend = MetaTrader5PythonDemoBackend(FakeMT5())
        orders = backend.broker_orders()
        positions = backend.broker_positions()
        self.assertEqual(orders[0]["broker_order_id"], "333")
        self.assertEqual(positions[0]["broker_position_id"], "444")
        self.assertTrue(
            str(orders[0]["protective_stop_id"]).startswith("sl:333:")
        )
        self.assertTrue(
            str(positions[0]["protective_stop_id"]).startswith("sl:444:")
        )

    def test_send_result_only_completes_on_done_and_full_volume(self) -> None:
        base = {
            "retcode": TRADE_RETCODE_DONE,
            "retcode_external": 0,
            "deal": 111,
            "order": 222,
            "volume": 0.1,
            "price": 1.1,
            "bid": 1.0998,
            "ask": 1.1,
            "comment": "Request executed",
            "request_id": 7,
        }
        result = build_phase9_mt5_send_result(
            request_fingerprint="1" * 64,
            order_check_request_fingerprint="2" * 64,
            order_check_fingerprint="3" * 64,
            expected_volume_lots=0.1,
            raw_result=base,
        )
        self.assertTrue(result["completed"])
        validate_phase9_mt5_send_result(result)

        partial = dict(base)
        partial["retcode"] = 10010
        partial["volume"] = 0.05
        result = build_phase9_mt5_send_result(
            request_fingerprint="1" * 64,
            order_check_request_fingerprint="2" * 64,
            order_check_fingerprint="3" * 64,
            expected_volume_lots=0.1,
            raw_result=partial,
        )
        self.assertFalse(result["completed"])
        self.assertFalse(result["full_volume_confirmed"])
        validate_phase9_mt5_send_result(result)

    def test_official_adapter_gate_precedes_every_backend_call(self) -> None:
        design, request = _request()
        backend = CountingBackend()
        adapter = GatedMT5DemoMutationAdapter(
            design=design,
            backend=backend,
        )
        with self.assertRaises(DemoExecutionLockedError):
            adapter.submit(request)
        self.assertEqual(backend.calls, [])


if __name__ == "__main__":
    unittest.main()
