# Phase 8A — Concrete 2017 Execution Authorization

**Date:** 2026-10-04  
**Status:** CONCRETE SOURCE-ONLY AUTHORIZATION / RUNTIME NOT INSTALLED  
**Decision:** DEC-535

## Basis

DEC-534 is concrete from successful repository-hosted preflight workflow run
`37210041270` on
`23231c82360da824e3b9eedbd4e2a5edcffd0d45`.

Its immutable artifact is:

- artifact ID: `11306121033`
- digest: `sha256:531c468e36ac80f6c0c24620c14b78d2b2faad869d53be098efe7a2b31425e04`
- expected 2017 annual workflow identity: run 379 / attempt 1
- predecessor: successful 2016 annual run `37206992367` / run 378 / attempt 1

The live annual dispatch inventory remains exactly:
failed run 1, failed run 376, successful 2015 run 377, and successful 2016 run
378. Run 379 is absent.

## Authorization

DEC-535 converts only the exact DEC-534 preflight into a source-only execution
authorization for annual segment 2017, run 379, attempt 1.

The contract enables only the historical artifact-read, catalogue-execution,
result-production, and annual-workflow-dispatch authority required by that one
future research run.

It does **not** install a 2017 runtime authorization gate. The current runtime
blob remains
`b564f5a26fdef146fc6080962e7c4762b0b5949a`, which has no 2017 route.

The repository-hosted DEC-535 builder is read-only. It rechecks the unconsumed
run-379 slot, downloads the exact DEC-534 artifact, validates the authorization,
and uploads a DEC-535 evidence artifact.

## Locked surfaces

DEC-535 contains no dispatch command and executes no dispatch. It authorizes no
rerun, retry, replacement run, run 380+, 2018+ execution, cross-year synthesis,
Strategy V1 promotion, Phase 8B, broker mutation, demo/live order, real-money
action, or trading.

## Next gate

`READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2017_RUNTIME_AUTHORIZATION_PLAN`
