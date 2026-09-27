# Phase 8A — EXP-062 Dormant Workflow / CLI Source Freeze

**Date:** 2026-09-27  
**Status:** DORMANT SOURCE FROZEN / NOT INSTALLED / HISTORICAL EXECUTION LOCKED  
**Decision:** DEC-299  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-298

## Purpose

DEC-299 freezes the future EXP-062 discovery workflow and CLI source without installing an active workflow or authorizing historical execution.

EXP-062 preserves DEC-270 research semantics and uses:

- the DEC-293 non-finite-to-null feature adapter repair;
- the frozen EXP-061 miner;
- the frozen DEC-273 verified 2015-2022 loader;
- the exact accepted EXP-044 feature/outcome artifacts;
- DEC-298 EXP-062 run/evidence wrappers.

## Dormant source boundary

Dormant workflow template:

`docs/superpowers/templates/phase8a-exp062-discovery.yml.disabled`

Reserved future active path:

`.github/workflows/phase8a-exp062-discovery.yml`

DEC-299 requires that the active path does not exist.

All remain false:

- template installation;
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

## Exact source stack

DEC-299 binds:

- DEC-298 run/evidence contract blob `d304c8fafcff64f967f6777b1c494819f69d4a03`;
- DEC-293 repaired adapter blob `491ba8c92cb6e6e4c715bfb1ecb934b6949e1596`;
- frozen EXP-061 source contract blob `68566fc86ff3470cc8b6ebef606becaff9f3450b`;
- frozen EXP-061 miner blob `495a67699eb5014e52129f0238a2737049fe38e6`;
- frozen EXP-061 range-limited loader blob `df1d029a6f8b8d3862ebbf990ed1170a5982e1ea`;
- runtime requirements blob `1ff32214dee10d877a067e750cd69ffad96d5fe5`.

The accepted EXP-044 source runs/artifacts are reused through the frozen predecessor source validator. No source substitution is allowed.

## CLI source

CLI:

`scripts/phase8a_exp062.py`

Git blob:

`e6a94c1733f952a8edc01584a198ead1816f4410`

The future cell path is:

`DEC-273 verified loader -> DEC-293 repaired adapter -> DEC-271 frozen miner -> DEC-298 EXP-062 cell evidence`

The future aggregate path is:

`18 DEC-298 cell evidences -> DEC-298 aggregate evidence`

The CLI gate:

`require_historical_execution_authorized`

is called before:

- any feature/outcome/evidence source path is opened by a cell command;
- any historical cell-result file is opened by aggregate.

Under DEC-299 it always raises:

`PermissionError: DEC-299 historical EXP-062 discovery execution remains locked`

## Dormant workflow topology

The disabled template preserves the exact DEC-298 success shape:

- one `exp062-preflight`;
- 18 explicit cell jobs;
- one `exp062-aggregate`;
- exact 20 expected artifact identities.

The 18 cells remain:

- EURUSD / GBPUSD / USDJPY;
- 5m / 15m / 1h;
- 60m / 240m horizons.

The template downloads the exact accepted EXP-044 source artifacts and rechecks the hard execution gate before each preflight/cell/aggregate execution path.

## Frozen implementation identities

Workflow source contract:

`src/fmp/discovery/exp062_workflow_source.py`

Git blob:

`e20ded13de24f99e8ea6cfdc6cb0d1309d984f24`

CLI:

`scripts/phase8a_exp062.py`

Git blob:

`e6a94c1733f952a8edc01584a198ead1816f4410`

Dormant workflow template:

`docs/superpowers/templates/phase8a-exp062-discovery.yml.disabled`

Git blob:

`1a7d42fd8d03d6ca3eae722209b1ad2a5dd2bc50`

Focused tests:

`tests/test_phase8a_exp062_dormant_workflow_source.py`

Git blob:

`15c054c305b57e6da7f73c24bdaab02235fa4a26`

## Next gate

After DEC-296/297/298/299 are green and merged, the next safe step is to install the exact reviewed dormant template at the reserved active workflow path **while historical execution remains locked**.

That installation must not dispatch the workflow and must not authorize discovery-result production. A separate merged-main proof should demonstrate that the installed workflow cannot progress past the execution gate before any historical-result slot is opened.
