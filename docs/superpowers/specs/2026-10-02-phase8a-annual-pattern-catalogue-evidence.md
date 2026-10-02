# Phase 8A Annual Pattern Catalogue Evidence Contract

**Decision:** DEC-472  
**Experiment:** EXP-20261002-067  
**Status:** SOURCE-ONLY EVIDENCE CONTRACT / HISTORICAL EXECUTION LOCKED  
**Source miner:** DEC-471 merge `3926daa8b64ca18c69d5a95a7b31b960dddde27b`

## Purpose

DEC-472 freezes how complete year-by-year Catalogue V1 results are serialized, fingerprinted, semantically validated, summarized, and combined into the exact full-collection matrix before any historical artifact loader/runtime is opened.

This layer does not read historical artifacts and cannot produce authoritative catalogue evidence by itself.

## Cell payload

One cell payload represents exactly:

`annual segment × symbol × timeframe × fixed horizon`

It contains the exact DEC-471 result identity, feature/outcome row counts, protocol fingerprint, and all **4,970** directional pattern records.

Every record preserves:

- canonical cross-year pattern fingerprint;
- annual record identity;
- annual segment;
- symbol/timeframe/horizon/direction;
- family, dimensions, states, and transition lag;
- event-set fingerprint;
- support/evaluable state;
- base/stress mean and median;
- base-cost win rate.

The payload is canonical JSON and receives its own SHA-256 and byte length.

## Semantic validation

Validation does not trust an outer hash alone.

After checking the payload hash, the validator reconstructs the complete frozen DEC-470 record universe in deterministic order and recomputes every canonical pattern fingerprint and annual record identity.

It rejects:

- missing or extra records;
- reordered or malformed identities;
- altered family/dimension/state/lag semantics;
- invalid event fingerprints;
- support/evaluable inconsistencies;
- non-null metrics for zero-support records;
- missing/non-finite metrics for supported records;
- invalid win rates;
- LONG/SHORT rows for the same condition with different event-set fingerprints;
- any source/authority drift.

Therefore changing a nested record and merely recomputing the payload/evidence hashes does not make the evidence valid.

## Cell evidence metadata

Cell evidence binds the catalogue payload to:

- exact DEC-470 protocol fingerprint;
- DEC-471 miner identity/blob;
- code commit;
- annual segment and cell;
- processed source manifest SHA;
- feature manifest SHA;
- outcome manifest SHA;
- aggregate feature-evidence fingerprint;
- aggregate outcome-evidence fingerprint;
- payload SHA and byte length;
- record/evaluable/zero-support/support summary counts;
- all execution, strategy, and trading locks.

A validated cell summary may be created only after full payload semantic validation.

## Full collection aggregate

The aggregate inventory is exactly:

- 12 annual segments;
- 18 symbol/timeframe/horizon cells per segment;
- **216 annual cells**;
- 4,970 directional records per annual cell;
- **1,073,520 total directional records**.

No annual cell can be missing or duplicated.

The aggregate contains the deterministic ordered validated-cell summary inventory and per-segment totals. Its validator checks the exact 12×18 identity universe, exact total record count, segment summaries, code-commit consistency, and all downstream authority locks.

For a full replay, the aggregate compiler/validator must be fed summaries produced by validated cell evidence; structural aggregate hashing is not a substitute for validating each underlying cell payload.

## Authority

DEC-472 does not authorize:

- historical artifact reads;
- annual catalogue execution;
- historical or cross-year result production;
- Strategy V1 synthesis;
- candidate compilation or promotion;
- Phase 8B;
- demo orders;
- broker mutation;
- live orders;
- real-money action or trading.

## Next gate

`SOURCE_ONLY_ANNUAL_PATTERN_CATALOGUE_FULL_HISTORY_LOADER`

That gate may extend the accepted feature/outcome loading path from the earlier 2015-2022 research range to the exact DEC-470 full annual collection, while remaining non-executing until a later explicit authorization.
