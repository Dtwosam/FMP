# Phase 8A — 2020 Runtime Authorization Plan

**Date:** 2026-10-05  
**Status:** SOURCE-READY READ-ONLY PLAN / RUN 382 UNCONSUMED  
**Decision:** DEC-569

## Concrete source evidence

DEC-568 workflow run `37315889656` completed successfully on main
`d4031faa3dc1f2a01882b222fc82292c7305822f`.

Its immutable authorization artifact is:

- artifact id: `11346849851`
- artifact digest: `sha256:a03cd0d85672e8ae760b8490982fe93f541738c68b733860f10bb16caf968308`
- authorization fingerprint: `cfd43db91d2703e743132e61540ed95acec11fc9d4f6f89d8a8c011345a95f55`

The authorization is exact to annual segment 2020, global annual workflow run
382 / attempt 1, with successful 2019 predecessor run `37310525635`.

## Dormant runtime targets

DEC-569 freezes, but does not install:

- 2020 runtime gate blob `695a50b418da752e1bd37d6302f209033ab611f5`;
- 2020-aware runtime target blob `4e124365430672fa63825b272001937c60151644`.

The currently installed runtime remains
`07ddfe7a968de10cd1d4f8592760cc9eb9e6300e` and has no 2020 route.

The future target adds only the exact 2020/run382 route and preserves the
existing 2019/run381, 2018/run380, 2017/run379, 2016/run378, and 2015 recovery
routes.

## Runtime-plan builder

The repository-hosted DEC-569 builder is path-scoped and read-only. It requires:

- exact successful DEC-568 workflow run 1 / attempt 1;
- exact DEC-568 artifact id, digest, and authorization fingerprint;
- current main equal to the builder landing commit;
- exact annual history containing failed runs 1 and 376 plus successful runs
  377, 378, 379, 380, and 381;
- no annual run 382 or later;
- exact source, workflow, runtime, and dormant-template blobs.

It emits only an immutable runtime authorization plan artifact.

## Authority boundary

DEC-569 performs no repository mutation and no annual dispatch. Runtime
installation, runtime-gate activation, run 382 dispatch, rerun/retry/replacement,
run 383+, 2021+ execution, strategy/promotion, broker mutation, order placement,
real-money action, and trading remain locked.

Next gate:
`READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2020_RUNTIME_AUTHORIZATION_INSTALL_PREFLIGHT_AFTER_CONCRETE_DEC569`.
