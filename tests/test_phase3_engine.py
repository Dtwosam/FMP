from __future__ import annotations

import unittest
from unittest import mock
from dataclasses import replace
from datetime import datetime, timedelta, timezone

from fmp.backtest.costs import ZeroCommission, ZeroFinancing
from fmp.backtest.engine import (
    DECLARED_EARLIEST_BAR,
    NEXT_SUPPLIED_BAR,
    BacktestConfig,
    _run_identity,
    run_backtest,
)
from fmp.contracts import Decision, Direction, ExitReason, QuoteBar, RejectionCode, ScheduledExit
from fmp.risk import RiskConfig


DAY = datetime(2026, 9, 14, 0, 0, tzinfo=timezone.utc)


def eurusd_bar(
    minute: int,
    *,
    bid_open: float = 1.1000,
    bid_high: float = 1.1008,
    bid_low: float = 1.0995,
    bid_close: float = 1.1003,
    ask_open: float = 1.1002,
    ask_high: float = 1.1010,
    ask_low: float = 1.0997,
    ask_close: float = 1.1005,
    day: datetime = DAY,
) -> QuoteBar:
    return QuoteBar(
        timestamp_utc=day + timedelta(minutes=minute),
        symbol="EURUSD",
        bid_open=bid_open,
        bid_high=bid_high,
        bid_low=bid_low,
        bid_close=bid_close,
        ask_open=ask_open,
        ask_high=ask_high,
        ask_low=ask_low,
        ask_close=ask_close,
    )


def gbpusd_bar(minute: int, *, target_hit: bool = False) -> QuoteBar:
    high = 1.3025 if target_hit else 1.3010
    return QuoteBar(
        timestamp_utc=DAY + timedelta(minutes=minute),
        symbol="GBPUSD",
        bid_open=1.3000,
        bid_high=high,
        bid_low=1.2995,
        bid_close=1.3004,
        ask_open=1.3002,
        ask_high=high + 0.0002,
        ask_low=1.2997,
        ask_close=1.3006,
    )


def usdjpy_bar(minute: int) -> QuoteBar:
    return QuoteBar(
        timestamp_utc=DAY + timedelta(minutes=minute),
        symbol="USDJPY",
        bid_open=150.00,
        bid_high=150.08,
        bid_low=149.95,
        bid_close=150.03,
        ask_open=150.02,
        ask_high=150.10,
        ask_low=149.97,
        ask_close=150.05,
    )


def long_decision(
    decision_id: str,
    *,
    symbol: str = "EURUSD",
    decision_minute: int,
    executable_minute: int,
    requested_risk_fraction: float | None = None,
    stop_price: float | None = None,
    target_price: float | None = None,
    day: datetime = DAY,
) -> Decision:
    defaults = {
        "EURUSD": (1.0992, None),
        "GBPUSD": (1.2992, None),
        "USDJPY": (149.90, None),
    }
    default_stop, default_target = defaults[symbol]
    return Decision(
        decision_id=decision_id,
        symbol=symbol,
        decision_timestamp_utc=day + timedelta(minutes=decision_minute),
        direction=Direction.LONG,
        earliest_executable_timestamp_utc=day + timedelta(minutes=executable_minute),
        requested_risk_fraction=requested_risk_fraction,
        stop_price=default_stop if stop_price is None else stop_price,
        target_price=default_target if target_price is None else target_price,
    )


def config(
    *,
    risk_config: RiskConfig | None = None,
    execution_timing_mode: str = NEXT_SUPPLIED_BAR,
) -> BacktestConfig:
    return BacktestConfig(
        starting_equity_usd=10_000.0,
        slippage_pips=0.0,
        risk_config=risk_config or RiskConfig(),
        commission_model=ZeroCommission(),
        financing_model=ZeroFinancing(),
        processed_data_manifest_id="phase2-manifest-sha",
        schema_version="fmp-canonical-1m-v1",
        timeframe="1m",
        requested_start_utc=DAY,
        requested_end_utc=DAY + timedelta(days=1),
        code_commit="engine-test-commit",
        decision_config={"fixture": "phase3-engine-tests"},
        execution_timing_mode=execution_timing_mode,
    )


