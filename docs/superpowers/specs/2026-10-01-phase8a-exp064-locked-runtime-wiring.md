# Phase 8A — EXP-064 Locked Runtime Wiring

**Date:** 2026-10-01  
**Status:** ACTIVE WORKFLOW INSTALLED / HISTORICAL EXECUTION LOCKED  
**Decision:** DEC-455  
**Experiment:** EXP-20261001-064  
**Predecessor:** DEC-454

## Purpose

DEC-455 consolidates the source-only run contract, runtime CLI, dormant workflow
source, and locked active workflow installation for EXP-064.

This is the final source-wiring milestone before any separate historical execution
authorization. It does not authorize a historical run.

## Bound implementation

DEC-455 pins:

- final merged DEC-454 evidence contract blob
  `9aee3f9e273e20329c9de5a7079ed924ffee0a9a`;
- DEC-453 continuous-stability miner blob
  `b0d799ec1afaf43b0441290c97a9f39c37ecd2fd`;
- DEC-452 continuous-stability protocol blob
  `c108ea047c7bfb3e588bfbac33993180066c28ad`;
- EXP-062 repaired non-finite feature adapter blob
  `491ba8c92cb6e6e4c715bfb1ecb934b6949e1596`;
- EXP-062 frozen source contract blob
  `e20ded13de24f99e8ea6cfdc6cb0d1309d984f24`;
- EXP-061 range-limited loader blob
  `df1d029a6f8b8d3862ebbf990ed1170a5982e1ea`;
- pinned Polars runtime requirements blob
  `1ff32214dee10d877a067e750cd69ffad96d5fe5`.

Runtime source:
`src/fmp/discovery/exp064_runtime_source.py` blob
`75434bf240f3f666a5562f53e970c10ffff05049`.

CLI:
`scripts/phase8a_exp064.py` blob
`a44aed6d890e25a781b7b92d7efb3dabe06f9047`.

Dormant workflow template and installed active workflow are byte-identical:

- `docs/superpowers/templates/phase8a-exp064-continuous-stability.yml.disabled`;
- `.github/workflows/phase8a-exp064-continuous-stability.yml`;
- Git blob `caca62672ad9796764c18be6b8da9785b98c9733`.

Focused tests:
`tests/test_phase8a_exp064_locked_runtime_wiring.py` blob
`1c66b68e18ea40fc2ba02e4fb1d3c8920f7a33c8`.

## Production data lineage

EXP-064 reuses the exact accepted EXP-044 market-learning source artifacts already
frozen for EXP-061/062/063.

The runtime source delegates source-snapshot validation to the EXP-062 source
contract, preserving the exact feature/outcome run identities, artifact ids,
artifact digests, and nine symbol/timeframe source pairs.

EXP-064 also inherits the EXP-062 non-finite continuous-feature normalization:
non-finite numeric feature values are converted to null before the frozen
continuous-stability miner receives observations. No new data repair is introduced.

## Exact run topology

The reserved workflow is:

`phase8a-exp064-continuous-stability`

at:

`.github/workflows/phase8a-exp064-continuous-stability.yml`

with manual `workflow_dispatch`, branch `main`, run attempt 1.

The frozen run shape is exactly 20 jobs:

- one `exp064-preflight`;
- 18 explicit `exp064-cell-<symbol>-<timeframe>-<horizon>m` jobs;
- one `exp064-aggregate`.

The exact artifact shape is also 20 artifacts:

- one commit-scoped preflight artifact;
- 18 commit-scoped cell evidence artifacts;
- one commit-scoped aggregate evidence artifact.

The 18 cells remain exactly:

EURUSD / GBPUSD / USDJPY × 5m / 15m / 1h × 60m / 240m.

## Runtime composition

If a later decision authorizes execution, each cell is wired as:

1. exact frozen EXP-044 artifact loader;
2. EXP-062 non-finite→null adapter;
3. DEC-453 EXP-064 continuous-stability miner;
4. DEC-454 cell evidence compiler/validator.

The aggregate path is wired as:

1. exact 18 cell-evidence reads;
2. DEC-454 aggregate compiler;
3. DEC-454 aggregate validator.

No predecessor discovery, confirmation, persistence, or validation miner is called.

## Hard execution boundary

The active workflow is installed but historical execution remains false.

Preflight may only read GitHub metadata for the exact already-completed EXP-044
source runs and validate those metadata snapshots.

The workflow then invokes:

`python scripts/phase8a_exp064.py require-execution --code-commit "$GITHUB_SHA"`

Under DEC-455 this always raises `PermissionError`.

Therefore a manual dispatch under DEC-455:

- may perform read-only source metadata checks;
- may write/upload preflight evidence;
- fails at the execution gate;
- cannot start any of the 18 cell jobs;
- cannot download feature/outcome/evidence artifacts for mining;
- cannot produce a continuous-stability result or aggregate evidence.

The CLI independently places the same gate before:

- any cell artifact/evidence path is opened;
- any aggregate cell-result file is opened.

## Authorizations

DEC-455 sets only these source-state facts true:

- workflow source frozen;
- active workflow installed.

It keeps false:

- workflow dispatch authorization;
- historical execution;
- historical result authorization;
- rerun;
- retry;
- replacement run;
- reserved robustness access;
- candidate compilation;
- promotion;
- Phase 8B;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.

## Next gate

After green merge, the next meaningful milestone is an explicit one-shot historical
execution authorization decision bound to this exact merged runtime.

That later authorization must define a single EXP-064 historical-result slot and
must continue to forbid rerun/retry/replacement and reserved 2023-2026 access.

DEC-455 itself provides no execute mode and does not dispatch EXP-064.
