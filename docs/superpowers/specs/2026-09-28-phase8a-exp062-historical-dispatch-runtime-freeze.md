# Phase 8A — EXP-062 Historical Dispatch Plan Runtime Evidence Freeze

**Date:** 2026-09-28  
**Status:** CONCRETE DEC-320 RUNTIME EVIDENCE BOUND / NO DISPATCH  
**Decision:** DEC-323  
**Experiment:** EXP-20260927-062  
**Predecessors:** DEC-320, DEC-321, DEC-322

## Purpose

DEC-323 binds the actual successful DEC-320 read-only dispatch-plan proof to immutable
runtime identities and independently verified artifact/plan hashes.

It re-runs DEC-321 review and DEC-322 deterministic freezing against the supplied raw
evidence. It does not dispatch historical discovery and does not expose an executor.

## Concrete proof evidence

The frozen DEC-320 proof is:

- merged head: `fee1a78168254e7e8fecc104859d1a231b727243`;
- workflow run id: `36418793172`;
- workflow run number / attempt: `1 / 1`;
- conclusion: `success`;
- sole job id: `108916232597`;
- sole artifact id: `10967344018`;
- artifact name:
  `exp062-dec320-historical-dispatch-plan-fee1a78168254e7e8fecc104859d1a231b727243`;
- GitHub artifact digest:
  `sha256:ca0f1156fab234327bbcdd9c3150cb7904ed6def230f035019b2139c4c523adf`;
- independently recomputed ZIP SHA-256:
  `ca0f1156fab234327bbcdd9c3150cb7904ed6def230f035019b2139c4c523adf`;
- raw plan SHA-256:
  `a6fa5f3a7f3f45df5d64efe1661a5b17887f88fded31e1cbb1620df5b18a95d1`;
- canonical plan SHA-256:
  `41ca6c710d8750851350c2108b42970501a5efa14481cff61e2a66877ee90f6d`.

The artifact contains only `historical-dispatch-plan.json`.

## Source bindings

DEC-323 pins:

- DEC-321 reviewer blob:
  `8dee8008204ed816df211861ff4a7fb9e952d781`;
- DEC-322 freeze-builder blob:
  `6b7ab36c939fca7a9d53569e4617ebe6584e5b7c`.

DEC-321 in turn pins the DEC-320/319/318/317 source stack.

## Replayed review and freeze

DEC-323 must reproduce:

- DEC-321 reviewed stage:
  `EXP062_HISTORICAL_DISPATCH_PLAN_PROOF_REVIEWED_SLOT_AVAILABLE`;
- zero historical-result attempts;
- unconsumed slot;
- target run #2 / attempt 1;
- exact frozen discovery command;
- one-shot dispatch source contract true;
- actual dispatch, executor availability, and execute mode false;
- DEC-322 freeze fingerprint:
  `b7d3e5461511c8e14dd4402028ad24daefcf431cece3b59575588ba915db510e`.

## Safety boundary

DEC-323 keeps false:

- historical-result dispatch;
- historical executor availability;
- execute mode;
- rerun / retry / replacement;
- reserved 2023-2026 robustness access;
- candidate compilation / promotion;
- Phase 8B;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.

The historical-result slot is still verified empty.

## Next gate

The next safe gate is a separate **source-only one-shot historical executor contract**.
It may define the exact prerequisites that a future executor would have to satisfy, but
must not submit the workflow itself.

A later repository-hosted executor remains a separate gate.
