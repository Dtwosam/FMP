# Phase 8A — 2019 Runtime Authorization Install Action

**Date:** 2026-10-05  
**Status:** CONCRETE EXACT ACTION / MUTATION NOT YET APPLIED  
**Decision:** DEC-560

## Concrete DEC-559 source

DEC-559 builder run `37295798286` completed successfully on main
`bb1c7901d1b5859bec97a381716166e9024a6022`.

Its immutable preflight artifact is:

- artifact id: `11338796649`
- artifact digest: `sha256:3d8b6933a1949c77a4e6b29df5bd86896a140d0011ba6859187d412df24cc8f9`
- preflight fingerprint: `1c585ad2a2a0bdf3a0fc811376d1fa5701b293b2fd888abca30ea5c13fcf3861`

The preflight is exact to annual segment 2019, future annual workflow run
381 / attempt 1, with successful 2018 predecessor run `37237817538`.

## Exact future mutation

DEC-560 freezes exactly two ordered repository actions:

1. create
   `src/fmp/discovery/annual_pattern_catalogue_2019_runtime_authorization.py`
   from dormant gate blob
   `d87fe85a5b426fa92caf7d6cc165445590f4097c`;
2. replace
   `src/fmp/discovery/annual_pattern_catalogue_runtime.py`
   from current blob
   `410180c34a9e3500bbbb42310a5253b993ac7785`
   with target blob
   `07ddfe7a968de10cd1d4f8592760cc9eb9e6300e`.

The action compiler requires unchanged current main metadata and validates the
concrete DEC-559 preflight before producing a deterministic action fingerprint.

## Repository-hosted action builder

The DEC-560 workflow is path-scoped and read-only. It:

- verifies exact DEC-559 run, artifact id, digest, and embedded preflight
  fingerprint;
- rechecks current runtime blob and requires the 2019 gate target to be absent;
- requires annual history exactly through successful run 380 and rejects run
  381 or later;
- compiles and uploads only the immutable DEC-560 action artifact.

It contains no `git push`, `git commit`, or annual workflow dispatch command.

## Authority boundary

DEC-560 sets repository mutation authority only on the frozen action payload; it
does not perform that mutation. Runtime installation, runtime-gate activation,
annual dispatch, historical execution/result production, rerun/retry,
run 382+, 2020+ execution, strategy/promotion, broker mutation, order placement,
real-money action, and trading remain locked.

Next gate:
`APPLY_EXACT_ANNUAL_PATTERN_CATALOGUE_2019_RUNTIME_AUTHORIZATION_INSTALL_ACTION_AFTER_DEC560`.
