# Phase 8A — 2018 Runtime Authorization Install Preflight

**Date:** 2026-10-04  
**Status:** SOURCE-READY READ-ONLY PREFLIGHT / RUN 380 UNDISPATCHED  
**Decision:** DEC-548

## Concrete source

DEC-548 consumes the successful DEC-547 runtime plan produced by:

- workflow run: `37231060551`;
- workflow head: `1c61ad18d07d6fbc034c20610d7a130e09630a66`;
- artifact: `11314500352`;
- artifact digest: `sha256:633476f0bab6a5e1f3165cab44be176c05c01f955569ff0018cae957006ab56c`.

That artifact contains the exact DEC-546 authorization and DEC-547 plan for
annual segment 2018, global run 380 / attempt 1, predecessor annual run
`37227536041`.

## Frozen installation target

The preflight validates that a future runtime installation would touch exactly
two files:

1. create `src/fmp/discovery/annual_pattern_catalogue_2018_runtime_authorization.py`
   from dormant blob `cd50f50156cf74c34cd97d69d24291dc373b390f`;
2. replace `src/fmp/discovery/annual_pattern_catalogue_runtime.py`, currently
   blob `e9cbc76dc9e6866e80088d223498fbcc3b870fd1`, with dormant target blob
   `410180c34a9e3500bbbb42310a5253b993ac7785`.

DEC-548 does not apply either change.

## Repository-hosted preflight

The path-scoped DEC-548 workflow:

- has contents/actions read permissions only;
- verifies exact DEC-547 workflow/artifact provenance and digest;
- verifies the exact DEC-546 authorization embedded in the artifact;
- requires current main to equal the DEC-548 landing commit;
- requires annual history exactly `{1, 376, 377, 378, 379}`;
- rejects any annual run 380 or later;
- installs dependencies without an editable project install;
- preserves a clean checkout;
- builds and uploads only an immutable DEC-548 preflight artifact.

## Authority boundary

Repository mutation, runtime installation, runtime-gate activation, annual
workflow dispatch, run 380 execution, run 381+, 2019+, Strategy V1 synthesis or
promotion, Phase 8B, broker mutation, demo/live orders, real-money action, and
trading remain false.

## Next gate

`EXACT_ANNUAL_PATTERN_CATALOGUE_2018_RUNTIME_AUTHORIZATION_INSTALL_MUTATION_AFTER_DEC548`
