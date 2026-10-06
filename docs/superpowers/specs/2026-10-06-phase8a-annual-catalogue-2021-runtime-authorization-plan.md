# Phase 8A — 2021 Runtime Authorization Plan

**Date:** 2026-10-06  
**Status:** SOURCE-READY READ-ONLY PLAN / RUN 383 UNCONSUMED  
**Decision:** DEC-582

## Concrete source evidence

DEC-581 authorization workflow run `37460105363` completed successfully on
main `cde122a5b70032733dc5699cb2258ed40defbc4d` as workflow run 2 /
attempt 1.

Run 1 (`37457496751`) failed before DEC-581 artifact creation. Recovery PR
#741 explicitly bound that failed run before allowing run 2.

The immutable DEC-581 authorization artifact is:

- artifact id: `11411376869`
- artifact digest: `sha256:233cdabf39d23016a6ba73915abeac7a5af333661c91b68752cfb61f9db513e4`
- authorization fingerprint: `56226545935b649e24077b1e108e17b865a65bbdbee36fb73a9605d4f766d6d6`

The authorization is exact to annual segment 2021, global annual workflow run
383 / attempt 1, with successful 2020 predecessor run `37443770076`.

## Dormant runtime targets

DEC-582 freezes, but does not install:

- 2021 runtime gate blob `cac68c905bedf3105aa7e766eaa968c87bff6ce9`;
- 2021-aware runtime target blob `d0db13ae9ae8dfbedf9c17ebe09d53f2ec4ff7e6`.

The currently installed runtime remains
`4e124365430672fa63825b272001937c60151644`, which includes the 2020/run382
route but has no 2021 route.

The dormant target adds only the exact 2021/run383 route and preserves the
existing 2020/run382, 2019/run381, 2018/run380, 2017/run379, 2016/run378,
and 2015 recovery routes.

## Runtime-plan builder

The DEC-582 builder is path-scoped and read-only. It requires:

- exact successful recovered DEC-581 workflow run 2 / attempt 1;
- exact DEC-581 artifact id, digest, and authorization fingerprint;
- current main equal to the DEC-582 landing commit;
- exact annual history containing failed runs 1 and 376 plus successful runs
  377 through 382;
- no annual run 383 or later;
- exact source, workflow, installed-runtime, and dormant-template blobs;
- the installed 2021 runtime gate target to remain absent.

It emits only an immutable runtime authorization plan artifact.

## Authority boundary

DEC-582 performs no repository installation and no annual dispatch. Runtime
installation, runtime-gate activation, repository mutation, run 383 dispatch,
rerun/retry/replacement, run 384+, 2022+ execution, strategy/promotion,
Phase 8B, broker mutation, order placement, real-money action, and trading
remain locked.

Next gate:
`READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2021_RUNTIME_AUTHORIZATION_INSTALL_PREFLIGHT_AFTER_CONCRETE_DEC582`.
