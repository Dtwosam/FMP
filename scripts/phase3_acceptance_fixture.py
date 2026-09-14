from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fmp.backtest.costs import FixedCommissionPerMillion, ZeroCommission, ZeroFinancing
from fmp.backtest.engine import BacktestConfig, run_backtest
from fmp.contracts import BacktestRun, Decision, Direction, QuoteBar, RejectionCode
from fmp.reporting.backtest import write_backtest_artifacts
from fmp.risk import RiskConfig


PROTOCOL = "fmp-phase3-acceptance-fixture-v1"
FIXTURE_ID = "phase3-merged-main-acceptance-v1"
DAY1 = datetime(2026, 9, 14, 0, 0, tzinfo=timezone.utc)
DAY2 = DAY1 + timedelta(days=1)
ARTIFACT_NAMES = (
    "summary.json",
    "trades.jsonl",
    "rejections.jsonl",
    "metrics.json",
    "manifest.json",
)


def _quote(
    timestamp: datetime,
    *,
    symbol: str = "EURUSD",
    bid_open: float = 1.1000,
    bid_high: float = 1.1008,
    bid_low: float = 1.0995,
    bid_close: float = 1.1003,
    ask_open: float = 1.1002,
    ask_high: float = 1.1010,
    ask_low: float = 1.0997,
    ask_close: float = 1.1005,
) -> QuoteBar:
    return QuoteBar(
        timestamp_utc=timestamp,
        symbol=symbol,
        bid_open=bid_open,
        bid_high=bid_high,
        bid_low=bid_low,
        bid_close=bid_close,
        ask_open=ask_open,
        ask_high=ask_high,
        ask_low=ask_low,
        ask_close=ask_close,
    )


def _decision(
    decision_id: str,
    *,
    symbol: str = "EURUSD",
    direction: Direction = Direction.LONG,
    decision_timestamp: datetime,
    executable_timestamp: datetime,
    stop_price: float,
    target_price: float | None = None,
    requested_risk_fraction: float | None = None,
) -> Decision:
    return Decision(
        decision_id=decision_id,
        symbol=symbol,
        decision_timestamp_utc=decision_timestamp,
        direction=direction,
        earliest_executable_timestamp_utc=executable_timestamp,
        requested_risk_fraction=requested_risk_fraction,
        stop_price=stop_price,
        target_price=target_price,
    )


def _config(
    *,
    scenario: str,
    code_commit: str,
    bars: list[QuoteBar],
    slippage_pips: float = 0.0,
    commission_model: ZeroCommission | FixedCommissionPerMillion | None = None,
) -> BacktestConfig:
    return BacktestConfig(
        starting_equity_usd=10_000.0,
        slippage_pips=slippage_pips,
        risk_config=RiskConfig(),
        commission_model=commission_model or ZeroCommission(),
        financing_model=ZeroFinancing(),
        processed_data_manifest_id="phase3-scripted-acceptance-data-v1",
        schema_version="fmp-canonical-1m-v1",
        timeframe="1m",
        requested_start_utc=bars[0].timestamp_utc,
        requested_end_utc=bars[-1].timestamp_utc,
        code_commit=code_commit,
        decision_config={"fixture": FIXTURE_ID, "scenario": scenario},
    )


def _long_cost(code_commit: str) -> BacktestRun:
    bars = [
        _quote(DAY1),
        _quote(DAY1 + timedelta(minutes=1)),
        _quote(
            DAY1 + timedelta(minutes=2),
            bid_open=1.1008,
            bid_high=1.1014,
            bid_low=1.1005,
            bid_close=1.1012,
            ask_open=1.1010,
            ask_high=1.1016,
            ask_low=1.1007,
            ask_close=1.1014,
        ),
    ]
    run = run_backtest(
        bars=bars,
        decisions=[
            _decision(
                "LONG-COST",
                decision_timestamp=DAY1,
                executable_timestamp=DAY1 + timedelta(minutes=1),
                stop_price=1.0992,
                target_price=1.1012,
            )
        ],
        config=_config(
            scenario="long-cost",
            code_commit=code_commit,
            bars=bars,
            slippage_pips=1.0,
            commission_model=FixedCommissionPerMillion(30.0),
        ),
    )
    trade = run.trades[0]
    assert trade.units == 25_000
    assert trade.entry_reference_price == 1.1002
    assert trade.exit_reference_price == 1.1012
    assert abs(trade.gross_pnl_usd - 25.0) < 1e-9
    assert abs(trade.slippage_cost_usd - 5.0) < 1e-9
    assert abs(trade.commission_cost_usd - 1.5) < 1e-9
    assert abs(trade.net_pnl_usd - 18.5) < 1e-9
    return run


