# Phase 8A — EXP-061 Verified Range-Limited Artifact Loader

**Date:** 2026-09-27  
**Status:** SOURCE-ONLY LOADER / HISTORICAL EXECUTION LOCKED  
**Decision:** DEC-273  
**Experiment:** EXP-20260927-061  
**Predecessors:** DEC-270, DEC-271, DEC-272

## 1. Purpose

DEC-273 adds the verified artifact-loader boundary for EXP-061.

It reuses the existing EXP-044 feature/outcome evidence indexes and exact cell manifests, verifies current selected artifact checksums, and reads only the 2015-01 through 2022-12 monthly partitions required by EXP-061.

It does not execute discovery and does not authorize a historical result run.

## 2. Evidence chain

The loader binds:

1. the EXP-044 feature aggregate evidence fingerprint;
2. the EXP-044 outcome aggregate evidence fingerprint;
3. the outcome evidence's exact feature-evidence fingerprint;
4. the requested feature cell's manifest SHA-256;
5. the requested outcome cell's manifest SHA-256;
6. the shared Phase 2 processed-manifest SHA-256;
7. the outcome manifest's exact feature-manifest SHA-256;
8. every selected monthly artifact's path, size, SHA-256, row count, and schema.

The aggregate evidence fingerprints are recomputed from canonical JSON even when already-parsed mappings are supplied.

## 3. Selected history

The selected month list is frozen exactly to:

- 2015-01 through 2022-12 inclusive;
- 96 feature partitions per pair/timeframe cell;
- 96 outcome partitions per pair/timeframe cell.

No 2023-01 or later monthly feature/outcome partition is selected or opened by DEC-273.

The selected feature frame is filtered to:

`2015-01-01T00:00:00Z <= available_at_utc < 2023-01-01T00:00:00Z`.

The selected outcome frame additionally requires:

`exit_timestamp_utc < 2023-01-01T00:00:00Z`.

Therefore late-2022 observations whose 60m/240m target crosses into 2023 are removed before the DEC-272 adapter receives them.

## 4. Current-file integrity

For every selected partition the loader verifies against the immutable cell manifest:

- safe path containment under the supplied artifact root;
- current file presence;
- exact current file size;
- exact current SHA-256;
- exact frozen Parquet schema;
- exact row count.

The loader validates the full manifest metadata inventory but does not open 2023+ partition bytes.

## 5. Upstream identity requirements

Feature evidence must retain:

- EXP-044 experiment identity;
- exact market-learning feature-set version;
- retrospective evidence label;
- complete evidence status;
- all model/shadow/demo/broker/live/real-money flags false.

Outcome evidence must retain the same feature identity plus:

- exact market-outcome-set version;
- complete outcome evidence status;
- exact binding to the supplied feature-evidence fingerprint;
- all model/shadow/demo/broker/live/real-money flags false.

Feature and outcome cell manifests must share one exact Phase 2 processed-manifest SHA-256.

The outcome manifest must bind the exact feature manifest SHA-256.

## 6. Output

The loader returns `VerifiedExp061CellFrames` containing:

- requested symbol/timeframe;
- verified 2015-2022 feature frame;
- verified 2015-2022 outcome frame with cross-2023 targets removed;
- processed-manifest SHA-256;
- feature manifest SHA-256;
- outcome manifest SHA-256;
- feature evidence fingerprint;
- outcome evidence fingerprint;
- exact selected feature artifact paths;
- exact selected outcome artifact paths.

The returned frames are intended for DEC-272 adaptation and then DEC-271 in-memory mining only after a later separate execution authorization.

## 7. Focused tests

Focused tests prove:

- the selected month inventory is exactly 96 months from 2015-01 through 2022-12;
- no selected path contains 2023;
- artifact-path inventory is deterministic and duplicate paths fail closed;
- aggregate evidence fingerprints are recomputed and tampering is rejected;
- selected artifact checksum mismatch fails before schema use;
- the loader contract keeps historical discovery/result and all downstream trading authorizations false.

These tests are software evidence only.

## 8. Frozen implementation identities

- loader source: `src/fmp/discovery/range_limited_loader.py`;
- source blob: `df1d029a6f8b8d3862ebbf990ed1170a5982e1ea`;
- focused tests: `tests/test_phase8a_exp061_range_limited_loader.py`;
- test blob: `f6ec2d8846491fb2cbc06d7eea064c0e72af45ee`.

## 9. Authorization boundary

DEC-273 does not authorize:

- historical discovery execution;
- discovery-result production;
- reserved 2023-2026 access;
- candidate compilation;
- promotion;
- Phase 8B;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.

## 10. Next gate

After DEC-273 merges green, the next safe task is an exact non-executing EXP-061 run contract that composes:

`verified loader -> DEC-272 adapter -> DEC-271 miner -> DEC-272 cell evidence`

for all 18 symbol/timeframe/horizon cells.

That contract must predeclare job/artifact identities and terminal review semantics while keeping workflow dispatch and historical result execution locked until a later explicit one-shot authorization.
