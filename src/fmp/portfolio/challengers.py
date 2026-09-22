from __future__ import annotations

import re

from .contracts import StrategyLifecycle, StrategyRecord, StrategyVersion

EXP013_ID = "EXP-20260922-013"
OPENING_RANGE_MOMENTUM_VERSION = "fmp-opening-range-momentum-v1"
OPENING_RANGE_MOMENTUM_SIGNAL_CONTRACT = "opening-range-momentum-signal-v1"
_COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")


def build_opening_range_momentum_challengers(
    *,
    code_commit: str,
) -> tuple[StrategyRecord, ...]:
    if not _COMMIT_RE.fullmatch(code_commit):
        raise ValueError("code_commit must be a 40-character lowercase hexadecimal SHA")

    records: list[StrategyRecord] = []
    for symbol in ("EURUSD", "GBPUSD", "USDJPY"):
        for timeframe in ("5m", "15m", "1h"):
            for body_fraction_threshold in (0.50, 0.70):
                for target_r_multiple in (1.0, 1.5):
                    strategy = StrategyVersion.create(
                        family="opening_range_momentum",
                        version=OPENING_RANGE_MOMENTUM_VERSION,
                        symbol=symbol,
                        timeframe=timeframe,
                        parameters={
                            "body_fraction_threshold": body_fraction_threshold,
                            "target_r_multiple": target_r_multiple,
                        },
                        signal_contract_version=OPENING_RANGE_MOMENTUM_SIGNAL_CONTRACT,
                        code_commit=code_commit,
                    )
                    records.append(
                        StrategyRecord(
                            strategy=strategy,
                            lifecycle=StrategyLifecycle.CHALLENGER,
                            evidence_id=f"{EXP013_ID}:PREDECLARED",
                        )
                    )

    fingerprints = [item.strategy.fingerprint for item in records]
    if len(set(fingerprints)) != 36:
        raise RuntimeError("EXP-013 challenger catalog identity collision")
    return tuple(sorted(records, key=lambda item: item.strategy.fingerprint))
