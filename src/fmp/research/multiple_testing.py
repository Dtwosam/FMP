"""Conservative multiple-testing adjustment for a fully enumerated hypothesis family.

This is a source-only statistical *tool*, not an adopted FMP promotion gate or
permission to run the annual catalogue. Benjamini-Yekutieli (2001) controls
false discovery rate under arbitrary dependence when its assumptions apply.
It adjusts supplied valid p-values; it does not calculate p-values, repair
selective reporting, establish data independence, or verify the family's
completeness. The caller must freeze and independently audit the family.

The existing historical trial ledger has an UNKNOWN programme-wide count.
Do not infer completeness from the five backfilled entries. This function
fails closed if the supplied total is unknown or does not match all inputs.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class FdrAssessment:
    family_id: str
    method: str
    alpha: float
    total_hypotheses: int
    adjusted_p_values: tuple[tuple[str, float], ...]
    rejected_hypotheses: tuple[str, ...]


def benjamini_yekutieli(
    p_values: Mapping[str, float],
    *,
    family_id: str,
    total_hypotheses: int | None,
    alpha: float = 0.05,
) -> FdrAssessment:
    """Adjust *every* p-value in a declared, complete, pre-specified family.

    The total is supplied externally; equality with the provided input count
    is only a structural check, never independent proof of a complete ledger.
    Never use a subset of winning tests or replace an unknown count with the
    number of surviving hypotheses.
    """
    if not isinstance(family_id, str) or not family_id.strip() or family_id != family_id.strip():
        raise ValueError("family_id must be a non-empty, normalized identifier")
    if isinstance(alpha, bool) or not isinstance(alpha, (int, float)):
        raise ValueError("alpha must be finite and strictly between 0 and 1")
    level = float(alpha)
    if not math.isfinite(level) or not 0.0 < level < 1.0:
        raise ValueError("alpha must be finite and strictly between 0 and 1")
    if not isinstance(p_values, Mapping) or not p_values:
        raise ValueError("p_values must be a nonempty mapping of all hypotheses")
    if (
        isinstance(total_hypotheses, bool)
        or not isinstance(total_hypotheses, int)
        or total_hypotheses < 1
        or total_hypotheses != len(p_values)
    ):
        raise ValueError("complete total_hypotheses is required and must equal the family size")

    ordered: list[tuple[str, float]] = []
    for hypothesis_id, value in p_values.items():
        if (
            not isinstance(hypothesis_id, str)
            or not hypothesis_id.strip()
            or hypothesis_id != hypothesis_id.strip()
        ):
            raise ValueError("hypothesis IDs must be non-empty normalized strings")
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"invalid p-value for {hypothesis_id}")
        p = float(value)
        if not math.isfinite(p) or not 0.0 <= p <= 1.0:
            raise ValueError(f"invalid p-value for {hypothesis_id}")
        ordered.append((hypothesis_id, p))

    ordered.sort(key=lambda item: (item[1], item[0]))
    m = total_hypotheses
    harmonic = math.fsum(1.0 / k for k in range(1, m + 1))
    adjusted: dict[str, float] = {}
    next_min = 1.0
    for rank_zero_indexed in range(m - 1, -1, -1):
        hypothesis_id, p = ordered[rank_zero_indexed]
        rank = rank_zero_indexed + 1
        next_min = min(next_min, 1.0, p * m * harmonic / rank)
        adjusted[hypothesis_id] = next_min

    sorted_adjusted = tuple(sorted(adjusted.items()))
    return FdrAssessment(
        family_id=family_id,
        method="benjamini_yekutieli",
        alpha=level,
        total_hypotheses=m,
        adjusted_p_values=sorted_adjusted,
        rejected_hypotheses=tuple(
            hypothesis_id
            for hypothesis_id, corrected_p in sorted_adjusted
            if corrected_p <= level
        ),
    )
