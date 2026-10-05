# Phase 8A — 2019 Dispatch Action Preflight

**Date:** 2026-10-05  
**Status:** SOURCE-READY READ-ONLY PREFLIGHT / RUN 381 UNCONSUMED  
**Decision:** DEC-564

## Concrete source

DEC-564 consumes only the successful concrete DEC-563 dispatch authorization:

- workflow run: `37306565277`;
- workflow head: `c9b93843c2b853fc23d78cdbcebdbf51a3cc390e`;
- artifact: `11344330424`;
- artifact digest: `sha256:06b72e13349a47106e36ce631713da55e51407fdeeb6dd26518c8115191bf520`;
- authorization fingerprint: `fd554fbfd2ca556b0e4a6e65ddb00ec805809eda70d80a1e1a401edfeb71fcf8`.

The authorization is already exact to annual segment 2019, predecessor annual run
`37237817538`, expected global annual run 381 / attempt 1, installed 2019 gate
blob `d87fe85a5b426fa92caf7d6cc165445590f4097c`, and installed runtime blob
`07ddfe7a968de10cd1d4f8592760cc9eb9e6300e`.

## DEC-564 contract

The read-only action preflight:

- validates the exact DEC-563 source, artifact identity, artifact digest, and
  authorization fingerprint;
- requires current main to equal the DEC-564 landing head;
- requires the exact annual workflow-dispatch history:
  - run 1: failure;
  - run 376: failure;
  - run 377 / 2015: success;
  - run 378 / 2016: success;
  - run 379 / 2017: success;
  - run 380 / 2018: success;
- rejects any existing annual run 381 or later;
- binds successful 2018 run `37237817538` as the only predecessor;
- freezes only ref `main`, segment `2019`, predecessor run
  `37237817538`, expected run 381 / attempt 1;
- emits an immutable DEC-564 artifact from a path-scoped
  contents/actions-read workflow.

DEC-564 contains no annual dispatch command and performs no repository mutation.

## Authority boundary

The preflight records that the existing DEC-563 contract permits the exact 2019
research dispatch, but DEC-564 itself remains read-only.

Rerun, retry, replacement, run 382+, 2020+ execution, cross-year result
production, Strategy V1 synthesis, promotion, Phase 8B, broker mutation, demo or
live orders, real-money action, and trading remain false.

## Next gate

`EXACT_2019_ANNUAL_PATTERN_CATALOGUE_WORKFLOW_DISPATCH_ON_CURRENT_MAIN`
