from __future__ import annotations

import unittest
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from fmp.backtest.costs import ZeroCommission, ZeroFinancing
from fmp.backtest.engine import NEXT_SUPPLIED_BAR, BacktestConfig, run_backtest
from fmp.contracts import Direction, ExitReason, QuoteBar, RejectionCode
from fmp.research.n1_news_shock import (
    HYPOTHETICAL_COST_LABEL,
    REASON_DISAGREEMENT,
    REASON_MISSING_QUOTE,
    REASON_MULTIPLE_RELEASES,
    REASON_RELEASE_NOT_PUBLISHED,
    REASON_RELEASE_TIME_MISMATCH,
    REASON_UNSUPPORTED_RELEASE,
    REASON_USD_STRENGTH,
    REASON_USD_WEAKNESS,
    REQUESTED_RISK_FRACTION,
    SEPARATE_SLIPPAGE_STRESS,
    N1Release,
    ReleaseKind,
    ReleaseStatus,
    evaluate_n1_v0,
    evaluate_n1_v0_releases,
    hypothetical_published_commission_model,
    n1_run_decision_config,
    new_york_clock_utc,
    required_n1_observation_keys,
    review_n1_observation,
)
from fmp.research.retail_costs import IC_MT4_RAW_COMMISSION
from fmp.risk import RiskConfig
from fmp.risk.sizing import size_units

NEW_YORK = ZoneInfo("America/New_York")
WINTER = date(2026, 1, 13)
SUMMER = date(2026, 7, 14)
EQUITY = 100_000.0


def _utc(day: date, hour: int, minute: int) -> datetime:
    return datetime(day.year, day.month, day.day, hour, minute, tzinfo=NEW_YORK).astimezone(
        timezone.utc
    )


def _quote(
    day: date,
    hour: int,
    minute: int,
    symbol: str,
    *,
    bid: float,
    ask: float,
    bid_low: float | None = None,
    bid_high: float | None = None,
    ask_low: float | None = None,
    ask_high: float | None = None,
    bid_close: float | None = None,
    ask_close: float | None = None,
) -> QuoteBar:
    bid_close = bid if bid_close is None else bid_close
    ask_close = ask if ask_close is None else ask_close
    bid_low = bid if bid_low is None else bid_low
    bid_high = bid if bid_high is None else bid_high
    ask_low = ask if ask_low is None else ask_low
    ask_high = ask if ask_high is None else ask_high
    bid_low = min(bid_low, bid, bid_close)
    bid_high = max(bid_high, bid, bid_close)
    ask_low = min(ask_low, ask, ask_close)
    ask_high = max(ask_high, ask, ask_close)
    return QuoteBar(
        timestamp_utc=_utc(day, hour, minute),
        symbol=symbol,
        bid_open=bid,
        bid_high=bid_high,
        bid_low=bid_low,
        bid_close=bid_close,
        ask_open=ask,
        ask_high=ask_high,
        ask_low=ask_low,
        ask_close=ask_close,
    )


