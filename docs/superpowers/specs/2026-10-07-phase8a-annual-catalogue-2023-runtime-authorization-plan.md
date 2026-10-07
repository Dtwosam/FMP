# Phase 8A — 2023 Protected Runtime Authorization Plan

**Date:** 2026-10-07  
**Status:** SOURCE-READY READ-ONLY PLAN / RUN 385 UNCONSUMED  
**Decision:** DEC-604

## Concrete source evidence

The recovered DEC-603 authorization workflow run `37685394468` completed
successfully on main `a4235aa2bc8501da8a7273d80a133e712cd04721` as workflow
run 1 / attempt 1.

The immutable DEC-603 authorization artifact is:

- artifact id: `11511180606`
- artifact digest: `sha256:ee25e982971a0c3ce65f4a6b25a2229e35e7a2f3285b30f2bfcdff87734c311a`
- authorization fingerprint: `dc1f6dc96e4bdbf527ffba49be9df175310389737bd7c70ca945bd260baf3946`
- canonical authorization SHA-256: `aa9b4e8c4bceee20f5d03d8579e1b0407bc21b6597528707f003f5f0bc5aef7d`

The authorization is exact to protected annual segment 2023, global annual
workflow run 385 / attempt 1, with successful 2022 predecessor run
`37663157285`. DEC-603 explicitly authorizes protected-history access for
that exact source contract, under DEC-469 / DEC-470.

## Dormant runtime targets

DEC-604 freezes, but does not install:

- protected 2023 runtime gate blob `cb4d32507dc93fa8a7a1296e630ce3bc9ee9c191`;
- 2023-aware runtime target blob `0fb5cf4d5de1355ff8faffcff565cbbabaf1d7a3`.

The currently installed runtime remains
`f2734c7ea32355b1024d1097812578b23fc4409d`, which includes the 2022/run384
route but has no 2023 route.

The dormant target adds only the exact 2023/run385 route and preserves the
existing 2022/run384, 2021/run383, 2020/run382, 2019/run381, 2018/run380,
2017/run379, 2016/run378, and 2015 recovery routes.

The dormant 2023 gate requires protected-history access to be true when it is
eventually installed. The DEC-604 plan itself keeps active protected-history
access false because no runtime installation or activation occurs in this
decision.

## Runtime-plan builder

The DEC-604 builder is path-scoped and read-only. It requires:

- exact successful DEC-603 recovery workflow run 1 / attempt 1;
- exact DEC-603 artifact id, digest, authorization fingerprint, and canonical hash;
- current main equal to the DEC-604 landing commit;
- exact annual history containing failed runs 1 and 376 plus successful runs
  377 through 384;
- no annual run 385 or later;
- exact source, workflow, installed-runtime, and dormant-template blobs;
- the installed 2023 runtime gate target to remain absent.

It emits only an immutable runtime authorization plan artifact.

## Authority boundary

DEC-604 performs no repository installation and no annual dispatch. Runtime
installation, runtime-gate activation, repository mutation, active protected
history access, run 385 dispatch, rerun/retry/replacement, run 386+,
cross-year comparison/result production, Strategy V1 synthesis, promotion,
Phase 8B, broker mutation, order placement, real-money action, and trading
remain locked.

Next gate:
`READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2023_RUNTIME_AUTHORIZATION_INSTALL_PREFLIGHT_AFTER_CONCRETE_DEC604`.
