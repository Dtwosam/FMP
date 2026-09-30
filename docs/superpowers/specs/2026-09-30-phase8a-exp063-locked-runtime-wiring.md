# Phase 8A — EXP-063 Locked Runtime Wiring

**Date:** 2026-09-30  
**Status:** ACTIVE WORKFLOW INSTALLED / HISTORICAL EXECUTION LOCKED  
**Decision:** DEC-447  
**Experiment:** EXP-20260930-063  
**Predecessor:** DEC-446

## Purpose

DEC-447 consolidates the source-only run contract, runtime CLI, dormant workflow
source, and locked active workflow installation for EXP-063.

This is the final source-wiring milestone before any separate historical execution
authorization. It does not authorize a historical run.

## Bound implementation

DEC-447 pins:

- DEC-446 evidence contract blob
  `e8614beb156d24584b82611db47afb8c00ece71c`;
- DEC-445 persistence miner blob
  `40c49a372b35dbc113dbfb71374b1ae5fc7acc45`;
- DEC-444 persistence protocol blob
  `2c781dd2811b66d2d88f008007bf5c8bcf99f14f`;
- EXP-062 repaired non-finite feature adapter blob
  `491ba8c92cb6e6e4c715bfb1ecb934b6949e1596`;
- EXP-062 frozen source contract blob
  `e20ded13de24f99e8ea6cfdc6cb0d1309d984f24`;
- EXP-061 range-limited loader blob
  `df1d029a6f8b8d3862ebbf990ed1170a5982e1ea`;
- pinned Polars runtime requirements blob
  `1ff32214dee10d877a067e750cd69ffad96d5fe5`.

Runtime source:
`src/fmp/discovery/exp063_runtime_source.py` blob
`6e7804a037fd386016fd45145be73b8dc00563f2`.

CLI:
`scripts/phase8a_exp063.py` blob
`1b969668f79b37bc68f701da103b3a2bb53b13c1`.

Dormant workflow template and installed active workflow are byte-identical:

- `docs/superpowers/templates/phase8a-exp063-persistence.yml.disabled`;
- `.github/workflows/phase8a-exp063-persistence.yml`;
- Git blob `1038beb4b704ddead4e5841a6f799858732189e6`.

Focused tests:
`tests/test_phase8a_exp063_locked_runtime_wiring.py` blob
`e75e30c648f166862e555422ac76c6d9033485ec`.

## Production data lineage

EXP-063 deliberately reuses the exact accepted EXP-044 market-learning source
artifacts already frozen for EXP-061/062.

The runtime source delegates source-snapshot validation to the EXP-062 source
contract, which in turn preserves the exact feature/outcome run identities,
artifact ids, artifact digests, and nine symbol/timeframe source pairs.

EXP-063 also deliberately inherits the EXP-062 non-finite continuous-feature
normalization: non-finite numeric feature values are converted to null before the
frozen state model is built. No new data repair is introduced.

## Exact run topology

The reserved workflow is:

`phase8a-exp063-persistence`

at:

`.github/workflows/phase8a-exp063-persistence.yml`

with manual `workflow_dispatch`, branch `main`, run attempt 1.

The frozen run shape is exactly 20 jobs:

- one `exp063-preflight`;
- 18 explicit
  `exp063-cell-<symbol>-<timeframe>-<horizon>m` jobs;
- one `exp063-aggregate`.

The exact artifact shape is also 20 artifacts:

- one commit-scoped preflight artifact;
- 18 commit-scoped cell evidence artifacts;
- one commit-scoped aggregate evidence artifact.

The 18 cells remain exactly:

EURUSD / GBPUSD / USDJPY × 5m / 15m / 1h × 60m / 240m.

## Runtime composition

If a later decision authorizes execution, each cell is already wired as:

1. exact frozen EXP-044 artifact loader;
2. EXP-062 non-finite→null adapter;
3. DEC-445 EXP-063 persistence miner;
4. DEC-446 cell evidence compiler/validator.

The aggregate path is wired as:

1. exact 18 cell-evidence reads;
2. DEC-446 aggregate compiler;
3. DEC-446 aggregate validator.

No predecessor discovery/confirmation/validation miner is called.

## Hard execution boundary

The active workflow is installed but historical execution remains false.

Preflight may only read GitHub metadata for the exact already-completed EXP-044
source runs and validate those metadata snapshots.

The workflow then invokes:

`python scripts/phase8a_exp063.py require-execution --code-commit "$GITHUB_SHA"`

Under DEC-447 this always raises `PermissionError`.

Therefore a manual dispatch under DEC-447:

- may perform read-only source metadata checks;
- may write/upload preflight evidence;
- fails at the execution gate;
- cannot start any of the 18 cell jobs;
- cannot download feature/outcome/evidence artifacts for mining;
- cannot produce a persistence result or aggregate evidence.

The CLI independently places the same gate before:

- any cell artifact/evidence path is opened;
- any aggregate cell-result file is opened.

## Authorizations

DEC-447 sets only these source-state facts true:

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

That later authorization must define a single EXP-063 historical-result slot and
must continue to forbid rerun/retry/replacement and reserved 2023-2026 access.

DEC-447 itself provides no execute mode and does not dispatch EXP-063.
