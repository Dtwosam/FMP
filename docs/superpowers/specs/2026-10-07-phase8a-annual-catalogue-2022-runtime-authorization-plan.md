# Phase 8A — 2022 Runtime Authorization Plan

**Date:** 2026-10-07  
**Status:** SOURCE-READY READ-ONLY PLAN / RUN 384 UNCONSUMED  
**Decision:** DEC-593

## Concrete source evidence

DEC-592 authorization workflow run `37608559036` completed successfully on
main `0d9b8deec0b6cd26f447596fc59a682f7c536e0b` as workflow run 1 /
attempt 1.

The immutable DEC-592 authorization artifact is:

- artifact id: `11475911390`
- artifact digest: `sha256:a70abd5972c0aa78459c6540ffc863f0a463183e880baa8b96752b0336fd5d85`
- authorization fingerprint: `5365ca95855d97df7ad28ff7d4e6f5c2ec51183899da7f88048d78b5d381bf54`
- canonical authorization SHA-256: `b335202460f6cd61d30f54717c97de5451fdc251e08fab45beffccdd2bd5df3d`

The authorization is exact to annual segment 2022, global annual workflow run
384 / attempt 1, with successful 2021 predecessor run `37531960014`.

## Dormant runtime targets

DEC-593 freezes, but does not install:

- 2022 runtime gate blob `ecb21dc7106e7bd43447f4135c3a696251a75e05`;
- 2022-aware runtime target blob `f2734c7ea32355b1024d1097812578b23fc4409d`.

The currently installed runtime remains
`d0db13ae9ae8dfbedf9c17ebe09d53f2ec4ff7e6`, which includes the 2021/run383
route but has no 2022 route.

The dormant target adds only the exact 2022/run384 route and preserves the
existing 2021/run383, 2020/run382, 2019/run381, 2018/run380, 2017/run379,
2016/run378, and 2015 recovery routes.

## Runtime-plan builder

The DEC-593 builder is path-scoped and read-only. It requires:

- exact successful DEC-592 workflow run 1 / attempt 1;
- exact DEC-592 artifact id, digest, authorization fingerprint, and canonical hash;
- current main equal to the DEC-593 landing commit;
- exact annual history containing failed runs 1 and 376 plus successful runs
  377 through 383;
- no annual run 384 or later;
- exact source, workflow, installed-runtime, and dormant-template blobs;
- the installed 2022 runtime gate target to remain absent.

It emits only an immutable runtime authorization plan artifact.

## Authority boundary

DEC-593 performs no repository installation and no annual dispatch. Runtime
installation, runtime-gate activation, repository mutation, run 384 dispatch,
rerun/retry/replacement, run 385+, 2023+ protected-history access, cross-year
comparison/result production, Strategy V1 synthesis, promotion, Phase 8B,
broker mutation, order placement, real-money action, and trading remain locked.

Next gate:
`READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2022_RUNTIME_AUTHORIZATION_INSTALL_PREFLIGHT_AFTER_CONCRETE_DEC593`.
