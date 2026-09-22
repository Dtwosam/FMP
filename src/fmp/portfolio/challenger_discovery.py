from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path

from .contracts import StrategyLifecycle, StrategyRecord, StrategyVersion

EXP015_ID = "EXP-20260922-015"
EXP015_STRATEGY_VERSION = "fmp-exp015-rule-challenger-v1"
EXP015_CATALOG_PROTOCOL = "fmp-phase8a-exp015-catalog-v1"
EXP015_CATALOG_ARTIFACT_PROTOCOL = "fmp-phase8a-exp015-catalog-artifacts-v1"

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


def exp015_catalog_identity_sha256(*, code_commit: str) -> str:
    records = build_exp015_challengers(code_commit=code_commit)
    payload = json.dumps(
        [item.strategy.fingerprint for item in records],
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def build_exp015_catalog_evidence(*, code_commit: str) -> dict[str, object]:
    records = build_exp015_challengers(code_commit=code_commit)
    return {
        "protocol": EXP015_CATALOG_PROTOCOL,
        "experiment_id": EXP015_ID,
        "promotion_authorized": False,
        "historical_status_mutation_authorized": False,
        "runner_code_commit": code_commit,
        "strategy_identity_count": len(records),
        "catalog_identity_sha256": exp015_catalog_identity_sha256(
            code_commit=code_commit
        ),
        "strategies": [
            {
                "fingerprint": item.strategy.fingerprint,
                "identity_json": item.strategy.identity_json,
                "family": item.strategy.family,
                "version": item.strategy.version,
                "symbol": item.strategy.symbol,
                "timeframe": item.strategy.timeframe,
                "parameters_json": item.strategy.parameters_json,
                "signal_contract_version": item.strategy.signal_contract_version,
                "lifecycle": item.lifecycle.value,
                "evidence_id": item.evidence_id,
            }
            for item in records
        ],
    }


def _stable_json_bytes(value: object) -> bytes:
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


def _atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(data)
    os.replace(temporary, path)


def write_exp015_catalog_artifacts(
    evidence: dict[str, object],
    out_dir: Path,
) -> dict[str, object]:
    if evidence.get("protocol") != EXP015_CATALOG_PROTOCOL:
        raise ValueError("EXP-015 catalog evidence protocol mismatch")
    if evidence.get("promotion_authorized") is not False:
        raise ValueError("EXP-015 catalog cannot authorize promotion")
    root = Path(out_dir)
    root.mkdir(parents=True, exist_ok=True)
    result_path = root / "catalog.json"
    payload = _stable_json_bytes(evidence)
    _atomic_write(result_path, payload)
    manifest = {
        "protocol": EXP015_CATALOG_ARTIFACT_PROTOCOL,
        "experiment_id": EXP015_ID,
        "promotion_authorized": False,
        "artifacts": [
            {
                "path": result_path.name,
                "size_bytes": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
            }
        ],
    }
    _atomic_write(root / "manifest.json", _stable_json_bytes(manifest))
    return manifest


__all__ = [
    "EXP015_CATALOG_ARTIFACT_PROTOCOL",
    "EXP015_CATALOG_PROTOCOL",
    "EXP015_ID",
    "EXP015_STRATEGY_VERSION",
    "build_exp015_catalog_evidence",
    "build_exp015_challengers",
    "exp015_catalog_identity_sha256",
    "write_exp015_catalog_artifacts",
]
