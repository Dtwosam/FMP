# Phase 8A — EXP-044 Operator Source and Evidence Preflight

**Date:** 2026-09-23  
**Status:** APPROVED BEFORE ANY EXP-044 RESULT-PRODUCING RUN  
**Decision:** DEC-082  
**Experiment:** EXP-20260923-044

## 1. Purpose

DEC-081 made EXP-044 manual dispatch reproducible from an authorized machine.

DEC-082 strengthens that helper so it refuses to prepare a dispatch when the underlying historical source or prior-stage evidence is already invalid.

The workflow remains the final authority and independently repeats the same checks after dispatch.

## 2. Source preflight before both stages

Before either feature or outcome preparation, the operator helper fetches current GitHub metadata for the exact accepted Phase 2 EURUSD, GBPUSD, and USDJPY artifacts.

It invokes the same DEC-078 source-preflight implementation used by the workflows.

The helper therefore requires, before constructing a dispatch command:

- exact frozen artifact IDs, names, sizes, and ZIP SHA-256 digests;
- exact Phase 2 source run and source commit;
- non-expired artifacts;
- at least 12 hours of remaining artifact lifetime.

No new Dukascopy acquisition or substitution is performed.

## 3. Aggregate feature evidence before outcome preparation

A successful feature workflow run is no longer sufficient by itself for operator-side outcome preparation.

The helper also:

1. lists the exact feature run's artifacts;
2. requires exactly one non-expired artifact named
   `exp044-market-feature-evidence-<feature head SHA>`;
3. downloads that ZIP;
4. safely extracts it;
5. requires exactly one `feature-evidence.json`;
6. validates the evidence fingerprint and full frozen feature-evidence contract through the existing EXP-044 evidence loader;
7. requires the evidence `code_commit` to equal the feature run's exact head SHA;
8. requires all model/shadow/demo/broker/live/real-money authorization flags to remain false.

Only after those checks may the helper report the outcome stage as ready to dispatch.

## 4. Artifact path safety

Downloaded evidence ZIP members are checked to ensure extraction cannot escape the temporary destination root.

The operator helper does not persist the downloaded aggregate feature evidence after the preflight completes.

The authoritative copy remains the GitHub Actions artifact and the outcome workflow independently downloads/revalidates it again.

## 5. Duplicate-run boundary

DEC-081 duplicate-run refusal remains unchanged.

If a manual `main` feature or outcome run already exists, the helper refuses to create another and requires inspection of the existing run/evidence.

## 6. Dry-run and execution boundary

The helper remains dry-run by default.

`--execute` is still required for the final `gh workflow run` invocation.

A successful submission still means only that GitHub accepted the dispatch request; it does not imply a run result or research result exists.

## 7. Frozen research semantics unchanged

DEC-082 changes no:

- historical data;
- feature definition;
- outcome definition;
- cost/slippage assumptions;
- artifact identity;
- aggregate evidence semantics;
- DEC-074 readiness;
- model protocol;
- model/trading authorization.

## 8. Next gate

The next hard gate remains the first authoritative manual dispatch of `phase8a-exp044-market-features` from merged `main`.

DEC-082 only makes the existing manual gate fail earlier and more clearly when prerequisite source/evidence is invalid.
