from __future__ import annotations

from collections.abc import Iterable

from .contracts import StrategyLifecycle, StrategyRecord, StrategyVersion

_SYMBOLS = ("EURUSD", "GBPUSD", "USDJPY")
_TIMEFRAMES = ("5m", "15m", "1h")

_PHASE4_IMPLEMENTATION_COMMITS = {
    "session_breakout": "cc01929b80cbd1d5619de8476caa8f3d3410262e",
    "trend_continuation": "d1c821cb8b4bfaaddbc334fee0f2f3b1dfe054a2",
    "mean_reversion": "87003a3982ca61eb6fd030c5291616d98dbb0c1a",
    "previous_day_rejection": "7db3a747236942fa393521e5866e3245d1a22a99",
    "volatility_breakout": "3bf36186900f5065e9e3ddced0305865433b9d69",
    "session_sweep_rejection": "120348d4a5df806f674551590610b216a9bc33ac",
}

_PHASE4_EXPERIMENT_IDS = {
    "session_breakout": "EXP-20260914-001",
    "trend_continuation": "EXP-20260914-002",
    "mean_reversion": "EXP-20260914-003",
    "previous_day_rejection": "EXP-20260914-004",
    "volatility_breakout": "EXP-20260914-005",
    "session_sweep_rejection": "EXP-20260914-006",
}

_SIGNAL_CONTRACT_VERSION = "phase4-baseline-signal-v1"


def _record(
    *,
    family: str,
    symbol: str,
    timeframe: str,
    parameters: dict[str, object],
) -> StrategyRecord:
    lifecycle = StrategyLifecycle.RETIRED
    evidence_id = f"{_PHASE4_EXPERIMENT_IDS[family]}:NOT_PROMOTED"

    if (
        family == "session_breakout"
        and symbol == "USDJPY"
        and timeframe == "15m"
        and parameters == {"buffer_pips": 5, "target_range_multiple": 1.5}
    ):
        lifecycle = StrategyLifecycle.HISTORICAL_QUALIFIED
        evidence_id = "EXP-20260915-008:PHASE7_PROMOTE_TO_SHADOW_DESIGN"
    elif (
        family == "volatility_breakout"
        and symbol == "USDJPY"
        and timeframe == "1h"
        and parameters == {"range_multiplier": 2.0}
    ):
        evidence_id = "EXP-20260915-008:STAGE1_REJECT"

    return StrategyRecord(
        strategy=StrategyVersion.create(
            family=family,
            version=_PHASE4_EXPERIMENT_IDS[family],
            symbol=symbol,
            timeframe=timeframe,
            parameters=parameters,
            signal_contract_version=_SIGNAL_CONTRACT_VERSION,
            code_commit=_PHASE4_IMPLEMENTATION_COMMITS[family],
        ),
        lifecycle=lifecycle,
        evidence_id=evidence_id,
    )


def _session_breakout_records() -> Iterable[StrategyRecord]:
    for symbol in _SYMBOLS:
        for timeframe in _TIMEFRAMES:
            for buffer_pips in (0, 2, 5):
                for target_range_multiple in (0.5, 1.0, 1.5):
                    yield _record(
                        family="session_breakout",
                        symbol=symbol,
                        timeframe=timeframe,
                        parameters={
                            "buffer_pips": buffer_pips,
                            "target_range_multiple": target_range_multiple,
                        },
                    )


def _trend_continuation_records() -> Iterable[StrategyRecord]:
    for symbol in _SYMBOLS:
        for timeframe in _TIMEFRAMES:
            for trend_window_id in ("A", "B", "C"):
                for target_r_multiple in (1.0, 1.5):
                    yield _record(
                        family="trend_continuation",
                        symbol=symbol,
                        timeframe=timeframe,
                        parameters={
                            "target_r_multiple": target_r_multiple,
                            "trend_window_id": trend_window_id,
                        },
                    )


def _mean_reversion_records() -> Iterable[StrategyRecord]:
    for symbol in _SYMBOLS:
        for timeframe in _TIMEFRAMES:
            for lookback_hours in (4, 8, 16):
                for threshold_sigma in (1.5, 2.0):
                    yield _record(
                        family="mean_reversion",
                        symbol=symbol,
                        timeframe=timeframe,
                        parameters={
                            "lookback_hours": lookback_hours,
                            "threshold_sigma": threshold_sigma,
                        },
                    )


def _previous_day_rejection_records() -> Iterable[StrategyRecord]:
    for symbol in _SYMBOLS:
        for timeframe in _TIMEFRAMES:
            for buffer_pips in (0, 2, 5):
                yield _record(
                    family="previous_day_rejection",
                    symbol=symbol,
                    timeframe=timeframe,
                    parameters={"buffer_pips": buffer_pips},
                )


def _volatility_breakout_records() -> Iterable[StrategyRecord]:
    for symbol in _SYMBOLS:
        for timeframe in _TIMEFRAMES:
            for range_multiplier in (1.0, 1.5, 2.0):
                yield _record(
                    family="volatility_breakout",
                    symbol=symbol,
                    timeframe=timeframe,
                    parameters={"range_multiplier": range_multiplier},
                )


def _session_sweep_rejection_records() -> Iterable[StrategyRecord]:
    for symbol in _SYMBOLS:
        for timeframe in _TIMEFRAMES:
            for buffer_pips in (0, 2, 5):
                yield _record(
                    family="session_sweep_rejection",
                    symbol=symbol,
                    timeframe=timeframe,
                    parameters={"buffer_pips": buffer_pips},
                )


def build_phase4_baseline_inventory() -> tuple[StrategyRecord, ...]:
    records = tuple(
        item
        for family_records in (
            _session_breakout_records(),
            _trend_continuation_records(),
            _mean_reversion_records(),
            _previous_day_rejection_records(),
            _volatility_breakout_records(),
            _session_sweep_rejection_records(),
        )
        for item in family_records
    )
    fingerprints = [item.strategy.fingerprint for item in records]
    if len(set(fingerprints)) != len(fingerprints):
        raise RuntimeError("historical strategy inventory contains duplicate identities")
    return tuple(sorted(records, key=lambda item: item.strategy.fingerprint))
