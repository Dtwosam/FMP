from __future__ import annotations

import re

from .contracts import StrategyLifecycle, StrategyRecord, StrategyVersion

EXP015_ID = "EXP-20260922-015"
EXP015_STRATEGY_VERSION = "fmp-exp015-rule-challenger-v1"

_SYMBOLS = ("EURUSD", "GBPUSD", "USDJPY")
_TIMEFRAMES = ("5m", "15m", "1h")
_COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")

_SIGNAL_CONTRACTS = {
    "session_breakout": "session-breakout-signal-v1",
    "trend_continuation": "trend-continuation-signal-v1",
    "mean_reversion": "mean-reversion-signal-v1",
    "previous_day_rejection": "previous-day-rejection-signal-v1",
    "volatility_breakout": "volatility-breakout-signal-v1",
    "session_sweep_rejection": "session-sweep-rejection-signal-v1",
}


def _record(
    *,
    family: str,
    symbol: str,
    timeframe: str,
    parameters: dict[str, object],
    code_commit: str,
) -> StrategyRecord:
    return StrategyRecord(
        strategy=StrategyVersion.create(
            family=family,
            version=EXP015_STRATEGY_VERSION,
            symbol=symbol,
            timeframe=timeframe,
            parameters=parameters,
            signal_contract_version=_SIGNAL_CONTRACTS[family],
            code_commit=code_commit,
        ),
        lifecycle=StrategyLifecycle.CHALLENGER,
        evidence_id=f"{EXP015_ID}:PREDECLARED",
    )


def build_exp015_challengers(
    *,
    code_commit: str,
) -> tuple[StrategyRecord, ...]:
    if not _COMMIT_RE.fullmatch(code_commit):
        raise ValueError(
            "code_commit must be a 40-character lowercase hexadecimal SHA"
        )

    records: list[StrategyRecord] = []
    for symbol in _SYMBOLS:
        for timeframe in _TIMEFRAMES:
            for buffer_pips in (1, 3, 4, 6, 8):
                for target_range_multiple in (0.75, 1.25, 1.75, 2.0):
                    records.append(
                        _record(
                            family="session_breakout",
                            symbol=symbol,
                            timeframe=timeframe,
                            parameters={
                                "buffer_pips": buffer_pips,
                                "target_range_multiple": target_range_multiple,
                            },
                            code_commit=code_commit,
                        )
                    )

            for trend_window_id in ("A", "B", "C"):
                for target_r_multiple in (0.75, 1.25, 1.75, 2.0):
                    records.append(
                        _record(
                            family="trend_continuation",
                            symbol=symbol,
                            timeframe=timeframe,
                            parameters={
                                "trend_window_id": trend_window_id,
                                "target_r_multiple": target_r_multiple,
                            },
                            code_commit=code_commit,
                        )
                    )

            for lookback_hours in (2, 6, 12, 24):
                for threshold_sigma in (1.25, 1.75, 2.25, 2.5):
                    records.append(
                        _record(
                            family="mean_reversion",
                            symbol=symbol,
                            timeframe=timeframe,
                            parameters={
                                "lookback_hours": lookback_hours,
                                "threshold_sigma": threshold_sigma,
                            },
                            code_commit=code_commit,
                        )
                    )

            for buffer_pips in (1, 3, 4, 6, 8):
                records.append(
                    _record(
                        family="previous_day_rejection",
                        symbol=symbol,
                        timeframe=timeframe,
                        parameters={"buffer_pips": buffer_pips},
                        code_commit=code_commit,
                    )
                )

            for range_multiplier in (0.75, 1.25, 1.75, 2.25, 2.5):
                records.append(
                    _record(
                        family="volatility_breakout",
                        symbol=symbol,
                        timeframe=timeframe,
                        parameters={"range_multiplier": range_multiplier},
                        code_commit=code_commit,
                    )
                )

            for buffer_pips in (1, 3, 4, 6, 8):
                records.append(
                    _record(
                        family="session_sweep_rejection",
                        symbol=symbol,
                        timeframe=timeframe,
                        parameters={"buffer_pips": buffer_pips},
                        code_commit=code_commit,
                    )
                )

    fingerprints = [item.strategy.fingerprint for item in records]
    if len(records) != 567:
        raise RuntimeError("EXP-015 challenger catalog must contain exactly 567 records")
    if len(set(fingerprints)) != 567:
        raise RuntimeError("EXP-015 challenger catalog identity collision")
    return tuple(sorted(records, key=lambda item: item.strategy.fingerprint))


__all__ = [
    "EXP015_ID",
    "EXP015_STRATEGY_VERSION",
    "build_exp015_challengers",
]
