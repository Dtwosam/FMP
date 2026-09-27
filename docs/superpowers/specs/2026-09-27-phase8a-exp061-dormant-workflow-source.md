# Phase 8A — EXP-061 Dormant Workflow / CLI Source Freeze

**Date:** 2026-09-27  
**Status:** DORMANT SOURCE FROZEN / NOT INSTALLED / HISTORICAL EXECUTION LOCKED  
**Decision:** DEC-275  
**Experiment:** EXP-20260927-061  
**Predecessor:** DEC-274

## 1. Purpose

DEC-275 freezes the future EXP-061 workflow and CLI source without making that workflow dispatchable.

The source is deliberately dormant:

- the YAML template is stored at `docs/superpowers/templates/phase8a-exp061-discovery.yml.disabled`;
- the reserved active path remains `.github/workflows/phase8a-exp061-discovery.yml`;
- no file exists at that active path under DEC-275;
- workflow-template installation is unauthorized;
- workflow dispatch is unauthorized;
- historical discovery execution is unauthorized.

## 2. Exact accepted upstream sources

The source is pinned to the already-reviewed EXP-044 data-preparation runs.

### Feature source

- run id: `35867307338`;
- workflow: `phase8a-exp044-market-features`;
- path: `.github/workflows/phase8a-exp044-market-features.yml`;
- event: `workflow_dispatch`;
- branch: `main`;
- head: `b71912e254d2a597c0ef55b5e1b3b87b052039ea`;
- attempt: `1`;
- conclusion: `success`;
- aggregate feature-evidence artifact id: `10753455784`;
- aggregate feature-evidence ZIP digest: `sha256:1d3763c3d8ef13ba5157786c019349f1a7fdb22d626800fbc5b41ad779448f04`.

### Outcome source

- run id: `35876715434`;
- workflow: `phase8a-exp044-market-outcomes`;
- path: `.github/workflows/phase8a-exp044-market-outcomes.yml`;
- event: `workflow_dispatch`;
- branch: `main`;
- head: `edeb43bb4de88923e3349caa8ace36350839ccb8`;
- attempt: `1`;
- conclusion: `success`;
- aggregate outcome-evidence artifact id: `10758027876`;
- aggregate outcome-evidence ZIP digest: `sha256:3c360629c8a408e6b0f97ee9c1254ca936c0144964fd1bb74855f394230a4d05`.

DEC-275 also pins the exact nine feature-cell artifact ids/digests and nine outcome-cell artifact ids/digests already reused by EXP-060.

No runtime input may substitute another feature or outcome run.

## 3. Dormant workflow shape

The frozen template keeps the DEC-274 success topology:

- one `exp061-preflight` job;
- one 18-entry cell matrix;
- each runtime cell uses the explicit name expression
  `exp061-cell-<symbol>-<timeframe>-<horizon>m`;
- one `exp061-aggregate` job.

The matrix therefore produces exactly 18 named cell jobs while avoiding GitHub's implicit matrix-value naming.

The template carries the exact DEC-274 preflight, cell, and aggregate artifact names.

## 4. Source preflight

The preflight fetches read-only GitHub metadata for the two pinned upstream runs and their artifact inventories.

`validate_source_snapshots` requires:

- exact run ids;
- exact workflow names/paths;
- exact manual-main heads;
- attempt 1;
- terminal success;
- exact aggregate evidence artifacts;
- exact 9+9 cell artifact ids/names/digests;
- every required source artifact non-expired.

Only then may `source_ready=true` be emitted.

This still authorizes no historical discovery.

## 5. Hard execution gate

The CLI command

`python scripts/phase8a_exp061.py require-execution --code-commit <sha>`

calls `require_historical_execution_authorized`.

Under DEC-275 it always raises:

`PermissionError: DEC-275 historical EXP-061 discovery execution remains locked`

The dormant template places that gate:

- in preflight after source validation;
- again before every cell;
- again before aggregate compilation.

The `cell` CLI function itself invokes the same gate **before opening any feature, outcome, or evidence path**.

The `aggregate` CLI invokes the gate **before opening any cell-result evidence**.

## 6. Future cell source path

If a later successor explicitly authorizes execution, the already-frozen cell CLI will compose:

`DEC-273 verified loader -> DEC-272 adapter -> DEC-271 in-memory miner -> DEC-272 cell evidence`

using:

- exact pinned feature/outcome artifacts;
- exact 2015-2022 range limiting;
- no 2023+ partition opening;
- exact requested symbol/timeframe/horizon;
- current workflow commit as the result code identity.

No behavior is activated by DEC-275.

## 7. Future aggregate source path

If separately authorized later, the aggregate CLI will:

- require exactly 18 `cell-evidence.json` files;
- semantically validate every cell;
- call DEC-274 `compile_aggregate_evidence`;
- independently revalidate the aggregate;
- write one canonical aggregate evidence file.

## 8. Runtime pin

The dormant workflow uses Python `3.12.14` and:

- `polars==1.44.2`;
- `polars-runtime-32==1.44.2`.

Frozen runtime file:

`requirements/exp061-discovery-run.txt`.

## 9. Focused safety tests

Focused tests require:

- exact accepted source run metadata;
- exact required source artifact ids/names/digests;
- tampered source digest rejection;
- attempt drift rejection;
- dormant source payload with all authorizations false;
- dormant template present;
- active workflow path absent;
- exact 18-entry matrix;
- exactly 9 × 60m and 9 × 240m rows;
- explicit cell job-name expression;
- CLI execution gate textually preceding any historical loader/result read;
- direct execution-gate call raising while locked.

## 10. Frozen implementation identities

- workflow source contract: `src/fmp/discovery/workflow_source.py`;
- workflow-source blob: `68566fc86ff3470cc8b6ebef606becaff9f3450b`;
- CLI: `scripts/phase8a_exp061.py`;
- CLI blob: `bd40f17566f4c03e623215fe9e615b00b2fc9039`;
- dormant workflow template: `docs/superpowers/templates/phase8a-exp061-discovery.yml.disabled`;
- template blob: `d4eb02d380ae8c9a5b95e6520cbb7ca192254cb9`;
- focused tests: `tests/test_phase8a_exp061_dormant_workflow_source.py`;
- focused-test blob: `4c8266b07c0fe9912691da298cc4963e28a2a66a`;
- runtime requirements blob: `1ff32214dee10d877a067e750cd69ffad96d5fe5`.

## 11. Authorization boundary

All remain false:

- active workflow installation;
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

## 12. Next gate

After DEC-275 merges green, the next safe step is to install the exact reviewed template at the reserved active workflow path **with the execution gate still false**, then prove on merged `main` that the workflow source is exact and cannot progress past authorization preflight.

That installation/proof decision must still authorize no historical discovery result.
