# Phase 8A — EXP-044 Source Artifact Availability Preflight

**Date:** 2026-09-23  
**Status:** APPROVED BEFORE ANY EXP-044 RESULT-PRODUCING RUN  
**Decision:** DEC-078  
**Experiment:** EXP-20260923-044

## 1. Purpose

EXP-044 depends on the accepted Phase 2 GitHub Actions artifacts for EURUSD, GBPUSD, and USDJPY.

Those artifacts are immutable by identity but not permanently retained by GitHub Actions. On 2026-09-23 their metadata showed expiry on 2026-12-12.

DEC-078 adds an early, read-only availability/identity preflight to both EXP-044 workflows.

## 2. Frozen source identities

The preflight freezes and validates:

- Phase 2 source workflow run ID: `34782357048`;
- Phase 2 source head SHA: `158c1c121655867b7fb2886fe755585dfcd682ec`;
- main source branch;
- exact EURUSD/GBPUSD/USDJPY artifact IDs;
- exact artifact names;
- exact ZIP SHA-256 digests;
- exact artifact sizes;
- exact processed-manifest SHA-256 identities.

No new Dukascopy acquisition is performed.

## 3. Availability rule

Before heavy EXP-044 work begins, GitHub artifact metadata is fetched for all three frozen artifacts.

Each must:

- be non-expired;
- retain the exact frozen digest and size;
- bind the exact Phase 2 source run and commit;
- have at least 12 hours of remaining artifact lifetime.

If any source fails, the workflow stops before feature generation or outcome materialization.

## 4. Feature workflow

`phase8a-exp044-market-features` now runs `source-preflight` first.

The three pair-generation jobs require that preflight to pass.

## 5. Outcome workflow

`phase8a-exp044-market-outcomes` independently runs the same preflight because it may be dispatched later than the feature workflow.

The three pair-materialization jobs require both:

- successful exact feature-run validation; and
- successful Phase 2 source preflight.

## 6. Preflight output

The preflight report records:

- check time;
- earliest source expiry;
- exact frozen source identities;
- remaining lifetime;
- `source_ready=true`;
- `new_acquisition_performed=false`.

The report explicitly keeps all model/trading authorizations false.

It is operational evidence only and does not replace Phase 2 acceptance or EXP-044 research evidence.

## 7. Frozen research semantics unchanged

DEC-078 changes no:

- historical price data;
- feature definitions;
- outcome labels;
- horizon/cost assumptions;
- pair/timeframe universe;
- aggregate evidence rules;
- DEC-074 readiness;
- DEC-075 status semantics;
- model/trading authorization.

## 8. Next gate

The next hard gate remains the first authoritative dispatch of `phase8a-exp044-market-features` from merged `main`.

If the frozen Phase 2 Actions artifacts expire before execution, EXP-044 must not silently reacquire or substitute data. A separate, explicit preservation/republication decision must be made while retaining the exact accepted Phase 2 identities.
