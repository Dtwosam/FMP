# Phase 8A — EXP-062 Run and Evidence Contract

**Date:** 2026-09-27  
**Status:** SOURCE-ONLY / NON-EXECUTING  
**Decision:** DEC-298  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-297

## Purpose

DEC-298 freezes the exact result/evidence contract for a future EXP-062 historical discovery attempt after the non-finite-value repair was verified on accepted 2015-2022 data.

It creates no workflow, slot, dispatch, or execution path.

The research semantics remain the frozen DEC-270 discovery-first protocol. EXP-062 receives distinct evidence identity solely because it is a new experiment with the verified DEC-293 adapter repair.

## Exact future cell universe

EXP-062 preserves the same 18 research cells:

- EURUSD / GBPUSD / USDJPY;
- 5m / 15m / 1h;
- 60m / 240m horizons.

Expected future success inventory:

- cells: `18`;
- jobs: `20`;
- artifacts: `20`.

## Reserved future workflow identity

DEC-298 reserves but does not create:

- workflow name: `phase8a-exp062-discovery`;
- path: `.github/workflows/phase8a-exp062-discovery.yml`;
- event: `workflow_dispatch`;
- branch: `main`;
- run attempt: `1`.

Exact job identities:

- `exp062-preflight`;
- 18 `exp062-cell-<symbol>-<timeframe>-<horizon>m`;
- `exp062-aggregate`.

Exact artifact identities for a result commit:

- `phase8a-exp062-preflight-<commit>`;
- 18 `phase8a-exp062-cell-<symbol>-<timeframe>-<horizon>m-<commit>`;
- `phase8a-exp062-aggregate-<commit>`.

## Evidence identity

Cell evidence:

- version: `1`;
- protocol: `fmp-exp062-cell-evidence-v1`;
- experiment: `EXP-20260927-062`.

Aggregate evidence:

- version: `1`;
- protocol: `fmp-exp062-aggregate-evidence-v1`;
- run contract: `fmp-exp062-run-contract-v1`;
- experiment: `EXP-20260927-062`.

The EXP-062 protocol fingerprint binds:

- exact semantic predecessor EXP-061 protocol fingerprint;
- DEC-293 repair decision/version;
- DEC-297 verified repair-proof decision/version;
- explicit `research_semantics_changed=false`.

## Cell evidence semantics

DEC-298 compiles the frozen EXP-061 cell evidence first, then wraps it under EXP-062 identity.

The wrapper stores:

- exact EXP-061 semantic-predecessor evidence fingerprint;
- exact predecessor experiment/protocol identity;
- DEC-293 repair identity;
- DEC-297 verified repair-proof identity;
- `nonfinite_to_null_repair_applied=true`.

Validation reverses the wrapper, reconstructs the exact predecessor EXP-061 evidence fingerprint, and reruns the frozen EXP-061 cell validator.

Therefore shortlist, confirmation, validation, support, economic-gate, source-manifest, chronology, and pattern semantics remain unchanged.

## Aggregate evidence semantics

DEC-298 requires exactly 18 validated EXP-062 cell evidence objects at one code commit.

It:

1. reconstructs each exact predecessor EXP-061 cell evidence object;
2. recompiles the frozen EXP-061 aggregate;
3. stores that predecessor aggregate fingerprint;
4. wraps the aggregate under EXP-062 identity;
5. stores the exact 18 outer EXP-062 cell-evidence fingerprints in sorted cell order;
6. computes a new EXP-062 aggregate fingerprint.

Validation reverses the wrapper, verifies the predecessor aggregate fingerprint, and reruns the frozen EXP-061 aggregate validator.

## Exact source bindings

DEC-298 binds:

- DEC-297 verified repair-proof source: `18b7dde7eadf0f051a09fda04e648650bb270eb7`;
- DEC-293 repaired adapter: `491ba8c92cb6e6e4c715bfb1ecb934b6949e1596`;
- frozen EXP-061 cell/evidence adapter: `978a33554fad7e9d78b002778c4896be0af3333a`;
- frozen EXP-061 miner: `495a67699eb5014e52129f0238a2737049fe38e6`;
- frozen EXP-061 range-limited loader: `df1d029a6f8b8d3862ebbf990ed1170a5982e1ea`;
- frozen EXP-061 run contract: `260eb6930673427266463517546969635188b143`;
- frozen EXP-061 protocol: `63b3f0121d6a50eb9e8e62ab666d70eb91791621`.

## Success and non-success shape

A future authorized run can be considered successful only with:

- all 20 exact jobs;
- all jobs successful;
- all 20 exact artifacts;
- all artifacts non-expired;
- aggregate evidence present;
- separate terminal/content review.

If a later slot is authorized, its first attempt consumes that slot regardless of terminal outcome.

DEC-298 predeclares:

- rerun: false;
- retry: false;
- replacement: false;
- expected partial evidence may be preserved after non-success.

## Frozen implementation

Run/evidence contract:

`src/fmp/discovery/exp062_run_contract.py`

Git blob:

`d304c8fafcff64f967f6777b1c494819f69d4a03`

Focused tests:

`tests/test_phase8a_exp062_run_evidence_contract.py`

Git blob:

`f951f67f438b61b78d7b1b8327d1946f1dc413a1`

## Authorization state

DEC-298 keeps false:

- workflow source authorization;
- workflow dispatch;
- historical discovery execution;
- discovery-result production;
- rerun/retry/replacement;
- reserved 2023-2026 robustness access;
- candidate compilation;
- promotion;
- Phase 8B;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.

## Next gate

After DEC-295/296/297/298 are green and merged, the next safe layer is dormant EXP-062 workflow/CLI source that uses:

- the verified DEC-293 repaired feature adapter;
- frozen EXP-061 miner and range-limited loader semantics;
- DEC-298 EXP-062 cell/aggregate evidence wrappers;
- a hard execution gate before any historical feature/outcome artifact read.

Installing or dispatching that workflow remains a separate later decision.
