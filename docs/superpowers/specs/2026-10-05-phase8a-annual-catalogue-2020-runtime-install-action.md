# Phase 8A — 2020 Runtime Authorization Install Action

**Date:** 2026-10-05  
**Status:** CONCRETE EXACT ACTION / MUTATION NOT YET APPLIED  
**Decision:** DEC-571

## Concrete DEC-570 source

DEC-570 builder run `37321690650` completed successfully on main
`6b8f0015a0d38276356b3370d73d4d6a26c9e644`.

Its immutable preflight artifact is:

- artifact id: `11350136423`
- artifact digest: `sha256:97eee3d49aec78ebbc1f3aa7190159d4dfba62c861f221163bd03c2699fdad7c`
- preflight fingerprint: `367ec514057b011711ab9734a839f8cf03d1334125db336c947e979d923cab36`

The preflight is exact to annual segment 2020, future annual workflow run
382 / attempt 1, with successful 2019 predecessor run `37310525635`.

## Exact future mutation

DEC-571 freezes exactly two ordered repository actions:

1. create
   `src/fmp/discovery/annual_pattern_catalogue_2020_runtime_authorization.py`
   from dormant gate blob
   `695a50b418da752e1bd37d6302f209033ab611f5`;
2. replace
   `src/fmp/discovery/annual_pattern_catalogue_runtime.py`
   from current blob
   `07ddfe7a968de10cd1d4f8592760cc9eb9e6300e`
   with target blob
   `4e124365430672fa63825b272001937c60151644`.

The action compiler requires unchanged current main metadata and validates the
concrete DEC-570 preflight before producing a deterministic action fingerprint.

## Repository-hosted action builder

The DEC-571 workflow is path-scoped and read-only. It:

- verifies exact DEC-570 run, artifact id, digest, and embedded preflight
  fingerprint;
- rechecks current runtime blob and requires the 2020 gate target to be absent;
- requires annual history exactly through successful run 381 and rejects run
  382 or later;
- compiles and uploads only the immutable DEC-571 action artifact.

It contains no `git push`, `git commit`, or annual workflow dispatch command.

## Authority boundary

DEC-571 sets repository mutation authority only on the frozen action payload; it
does not perform that mutation. Runtime installation, runtime-gate activation,
annual dispatch, historical execution/result production, rerun/retry,
run 383+, 2021+ execution, strategy/promotion, broker mutation, order placement,
real-money action, and trading remain locked.

Next gate:
`APPLY_EXACT_ANNUAL_PATTERN_CATALOGUE_2020_RUNTIME_AUTHORIZATION_INSTALL_ACTION_AFTER_DEC571`.