class Phase3EngineTests(unittest.TestCase):
    def test_signal_cannot_fill_on_decision_bar_and_fills_next_bar(self) -> None:
        bars = [eurusd_bar(0), eurusd_bar(1), eurusd_bar(2)]
        decision = long_decision("D-1", decision_minute=0, executable_minute=1)
        run = run_backtest(bars=bars, decisions=[decision], config=config())
        self.assertEqual(len(run.trades), 1)
        self.assertEqual(run.trades[0].entry_timestamp_utc, DAY + timedelta(minutes=1))
        self.assertNotEqual(run.trades[0].entry_timestamp_utc, decision.decision_timestamp_utc)

    def test_declared_execution_later_than_first_next_bar_is_timing_rejection(self) -> None:
        bars = [eurusd_bar(0), eurusd_bar(1), eurusd_bar(2)]
        decision = long_decision("D-LATE", decision_minute=0, executable_minute=2)
        run = run_backtest(bars=bars, decisions=[decision], config=config())
        self.assertEqual(run.trades, ())
        self.assertEqual(len(run.rejections), 1)
        self.assertEqual(run.rejections[0].code, RejectionCode.TIMING_CONTRACT)


    def test_declared_earliest_mode_can_execute_after_intervening_1m_bars(self) -> None:
        bars = [eurusd_bar(0), eurusd_bar(1), eurusd_bar(2), eurusd_bar(3)]
        decision = long_decision("D-DECLARED", decision_minute=0, executable_minute=3)
        run = run_backtest(
            bars=bars,
            decisions=[decision],
            config=config(execution_timing_mode=DECLARED_EARLIEST_BAR),
        )
        self.assertEqual(len(run.trades), 1)
        self.assertEqual(
            run.trades[0].entry_timestamp_utc,
            DAY + timedelta(minutes=3),
        )
        self.assertEqual(
            run.run_identity["execution_timing_mode"],
            DECLARED_EARLIEST_BAR,
        )

    def test_declared_earliest_mode_rejects_missing_exact_execution_bar(self) -> None:
        bars = [eurusd_bar(0), eurusd_bar(1), eurusd_bar(3)]
        decision = long_decision("D-MISSING", decision_minute=0, executable_minute=2)
        run = run_backtest(
            bars=bars,
            decisions=[decision],
            config=config(execution_timing_mode=DECLARED_EARLIEST_BAR),
        )
        self.assertEqual(run.trades, ())
        self.assertEqual(len(run.rejections), 1)
        self.assertEqual(run.rejections[0].code, RejectionCode.TIMING_CONTRACT)

    def test_backtest_config_rejects_boolean_or_non_numeric_equity(self):
        for value in (True, False, "10000", None, 10 ** 400):
            with self.subTest(value=repr(value)):
                with self.assertRaisesRegex(ValueError, "equity|finite"):
                    replace(config(), starting_equity_usd=value)

    def test_backtest_config_rejects_boolean_or_non_numeric_slippage(self):
        for value in (True, False, "1.0", None, 10 ** 400):
            with self.subTest(value=repr(value)):
                with self.assertRaisesRegex(ValueError, "slippage|finite"):
                    replace(config(), slippage_pips=value)

    def test_backtest_config_keeps_valid_integer_and_float_scalars(self):
        for equity, pips in ((10000, 0), (10000.0, 0.0),
                             (12500.5, 0.5)):
            with self.subTest(equity=equity, pips=pips):
                candidate = replace(
                    config(), starting_equity_usd=equity,
                    slippage_pips=pips,
                )
                self.assertEqual(candidate.starting_equity_usd, equity)
                self.assertEqual(candidate.slippage_pips, pips)

    def test_backtest_config_rejects_unknown_execution_timing_mode(self) -> None:
        with self.assertRaises(ValueError):
            config(execution_timing_mode="LOOKAHEAD")

    def test_run_identity_rejects_untyped_or_blank_metadata(self):
        fields = (
            "processed_data_manifest_id", "schema_version",
            "timeframe", "code_commit",
        )
        for field in fields:
            for value in (None, [], {}, 42, "   "):
                with self.subTest(field=field, value=repr(value)):
                    with self.assertRaisesRegex(ValueError, field):
                        replace(config(), **{field: value})

    def test_run_identity_rejects_metadata_control_characters(self):
        for field in (
            "processed_data_manifest_id", "schema_version",
            "timeframe", "code_commit",
        ):
            for char in (chr(0), chr(9), chr(10), chr(13), chr(27), chr(127)):
                with self.subTest(field=field, character=ord(char)):
                    with self.assertRaisesRegex(ValueError, "control"):
                        replace(config(), **{field: "value" + char})

    def test_engine_config_rejects_unhashable_or_nonstring_timing_mode(self):
        for mode in ([], {}, None, True, 1):
            with self.subTest(mode=repr(mode)):
                with self.assertRaisesRegex(ValueError, "execution_timing_mode"):
                    replace(config(), execution_timing_mode=mode)

    def test_engine_config_preserves_normal_identity_strings(self):
        instance = replace(
            config(),
            processed_data_manifest_id="synthetic-only-manifest",
            schema_version="fmp-canonical-1m-v1",
            timeframe="1m",
            code_commit="reviewed-synthetic-test-hash",
        )
        self.assertEqual(instance.timeframe, "1m")
        self.assertEqual(instance.code_commit, "reviewed-synthetic-test-hash")

    def test_backtest_time_window_rejects_nondatetime_inputs(self):
        for field in ("requested_start_utc", "requested_end_utc"):
            for value in (None, "2026-09-14T00:00:00Z", 42, {},
                          DAY.date()):
                with self.subTest(field=field, value=repr(value)):
                    with self.assertRaisesRegex(ValueError, field):
                        replace(config(), **{field: value})

    def test_backtest_time_window_rejects_naive_or_non_utc_datetimes(self):
        for field in ("requested_start_utc", "requested_end_utc"):
            for value in (
                datetime(2026, 9, 14),
                datetime(
                    2026, 9, 14,
                    tzinfo=timezone(timedelta(hours=1))
                ),
            ):
                with self.subTest(field=field, value=repr(value)):
                    with self.assertRaisesRegex(ValueError, "UTC"):
                        replace(config(), **{field: value})

    def test_backtest_time_window_allows_valid_utc_interval(self):
        value = replace(
            config(), requested_start_utc=DAY,
            requested_end_utc=DAY + timedelta(hours=2)
        )
        self.assertEqual(value.requested_start_utc, DAY)
        self.assertGreater(value.requested_end_utc,
                           value.requested_start_utc)

    def test_backtest_config_requires_real_risk_contract(self):
        for value in (None, [], {}, "RiskConfig", True):
            with self.subTest(value=repr(value)):
                with self.assertRaisesRegex(ValueError, "risk_config"):
                    replace(config(), risk_config=value)

    def test_backtest_config_rejects_nondictionary_decision_metadata(self):
        for value in (None, 42, [], True, "not-a-map"):
            with self.subTest(value=repr(value)):
                with self.assertRaisesRegex(ValueError, "decision_config"):
                    replace(config(), decision_config=value)

    def test_backtest_config_rejects_malformed_decision_metadata_keys(self):
        for key in (None, 12, "", "bad" + chr(10), "bad" + chr(27)):
            with self.subTest(key=repr(key)):
                with self.assertRaisesRegex(ValueError, "decision_config keys"):
                    replace(config(), decision_config={key: "synthetic"})

    def test_backtest_config_preserves_synthetic_valid_decision_metadata(self):
        settings = replace(
            config(), decision_config={
                "synthetic_fixture": "no_real_market_data",
                "cost_scenario": 3
            }
        )
        self.assertEqual(
            settings.decision_config["synthetic_fixture"],
            "no_real_market_data"
        )

    def test_backtest_config_rejects_missing_commission_model_interface(self):
        for bad in (None, {}, object(), "zero-commission"):
            with self.subTest(model=repr(bad)):
                with self.assertRaisesRegex(ValueError, "commission_model"):
                    replace(config(), commission_model=bad)

    def test_backtest_config_rejects_missing_financing_model_interface(self):
        for bad in (None, [], object(), "zero-financing"):
            with self.subTest(model=repr(bad)):
                with self.assertRaisesRegex(ValueError, "financing_model"):
                    replace(config(), financing_model=bad)

    def test_backtest_config_rejects_partial_cost_model_objects(self):
        class MissingConfig:
            def cost_usd(self, **kwargs):
                return 0.0

        class MissingCost:
            def to_config(self):
                return {"model": "test"}

        for field in ("commission_model", "financing_model"):
            for model in (MissingConfig(), MissingCost()):
                with self.subTest(field=field, model=type(model).__name__):
                    with self.assertRaisesRegex(ValueError, field):
                        replace(config(), **{field: model})

    def test_backtest_config_preserves_valid_zero_cost_model_protocols(self):
        candidate = config()
        self.assertEqual(candidate.commission_model.to_config(),
                         {"model": "zero_commission"})
        self.assertEqual(candidate.financing_model.to_config(),
                         {"model": "zero_financing"})

    def test_backtest_config_decision_metadata_is_caller_independent(self):
        original = {"scenario": "invented", "cost_case": 1}
        instance = replace(config(), decision_config=original)
        original["scenario"] = "altered-after-construction"
        original["added"] = True
        self.assertEqual(instance.decision_config["scenario"], "invented")
        self.assertNotIn("added", instance.decision_config)

    def test_backtest_config_decision_metadata_is_top_level_read_only(self):
        instance = replace(config(), decision_config={"scenario": "invented"})
        with self.assertRaises(TypeError):
            instance.decision_config["scenario"] = "forged"
        self.assertEqual(instance.decision_config["scenario"], "invented")

    def test_backtest_run_identity_uses_frozen_decision_snapshot(self):
        original = {"source": "SYNTHETIC-ONLY"}
        instance = replace(config(), decision_config=original)
        original["source"] = "MUTATED-BY-CALLER"
        identity = _run_identity(instance, ())
        self.assertEqual(identity["decision_config"], {"source": "SYNTHETIC-ONLY"})
        self.assertEqual(dict(instance.decision_config), {"source": "SYNTHETIC-ONLY"})

    def test_backtest_config_does_not_alias_nested_caller_metadata(self):
        nested = {"thresholds": [1, 2], "labels": {"scope": "SYNTHETIC"}}
        original = {"scenario": nested}
        instance = replace(config(), decision_config=original)
        nested["thresholds"].append(999)
        nested["labels"]["scope"] = "FORGED-AFTER-CREATION"
        original["scenario"] = {"thresholds": [-1]}
        self.assertEqual(
            _run_identity(instance, ())["decision_config"]["scenario"],
            {"thresholds": [1, 2], "labels": {"scope": "SYNTHETIC"}},
        )

    def test_backtest_identity_keeps_original_nested_caller_values(self):
        provided = {"cost_cases": [0, {"commission": 30.0}]}
        instance = replace(config(), decision_config=provided)
        provided["cost_cases"][1]["commission"] = -30.0
        identity = _run_identity(instance, ())
        self.assertEqual(
            identity["decision_config"],
            {"cost_cases": [0, {"commission": 30.0}]},
        )

    def test_deepcopy_unsafe_metadata_raises_controlled_error(self):
        class Uncopyable:
            def __deepcopy__(self, memo):
                raise TypeError("cannot copy unsafe mutable identity")

        with self.assertRaisesRegex(ValueError, "JSON-compatible"):
            replace(config(), decision_config={"unsafe": Uncopyable()})

    def test_run_identity_nested_values_do_not_mutate_source_config(self):
        conf = replace(
            config(), decision_config={"scenarios": [{"cost": 30.0}]}
        )
        report = _run_identity(conf, ())
        report["decision_config"]["scenarios"][0]["cost"] = -99.0
        self.assertEqual(
            conf.decision_config["scenarios"][0]["cost"], 30.0
        )
        self.assertEqual(
            _run_identity(conf, ())["decision_config"]["scenarios"][0]["cost"],
            30.0,
        )

    def test_two_run_identity_snapshots_do_not_share_nested_lists(self):
        conf = replace(
            config(), decision_config={"trials": ["synthetic", "offline"]}
        )
        first = _run_identity(conf, ())
        second = _run_identity(conf, ())
        first["decision_config"]["trials"].append("forged")
        self.assertEqual(
            second["decision_config"]["trials"], ["synthetic", "offline"]
        )
        self.assertEqual(
            conf.decision_config["trials"], ("synthetic", "offline")
        )

    def test_recursively_frozen_metadata_rejects_nested_mutations(self):
        c = replace(config(), decision_config={
            "nested": {"trials": [1, {"commission": 30.0}]}
        })
        with self.assertRaises(TypeError):
            c.decision_config["nested"]["trials"] = [999]
        with self.assertRaises(AttributeError):
            c.decision_config["nested"]["trials"].append(999)
        with self.assertRaises(TypeError):
            c.decision_config["nested"]["trials"][1]["commission"] = -30.0
        self.assertEqual(
            _run_identity(c, ())["decision_config"],
            {"nested": {"trials": [1, {"commission": 30.0}]}},
        )

    def test_decision_metadata_denies_nonfinite_cycles_and_opaque_values(self):
        cyclic = []
        cyclic.append(cyclic)
        for value in (cyclic, {"nan": float("nan")},
                      {"inf": float("inf")}, {"custom": object()},
                      {"nested": {True: "invalid key"}},
                      {"nested": {2: "invalid key"}}):
            with self.subTest(type=type(value).__name__):
                with self.assertRaisesRegex(ValueError, "decision_config"):
                    replace(config(), decision_config={"scenario": value})

    def test_run_identity_nested_report_is_fresh_each_time(self):
        original = {"trials": [1, {"fees": [0.0, 0.5]}]}
        c = replace(config(), decision_config=original)
        original["trials"][1]["fees"].append(100)
        first = _run_identity(c, ())
        self.assertEqual(first["decision_config"],
                         {"trials": [1, {"fees": [0.0, 0.5]}]})
        first["decision_config"]["trials"][1]["fees"].append(-1)
        second = _run_identity(c, ())
        self.assertEqual(second["decision_config"],
                         {"trials": [1, {"fees": [0.0, 0.5]}]})

    def test_decision_metadata_depth_limit_is_fail_closed(self):
        deeply_nested = []
        for _ in range(36):
            deeply_nested = [deeply_nested]
        with self.assertRaisesRegex(ValueError, "maximum nesting"):
            replace(config(), decision_config={"scenario": deeply_nested})

    def test_decision_metadata_rejects_excessive_node_count(self):
        with self.assertRaisesRegex(ValueError, "node budget"):
            replace(config(), decision_config={"values": list(range(8300))})

    def test_decision_metadata_rejects_oversized_serialized_input(self):
        with self.assertRaisesRegex(ValueError, "64 KiB"):
            replace(config(), decision_config={"payload": "x" * 70000})

    def test_decision_metadata_rejects_unbounded_integer_values(self):
        for value in (1 << 600, -(1 << 600)):
            with self.subTest(negative=value < 0):
                with self.assertRaisesRegex(ValueError, "integer exceeds"):
                    replace(config(), decision_config={"integer": value})

    def test_small_unicode_and_finite_nested_metadata_round_trip(self):
        sample = {"note": "invented 测试", "levels": [-1, 0.5, True, None]}
        c = replace(config(), decision_config=sample)
        self.assertEqual(_run_identity(c, ())["decision_config"], sample)
        self.assertEqual(_run_identity(c, ())["decision_config"], sample)

    def test_nested_decision_metadata_rejects_terminal_control_values(self):
        for char in (chr(0), chr(9), chr(10), chr(13), chr(27), chr(127)):
            with self.subTest(control=ord(char)):
                with self.assertRaisesRegex(ValueError, "string values"):
                    replace(config(), decision_config={
                        "outer": [{"comment": "synthetic" + char + "APPROVED"}]
                    })

    def test_nested_decision_metadata_rejects_surrogate_codepoints(self):
        for bad in (chr(0xD800), chr(0xDC00)):
            for as_key in (True, False):
                with self.subTest(code=ord(bad), as_key=as_key):
                    value = {bad: "safe"} if as_key else {"comment": bad}
                    with self.assertRaisesRegex(ValueError, "decision_config"):
                        replace(config(), decision_config={"nested": value})

    def test_normal_unicode_nested_values_remain_supported(self):
        payload = {"comment": "invented café 测试", "levels": ["零", 0.5]}
        instance = replace(config(), decision_config=payload)
        self.assertEqual(_run_identity(instance, ())["decision_config"], payload)

    def test_scheduled_exit_collection_rejects_untyped_members(self):
        bars = [eurusd_bar(0), eurusd_bar(1)]
        for invalid in (None, "SYNTHETIC-EXIT", b"SYNTHETIC-EXIT",
                        42, [None], [{}], ["SYNTHETIC-EXIT"]):
            with self.subTest(value=repr(invalid)):
                with self.assertRaisesRegex(ValueError, "ScheduledExit"):
                    run_backtest(
                        bars=bars, decisions=[], config=config(),
                        scheduled_exits=invalid,
                    )

    def test_scheduled_exit_collection_accepts_empty_list_and_tuple(self):
        bars = [eurusd_bar(0), eurusd_bar(1)]
        for exits in ([], ()):
            with self.subTest(exits=type(exits).__name__):
                result = run_backtest(
                    bars=bars, decisions=[], config=config(),
                    scheduled_exits=exits,
                )
                self.assertEqual(result.trades, ())

    def test_malformed_scheduled_exits_fail_before_any_trade_approvals(self):
        bars = [eurusd_bar(0), eurusd_bar(1)]
        decision = long_decision(
            "SYNTHETIC-LONG", decision_minute=0, executable_minute=1)
        with self.assertRaisesRegex(ValueError, "ScheduledExit"):
            run_backtest(
                bars=bars, decisions=[decision], config=config(),
                scheduled_exits=[{"decision_id": "SYNTHETIC-LONG"}],
            )

    @staticmethod
    def _deny_external_calls():
        from contextlib import ExitStack
        stack = ExitStack()
        for name in ("subprocess.Popen", "socket.socket",
                     "builtins.open", "os.open"):
            stack.enter_context(mock.patch(
                name, side_effect=AssertionError(
                    "synthetic preflight must not access external resources"
                )))
        return stack

    def test_engine_rejects_invalid_quote_members_without_external_calls(self):
        for rows in ([eurusd_bar(0), None], [eurusd_bar(0), {}], "EURUSD"):
            with self.subTest(rows=repr(rows)[:60]):
                with self._deny_external_calls():
                    with self.assertRaisesRegex(ValueError, "QuoteBar"):
                        run_backtest(
                            bars=rows, decisions=[], config=config(),
                        )

    def test_engine_rejects_invalid_decision_members_without_external_calls(self):
        bars = [eurusd_bar(0), eurusd_bar(1)]
        for decisions in ([None], [{}], "NO_TRADE"):
            with self.subTest(decisions=repr(decisions)):
                with self._deny_external_calls():
                    with self.assertRaisesRegex(ValueError, "Decision"):
                        run_backtest(
                            bars=bars, decisions=decisions, config=config(),
                        )

    def test_engine_rejects_invalid_scheduled_exits_without_external_calls(self):
        bars = [eurusd_bar(0), eurusd_bar(1)]
        decision = long_decision(
            "SYNTHETIC-1", decision_minute=0, executable_minute=1)
        for exits in ([None], [{}], "SYNTHETIC"):
            with self.subTest(exits=repr(exits)):
                with self._deny_external_calls():
                    with self.assertRaisesRegex(ValueError, "ScheduledExit"):
                        run_backtest(
                            bars=bars, decisions=[decision], config=config(),
                            scheduled_exits=exits,
                        )

    def test_no_trade_is_preserved_as_reasoned_record(self) -> None:
        decision = Decision(
            decision_id="NT-1",
            symbol="EURUSD",
            decision_timestamp_utc=DAY,
            direction=Direction.NO_TRADE,
            earliest_executable_timestamp_utc=None,
            requested_risk_fraction=None,
            stop_price=None,
            target_price=None,
            reason_code="FILTERED",
            reason_text="fixture says no trade",
        )
        run = run_backtest(bars=[eurusd_bar(0)], decisions=[decision], config=config())
        self.assertEqual(run.trades, ())
        self.assertEqual(run.rejections[0].code, RejectionCode.NO_TRADE)
        self.assertIn("fixture says no trade", run.rejections[0].explanation)

    def test_same_bar_after_entry_both_thresholds_resolve_to_stop(self) -> None:
        entry_bar = eurusd_bar(
            1,
            bid_high=1.1025,
            bid_low=1.0988,
            ask_high=1.1027,
            ask_low=1.0990,
        )
        decision = long_decision(
            "D-AMB",
            decision_minute=0,
            executable_minute=1,
            stop_price=1.0992,
            target_price=1.1020,
        )
        run = run_backtest(
            bars=[eurusd_bar(0), entry_bar],
            decisions=[decision],
            config=config(),
        )
        self.assertEqual(len(run.trades), 1)
        closed = run.trades[0]
        self.assertEqual(closed.entry_timestamp_utc, entry_bar.timestamp_utc)
        self.assertEqual(closed.exit_timestamp_utc, entry_bar.timestamp_utc)
        self.assertEqual(closed.exit_reason, ExitReason.STOP)
        self.assertTrue(closed.intrabar_ambiguous)

    def test_stable_decision_order_rejects_second_when_only_one_slot_remains(self) -> None:
        bars = [
            eurusd_bar(0),
            eurusd_bar(1),
            gbpusd_bar(1),
            usdjpy_bar(1),
            eurusd_bar(2),
            gbpusd_bar(2),
            usdjpy_bar(2),
        ]
        existing = long_decision(
            "EXISTING",
            decision_minute=0,
            executable_minute=1,
            requested_risk_fraction=0.005,
            target_price=1.1100,
        )
        decision_a = long_decision(
            "A",
            symbol="GBPUSD",
            decision_minute=1,
            executable_minute=2,
            requested_risk_fraction=0.005,
            stop_price=1.2992,
            target_price=1.3100,
        )
        decision_b = long_decision(
            "B",
            symbol="USDJPY",
            decision_minute=1,
            executable_minute=2,
            requested_risk_fraction=0.005,
            stop_price=149.90,
            target_price=151.0,
        )
        run = run_backtest(
            bars=bars,
            decisions=[decision_b, existing, decision_a],
            config=config(),
        )
        rejected = {item.decision_id: item.code for item in run.rejections}
        self.assertNotIn("A", rejected)
        self.assertEqual(rejected["B"], RejectionCode.SIMULTANEOUS_RISK)
        self.assertTrue(any(trade.decision_id == "A" for trade in run.trades))

    def test_exit_before_entry_releases_reserved_risk_at_same_timestamp(self) -> None:
        bars = [
            eurusd_bar(0),
            eurusd_bar(1),
            gbpusd_bar(1),
            eurusd_bar(2),
            gbpusd_bar(2, target_hit=True),
            usdjpy_bar(2),
        ]
        first = long_decision(
            "EUR-OPEN",
            decision_minute=0,
            executable_minute=1,
            requested_risk_fraction=0.005,
            target_price=1.1100,
        )
        second = long_decision(
            "GBP-CLOSE",
            symbol="GBPUSD",
            decision_minute=0,
            executable_minute=1,
            requested_risk_fraction=0.005,
            stop_price=1.2992,
            target_price=1.3020,
        )
        replacement = long_decision(
            "JPY-NEW",
            symbol="USDJPY",
            decision_minute=1,
            executable_minute=2,
            requested_risk_fraction=0.005,
            stop_price=149.90,
            target_price=151.0,
        )
        run = run_backtest(
            bars=bars,
            decisions=[first, second, replacement],
            config=config(),
        )
        rejected = {item.decision_id: item.code for item in run.rejections}
        self.assertNotIn("JPY-NEW", rejected)
        self.assertTrue(any(trade.decision_id == "JPY-NEW" for trade in run.trades))

    def test_daily_halt_blocks_later_same_day_entry_and_resets_next_utc_day(self) -> None:
        bars: list[QuoteBar] = [eurusd_bar(0)]
        decisions: list[Decision] = []
        for minute in range(1, 6):
            bars.append(
                eurusd_bar(
                    minute,
                    bid_open=1.1000,
                    bid_high=1.1005,
                    bid_low=1.0990,
                    bid_close=1.0995,
                    ask_open=1.1002,
                    ask_high=1.1007,
                    ask_low=1.0992,
                    ask_close=1.0997,
                )
            )
            decisions.append(
                long_decision(
                    f"LOSS-{minute}",
                    decision_minute=minute - 1,
                    executable_minute=minute,
                    requested_risk_fraction=0.005,
                    stop_price=1.0992,
                    target_price=1.1100,
                )
            )

        next_day = DAY + timedelta(days=1)
        bars.append(
            QuoteBar(
                timestamp_utc=next_day,
                symbol="EURUSD",
                bid_open=1.1000,
                bid_high=1.1005,
                bid_low=1.0995,
                bid_close=1.1002,
                ask_open=1.1002,
                ask_high=1.1007,
                ask_low=1.0997,
                ask_close=1.1004,
            )
        )
        decisions.append(
            Decision(
                decision_id="NEXT-DAY",
                symbol="EURUSD",
                decision_timestamp_utc=next_day - timedelta(minutes=1),
                direction=Direction.LONG,
                earliest_executable_timestamp_utc=next_day,
                requested_risk_fraction=0.0025,
                stop_price=1.0992,
                target_price=None,
            )
        )

        run = run_backtest(bars=bars, decisions=decisions, config=config())
        rejected = {item.decision_id: item.code for item in run.rejections}
        self.assertEqual(rejected["LOSS-5"], RejectionCode.DAILY_HALT)
        self.assertNotIn("NEXT-DAY", rejected)
        self.assertTrue(any(trade.decision_id == "NEXT-DAY" for trade in run.trades))

    def test_open_position_closes_at_end_of_data_on_bid_close(self) -> None:
        bars = [eurusd_bar(0), eurusd_bar(1), eurusd_bar(2, bid_close=1.1006, ask_close=1.1008)]
        decision = long_decision(
            "D-EOD",
            decision_minute=0,
            executable_minute=1,
            stop_price=1.0900,
            target_price=None,
        )
        run = run_backtest(bars=bars, decisions=[decision], config=config())
        self.assertEqual(len(run.trades), 1)
        closed = run.trades[0]
        self.assertEqual(closed.exit_reason, ExitReason.END_OF_DATA)
        self.assertEqual(closed.exit_timestamp_utc, DAY + timedelta(minutes=2))
        self.assertEqual(closed.exit_reference_price, 1.1006)

    def test_invalid_stop_geometry_is_preserved_as_rejection(self) -> None:
        decision = long_decision(
            "BAD-STOP",
            decision_minute=0,
            executable_minute=1,
            stop_price=1.1010,
        )
        run = run_backtest(
            bars=[eurusd_bar(0), eurusd_bar(1)],
            decisions=[decision],
            config=config(),
        )
        self.assertEqual(run.trades, ())
        self.assertEqual(run.rejections[0].code, RejectionCode.INVALID_STOP_TARGET)

    def test_scheduled_exit_precedes_same_bar_stop_target_evaluation(self) -> None:
        bars = [
            eurusd_bar(0),
            eurusd_bar(1, bid_low=1.0995, bid_high=1.1008),
            eurusd_bar(
                2,
                bid_open=1.1004,
                bid_high=1.1030,
                bid_low=1.0980,
                ask_open=1.1006,
                ask_high=1.1032,
                ask_low=1.0982,
            ),
        ]
        decision = long_decision(
            "TIME-FIRST",
            decision_minute=0,
            executable_minute=1,
            stop_price=1.0990,
            target_price=1.1020,
        )
        run = run_backtest(
            bars=bars,
            decisions=[decision],
            scheduled_exits=[ScheduledExit("TIME-FIRST", "EURUSD", DAY + timedelta(minutes=2))],
            config=config(),
        )
        self.assertEqual(len(run.trades), 1)
        self.assertEqual(run.trades[0].exit_reason, ExitReason.TIME_EXIT)
        self.assertEqual(run.trades[0].exit_reference_price, 1.1004)
        self.assertFalse(run.trades[0].intrabar_ambiguous)

    def test_scheduled_exit_releases_risk_before_same_timestamp_entry(self) -> None:
        bars = [
            eurusd_bar(0),
            eurusd_bar(1),
            gbpusd_bar(1),
            usdjpy_bar(1),
            # Make the timed EURUSD exit PnL-neutral at reference prices so this
            # fixture isolates reservation-release ordering rather than changing
            # the simultaneous-risk denominator via realized PnL.
            eurusd_bar(2, bid_open=1.1002, ask_open=1.1004),
            gbpusd_bar(2),
            usdjpy_bar(2),
        ]
        scheduled = long_decision(
            "EUR-TIME",
            decision_minute=0,
            executable_minute=1,
            requested_risk_fraction=0.005,
            stop_price=1.0900,
            target_price=1.1100,
        )
        persistent = long_decision(
            "GBP-HOLD",
            symbol="GBPUSD",
            decision_minute=0,
            executable_minute=1,
            requested_risk_fraction=0.005,
            stop_price=1.2900,
            target_price=1.3200,
        )
        replacement = long_decision(
            "JPY-NEW-TIME",
            symbol="USDJPY",
            decision_minute=1,
            executable_minute=2,
            requested_risk_fraction=0.005,
            stop_price=149.90,
            target_price=151.0,
        )
        run = run_backtest(
            bars=bars,
            decisions=[scheduled, persistent, replacement],
            scheduled_exits=[ScheduledExit("EUR-TIME", "EURUSD", DAY + timedelta(minutes=2))],
            config=config(),
        )
        rejected = {item.decision_id: item.code for item in run.rejections}
        self.assertNotIn("JPY-NEW-TIME", rejected)
        self.assertTrue(any(trade.decision_id == "JPY-NEW-TIME" for trade in run.trades))
        timed = next(trade for trade in run.trades if trade.decision_id == "EUR-TIME")
        self.assertEqual(timed.exit_reason, ExitReason.TIME_EXIT)
        self.assertAlmostEqual(timed.net_pnl_usd, 0.0)

    def test_scheduled_exit_is_noop_after_prior_target(self) -> None:
        bars = [
            eurusd_bar(0),
            eurusd_bar(1),
            eurusd_bar(2, bid_high=1.1030, ask_high=1.1032),
            eurusd_bar(3),
        ]
        decision = long_decision(
            "TARGET-FIRST",
            decision_minute=0,
            executable_minute=1,
            stop_price=1.0900,
            target_price=1.1020,
        )
        run = run_backtest(
            bars=bars,
            decisions=[decision],
            scheduled_exits=[ScheduledExit("TARGET-FIRST", "EURUSD", DAY + timedelta(minutes=3))],
            config=config(),
        )
        self.assertEqual(len(run.trades), 1)
        self.assertEqual(run.trades[0].exit_reason, ExitReason.TARGET)
        self.assertEqual(run.trades[0].exit_timestamp_utc, DAY + timedelta(minutes=2))


if __name__ == "__main__":
    unittest.main()
