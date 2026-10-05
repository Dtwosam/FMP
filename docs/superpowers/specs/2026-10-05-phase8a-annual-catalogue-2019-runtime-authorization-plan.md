# Phase 8A — 2019 Runtime Authorization Plan

**Date:** 2026-10-05  
**Status:** SOURCE-READY READ-ONLY PLAN / RUN 381 UNCONSUMED  
**Decision:** DEC-558

## Concrete source evidence

DEC-557 recovery workflow run `37241812968` completed successfully on main
`eb72a2ab8639da62d6c6e4a084a6b11470b72bf1`.

Its immutable authorization artifact is:

- artifact id: `11317224241`
- artifact digest: `sha256:ecdbb57924cf74945e9e8bba12dcaae2d869ef264813ef012d21ba175c5ef52e`
- authorization fingerprint: `c785127b20f57210e60ebd681d7b0e48a66f419fa8fbbbdd9cdd8fa560b464f9`

The authorization is exact to annual segment 2019, global annual workflow run
381 / attempt 1, with successful 2018 predecessor run `37237817538`.

## Dormant runtime targets

DEC-558 freezes, but does not install:

- 2019 runtime gate blob `d87fe85a5b426fa92caf7d6cc165445590f4097c`;
- 2019-aware runtime target blob `07ddfe7a968de10cd1d4f8592760cc9eb9e6300e`.

The currently installed runtime remains
`410180c34a9e3500bbbb42310a5253b993ac7785` and has no 2019 route.

The future target adds only the exact 2019/run381 route and preserves the
existing 2018/run380, 2017/run379, 2016/run378, and 2015 recovery routes.

## Runtime-plan builder

The repository-hosted DEC-558 builder is path-scoped and read-only. It requires:

- exact successful DEC-557 workflow run 2 / attempt 1;
- exact DEC-557 artifact id, digest, and authorization fingerprint;
- current main equal to the builder landing commit;
- exact annual history containing failed runs 1 and 376 plus successful runs
  377, 378, 379, and 380;
- no annual run 381 or later;
- exact source, workflow, runtime, and dormant-template blobs.

It emits only an immutable runtime authorization plan artifact.

## Authority boundary

DEC-558 performs no repository mutation and no annual dispatch. Runtime
installation, runtime-gate activation, run 381 dispatch, rerun/retry/replacement,
run 382+, 2020+ execution, strategy/promotion, broker mutation, order placement,
real-money action, and trading remain locked.

Next gate:
`READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2019_RUNTIME_AUTHORIZATION_INSTALL_PREFLIGHT_AFTER_CONCRETE_DEC558`.
