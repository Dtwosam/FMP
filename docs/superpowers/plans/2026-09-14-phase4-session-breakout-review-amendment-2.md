# Phase 4 Session-Breakout Plan Self-Review Amendment 2

This file is authoritative over Task 3 of `2026-09-14-phase4-session-breakout.md` and complements `2026-09-14-phase4-session-breakout-review-amendments.md`.

Replace Task 3's bare tuple return with a frozen result record so later tasks do not depend on an undefined diagnostic side channel:

```python
@dataclass(frozen=True, slots=True)
class LoadedResearchBars:
    bars: tuple[QuoteBar, ...]
    excluded_incomplete_count: int
    eligible_utc_dates: tuple[date, ...]


def load_processed_bars(
    *,
    dataset_root: Path,
    manifest_path: Path,
    symbol: str,
    timeframe: str,
    split_name: str,
) -> LoadedResearchBars:
    ...
```

`eligible_utc_dates` is the sorted unique UTC-date set from retained complete bars. Task 5 consumes `.bars`; Task 6 consumes `.eligible_utc_dates`; Task 7 records `.excluded_incomplete_count` in benchmark evidence.

`tests/test_phase4_research_data.py` must assert all three fields exactly in addition to the manifest, duplicate, ordering, split, timeframe, and final-test-lock cases already listed in Task 3.

No implementation has started.