def _short_target(code_commit: str) -> BacktestRun:
    bars = [
        _quote(DAY1),
        _quote(
            DAY1 + timedelta(minutes=1),
            bid_high=1.1006,
            ask_high=1.1008,
        ),
        _quote(
            DAY1 + timedelta(minutes=2),
            bid_open=1.0994,
            bid_high=1.0998,
            bid_low=1.0986,
            bid_close=1.0990,
            ask_open=1.0996,
            ask_high=1.1000,
            ask_low=1.0988,
            ask_close=1.0992,
        ),
    ]
    run = run_backtest(
        bars=bars,
        decisions=[
            _decision(
                "SHORT-TARGET",
                direction=Direction.SHORT,
                decision_timestamp=DAY1,
                executable_timestamp=DAY1 + timedelta(minutes=1),
                stop_price=1.1010,
                target_price=1.0990,
            )
        ],
        config=_config(scenario="short-target", code_commit=code_commit, bars=bars),
    )
    trade = run.trades[0]
    assert trade.units == 25_000
    assert trade.entry_reference_price == 1.1000
    assert trade.exit_reference_price == 1.0990
    assert abs(trade.gross_pnl_usd - 25.0) < 1e-9
    assert abs(trade.net_pnl_usd - 25.0) < 1e-9
    return run


def _ambiguity(code_commit: str) -> BacktestRun:
    bars = [
        _quote(DAY1),
        _quote(DAY1 + timedelta(minutes=1)),
        _quote(
            DAY1 + timedelta(minutes=2),
            bid_open=1.1000,
            bid_high=1.1025,
            bid_low=1.0988,
            bid_close=1.1000,
            ask_open=1.1002,
            ask_high=1.1027,
            ask_low=1.0990,
            ask_close=1.1002,
        ),
    ]
    run = run_backtest(
        bars=bars,
        decisions=[
            _decision(
                "AMBIGUITY",
                decision_timestamp=DAY1,
                executable_timestamp=DAY1 + timedelta(minutes=1),
                stop_price=1.0992,
                target_price=1.1020,
            )
        ],
        config=_config(scenario="ambiguity", code_commit=code_commit, bars=bars),
    )
    trade = run.trades[0]
    assert trade.exit_reason.value == "STOP"
    assert trade.intrabar_ambiguous is True
    assert trade.exit_reference_price == 1.0992
    return run


def _simultaneous_risk(code_commit: str) -> BacktestRun:
    t0 = DAY1
    t1 = DAY1 + timedelta(minutes=1)
    bars = sorted(
        [
            _quote(t0, symbol="EURUSD"),
            _quote(
                t0,
                symbol="GBPUSD",
                bid_open=1.3000,
                bid_high=1.3008,
                bid_low=1.2995,
                bid_close=1.3003,
                ask_open=1.3002,
                ask_high=1.3010,
                ask_low=1.2997,
                ask_close=1.3005,
            ),
            _quote(
                t0,
                symbol="USDJPY",
                bid_open=150.00,
                bid_high=150.08,
                bid_low=149.95,
                bid_close=150.03,
                ask_open=150.02,
                ask_high=150.10,
                ask_low=149.97,
                ask_close=150.05,
            ),
            _quote(t1, symbol="EURUSD"),
            _quote(
                t1,
                symbol="GBPUSD",
                bid_open=1.3000,
                bid_high=1.3008,
                bid_low=1.2995,
                bid_close=1.3003,
                ask_open=1.3002,
                ask_high=1.3010,
                ask_low=1.2997,
                ask_close=1.3005,
            ),
            _quote(
                t1,
                symbol="USDJPY",
                bid_open=150.00,
                bid_high=150.08,
                bid_low=149.95,
                bid_close=150.03,
                ask_open=150.02,
                ask_high=150.10,
                ask_low=149.97,
                ask_close=150.05,
            ),
        ],
        key=lambda bar: (bar.timestamp_utc, bar.symbol),
    )
    decisions = [
        _decision(
            "A",
            decision_timestamp=t0,
            executable_timestamp=t1,
            stop_price=1.0992,
            requested_risk_fraction=0.005,
        ),
        _decision(
            "B",
            symbol="GBPUSD",
            decision_timestamp=t0,
            executable_timestamp=t1,
            stop_price=1.2992,
            requested_risk_fraction=0.005,
        ),
        _decision(
            "C",
            symbol="USDJPY",
            decision_timestamp=t0,
            executable_timestamp=t1,
            stop_price=149.92,
            requested_risk_fraction=0.005,
        ),
    ]
    run = run_backtest(
        bars=bars,
        decisions=decisions,
        config=_config(scenario="simultaneous-risk", code_commit=code_commit, bars=bars),
    )
    assert [(item.decision_id, item.code) for item in run.rejections] == [
        ("C", RejectionCode.SIMULTANEOUS_RISK)
    ]
    assert {trade.decision_id for trade in run.trades} == {"A", "B"}
    return run


