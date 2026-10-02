# Phase 8A Annual Pattern Catalogue In-Memory Miner

**Decision:** DEC-471  
**Experiment:** EXP-20261002-067  
**Status:** SOURCE-ONLY MINER / HISTORICAL EXECUTION LOCKED  
**Protocol:** DEC-470 Annual Pattern Catalogue V1  
**Protocol merge:** `e5b20a2d8b45e5eda54673060060fbb9f480f545`

## Purpose

DEC-471 implements the exact DEC-470 annual catalogue semantics in memory without adding any artifact loader, workflow, historical execution path, result production, Strategy V1 synthesis, or trading authority.

The miner operates on one annual segment × symbol × timeframe × fixed horizon at a time and emits the complete frozen Catalogue V1 directional record universe for that cell.

## Prior-only state construction

For each annual segment, continuous states are computed sequentially.

At observation T, each continuous dimension uses only finite same-year observations whose `available_at_utc` is strictly earlier than T. The implementation uses a deterministic order-statistic tree, so no later annual value is needed to compute an earlier state.

A continuous state is unavailable until at least 300 prior finite values exist. Tied lower/upper tertile cutpoints also make that dimension unavailable for the observation.

The current observation is inserted into the historical state only **after** its state has been encoded.

Session state continues to use the accepted deterministic session precedence.

## Exact annual boundaries

Both the signal observation and its fixed-horizon exit must stay inside the same annual segment.

An outcome whose signal begins in a year but whose 60m/240m exit crosses the annual boundary is excluded from that annual catalogue. This prevents one year's catalogue from borrowing future outcome information from the next segment.

## Complete record generation

For every one of DEC-470's 2,485 pattern conditions, the miner evaluates both LONG and SHORT.

Therefore every cell/horizon annual result contains exactly **4,970** directional records.

No record disappears because it is unprofitable, weak, or unsupported.

A record with support below 75 remains present and is marked non-evaluable. A zero-support record keeps null economic statistics.

Supported records preserve:

- support;
- evaluable flag;
- mean and median net pips at 0.5-pip cost;
- win rate at 0.5-pip cost;
- mean and median net pips at 1.0-pip stress;
- a deterministic event-set fingerprint.

The miner contains no winner-selection, shortlist, reranking, strategy-compilation, or promotion logic.

## Snapshot and transition matching

Snapshot events are indexed by exact encoded state.

Two-dimension snapshot conditions use the intersection of their two atomic event sets.

Temporal transitions require an encoded observation at exactly T−60m or T−240m. A nearby observation such as T−59m cannot satisfy the transition.

The prior observation itself does not need an outcome row; only the current event needs the requested fixed-horizon outcome.

## Deterministic identities

Every record binds:

- DEC-470 protocol fingerprint;
- annual segment;
- symbol;
- timeframe;
- horizon;
- direction;
- exact pattern family/condition;
- canonical cross-year pattern fingerprint;
- annual record identity;
- event-set fingerprint.

Year remains excluded from the canonical pattern fingerprint and included in the annual-record identity, preserving the DEC-470 cross-year comparison contract.

## Synthetic verification

Focused tests prove that:

- exactly 4,970 records are emitted even from a tiny annual fixture;
- weak and zero-support records remain present;
- the first continuous state appears only after 300 strictly prior values;
- adding a later extreme value cannot change earlier encoded states;
- exact T−60m transition matching works while T−59m does not;
- outcomes crossing an annual boundary are excluded;
- duplicate feature/outcome identities fail closed;
- all runtime, Strategy V1, and trading authorities remain false.

## Authority

DEC-471 is source-only.

It does not authorize:

- reading historical artifacts;
- annual catalogue execution on the accepted collection;
- historical or cross-year result production;
- Strategy V1 synthesis;
- candidate compilation or promotion;
- Phase 8B;
- demo orders;
- broker mutation;
- live orders;
- real-money action or trading.

## Next gate

`SOURCE_ONLY_ANNUAL_PATTERN_CATALOGUE_EVIDENCE_CONTRACT`

That gate must freeze how each annual cell result and later aggregate catalogue evidence are serialized, fingerprinted, validated, and cross-bound before any full-history loader/runtime is opened.
