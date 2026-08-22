# FMP V1 Data Specification

**Status:** Approved baseline  
**Canonical source candidate:** Dukascopy historical forex data  
**Development cost:** $0

## 1. Instruments

Only:

- EUR/USD (`EURUSD` internal symbol)
- GBP/USD (`GBPUSD` internal symbol)
- USD/JPY (`USDJPY` internal symbol)

## 2. Coverage target

Target approximately 2015 through the latest **complete** available period. Exact usable start/end timestamps are determined by Phase 1 acquisition and Phase 2 quality analysis; they are not fabricated to make all symbols match.

## 3. Time standard

All stored timestamps use UTC. Session features must be timezone-aware and daylight-saving aware.

## 4. Canonical resolution

Canonical research resolution: **1 minute**.

Derived internally from canonical data:

- 5 minutes
- 15 minutes
- 1 hour

Tick data is deferred to later execution-quality validation for strategies that already pass earlier gates.

## 5. Quote semantics

Bid and ask must remain separate. A midpoint may be derived for analysis but may not replace realistic bid/ask execution logic.

### Minimum canonical columns

| Field | Meaning |
|---|---|
| `timestamp_utc` | bar timestamp in UTC |
| `symbol` | normalized internal instrument ID |
| `bid_open` | bid open |
| `bid_high` | bid high |
| `bid_low` | bid low |
| `bid_close` | bid close |
| `ask_open` | ask open |
| `ask_high` | ask high |
| `ask_low` | ask low |
| `ask_close` | ask close |
| `bid_volume` | source-provided activity/volume if available |
| `ask_volume` | source-provided activity/volume if available |
| `source` | original data source ID |
| `ingestion_version` | version of ingestion logic |
| `schema_version` | canonical schema version |

If a source cannot provide a volume field, use a documented null/missing representation; do not invent volume.

## 6. Derived quote fields

Processed data may add:

- midpoint OHLC where useful
- spread at open/high/low/close under explicitly defined semantics
- spread in price units and pips
- source activity ratios
- missing-gap flags
- market-open/session annotations

Derived columns must be reproducible and versioned.

## 7. Raw-data immutability

Raw source files are append-only/immutable artifacts. Never:

- fix rows manually
- delete ugly spreads manually
- remove gaps to make charts cleaner
- overwrite the only source copy with normalized data

Any correction belongs in transformation code with tests and provenance.

## 8. Data directory policy

```text
data/
  raw/          # source-faithful; ignored by Git
  manifests/    # provenance, hashes, coverage summaries; Git-eligible if small
  processed/    # normalized canonical + derived bars; ignored by Git
  features/     # versioned feature datasets; ignored by Git
```

## 9. Required ingestion manifest

For every acquired chunk/file, record at minimum:

- source
- retrieval method/version
- symbol
- requested start/end
- actual start/end
- row count
- file path
- byte size
- checksum (SHA-256 preferred)
- retrieval timestamp UTC
- warnings/errors

## 10. Phase 1 acquisition rules

- Acquisition must be scripted/reproducible once the official/free retrieval path is chosen.
- Use bounded chunks so failed downloads can resume without restarting the whole history.
- Retries must be rate-conscious and deterministic.
- Partial/corrupt files must not masquerade as successful chunks.
- No private broker credentials are required for the historical-data phase.

## 11. Data validation rules

Before research eligibility, measure and report:

### Structural
- monotonic timestamp order after normalization
- duplicate `symbol + timestamp`
- null required fields
- schema/type failures

### Quote sanity
- ask below bid anomalies
- OHLC internal inconsistency (`low <= open/close <= high`)
- non-positive/invalid prices
- extreme one-bar price jumps
- spread outliers

### Time continuity
- missing 1-minute intervals during expected open-market periods
- weekend closure gaps
- known/likely holiday closures
- unexpectedly long weekday gaps

The system flags suspicious observations. It does not silently rewrite them.

## 12. Resampling contract

For each side independently:

```text
open  = first valid open in interval
high  = max high in interval
low   = min low in interval
close = last valid close in interval
```

Volume/activity aggregation rules are source-dependent and must be explicitly tested before use.

Timestamp labels and closed/open interval conventions must be frozen in Phase 2 and covered by unit tests, including exact boundary examples.

## 13. Market sessions

Session features are derived, not stored as source truth. They must account for DST using named time zones rather than hard-coded UTC hours.

At minimum support labels for:

- Asia
- London
- New York
- London/New York overlap

Exact session definitions must be documented in code and tests during Phase 5.

## 14. Volume caveat

Spot FX is decentralized. Dukascopy/source volume is not total global forex volume. Treat it as source-local/relative activity unless proven otherwise. Research may test relative activity features, but documentation must not describe the value as total global market volume.

## 15. Data-version identity

A research run must be able to cite a data snapshot using an immutable manifest/version. If data is refreshed, the prior manifest remains recoverable.

## 16. Phase 1 exit gate

Phase 1 passes when all three symbols have reproducibly acquired canonical-source raw history with manifests, checksums, resume behavior, and automated acquisition tests on a small bounded sample.

Phase 1 does **not** claim the dataset is research-clean. That is Phase 2.

## 17. Phase 2 exit gate

Phase 2 passes when:

- canonical schema is frozen and tested;
- all three pair histories are normalized;
- quality report quantifies gaps/anomalies rather than hiding them;
- deterministic 5m/15m/1h bars are produced;
- boundary/DST/resampling tests pass;
- a versioned processed-data manifest exists.
