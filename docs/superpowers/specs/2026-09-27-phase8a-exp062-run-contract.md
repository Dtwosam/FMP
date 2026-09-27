# Phase 8A — EXP-062 Run and Aggregate-Evidence Contract

**Date:** 2026-09-27  
**Status:** SOURCE-ONLY / NON-EXECUTING  
**Decision:** DEC-294  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-293

## Purpose

DEC-294 freezes the exact non-executing result contract for the repaired EXP-062 experiment before any workflow source or historical slot is opened.

It preserves the EXP-061 18-cell research shape while giving EXP-062 distinct job/artifact/evidence identities.

## Exact cells

EXP-062 retains the same 18 cells:

- EURUSD / GBPUSD / USDJPY;
- 5m / 15m / 1h;
- 60m / 240m horizons.

Expected counts:

- cells: `18`;
- jobs: `20`;
- artifacts: `20`.

## Future workflow identity

Reserved future workflow identity:

- name: `phase8a-exp062-discovery`;
- path: `.github/workflows/phase8a-exp062-discovery.yml`;
- event: `workflow_dispatch`;
- branch: `main`;
- run attempt: `1`.

DEC-294 does not create, install, or dispatch this workflow.

## Job identities

The exact future success inventory is:

- `exp062-preflight`;
- 18 `exp062-cell-<symbol>-<timeframe>-<horizon>m` jobs;
- `exp062-aggregate`.

All names are deterministic from the frozen cell universe.

## Artifact identities

For a 40-character result commit, the exact future artifact inventory is:

- `phase8a-exp062-preflight-<commit>`;
- 18 `phase8a-exp062-cell-<symbol>-<timeframe>-<horizon>m-<commit>`;
- `phase8a-exp062-aggregate-<commit>`.

No artifact name is authorized outside this inventory.

## Source bindings

DEC-294 binds:

- DEC-292 repair protocol blob `1d26da24134c825e2f405224316e1dd3136a38fb`;
- DEC-293 repaired adapter/evidence blob `53f85d99bad42decb673e9fa2ff0f771150e17db`;
- frozen EXP-061 miner blob `495a67699eb5014e52129f0238a2737049fe38e6`;
- frozen EXP-061 range-limited loader blob `df1d029a6f8b8d3862ebbf990ed1170a5982e1ea`;
- frozen EXP-061 run-contract blob `260eb6930673427266463517546969635188b143`.

## Aggregate semantics

EXP-062 aggregate compilation:

1. validates all 18 EXP-062 cell evidence objects;
2. requires a single exact result commit across all cells;
3. reconstructs each exact semantic-predecessor EXP-061 cell evidence object;
4. deterministically recompiles the frozen EXP-061 aggregate evidence;
5. wraps that aggregate under EXP-062 identity;
6. stores the exact predecessor aggregate evidence fingerprint;
7. stores the exact 18 EXP-062 outer cell-evidence fingerprints;
8. recomputes a new EXP-062 aggregate evidence fingerprint.

The EXP-062 aggregate validator reverses that wrapper, verifies the predecessor aggregate fingerprint, and reruns the frozen EXP-061 aggregate validator.

Therefore discovery shortlist, confirmation-frozen, validation-accepted, source-manifest, cap, and subset semantics remain unchanged.

## Aggregate evidence identity

- version: `1`;
- protocol: `fmp-exp062-aggregate-evidence-v1`;
- run contract: `fmp-exp062-run-contract-v1`;
- experiment: `EXP-20260927-062`;
- repair protocol: DEC-292;
- semantic predecessor: EXP-061.

## Success shape

A later authorized run can be successful only with:

- all 20 exact jobs;
- all jobs successful;
- all 20 exact artifacts;
- all artifacts non-expired;
- aggregate evidence present;
- separate result review required.

## Non-success shape

If a later run is authorized, any first attempt consumes its slot.

DEC-294 predeclares:

- rerun: false;
- retry: false;
- replacement: false;
- expected partial cell evidence may be preserved;
- aggregate success evidence is not required after non-success.

## Authorization state

DEC-294 keeps false:

- workflow source authorization;
- workflow dispatch;
- historical discovery execution;
- discovery result production;
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

## Frozen implementation

Run/aggregate contract:

`src/fmp/discovery/nan_null_repair_run_contract.py`

Git blob:

`0d1532e6a747e2dd9f0e70cd395e97433e6320ce`

Focused tests:

`tests/test_phase8a_exp062_run_contract.py`

Git blob:

`7e11fb4c8c739898d0e25070ee49a832fe85996f`

## Next gate

After DEC-294 is green and merged, the next safe step is dormant EXP-062 workflow/CLI source that uses:

- DEC-293 repaired adapter;
- frozen EXP-061 miner/loader semantics;
- DEC-294 exact jobs/artifacts;
- a hard execution gate before any historical artifact read.

Installing or dispatching that workflow remains a separate later decision.
