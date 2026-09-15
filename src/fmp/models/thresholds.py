from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Sequence


RETAINED_FRACTIONS = (0.75, 0.50, 0.25)


@dataclass(frozen=True, slots=True)
class ScoreCutoff:
    retained_fraction: float
    fit_index: int
    score: float
    fit_row_count: int
    fit_retained_count: int
    fit_retained_rate: float

    def admits(self, model_score: float) -> bool:
        value = float(model_score)
        if not math.isfinite(value):
            raise ValueError("Phase 6 model score must be finite")
        return value >= self.score


def derive_fit_cutoffs(scores: Sequence[float]) -> tuple[ScoreCutoff, ScoreCutoff, ScoreCutoff]:
    values = tuple(float(value) for value in scores)
    if not values:
        raise ValueError("Phase 6 fit score distribution must be non-empty")
    if any(not math.isfinite(value) for value in values):
        raise ValueError("Phase 6 fit scores must be finite")
    if any(value < 0.0 or value > 1.0 for value in values):
        raise ValueError("Phase 6 fit scores must be in [0, 1]")

    ordered = tuple(sorted(values))
    count = len(ordered)
    out: list[ScoreCutoff] = []
    for retained_fraction in RETAINED_FRACTIONS:
        index = min(count - 1, math.ceil((1.0 - retained_fraction) * count))
        cutoff = ordered[index]
        retained_count = sum(value >= cutoff for value in values)
        out.append(
            ScoreCutoff(
                retained_fraction=retained_fraction,
                fit_index=index,
                score=cutoff,
                fit_row_count=count,
                fit_retained_count=retained_count,
                fit_retained_rate=retained_count / count,
            )
        )
    return tuple(out)  # type: ignore[return-value]
