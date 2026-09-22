from __future__ import annotations

from collections.abc import Iterable

from .contracts import (
    PHASE8A_EXPERIMENT_ID,
    ChampionSet,
    StrategyLifecycle,
    StrategyRecord,
)

_ORDERED_NEXT = {
    StrategyLifecycle.DISCOVERY: StrategyLifecycle.CHALLENGER,
    StrategyLifecycle.CHALLENGER: StrategyLifecycle.HISTORICAL_QUALIFIED,
    StrategyLifecycle.HISTORICAL_QUALIFIED: StrategyLifecycle.SHADOW_CANDIDATE,
    StrategyLifecycle.SHADOW_CANDIDATE: StrategyLifecycle.SHADOW_VALIDATED,
    StrategyLifecycle.SHADOW_VALIDATED: StrategyLifecycle.DEMO_ELIGIBLE,
}

_SHADOW_CHAMPION_STATES = frozenset(
    {
        StrategyLifecycle.SHADOW_CANDIDATE,
        StrategyLifecycle.SHADOW_VALIDATED,
        StrategyLifecycle.DEMO_ELIGIBLE,
    }
)


def transition_strategy(
    record: StrategyRecord,
    to_lifecycle: StrategyLifecycle,
    *,
    evidence_id: str,
) -> StrategyRecord:
    if not isinstance(record, StrategyRecord):
        raise TypeError("record must be StrategyRecord")
    if not isinstance(to_lifecycle, StrategyLifecycle):
        raise TypeError("to_lifecycle must be StrategyLifecycle")
    if record.lifecycle is StrategyLifecycle.RETIRED:
        raise ValueError("RETIRED is terminal")
    if to_lifecycle is record.lifecycle:
        raise ValueError("lifecycle transition must change state")

    if to_lifecycle is not StrategyLifecycle.RETIRED:
        expected = _ORDERED_NEXT.get(record.lifecycle)
        if expected is not to_lifecycle:
            raise ValueError(
                f"invalid lifecycle transition: {record.lifecycle.value} -> {to_lifecycle.value}"
            )

    return StrategyRecord(
        strategy=record.strategy,
        lifecycle=to_lifecycle,
        evidence_id=evidence_id,
    )


def freeze_shadow_champion_set(
    records: Iterable[StrategyRecord],
    *,
    champion_set_id: str,
) -> ChampionSet:
    materialized = tuple(records)
    if not materialized:
        raise ValueError("at least one strategy record is required")
    for record in materialized:
        if not isinstance(record, StrategyRecord):
            raise TypeError("champion records must be StrategyRecord")
        if record.lifecycle not in _SHADOW_CHAMPION_STATES:
            raise ValueError(
                f"strategy {record.strategy.fingerprint} is not shadow-eligible: "
                f"{record.lifecycle.value}"
            )

    strategies = tuple(sorted((record.strategy for record in materialized), key=lambda item: item.fingerprint))
    fingerprints = tuple(item.fingerprint for item in strategies)
    if len(set(fingerprints)) != len(fingerprints):
        raise ValueError("duplicate strategy version in champion records")

    return ChampionSet(
        champion_set_id=champion_set_id,
        experiment_id=PHASE8A_EXPERIMENT_ID,
        strategies=strategies,
    )
