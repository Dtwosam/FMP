# Phase 8A — EXP-061 One-Shot Historical Executor

**Date:** 2026-09-27  
**Status:** SOURCE-ONLY ONE-SHOT EXECUTOR / MERGE TRIGGERS THE SOLE HISTORICAL DISPATCH  
**Decision:** DEC-289  
**Experiment:** EXP-20260927-061  
**Predecessor:** DEC-288

## Purpose

DEC-289 adds the one-shot executor for the single historical-result attempt already authorized by DEC-285 and reviewed through DEC-288.

Merging DEC-289 to `main` causes its push-only executor workflow to run. If every fail-closed check passes, the executor may submit exactly one manual-main dispatch of:

`phase8a-exp061-discovery.yml`

That dispatch is expected to become EXP-061 workflow run number `2`, attempt `1`.

DEC-289 creates no retry, rerun, replacement, candidate-compilation, promotion, Phase 8B, demo, broker-mutation, live-order, real-money, or trading path.

## Reviewed predecessor

The executor binds DEC-288 reviewed execution-plan source:

`src/fmp/discovery/historical_execution_plan_result_decision.py`

Git blob:

`b01ee28b7ab636cb6729423504ff8e2038ce4375`

At runtime the executor also re-downloads DEC-287 proof artifact `10935233025`, verifies its ZIP SHA-256, raw plan SHA-256, canonical plan SHA-256, exact proof run `36329787371`, and then invokes the DEC-288 freeze validator again against the current checkout.

Required reviewed identities include:

- DEC-287 proof artifact digest: `sha256:bb81bd8f0cb1adfc0054db4f5c16f13808793c520d443a0f05a89a90f92a415d`;
- raw plan SHA-256: `2ca76921e17096b444202573a950825244e07c27e0f476cecfb510ad5e0a95e5`;
- canonical plan SHA-256: `86b37433e183bfd9199822da0212b79fe11950461206335fc53e6f783210a74e`;
- frozen fail-closed proof run `36319888985` as workflow run number 1;
- zero historical-result attempts;
- target workflow run number 2 / attempt 1.

## Fresh live-plan requirement

Immediately before any write, the executor builds the DEC-286 live plan twice from:

- current `main` branch metadata;
- current `phase8a-exp061-discovery` manual-main run inventory.

Both plans must be byte-for-byte equivalent as Python objects.

Both must prove:

- exact executor head equals current main;
- proof run count = 1;
- proof run id = `36319888985`;
- proof workflow run number = 1;
- historical-result attempt count = 0;
- slot consumed = false;
- no historical-result run id exists;
- target workflow run number = 2;
- target run attempt = 1;
- planned command exactly `gh workflow run phase8a-exp061-discovery.yml --ref main`;
- historical execution source authorization = true;
- target runtime historical discovery execution authorization = true;
- target runtime discovery-result authorization = true;
- DEC-286 dispatch authorization = false;
- DEC-286 execute mode = false;
- all downstream locks remain false.

Any drift fails closed before dispatch.

## Executor implementation

Core:

`src/fmp/discovery/historical_executor.py`

Git blob:

`82dbec289ed69e7333a90fd28ce430b024a99936`

CLI:

`scripts/phase8a_exp061_historical_executor.py`

Git blob:

`a899b71c1054e4ccd5639f4487dad038b2e1f55f`

Workflow:

`.github/workflows/phase8a-exp061-historical-one-shot-execute.yml`

Git blob:

`4efb80cf9eee3f7073de28531babc269d3c7a8cc`

Focused tests:

`tests/test_phase8a_exp061_historical_executor.py`

Git blob:

`62b40b4577462d32deb0b341a778cb87ba7d2cba`

## One-shot workflow guard

The executor workflow:

- triggers only from a push to `main` affecting the executor workflow/core/CLI;
- requires `GITHUB_RUN_ATTEMPT=1`;
- requires exact merged-main checkout;
- pins DEC-288, DEC-285, DEC-286, active discovery workflow, activated CLI, executor source, and runtime dependency blobs;
- grants only `contents: read` and `actions: write`;
- queries its own workflow history and requires the current run to be the only main-push DEC-289 executor run ever materialized;
- requires that sole executor run to be workflow run number `1`;
- fails closed on any later executor push/rerun.

## Immediate pre-dispatch inventory guard

Immediately before invoking the executor CLI, the workflow reads the EXP-061 discovery workflow inventory and requires exactly one matching manual-main run:

- run id `36319888985`;
- workflow run number `1`;
- attempt `1`;
- terminal status `completed`;
- conclusion `failure`;
- exact gate-proof head `041b7b2f5aac8821156fab346df8ab30f4be2a7b`.

Any existing historical run blocks the executor.

## Post-dispatch identity proof

After submission, the executor workflow polls only the EXP-061 discovery workflow inventory until exactly two matching manual-main runs are visible.

It then requires:

- proof run `36319888985` still exists as run number 1 / attempt 1;
- exactly one non-proof run exists;
- the new historical run is workflow run number 2;
- its run attempt is 1;
- its head SHA equals the DEC-289 merged-main executor head;
- its run id is a positive integer.

The new historical run consumes the sole historical-result slot immediately, regardless of whether its later terminal result is success or failure.

## Immutable dispatch evidence

DEC-289 uploads one executor evidence artifact containing:

- executor JSON;
- latest exact discovery-workflow run inventory;
- exact historical run JSON after submission.

The evidence records:

- executor decision/version;
- executor head SHA;
- reviewed DEC-288 proof/artifact identities;
- reviewed plan raw/canonical SHA-256 values;
- both fresh plans agreed;
- exact dispatch command;
- historical-result dispatch authorized by DEC-289;
- dispatch submitted;
- historical-result slot consumed on submission;
- expected target run number 2 / attempt 1;
- target historical discovery/result execution authorization true;
- all downstream locks false.

## Downstream locks

DEC-289 keeps false:

- historical rerun;
- historical retry;
- historical replacement;
- reserved 2023-2026 robustness access;
- candidate compilation;
- promotion;
- Phase 8B;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.

The historical result, whether successful or not, is evidence only until separately reviewed.

## Next gate

After the DEC-289 executor has submitted run #2, no further historical dispatch is authorized.

The next task is terminal review of the exact run #2 result:

- bind exact run/job/artifact identities;
- inspect every cell and aggregate result if present;
- classify success, partial failure, or fail-closed outcome;
- freeze the result with no retry/replacement;
- only then decide whether any pattern hypotheses qualify for later candidate compilation.

Candidate compilation and all trading paths remain locked during that review.
