# Phase 8A — EXP-061 Market-Learning Adapter and Cell Evidence Contract

**Date:** 2026-09-27  
**Status:** SOURCE-ONLY ADAPTER / HISTORICAL EXECUTION LOCKED  
**Decision:** DEC-272  
**Experiment:** EXP-20260927-061  
**Predecessors:** DEC-270, DEC-271

## 1. Purpose

DEC-272 connects the already-approved EXP-044 market-learning schemas to the DEC-271 in-memory pattern miner without creating a second historical data pipeline.

It adds:

- a deterministic adapter from verified Polars feature/outcome frames into DEC-271 immutable row contracts;
- hard input boundaries that reject 2023+ feature rows and any outcome whose target reaches 2023+;
- exact feature/outcome source-identity matching;
- a deterministic, tamper-detectable EXP-061 cell-evidence contract.

It does not locate, download, or open historical artifacts itself.

## 2. Reused upstream schemas

Feature inputs reuse the accepted `fmp-market-feature-v1` frame identity and the exact 20 DEC-270 discovery measurements plus session flags.

Outcome inputs reuse the accepted `fmp-market-outcome-grid-v1` fields:

- 60m / 240m horizons;
- `long_net_pips_0p5`;
- `short_net_pips_0p5`;
- `long_net_pips_1p0`;
- `short_net_pips_1p0`;
- exact `exit_timestamp_utc`;
- existing retrospective evidence label and processed-manifest identity.

No new price label is invented by DEC-272.

## 3. Observation identity

The adapter deterministically hashes:

- symbol;
- timeframe;
- bar start;
- feature availability time;
- feature-set version;
- processed Phase 2 manifest SHA-256.

The same identity calculation is applied to feature and outcome rows.

Every adapted outcome must reference an adapted feature observation. Duplicate identities fail closed.

## 4. Input time boundary

DEC-272 accepts only observations with:

`2015-01-01T00:00:00Z <= available_at_utc < 2023-01-01T00:00:00Z`.

Feature rows at or after 2023-01-01 are rejected.

Outcome rows are rejected when either:

- their observation time is outside 2015-2022; or
- their fixed-horizon exit timestamp is at or after 2023-01-01.

This is stronger than silently filtering a full-history frame: a caller must supply a pre-2023 frame, preventing accidental presentation of reserved target rows to EXP-061.

The DEC-270/271 internal discovery/confirmation/validation boundary purge still applies inside that accepted 2015-2022 input range.

## 5. Source identity gates

The adapter requires:

- exact requested symbol/timeframe;
- exact `MARKET_FEATURE_SET_VERSION`;
- singular valid processed-manifest SHA-256;
- feature and outcome frames bound to the same processed-manifest SHA-256;
- exact `MARKET_OUTCOME_SET_VERSION`;
- exact retrospective market-learning evidence label;
- supported 60m/240m horizon identities;
- unique feature and outcome keys.

Any mismatch fails closed.

## 6. Cell evidence

`compile_cell_evidence` turns one DEC-271 `InMemoryDiscoveryResult` into canonical evidence containing:

- DEC-270 protocol fingerprint;
- code commit;
- Phase 2 processed-manifest identity;
- feature-evidence fingerprint;
- outcome-evidence fingerprint;
- symbol/timeframe/horizon cell;
- exact state cutpoints;
- discovery search counts and shortlist;
- confirmation evaluations and frozen fingerprints;
- validation evaluations and validated fingerprints;
- explicit reserved-block and all downstream authorization locks.

The evidence is canonical-JSON hashed. `validate_cell_evidence` recomputes the fingerprint and rejects tampering or any authorization drift.

## 7. Security/safety meaning

A valid DEC-272 cell evidence object is not permission to run a historical experiment. It is only the format a future separately authorized run must produce.

It cannot authorize:

- historical source access;
- discovery execution;
- reserved 2023-2026 access;
- candidate compilation;
- promotion;
- Phase 8B;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.

## 8. Focused tests

The focused tests prove:

- a valid feature/outcome row pair adapts to the same immutable observation identity;
- 2023 feature rows are rejected;
- an outcome whose target crosses into 2023 is rejected;
- feature/outcome processed-manifest mismatch is rejected;
- cell evidence is deterministic;
- evidence tampering invalidates its fingerprint;
- all downstream authorization fields remain false.

These are software-contract tests, not market evidence.

## 9. Frozen implementation identities

- adapter/evidence source: `src/fmp/discovery/market_learning_adapter.py`;
- source blob: `3655652f366bea41ef28009b87f5904b1a5894ea`;
- focused tests: `tests/test_phase8a_exp061_market_learning_adapter.py`;
- test blob: `4d1784bbef3d1f527bba6dd6f97d6b7e88cc5588`.

## 10. Next gate

The next safe task is a deterministic verified artifact loader that:

- consumes the existing EXP-044 feature and outcome evidence indexes;
- validates exact manifests/checksums;
- selects only 2015-2022 feature/outcome partitions;
- refuses any artifact selection that could expose a 2023+ target;
- feeds frames to DEC-272.

That loader remains source code only until a later separately frozen historical-run authorization.
