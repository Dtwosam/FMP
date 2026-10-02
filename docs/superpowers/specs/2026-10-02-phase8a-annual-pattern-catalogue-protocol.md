# Phase 8A Annual Pattern Catalogue Protocol and Full-Collection Research Access

**Decision:** DEC-470  
**Experiment:** EXP-20261002-067  
**Status:** SOURCE-ONLY PROTOCOL FROZEN / HISTORICAL EXECUTION LOCKED  
**Parent method:** DEC-469 annual pattern catalogue discovery

## Purpose

DEC-470 turns the annual-first method into an exact bounded protocol before any annual catalogue is executed.

The protocol is deliberately broad enough to catalogue several kinds of market behaviour, but bounded enough that “derive every pattern” has an auditable meaning. Every pattern means every directional hypothesis in the frozen Catalogue V1 grammar, including weak, negative, and insufficient-support records.

## Historical collection decision

DEC-470 explicitly authorizes the **full accepted collection** for the annual catalogue research design:

- 2015 through 2025 as full calendar-year segments;
- 2026 as the partial segment 2026-01-01 through 2026-08-20.

The 2023-2026 block that EXP-061 through EXP-065 kept closed is now repurposed **only for the DEC-469 annual-catalogue / Strategy V1 research path**.

This does not reopen or rerun EXP-061, EXP-062, EXP-063, EXP-064, or EXP-065.

This also permanently means that 2023-2026 cannot be described as untouched OOS for Strategy V1 once used by the catalogue. Strategy V1's genuinely fresh evidence begins only after Strategy V1 is frozen.

DEC-470 still does not authorize artifact reads or historical execution. It authorizes the research scope so the later loader/runtime can be built against all collected years without another ambiguity about the former reserve.

## Market vocabulary

Catalogue V1 reuses the accepted DEC-270 measurement universe:

- EURUSD, GBPUSD, USDJPY;
- 5m, 15m, 1h;
- fixed 60m and 240m future outcomes;
- the same 20 accepted leakage-safe continuous measurements;
- deterministic session state.

No new raw data, feature, symbol, timeframe, horizon, or alternative data source is introduced.

## Leakage-safe annual state encoding

Each annual segment is independent.

For every continuous measurement at observation time T:

1. use only finite observations from the same symbol/timeframe and same annual segment with `available_at_utc < T`;
2. require at least 300 prior finite values;
3. compute empirical tertiles with the frozen DEC-270 index formula;
4. classify the current value as LOW, MID, or HIGH;
5. if prior support is insufficient or cutpoints tie, that dimension is unavailable for that observation.

No later row in the year may affect an earlier state.

Session state retains the existing deterministic session precedence.

## Catalogue V1 pattern grammar

Three pattern families are frozen.

### 1. Snapshot single-state patterns

One state from one dimension.

- 20 continuous dimensions × 3 states = 60;
- session dimension × 5 states = 5;
- total = **65**.

### 2. Snapshot two-dimension patterns

Two simultaneous states from two **different** dimensions.

The exact cross-dimension Cartesian count is **2,010**.

No same-dimension contradictory pair and no three-predicate snapshot is allowed.

### 3. Same-dimension temporal transitions

Prior state -> current state for one dimension at an exact lag.

Frozen lags: **60 minutes and 240 minutes**.

- 20 continuous dimensions × 3 prior states × 3 current states × 2 lags = 360;
- session dimension × 5 prior states × 5 current states × 2 lags = 50;
- total = **410**.

The prior observation must exist at the exact timestamp T-lag. Nearby rows do not substitute.

Cross-dimension transitions and sequences longer than prior -> current are not part of Catalogue V1.

## Search-volume accounting

Per symbol/timeframe/horizon cell:

- pattern conditions = 65 + 2,010 + 410 = **2,485**;
- LONG/SHORT directions = 2;
- directional hypotheses = **4,970**.

Across 18 symbol/timeframe/horizon cells:

- directional hypotheses per annual segment = **89,460**.

Across 12 annual segments:

- annual directional records = **1,073,520**.

The canonical cross-year hypothesis universe is **89,460** because the canonical pattern identity excludes year.

These are nominal records. Missing state availability or low support does not delete a pattern identity.

## Annual catalogue evidence

Every nominal annual pattern record is retained.

A record is called evaluable only with at least **75** matched observations, but insufficient-support records remain in the catalogue.

For evaluable records, preserve at minimum:

- support;
- mean net pips at 0.5-pip slippage;
- median net pips at 0.5;
- win rate at 0.5;
- mean net pips at 1.0-pip stress;
- median net pips at 1.0.

The annual catalogue does not select winners and does not rerank patterns. Its job is to describe that year completely under the frozen grammar.

Both observation time and the fixed-horizon exit must remain inside the same annual segment. A late-year signal whose outcome crosses into the next annual segment is excluded from that year's support.

## Canonical cross-year comparison

The canonical pattern fingerprint excludes year but includes:

- pattern family and exact condition;
- symbol;
- timeframe;
- horizon;
- direction;
- protocol version.

This lets the exact same behavioural hypothesis be compared across annual catalogues.

Before any results exist, DEC-470 freezes the cross-year carry-forward gate:

- at least 9 evaluable annual segments;
- at least 80% of evaluable segments positive at 0.5-pip cost;
- at least 2/3 of evaluable segments positive at 1.0-pip stress;
- median annual 0.5-pip mean at least 0.10 pips;
- pooled 0.5-pip mean at least 0.25 pips;
- pooled 1.0-pip stress mean strictly positive;
- no more than 3 chronological positive/non-positive sign flips.

Qualifying cross-year hypotheses are ranked by:

1. base positive-year fraction;
2. stress positive-year fraction;
3. worst evaluable annual 0.5-pip mean;
4. median annual 0.5-pip mean;
5. pooled 0.5-pip mean;
6. pooled 1.0-pip mean;
7. total support;
8. canonical fingerprint.

Near-duplicates use same-cell/family/direction event-set Jaccard >= 0.90 and retain the higher-ranked hypothesis.

Carry-forward is capped at **5 per cell/family**, at most **270 globally**.

This shortlist is still pattern evidence, not Strategy V1.

## What remains locked

DEC-470 does not authorize:

- historical artifact reads;
- annual catalogue execution;
- annual result production;
- cross-year result production;
- Strategy V1 synthesis;
- candidate compilation or promotion;
- Phase 8B;
- demo orders;
- broker mutation;
- live orders;
- real-money action or trading.

## Next gate

`SOURCE_ONLY_ANNUAL_PATTERN_CATALOGUE_MINER`

The miner must implement this exact annual-first grammar and evidence semantics in memory before any loader/runtime is allowed.