def _session(
    day: date,
    *,
    direction: str,
    eurusd_entry_bid: float | None = None,
    eurusd_entry_ask: float | None = None,
    stop_bar_extreme: float | None = None,
    gap_at: tuple[int, int, float, float] | None = None,
    omit: set[tuple[str, int]] | None = None,
    through: tuple[int, int] = (9, 30),
    poison_later: bool = False,
) -> list[QuoteBar]:
    """Build synthetic quotes from 08:29 through ``through``.

    ``direction`` is ``strength``, ``weakness``, ``mixed``, or ``flat``.
    Bars after 08:34 are EURUSD only. A poisoned later price must not leak
    into the signal. A requested gap replaces one EURUSD bar.
    """

    omit = omit or set()
    bases = {
        "EURUSD": (1.10000, 1.10020),
        "GBPUSD": (1.30000, 1.30020),
        "USDJPY": (150.000, 150.020),
    }
    closes = {
        "strength": {
            "EURUSD": (1.09900, 1.09920),
            "GBPUSD": (1.29900, 1.29920),
            "USDJPY": (150.100, 150.120),
        },
        "weakness": {
            "EURUSD": (1.10100, 1.10120),
            "GBPUSD": (1.30100, 1.30120),
            "USDJPY": (149.900, 149.920),
        },
        "mixed": {
            "EURUSD": (1.09900, 1.09920),
            "GBPUSD": (1.30100, 1.30120),
            "USDJPY": (150.100, 150.120),
        },
        "flat": {
            "EURUSD": (1.10000, 1.10020),
            "GBPUSD": (1.29900, 1.29920),
            "USDJPY": (150.100, 150.120),
        },
    }[direction]
    bars: list[QuoteBar] = []
    for minute in range(29, 35):
        for symbol, (bid, ask) in bases.items():
            if (symbol, minute) in omit:
                continue
            bid_close, ask_close = (bid, ask)
            bid_low = bid
            bid_high = bid
            ask_low = ask
            ask_high = ask
            if minute == 34:
                bid_close, ask_close = closes[symbol]
            if (
                symbol == "EURUSD"
                and minute == 32
                and stop_bar_extreme is not None
                and direction == "strength"
            ):
                ask_high = stop_bar_extreme
            if (
                symbol == "EURUSD"
                and minute == 32
                and stop_bar_extreme is not None
                and direction == "weakness"
            ):
                bid_low = stop_bar_extreme
            bars.append(
                _quote(
                    day,
                    8,
                    minute,
                    symbol,
                    bid=bid,
                    ask=ask,
                    bid_close=bid_close,
                    ask_close=ask_close,
                    bid_low=bid_low,
                    bid_high=bid_high,
                    ask_low=ask_low,
                    ask_high=ask_high,
                )
            )
    if eurusd_entry_bid is None or eurusd_entry_ask is None:
        if direction == "weakness":
            eurusd_entry_bid, eurusd_entry_ask = 1.10100, 1.10120
        else:
            eurusd_entry_bid, eurusd_entry_ask = 1.09900, 1.09920
    cursor = datetime(day.year, day.month, day.day, 8, 35, tzinfo=NEW_YORK)
    stop_clock = datetime(
        day.year,
        day.month,
        day.day,
        through[0],
        through[1],
        tzinfo=NEW_YORK,
    )
    while cursor <= stop_clock:
        local = cursor.astimezone(timezone.utc).astimezone(NEW_YORK)
        if (local.hour, local.minute) == (8, 36):
            bid, ask = eurusd_entry_bid, eurusd_entry_ask
        elif poison_later:
            bid, ask = 1.25000, 1.25020
        else:
            bid, ask = eurusd_entry_bid, eurusd_entry_ask
        if gap_at is not None and (local.hour, local.minute) == (gap_at[0], gap_at[1]):
            bid, ask = gap_at[2], gap_at[3]
        bars.append(_quote(day, local.hour, local.minute, "EURUSD", bid=bid, ask=ask))
        cursor += timedelta(minutes=1)
    return bars


def _release(
    day: date = WINTER,
    *,
    release_id: str = "cpi-1",
    kind: str = ReleaseKind.CPI,
    status: str = ReleaseStatus.PUBLISHED,
    actual: datetime | None = None,
) -> N1Release:
    if actual is None and status == ReleaseStatus.PUBLISHED:
        actual = _utc(day, 8, 30)
    return N1Release(
        release_id=release_id,
        kind=kind,
        status=status,
        new_york_date=day,
        actual_release_utc=actual,
    )


def _config(
    bars: list[QuoteBar],
    *,
    slippage_pips: float = 0.0,
    equity: float = EQUITY,
    commission: bool = False,
) -> BacktestConfig:
    start = min(bar.timestamp_utc for bar in bars)
    end = max(bar.timestamp_utc for bar in bars)
    return BacktestConfig(
        starting_equity_usd=equity,
        slippage_pips=slippage_pips,
        risk_config=RiskConfig(),
        commission_model=(
            hypothetical_published_commission_model() if commission else ZeroCommission()
        ),
        financing_model=ZeroFinancing(),
        processed_data_manifest_id="n1-v0-synthetic-quotes",
        schema_version="fmp-synthetic-n1-v0",
        timeframe="1m",
        requested_start_utc=start,
        requested_end_utc=end,
        code_commit="n1-v0-synthetic-fixture",
        decision_config=n1_run_decision_config(),
        execution_timing_mode=NEXT_SUPPLIED_BAR,
    )


