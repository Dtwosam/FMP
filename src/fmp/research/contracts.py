from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from datetime import date
from types import MappingProxyType
from typing import Mapping


@dataclass(frozen=True, slots=True)
class ResearchSplit:
    name: str
    start: date
    end_exclusive: date

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("research split name must be non-empty")
        if self.end_exclusive <= self.start:
            raise ValueError("research split end must be after start")


DEVELOPMENT_SPLIT = ResearchSplit("development", date(2015, 1, 1), date(2021, 1, 1))
VALIDATION_SPLIT = ResearchSplit("validation", date(2021, 1, 1), date(2024, 1, 1))
FINAL_TEST_SPLIT = ResearchSplit("final", date(2024, 1, 1), date(2026, 8, 21))


def allowed_split(name: str) -> ResearchSplit:
    if name == DEVELOPMENT_SPLIT.name:
        return DEVELOPMENT_SPLIT
    if name == VALIDATION_SPLIT.name:
        return VALIDATION_SPLIT
    if name == FINAL_TEST_SPLIT.name:
        raise ValueError("final test is not available from the normal Phase 4 runner")
    raise ValueError(f"unsupported Phase 4 research split: {name!r}")


def _freeze_mapping(value: Mapping[str, object]) -> Mapping[str, object]:
    return MappingProxyType(dict(value))


def _jsonable(value: object) -> object:
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_jsonable(item) for item in value]
    if value is None or isinstance(value, (str, int, bool)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("experiment config cannot contain non-finite floats")
        return value
    raise TypeError(f"unsupported experiment config value: {type(value).__name__}")


@dataclass(frozen=True, slots=True)
class ExperimentSpec:
    experiment_id: str
    hypothesis: str
    code_commit: str
    processed_manifest_sha256: str
    schema_version: str
    family_id: str
    strategy_version: str
    symbol: str
    timeframe: str
    split_name: str
    parameters: Mapping[str, object]
    slippage_pips: float
    commission_config: Mapping[str, object]
    financing_config: Mapping[str, object]
    risk_config: Mapping[str, object]

    def __post_init__(self) -> None:
        for field_name in (
            "experiment_id",
            "hypothesis",
            "code_commit",
            "processed_manifest_sha256",
            "schema_version",
            "family_id",
            "strategy_version",
            "symbol",
            "timeframe",
            "split_name",
        ):
            value = getattr(self, field_name)
            if not value.strip():
                raise ValueError(f"{field_name} must be non-empty")
        if not math.isfinite(self.slippage_pips) or self.slippage_pips < 0:
            raise ValueError("slippage_pips must be finite and non-negative")
        allowed_split(self.split_name)
        object.__setattr__(self, "parameters", _freeze_mapping(self.parameters))
        object.__setattr__(self, "commission_config", _freeze_mapping(self.commission_config))
        object.__setattr__(self, "financing_config", _freeze_mapping(self.financing_config))
        object.__setattr__(self, "risk_config", _freeze_mapping(self.risk_config))

    def config_sha256(self) -> str:
        payload = {
            "experiment_id": self.experiment_id,
            "hypothesis": self.hypothesis,
            "code_commit": self.code_commit,
            "processed_manifest_sha256": self.processed_manifest_sha256,
            "schema_version": self.schema_version,
            "family_id": self.family_id,
            "strategy_version": self.strategy_version,
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "split_name": self.split_name,
            "parameters": self.parameters,
            "slippage_pips": self.slippage_pips,
            "commission_config": self.commission_config,
            "financing_config": self.financing_config,
            "risk_config": self.risk_config,
        }
        encoded = json.dumps(
            _jsonable(payload),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()
