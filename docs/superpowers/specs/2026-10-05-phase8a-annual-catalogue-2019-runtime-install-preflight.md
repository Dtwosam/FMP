# Phase 8A — 2019 Runtime Authorization Install Preflight

**Date:** 2026-10-05  
**Status:** CONCRETE READ-ONLY PREFLIGHT / RUN 381 UNCONSUMED  
**Decision:** DEC-559

## Concrete source plan

DEC-558 builder run `37294642532` completed successfully on main
`2e8d66e515b9f87023f78ae06c644bf804440501`.

Its immutable plan artifact is:

- artifact id: `11337484835`
- artifact digest: `sha256:7ee0dbfd168a8a63664419cce85e41a65fde46f9e492dbee65868386d74975a8`
- plan canonical SHA-256: `5e35a860916137118e6a1ca9d751045373c59ad9e5e0ac373545b20740ccd074`

The plan is exact to annual segment 2019, global annual workflow run 381 /
attempt 1, with successful 2018 predecessor run `37237817538`.

## Exact activation target

DEC-559 validates a future two-file activation only:

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

No mutation is executed by DEC-559.

## Repository-hosted preflight

The DEC-559 workflow is path-scoped and read-only. It requires:

- exact successful DEC-558 workflow run 1 / attempt 1;
- exact DEC-558 artifact id, digest, and embedded DEC-557 authorization;
- current main equal to the preflight landing commit;
- annual history containing failed runs 1 and 376 and successful runs
  377, 378, 379, and 380;
- no annual run 381 or later;
- exact authorization, plan, runtime, and dormant target blobs.

It emits an immutable preflight with a deterministic fingerprint.

## Authority boundary

Repository mutation, runtime installation, runtime-gate activation, annual
dispatch, rerun/retry/replacement, run 382+, 2020+ execution,
strategy/promotion, broker mutation, order placement, real-money action, and
trading remain locked.

Next gate:
`EXACT_ANNUAL_PATTERN_CATALOGUE_2019_RUNTIME_AUTHORIZATION_INSTALL_MUTATION_AFTER_DEC559`.