def _loss_bar(timestamp: datetime) -> QuoteBar:
    return _quote(
        timestamp,
        bid_open=1.1000,
        bid_high=1.1005,
        bid_low=1.0980,
        bid_close=1.0990,
        ask_open=1.1002,
        ask_high=1.1007,
        ask_low=1.0982,
        ask_close=1.0992,
    )


def _daily_halt_reset(code_commit: str) -> BacktestRun:
    bars: list[QuoteBar] = []
    for minute in range(10):
        timestamp = DAY1 + timedelta(minutes=minute)
        bars.append(_loss_bar(timestamp) if minute in {1, 3, 5, 7} else _quote(timestamp))
    bars.extend(
        [
            _quote(DAY2),
            _quote(
                DAY2 + timedelta(minutes=1),
                bid_open=1.1000,
                bid_high=1.1012,
                bid_low=1.0995,
                bid_close=1.1010,
                ask_open=1.1002,
                ask_high=1.1014,
                ask_low=1.0997,
                ask_close=1.1012,
            ),
        ]
    )
    decisions = [
        _decision(
            f"LOSS-{index}",
            decision_timestamp=DAY1 + timedelta(minutes=2 * (index - 1)),
            executable_timestamp=DAY1 + timedelta(minutes=2 * (index - 1) + 1),
            stop_price=1.0982,
            requested_risk_fraction=0.005,
        )
        for index in range(1, 5)
    ]
    decisions.extend(
        [
            _decision(
                "HALTED",
                decision_timestamp=DAY1 + timedelta(minutes=8),
                executable_timestamp=DAY1 + timedelta(minutes=9),
                stop_price=1.0982,
                requested_risk_fraction=0.005,
            ),
            _decision(
                "NEXT-DAY",
                decision_timestamp=DAY2,
                executable_timestamp=DAY2 + timedelta(minutes=1),
                stop_price=1.0982,
                target_price=1.1010,
                requested_risk_fraction=0.005,
            ),
        ]
    )
    run = run_backtest(
        bars=bars,
        decisions=decisions,
        config=_config(scenario="daily-halt-reset", code_commit=code_commit, bars=bars),
    )
    assert [(item.decision_id, item.code) for item in run.rejections] == [
        ("HALTED", RejectionCode.DAILY_HALT)
    ]
    assert [trade.decision_id for trade in run.trades] == [
        "LOSS-1",
        "LOSS-2",
        "LOSS-3",
        "LOSS-4",
        "NEXT-DAY",
    ]
    assert run.trades[-1].exit_timestamp_utc.date() == DAY2.date()
    return run


SCENARIO_BUILDERS = {
    "ambiguity": _ambiguity,
    "daily-halt-reset": _daily_halt_reset,
    "long-cost": _long_cost,
    "short-target": _short_target,
    "simultaneous-risk": _simultaneous_risk,
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_index(path: Path, payload: object) -> None:
    path.write_text(
        json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def generate_acceptance_evidence(*, out: Path, code_commit: str) -> dict[str, object]:
    if not code_commit.strip():
        raise ValueError("code commit must be non-empty")
    out.mkdir(parents=True, exist_ok=True)
    scenario_records: list[dict[str, object]] = []

    for name, builder in SCENARIO_BUILDERS.items():
        first = builder(code_commit)
        second = builder(code_commit)
        if first != second:
            raise AssertionError(f"scenario {name} is not semantically deterministic")

        primary_dir = out / "primary" / name
        repeat_dir = out / "repeat" / name
        write_backtest_artifacts(first, primary_dir)
        write_backtest_artifacts(second, repeat_dir)

        bytes_equal = all(
            (primary_dir / artifact).read_bytes() == (repeat_dir / artifact).read_bytes()
            for artifact in ARTIFACT_NAMES
        )
        if not bytes_equal:
            raise AssertionError(f"scenario {name} artifact bytes differ across repeated runs")

        scenario_records.append(
            {
                "name": name,
                "bytes_equal": True,
                "primary_manifest_sha256": _sha256(primary_dir / "manifest.json"),
                "repeat_manifest_sha256": _sha256(repeat_dir / "manifest.json"),
                "trade_count": len(first.trades),
                "rejection_count": len(first.rejections),
            }
        )

    index: dict[str, object] = {
        "protocol": PROTOCOL,
        "fixture_id": FIXTURE_ID,
        "code_commit": code_commit,
        "scenario_count": len(scenario_records),
        "scenarios": scenario_records,
    }
    _write_index(out / "acceptance-index.json", index)
    return index


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate deterministic Phase 3 acceptance artifacts")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--code-commit", required=True)
    return parser


def main() -> int:
    args = _parser().parse_args()
    index = generate_acceptance_evidence(out=args.out, code_commit=args.code_commit)
    print(json.dumps(index, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
