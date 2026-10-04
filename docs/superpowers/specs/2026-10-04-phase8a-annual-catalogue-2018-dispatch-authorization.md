# Phase 8A — 2018 Dispatch Authorization

**Date:** 2026-10-04  
**Status:** SOURCE-READY AUTHORIZATION / NOT DISPATCHED  
**Decision:** DEC-552

## Concrete source evidence

DEC-551 completed successfully as workflow run `37233894381` on
`35263ec4c59bae4733507c53b080f3ea07ff1325`.

Its immutable artifact is `11314757055`, digest
`sha256:7a7ba8c4c008e6e1d6ce144eb8c2df17f506a18894d1487f044fef9533fcd9d7`,
with preflight fingerprint
`f756088f404f77220b366eaffdfd36cfe805f9fcd91a274ef7c5a364994893c8`.

The preflight freezes only:
- annual segment `2018`;
- predecessor annual freeze run `37227536041` (2017);
- expected annual workflow run `380`;
- run attempt `1`;
- installed 2018 gate blob `cd50f50156cf74c34cd97d69d24291dc373b390f`;
- installed annual runtime blob `410180c34a9e3500bbbb42310a5253b993ac7785`.

## Authorization

DEC-552 converts that exact read-only preflight into source-only authorization
for 2018 run 380 / attempt 1.

At the contract layer it authorizes the historical artifact reads, annual
catalogue execution, result production, and annual workflow dispatch needed for
that single run. It does not contain or execute a dispatch command.

The repository-hosted authorization builder rechecks:
- the exact DEC-551 workflow run and artifact digest;
- the exact DEC-551 fingerprint;
- current main;
- exact annual history `{1, 376, 377, 378, 379}`;
- absence of run 380 or later;
- unchanged installed workflow, gate, and runtime blobs.

## Locked scopes

Rerun, retry, replacement execution, run 381+, 2019+, cross-year synthesis,
Strategy V1 synthesis, promotion, Phase 8B, broker mutation, demo/live orders,
real-money action, and trading remain false.

## Next gate

`READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2018_DISPATCH_ACTION_PREFLIGHT`.
