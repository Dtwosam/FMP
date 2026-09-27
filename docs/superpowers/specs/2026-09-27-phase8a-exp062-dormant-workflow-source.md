# Phase 8A — EXP-062 Dormant Workflow and CLI Source

**Date:** 2026-09-27  
**Status:** SOURCE-ONLY DORMANT / EXECUTION LOCKED  
**Decision:** DEC-295  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-294

## Purpose

DEC-295 builds the dormant workflow/CLI source for EXP-062 without installing an active GitHub Actions workflow.

It binds the repaired adapter and EXP-062 run contract to the exact accepted EXP-044 feature/outcome sources while preserving a hard fail-closed execution gate before any historical artifact download or historical result read.

## Source reuse

EXP-062 intentionally reuses the frozen EXP-061 source verifier and range-limited loader because:

- accepted EXP-044 feature/outcome source runs are unchanged;
- artifact ids/digests are unchanged;
- feature/outcome manifests are unchanged;
- selected history remains 2015-2022 only;
- targets reaching 2023+ remain filtered before adaptation.

The only changed data interpretation is already isolated in DEC-293: float NaN -> None immediately before FeatureObservation.

## Exact accepted sources

The dormant source reuses:

- feature run `35867307338`;
- outcome run `35876715434`;
- feature evidence artifact `10753455784`;
- outcome evidence artifact `10758027876`;
- the exact nine pair/timeframe feature artifacts;
- the exact nine pair/timeframe outcome artifacts.

No new source data is downloaded or accepted by DEC-295.

## Hard execution gate

`scripts/phase8a_exp062.py` calls the DEC-295 gate:

- before `load_verified_exp061_cell_from_indexes`;
- before any aggregate `cell-evidence.json` read.

The DEC-295 gate always raises:

`EXP-062 historical discovery execution is not authorized by DEC-295`

The dormant workflow template also rechecks that gate:

- before any feature/outcome/evidence artifact ZIP download in cell jobs;
- before any cell-result artifact download in aggregate.

Therefore the dormant source cannot produce an EXP-062 historical result.

## Dormant workflow

Template:

`docs/superpowers/templates/phase8a-exp062-discovery.yml.disabled`

Git blob:

`dd93a3d87801bacae05ae2f45a2d66c1aecd4590`

Reserved future active path:

`.github/workflows/phase8a-exp062-discovery.yml`

That active file does not exist under DEC-295.

The template contains:

- one preflight job;
- the exact 18 DEC-294 matrix cells;
- one aggregate job;
- exact accepted source artifact ids/digests;
- EXP-062 CLI/runtime references;
- exact EXP-062 artifact names.

## Frozen sources

Dormant workflow-source gate:

`src/fmp/discovery/nan_null_repair_workflow_source.py`

Git blob:

`e1355915beeb06046662de813d6cc11b4d0ca6df`

Dormant CLI:

`scripts/phase8a_exp062.py`

Git blob:

`585394acda43a037d07db3b35a5aa6f5f22d8309`

Pinned runtime:

`requirements/exp062-discovery-run.txt`

Git blob:

`1ff32214dee10d877a067e750cd69ffad96d5fe5`

Focused tests:

`tests/test_phase8a_exp062_dormant_workflow_source.py`

Git blob:

`43bee85c1268467df01dcb7d68fa1d3f28f201a3`

## Dependency bindings

The source gate pins:

- DEC-294 run contract blob `0d1532e6a747e2dd9f0e70cd395e97433e6320ce`;
- DEC-293 repaired adapter blob `53f85d99bad42decb673e9fa2ff0f771150e17db`;
- EXP-061 accepted source validator blob `68566fc86ff3470cc8b6ebef606becaff9f3450b`;
- EXP-061 range-limited loader blob `df1d029a6f8b8d3862ebbf990ed1170a5982e1ea`;
- frozen miner blob `495a67699eb5014e52129f0238a2737049fe38e6`;
- pinned runtime blob `1ff32214dee10d877a067e750cd69ffad96d5fe5`.

## Authorization state

DEC-295 keeps false:

- workflow-template installation;
- workflow dispatch;
- historical discovery execution;
- discovery-result production;
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

After DEC-295 is green and merged, the next safe gate is a separate decision to install the exact dormant template byte-for-byte at the reserved active workflow path **while keeping execution locked**.

No dispatch is authorized by DEC-295.