class N1NewsShockTests(unittest.TestCase):
    def test_clock_uses_new_york_dst_offset(self) -> None:
        winter_release = new_york_clock_utc(WINTER, 8, 30)
        summer_release = new_york_clock_utc(SUMMER, 8, 30)
        after_spring = new_york_clock_utc(date(2026, 3, 9), 8, 30)
        after_fall = new_york_clock_utc(date(2026, 11, 2), 8, 30)
        self.assertEqual(winter_release, datetime(2026, 1, 13, 13, 30, tzinfo=timezone.utc))
        self.assertEqual(summer_release, datetime(2026, 7, 14, 12, 30, tzinfo=timezone.utc))
        self.assertEqual(after_spring, datetime(2026, 3, 9, 12, 30, tzinfo=timezone.utc))
        self.assertEqual(after_fall, datetime(2026, 11, 2, 13, 30, tzinfo=timezone.utc))
        self.assertEqual(winter_release, _utc(WINTER, 8, 30))
        self.assertEqual(summer_release, _utc(SUMMER, 8, 30))
        with self.assertRaises(ValueError):
            new_york_clock_utc(date(2026, 3, 8), 2, 30)

    def test_strength_is_short_eurusd_at_0836_with_ask_high_stop(self) -> None:
        bars = _session(WINTER, direction="strength", stop_bar_extreme=1.10150)
        signal = evaluate_n1_v0(_release(), bars)
        decision = signal.decision
        self.assertEqual(decision.direction, Direction.SHORT)
        self.assertEqual(decision.symbol, "EURUSD")
        self.assertEqual(decision.reason_code, REASON_USD_STRENGTH)
        self.assertEqual(decision.decision_timestamp_utc, _utc(WINTER, 8, 35))
        self.assertEqual(decision.earliest_executable_timestamp_utc, _utc(WINTER, 8, 36))
        self.assertEqual(decision.stop_price, 1.10150)
        self.assertIsNone(decision.target_price)
        self.assertEqual(decision.requested_risk_fraction, REQUESTED_RISK_FRACTION)
        self.assertIsNotNone(signal.scheduled_exit)
        assert signal.scheduled_exit is not None
        self.assertEqual(signal.scheduled_exit.timestamp_utc, _utc(WINTER, 9, 30))
        self.assertEqual(signal.bars_used_through_utc, decision.decision_timestamp_utc)
        again = evaluate_n1_v0(_release(), bars)
        self.assertEqual(again.decision, signal.decision)
        self.assertEqual(again.scheduled_exit, signal.scheduled_exit)

    def test_weakness_is_long_eurusd_with_bid_low_stop(self) -> None:
        bars = _session(WINTER, direction="weakness", stop_bar_extreme=1.09800)
        signal = evaluate_n1_v0(_release(kind=ReleaseKind.EMPLOYMENT_SITUATION), bars)
        self.assertEqual(signal.decision.direction, Direction.LONG)
        self.assertEqual(signal.reason_code, REASON_USD_WEAKNESS)
        self.assertEqual(signal.decision.stop_price, 1.09800)
        self.assertEqual(signal.decision.symbol, "EURUSD")

    def test_mixed_flat_missing_and_release_failures_stay_no_trade(self) -> None:
        mixed = evaluate_n1_v0(_release(), _session(WINTER, direction="mixed"))
        flat = evaluate_n1_v0(_release(), _session(WINTER, direction="flat"))
        missing = evaluate_n1_v0(
            _release(),
            _session(WINTER, direction="strength", omit={("GBPUSD", 32)}),
        )
        unpublished = evaluate_n1_v0(
            _release(status=ReleaseStatus.NOT_PUBLISHED, actual=None),
            _session(WINTER, direction="strength"),
        )
        delayed = evaluate_n1_v0(
            _release(status=ReleaseStatus.DELAYED, actual=_utc(WINTER, 8, 45)),
            _session(WINTER, direction="strength"),
        )
        wrong_clock = evaluate_n1_v0(
            _release(actual=datetime(2026, 1, 13, 8, 30, tzinfo=timezone.utc)),
            _session(WINTER, direction="strength"),
        )
        other_kind = evaluate_n1_v0(
            _release(kind="FOMC"),
            _session(WINTER, direction="strength"),
        )
        self.assertEqual(mixed.reason_code, REASON_DISAGREEMENT)
        self.assertEqual(flat.reason_code, REASON_DISAGREEMENT)
        self.assertEqual(missing.reason_code, REASON_MISSING_QUOTE)
        self.assertIn("GBPUSD", missing.decision.reason_text or "")
        self.assertEqual(unpublished.reason_code, REASON_RELEASE_NOT_PUBLISHED)
        self.assertEqual(delayed.reason_code, REASON_RELEASE_NOT_PUBLISHED)
        self.assertEqual(wrong_clock.reason_code, REASON_RELEASE_TIME_MISMATCH)
        self.assertEqual(other_kind.reason_code, REASON_UNSUPPORTED_RELEASE)
        for signal in (mixed, flat, missing, unpublished, delayed, wrong_clock, other_kind):
            self.assertEqual(signal.decision.direction, Direction.NO_TRADE)
            self.assertIsNone(signal.scheduled_exit)
            self.assertIsNone(signal.decision.stop_price)

    def test_same_day_releases_do_not_pyramid(self) -> None:
        bars = _session(WINTER, direction="strength", stop_bar_extreme=1.10150)
        signals = evaluate_n1_v0_releases(
            (
                _release(release_id="cpi"),
                _release(release_id="nfp", kind=ReleaseKind.EMPLOYMENT_SITUATION),
            ),
            bars,
        )
        self.assertEqual([signal.reason_code for signal in signals], [REASON_MULTIPLE_RELEASES, REASON_MULTIPLE_RELEASES])
        result = run_backtest(
            bars=bars,
            decisions=tuple(signal.decision for signal in signals),
            config=_config(bars),
        )
        self.assertEqual(result.trades, ())
        self.assertEqual(
            [row.code for row in result.rejections],
            [RejectionCode.NO_TRADE, RejectionCode.NO_TRADE],
        )

    def test_later_prices_do_not_change_signal_or_initial_stop(self) -> None:
        original_bars = _session(WINTER, direction="strength", stop_bar_extreme=1.10150)
        original = evaluate_n1_v0(_release(), original_bars)
        poisoned = _session(
            WINTER,
            direction="strength",
            stop_bar_extreme=1.10150,
            poison_later=True,
            eurusd_entry_bid=1.10000,
            eurusd_entry_ask=1.10020,
        )
        poisoned_signal = evaluate_n1_v0(_release(), poisoned)
        self.assertEqual(poisoned_signal.decision.direction, original.decision.direction)
        self.assertEqual(poisoned_signal.decision.stop_price, original.decision.stop_price)
        self.assertEqual(
            poisoned_signal.decision.earliest_executable_timestamp_utc,
            original.decision.earliest_executable_timestamp_utc,
        )
        flipped = _session(WINTER, direction="weakness", stop_bar_extreme=1.09800)
        self.assertEqual(evaluate_n1_v0(_release(), flipped).decision.direction, Direction.LONG)

        assert original.scheduled_exit is not None
        assert original.decision.stop_price is not None
        first = run_backtest(
            bars=original_bars,
            decisions=(original.decision,),
            scheduled_exits=(original.scheduled_exit,),
            config=_config(original_bars, equity=EQUITY),
        )
        second = run_backtest(
            bars=poisoned,
            decisions=(poisoned_signal.decision,),
            scheduled_exits=(poisoned_signal.scheduled_exit,),
            config=_config(poisoned, equity=EQUITY * 2),
        )
        self.assertEqual(len(first.trades), 1)
        self.assertEqual(len(second.trades), 1)
        self.assertEqual(first.trades[0].stop_price, 1.10150)
        self.assertEqual(second.trades[0].stop_price, 1.10150)
        self.assertNotEqual(first.trades[0].units, second.trades[0].units)
        self.assertNotEqual(first.trades[0].entry_reference_price, second.trades[0].entry_reference_price)
        expected_units = size_units(
            symbol="EURUSD",
            entry_price=second.trades[0].entry_reference_price,
            stop_price=1.10150,
            allowed_risk_usd=EQUITY * 2 * REQUESTED_RISK_FRACTION,
        )
        self.assertEqual(second.trades[0].units, expected_units)

    def test_entry_is_0836_open_and_time_exit_is_0930_open(self) -> None:
        bars = _session(SUMMER, direction="strength", stop_bar_extreme=1.10150)
        signal = evaluate_n1_v0(_release(day=SUMMER), bars)
        assert signal.scheduled_exit is not None
        result = run_backtest(
            bars=bars,
            decisions=(signal.decision,),
            scheduled_exits=(signal.scheduled_exit,),
            config=_config(bars),
        )
        self.assertEqual(len(result.trades), 1)
        trade = result.trades[0]
        self.assertEqual(trade.entry_timestamp_utc, _utc(SUMMER, 8, 36))
        self.assertEqual(trade.exit_timestamp_utc, _utc(SUMMER, 9, 30))
        self.assertEqual(trade.exit_reason, ExitReason.TIME_EXIT)
        self.assertEqual(trade.entry_reference_price, 1.09900)
        self.assertEqual(trade.exit_reference_price, 1.09920)
        self.assertEqual(trade.financing_cost_usd, 0.0)
        self.assertEqual(trade.stop_price, 1.10150)
        self.assertIsNone(trade.target_price)
        self.assertNotEqual(trade.entry_timestamp_utc, _utc(SUMMER, 8, 35))

    def test_gap_stop_fills_at_the_opened_through_price(self) -> None:
        bars = _session(
            WINTER,
            direction="strength",
            stop_bar_extreme=1.10150,
            gap_at=(8, 40, 1.10300, 1.10320),
        )
        signal = evaluate_n1_v0(_release(), bars)
        assert signal.scheduled_exit is not None
        result = run_backtest(
            bars=bars,
            decisions=(signal.decision,),
            scheduled_exits=(signal.scheduled_exit,),
            config=_config(bars),
        )
        trade = result.trades[0]
        self.assertEqual(trade.exit_reason, ExitReason.STOP)
        self.assertEqual(trade.exit_timestamp_utc, _utc(WINTER, 8, 40))
        self.assertEqual(trade.exit_reference_price, 1.10320)
        self.assertFalse(trade.intrabar_ambiguous)
        self.assertEqual(trade.stop_price, 1.10150)

    def test_entry_open_through_the_original_stop_is_rejected(self) -> None:
        bars = _session(
            WINTER,
            direction="strength",
            stop_bar_extreme=1.10150,
            eurusd_entry_bid=1.10200,
            eurusd_entry_ask=1.10220,
        )
        signal = evaluate_n1_v0(_release(), bars)
        self.assertEqual(signal.decision.stop_price, 1.10150)
        self.assertEqual(signal.decision.direction, Direction.SHORT)
        assert signal.scheduled_exit is not None
        result = run_backtest(
            bars=bars,
            decisions=(signal.decision,),
            scheduled_exits=(signal.scheduled_exit,),
            config=_config(bars),
        )
        self.assertEqual(result.trades, ())
        self.assertEqual(result.rejections[0].code, RejectionCode.INVALID_STOP_TARGET)

    def test_missing_entry_bar_is_a_timing_rejection(self) -> None:
        bars = [
            bar
            for bar in _session(WINTER, direction="strength", stop_bar_extreme=1.10150)
            if not (bar.symbol == "EURUSD" and bar.timestamp_utc == _utc(WINTER, 8, 36))
        ]
        signal = evaluate_n1_v0(_release(), bars)
        self.assertEqual(signal.decision.direction, Direction.SHORT)
        self.assertEqual(signal.decision.earliest_executable_timestamp_utc, _utc(WINTER, 8, 36))
        assert signal.scheduled_exit is not None
        result = run_backtest(
            bars=bars,
            decisions=(signal.decision,),
            scheduled_exits=(signal.scheduled_exit,),
            config=_config(bars),
        )
        self.assertEqual(result.trades, ())
        self.assertEqual(result.rejections[0].code, RejectionCode.TIMING_CONTRACT)

    def test_missing_0930_bar_is_end_of_data_not_a_rewritten_exit(self) -> None:
        bars = _session(
            WINTER,
            direction="strength",
            stop_bar_extreme=1.10150,
            through=(8, 50),
        )
        self.assertFalse(any(bar.timestamp_utc == _utc(WINTER, 9, 30) for bar in bars))
        signal = evaluate_n1_v0(_release(), bars)
        assert signal.scheduled_exit is not None
        self.assertEqual(signal.scheduled_exit.timestamp_utc, _utc(WINTER, 9, 30))
        result = run_backtest(
            bars=bars,
            decisions=(signal.decision,),
            scheduled_exits=(signal.scheduled_exit,),
            config=_config(bars),
        )
        self.assertEqual(result.trades[0].exit_reason, ExitReason.END_OF_DATA)
        self.assertNotEqual(result.trades[0].exit_timestamp_utc, _utc(WINTER, 9, 30))

    def test_tiny_risk_budget_is_rejected_by_the_existing_sizer(self) -> None:
        bars = _session(WINTER, direction="strength", stop_bar_extreme=1.10150)
        signal = evaluate_n1_v0(_release(), bars)
        assert signal.scheduled_exit is not None
        result = run_backtest(
            bars=bars,
            decisions=(signal.decision,),
            scheduled_exits=(signal.scheduled_exit,),
            config=_config(bars, equity=0.10),
        )
        self.assertEqual(result.trades, ())
        self.assertEqual(result.rejections[0].code, RejectionCode.INVALID_SIZE)

    def test_no_trade_is_kept_by_the_engine(self) -> None:
        bars = _session(WINTER, direction="mixed")
        signal = evaluate_n1_v0(_release(), bars)
        result = run_backtest(
            bars=bars,
            decisions=(signal.decision,),
            config=_config(bars),
        )
        self.assertEqual(result.trades, ())
        self.assertEqual(result.rejections[0].code, RejectionCode.NO_TRADE)
        self.assertEqual(result.rejections[0].explanation, signal.decision.reason_text)

    def test_hypothetical_commission_and_one_slippage_value_are_recorded(self) -> None:
        bars = _session(WINTER, direction="strength", stop_bar_extreme=1.10150)
        signal = evaluate_n1_v0(_release(), bars)
        assert signal.scheduled_exit is not None
        model = hypothetical_published_commission_model()
        self.assertEqual(IC_MT4_RAW_COMMISSION.usd_per_standard_lot_per_side, 3.50)
        self.assertEqual(model.usd_per_million_per_side, 35.0)
        self.assertIn("hypothetical", HYPOTHETICAL_COST_LABEL)
        result = run_backtest(
            bars=bars,
            decisions=(signal.decision,),
            scheduled_exits=(signal.scheduled_exit,),
            config=_config(bars, slippage_pips=0.5, commission=True),
        )
        trade = result.trades[0]
        self.assertEqual(trade.entry_reference_price, 1.09900)
        self.assertAlmostEqual(trade.entry_price, 1.09900 - 0.00005)
        self.assertGreater(trade.slippage_cost_usd, 0.0)
        self.assertEqual(trade.commission_cost_usd, model.cost_usd(units=trade.units) * 2)
        self.assertEqual(trade.units, 100_000)
        self.assertEqual(trade.commission_cost_usd, 7.0)
        self.assertEqual(result.run_identity["slippage_pips"], 0.5)
        self.assertEqual(
            result.run_identity["commission_model"],
            dict(model.to_config()),
        )
        self.assertEqual(
            result.run_identity["decision_config"]["evidence_class"],
            "synthetic_engineering_check",
        )

    def test_separate_slippage_runs_are_not_one_asymmetric_fill(self) -> None:
        bars = _session(WINTER, direction="strength", stop_bar_extreme=1.10150)
        signal = evaluate_n1_v0(_release(), bars)
        assert signal.scheduled_exit is not None
        runs = []
        for pips in (0.2, 1.0):
            result = run_backtest(
                bars=bars,
                decisions=(signal.decision,),
                scheduled_exits=(signal.scheduled_exit,),
                config=_config(bars, slippage_pips=pips),
            )
            self.assertEqual(result.run_identity["slippage_pips"], pips)
            self.assertEqual(SEPARATE_SLIPPAGE_STRESS, "separate_run_single_adverse_slippage")
            runs.append(result.trades[0])
        self.assertAlmostEqual(runs[0].entry_price - runs[1].entry_price, 0.00008)
        self.assertEqual(runs[0].stop_price, runs[1].stop_price)

    def test_duplicate_quote_is_rejected_instead_of_choosing_one(self) -> None:
        bars = _session(WINTER, direction="strength", stop_bar_extreme=1.10150)
        bars.append(bars[0])
        with self.assertRaises(ValueError):
            evaluate_n1_v0(_release(), bars)
        with self.assertRaises(ValueError):
            review_n1_observation(WINTER, bars, exit_reason=ExitReason.TIME_EXIT)

    def test_complete_time_exit_is_ordinary_and_does_not_require_0835(self) -> None:
        bars = _session(WINTER, direction="strength", stop_bar_extreme=1.10150)
        signal = evaluate_n1_v0(_release(), bars)
        assert signal.scheduled_exit is not None
        result = run_backtest(
            bars=bars,
            decisions=(signal.decision,),
            scheduled_exits=(signal.scheduled_exit,),
            config=_config(bars),
        )
        self.assertEqual(result.trades[0].exit_reason, ExitReason.TIME_EXIT)
        review = review_n1_observation(
            WINTER,
            bars,
            exit_reason=result.trades[0].exit_reason,
        )
        self.assertEqual(review.quality, "COMPLETE")
        self.assertEqual(review.missing_labels, ())
        self.assertTrue(review.ordinary_n1_time_exit)
        self.assertEqual(review.exit_reason, ExitReason.TIME_EXIT.value)
        keys = required_n1_observation_keys(WINTER)
        self.assertEqual(len(keys), 73)
        self.assertNotIn((_utc(WINTER, 8, 35), "EURUSD"), keys)
        self.assertNotIn((_utc(WINTER, 8, 36), "GBPUSD"), keys)
        self.assertIn((_utc(WINTER, 8, 29), "USDJPY"), keys)
        self.assertIn((_utc(WINTER, 8, 34), "GBPUSD"), keys)
        self.assertIn((_utc(WINTER, 8, 36), "EURUSD"), keys)
        self.assertIn((_utc(WINTER, 9, 30), "EURUSD"), keys)

        without_decision_bar = [
            bar
            for bar in bars
            if not (bar.symbol == "EURUSD" and bar.timestamp_utc == _utc(WINTER, 8, 35))
        ]
        unchanged = evaluate_n1_v0(_release(), without_decision_bar)
        self.assertEqual(unchanged.decision.direction, Direction.SHORT)
        self.assertEqual(unchanged.decision.stop_price, 1.10150)
        rerun = run_backtest(
            bars=without_decision_bar,
            decisions=(unchanged.decision,),
            scheduled_exits=(unchanged.scheduled_exit,),
            config=_config(without_decision_bar),
        )
        self.assertEqual(rerun.trades[0].exit_reason, ExitReason.TIME_EXIT)
        still_complete = review_n1_observation(
            WINTER,
            without_decision_bar,
            exit_reason=rerun.trades[0].exit_reason,
        )
        self.assertEqual(still_complete.quality, "COMPLETE")
        self.assertTrue(still_complete.ordinary_n1_time_exit)

    def test_missing_0930_end_of_data_is_not_an_ordinary_time_exit(self) -> None:
        bars = _session(
            WINTER,
            direction="strength",
            stop_bar_extreme=1.10150,
            through=(8, 50),
        )
        signal = evaluate_n1_v0(_release(), bars)
        assert signal.scheduled_exit is not None
        self.assertEqual(signal.scheduled_exit.timestamp_utc, _utc(WINTER, 9, 30))
        self.assertEqual(signal.decision.stop_price, 1.10150)
        result = run_backtest(
            bars=bars,
            decisions=(signal.decision,),
            scheduled_exits=(signal.scheduled_exit,),
            config=_config(bars),
        )
        self.assertEqual(result.trades[0].exit_reason, ExitReason.END_OF_DATA)
        review = review_n1_observation(
            WINTER,
            bars,
            exit_reason=result.trades[0].exit_reason,
        )
        self.assertEqual(review.quality, "INCOMPLETE")
        self.assertFalse(review.ordinary_n1_time_exit)
        self.assertEqual(review.exit_reason, ExitReason.END_OF_DATA.value)
        self.assertIn("EURUSD 09:30 America/New_York", review.missing_labels)
        self.assertIn("not an ordinary", review.explanation)
        forced = review_n1_observation(WINTER, bars, exit_reason=ExitReason.TIME_EXIT)
        self.assertEqual(forced.quality, "INCOMPLETE")
        self.assertFalse(forced.ordinary_n1_time_exit)

    def test_missing_intermediate_bar_is_incomplete_despite_time_exit(self) -> None:
        bars = [
            bar
            for bar in _session(WINTER, direction="strength", stop_bar_extreme=1.10150)
            if not (bar.symbol == "EURUSD" and bar.timestamp_utc == _utc(WINTER, 8, 40))
        ]
        signal = evaluate_n1_v0(_release(), bars)
        self.assertEqual(signal.decision.direction, Direction.SHORT)
        self.assertEqual(signal.decision.stop_price, 1.10150)
        assert signal.scheduled_exit is not None
        result = run_backtest(
            bars=bars,
            decisions=(signal.decision,),
            scheduled_exits=(signal.scheduled_exit,),
            config=_config(bars),
        )
        self.assertEqual(result.trades[0].exit_reason, ExitReason.TIME_EXIT)
        self.assertEqual(result.trades[0].exit_timestamp_utc, _utc(WINTER, 9, 30))
        review = review_n1_observation(
            WINTER,
            bars,
            exit_reason=result.trades[0].exit_reason,
        )
        self.assertEqual(review.quality, "INCOMPLETE")
        self.assertFalse(review.ordinary_n1_time_exit)
        self.assertEqual(review.missing_labels, ("EURUSD 08:40 America/New_York",))
        self.assertIn("stop path", review.explanation)

    def test_missing_entry_bar_is_incomplete_and_stays_rejected(self) -> None:
        bars = [
            bar
            for bar in _session(WINTER, direction="strength", stop_bar_extreme=1.10150)
            if not (bar.symbol == "EURUSD" and bar.timestamp_utc == _utc(WINTER, 8, 36))
        ]
        signal = evaluate_n1_v0(_release(), bars)
        self.assertEqual(signal.decision.direction, Direction.SHORT)
        self.assertEqual(signal.decision.earliest_executable_timestamp_utc, _utc(WINTER, 8, 36))
        assert signal.scheduled_exit is not None
        result = run_backtest(
            bars=bars,
            decisions=(signal.decision,),
            scheduled_exits=(signal.scheduled_exit,),
            config=_config(bars),
        )
        self.assertEqual(result.rejections[0].code, RejectionCode.TIMING_CONTRACT)
        review = review_n1_observation(WINTER, bars, exit_reason=None)
        self.assertEqual(review.quality, "INCOMPLETE")
        self.assertFalse(review.ordinary_n1_time_exit)
        self.assertIn("EURUSD 08:36 America/New_York", review.missing_labels)

    def test_missing_signal_window_is_no_trade_and_incomplete(self) -> None:
        bars = _session(
            WINTER,
            direction="strength",
            stop_bar_extreme=1.10150,
            omit={("GBPUSD", 32)},
        )
        signal = evaluate_n1_v0(_release(), bars)
        self.assertEqual(signal.decision.direction, Direction.NO_TRADE)
        self.assertEqual(signal.reason_code, REASON_MISSING_QUOTE)
        result = run_backtest(
            bars=bars,
            decisions=(signal.decision,),
            config=_config(bars),
        )
        self.assertEqual(result.rejections[0].code, RejectionCode.NO_TRADE)
        review = review_n1_observation(WINTER, bars, exit_reason=None)
        self.assertEqual(review.quality, "INCOMPLETE")
        self.assertFalse(review.ordinary_n1_time_exit)
        self.assertIn("GBPUSD 08:32 America/New_York", review.missing_labels)

    def test_complete_stop_is_not_an_ordinary_time_exit(self) -> None:
        bars = _session(
            WINTER,
            direction="strength",
            stop_bar_extreme=1.10150,
            gap_at=(8, 40, 1.10300, 1.10320),
        )
        signal = evaluate_n1_v0(_release(), bars)
        assert signal.scheduled_exit is not None
        result = run_backtest(
            bars=bars,
            decisions=(signal.decision,),
            scheduled_exits=(signal.scheduled_exit,),
            config=_config(bars),
        )
        self.assertEqual(result.trades[0].exit_reason, ExitReason.STOP)
        review = review_n1_observation(
            WINTER,
            bars,
            exit_reason=result.trades[0].exit_reason,
        )
        self.assertEqual(review.quality, "COMPLETE")
        self.assertEqual(review.missing_labels, ())
        self.assertFalse(review.ordinary_n1_time_exit)
        self.assertEqual(review.exit_reason, ExitReason.STOP.value)

    def test_complete_disagreement_is_not_an_ordinary_time_exit(self) -> None:
        bars = _session(WINTER, direction="mixed")
        signal = evaluate_n1_v0(_release(), bars)
        self.assertEqual(signal.reason_code, REASON_DISAGREEMENT)
        self.assertEqual(signal.decision.direction, Direction.NO_TRADE)
        review = review_n1_observation(WINTER, bars, exit_reason=None)
        self.assertEqual(review.quality, "COMPLETE")
        self.assertFalse(review.ordinary_n1_time_exit)
        self.assertIsNone(review.exit_reason)

    def test_review_rejects_a_string_exit_reason(self) -> None:
        bars = _session(WINTER, direction="strength", stop_bar_extreme=1.10150)
        with self.assertRaises(TypeError):
            review_n1_observation(WINTER, bars, exit_reason="TIME_EXIT")  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
