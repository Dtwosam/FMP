# Phase 8A — EXP-061 Non-Executing 18-Cell Run and Aggregate-Evidence Contract

**Date:** 2026-09-27  
**Status:** SOURCE-ONLY RUN CONTRACT / WORKFLOW AND HISTORICAL EXECUTION LOCKED  
**Decision:** DEC-274  
**Experiment:** EXP-20260927-061  
**Predecessors:** DEC-270, DEC-271, DEC-272, DEC-273

## 1. Purpose

DEC-274 freezes the exact result shape required for any later authorized EXP-061 historical discovery run.

It defines:

- exact workflow identity reserved for a later source implementation;
- exact attempt-1/manual-main semantics;
- exact 18 symbol/timeframe/horizon cells;
- explicit non-ambiguous job names;
- exact per-cell/preflight/aggregate artifact names;
- deterministic 18-cell aggregate evidence;
- success/non-success terminal expectations;
- permanent no-retry defaults unless a later decision explicitly changes governance before any run.

DEC-274 does not add the workflow and does not authorize execution.

## 2. Frozen upstream implementation identities

Any later EXP-061 run source must bind these exact predecessor blobs unless a separately versioned successor decision is created:

- pattern protocol: `63b3f0121d6a50eb9e8e62ab666d70eb91791621`;
- in-memory miner: `495a67699eb5014e52129f0238a2737049fe38e6`;
- market-learning adapter/evidence: `978a33554fad7e9d78b002778c4896be0af3333a`;
- verified range-limited loader: `df1d029a6f8b8d3862ebbf990ed1170a5982e1ea`.

## 3. Exact cell inventory

Exactly 18 cells:

- EURUSD × 5m/15m/1h × 60m/240m;
- GBPUSD × 5m/15m/1h × 60m/240m;
- USDJPY × 5m/15m/1h × 60m/240m.

No additional pair, timeframe, or horizon can appear in an EXP-061 aggregate.

## 4. Reserved workflow identity

A later implementation may use only the reserved identity:

- workflow name: `phase8a-exp061-discovery`;
- path: `.github/workflows/phase8a-exp061-discovery.yml`;
- event: manual `workflow_dispatch`;
- branch: `main`;
- authoritative run attempt: exactly `1`.

DEC-274 itself creates no workflow source and authorizes no dispatch.

## 5. Exact job names

The success shape contains exactly 20 jobs:

1. `exp061-preflight`;
2. exactly one explicit cell job for each of the 18 cells;
3. `exp061-aggregate`.

Cell names are explicit strings such as:

`exp061-cell-EURUSD-5m-60m`

rather than GitHub's implicit matrix-value display names. This avoids the matrix-name ambiguity that affected the old EXP-015 reviewer.

## 6. Exact artifact names

A future run at commit `<sha>` must use:

- preflight: `phase8a-exp061-preflight-<sha>`;
- per cell: `phase8a-exp061-cell-<symbol>-<timeframe>-<horizon>m-<sha>`;
- aggregate: `phase8a-exp061-aggregate-<sha>`.

Exactly 20 non-expired artifacts are required for a successful run contract.

## 7. Cell evidence requirements

Every cell evidence object must pass the hardened DEC-272 semantic validator, including:

- outer canonical evidence fingerprint;
- exact EXP-061 protocol fingerprint;
- exact code commit;
- exact Phase 2 processed-manifest SHA-256;
- exact feature-manifest SHA-256;
- exact outcome-manifest SHA-256;
- exact feature/outcome aggregate evidence fingerprints;
- exact cell/state/search identities;
- recomputed pattern fingerprints;
- discovery support/economic gates and rank order;
- confirmation pass/freeze semantics;
- validation pass/accepted semantics;
- all reserved/trading authorizations false.

## 8. Aggregate evidence

`compile_aggregate_evidence` accepts exactly 18 validated cell evidence objects.

It requires:

- exact complete cell inventory;
- one exact code commit across all cells;
- exact accepted Phase 2 source SHA-256 for each symbol;
- the same feature aggregate evidence fingerprint across all cells;
- the same outcome aggregate evidence fingerprint across all cells;
- identical feature/outcome manifest SHA-256s across the 60m and 240m horizons of the same symbol/timeframe;
- no duplicate cell identities;
- global discovery shortlist <= 180;
- global confirmation-frozen count <= 54;
- global validation-accepted count <= 54.

Each aggregate cell summary binds the exact cell evidence fingerprint and source/manifests plus discovery/frozen/accepted pattern fingerprints.

The aggregate itself is canonical-JSON fingerprinted.

## 9. Aggregate validation

`validate_aggregate_evidence` recomputes the outer aggregate fingerprint and independently checks:

- exact evidence/run/protocol identities;
- exact 18 sorted cell summaries;
- expected Phase 2 source SHA per symbol;
- cross-horizon manifest consistency;
- per-cell fingerprint inventories and subset relations;
- per-cell and global count reconciliation;
- all global caps;
- all downstream authorization locks.

A re-fingerprinted but semantically inconsistent aggregate must fail.

## 10. Terminal semantics

A later separately authorized attempt-1 run is successful only when:

- exact workflow/event/main/attempt identity matches;
- all 20 expected jobs complete successfully;
- all 20 expected artifacts exist and are non-expired;
- every cell evidence validates;
- the aggregate evidence validates;
- the aggregate can be deterministically reproduced from the 18 cell evidence objects.

Any terminal non-success consumes the run slot **if a later decision authorizes that slot**.

By default after such a non-success:

- rerun: false;
- retry: false;
- replacement run: false.

Produced expected cell evidence may be retained diagnostically. No aggregate success evidence is required on a failed run.

## 11. Result meaning

Even a successful historical EXP-061 result only answers:

> which frozen market-state hypotheses survived the 2015-2017 discovery, 2018 confirmation, and 2019-2022 validation protocol?

It does not authorize opening the reserved 2023-2026 block, compiling patterns into executable strategies, shadow/demo trading, or real-money trading.

## 12. Frozen implementation identities

- run-contract source: `src/fmp/discovery/run_contract.py`;
- source blob: `260eb6930673427266463517546969635188b143`;
- focused tests: `tests/test_phase8a_exp061_run_contract.py`;
- test blob: `820a616fe98d08dc7a15973ccec4246a64f2b30a`.

## 13. Authorization boundary

All remain false:

- workflow source authorization;
- workflow dispatch;
- historical discovery execution;
- discovery-result production;
- rerun/retry/replacement;
- reserved 2023-2026 access;
- candidate compilation;
- promotion;
- Phase 8B;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.

## 14. Next gate

After DEC-274 merges green, the next safe step is the **workflow/CLI source freeze only** for the reserved EXP-061 workflow identity, still with its execution gate false.

That source must use the explicit DEC-274 job names and artifact names, compose DEC-273 -> DEC-272 -> DEC-271 -> DEC-272 evidence exactly, and contain no dispatch path.
