# Phase 8A — 2018 Runtime Authorization Plan

**Date:** 2026-10-04  
**Status:** SOURCE-READY READ-ONLY PLAN / RUN 380 UNDISPATCHED  
**Decision:** DEC-547

## Concrete source

DEC-547 consumes only the successful DEC-546 execution authorization produced by:

- workflow run: `37229862532`;
- workflow head: `8440244e1c77ecaf5773427d6d4efcd1a7d4dc16`;
- artifact: `11313482812`;
- artifact digest: `sha256:79e9bd2485160dd59fbb88a2d50f32a52b6cfd573f80555a8716fde4ea18c71e`;
- authorization fingerprint: `34fe76b3bd30d054853b43f660f996757e8bdb30793c03ad6937cc3078b427a0`.

The source authorization is exact to annual segment 2018, global annual run 380 /
attempt 1, with predecessor 2017 run `37227536041`.

## Frozen runtime targets

DEC-547 freezes two dormant future installation targets without applying them:

1. `annual_pattern_catalogue_2018_runtime_authorization.py.disabled`
   - blob: `cd50f50156cf74c34cd97d69d24291dc373b390f`;
   - authorizes only segment 2018, run 380 / attempt 1;
   - requires predecessor run `37227536041`;
   - keeps run 381+ and all later authority false.

2. `annual_pattern_catalogue_runtime_with_2018_authorization.py.disabled`
   - blob: `410180c34a9e3500bbbb42310a5253b993ac7785`;
   - adds only the 2018/run-380 route;
   - preserves exact 2017/run-379, 2016/run-378, 2015/run-377 and historical
     run-376 routes.

The current installed runtime remains blob
`e9cbc76dc9e6866e80088d223498fbcc3b870fd1` and contains no 2018 route.

## Read-only workflow

The repository-hosted DEC-547 builder:

- is path-scoped to its own workflow file;
- has contents/actions read permissions only;
- verifies the exact DEC-546 run/artifact/digest/fingerprint;
- requires current main to equal the DEC-547 landing commit;
- requires annual history exactly `{1, 376, 377, 378, 379}`;
- rejects any annual run 380 or later;
- installs dependencies without an editable project install;
- preserves a clean checkout;
- emits only an immutable plan artifact.

## Authority boundary

DEC-547 performs no repository mutation and no annual workflow dispatch. Runtime
installation, runtime-gate activation, run 380 execution, run 381+, 2019+,
cross-year synthesis, Strategy V1 promotion, Phase 8B, broker mutation, demo/live
orders, real-money action, and trading remain locked.

## Next gate

`READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2018_RUNTIME_AUTHORIZATION_INSTALL_PREFLIGHT_AFTER_CONCRETE_DEC547`
