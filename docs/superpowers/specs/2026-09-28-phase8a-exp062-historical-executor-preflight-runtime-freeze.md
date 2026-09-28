# Phase 8A — EXP-062 Historical Executor Preflight Runtime Evidence Freeze

**Date:** 2026-09-28  
**Status:** CONCRETE DEC-326 RUNTIME EVIDENCE BOUND / EXECUTOR STILL LOCKED  
**Decision:** DEC-329  
**Experiment:** EXP-20260927-062  
**Predecessors:** DEC-326, DEC-327, DEC-328

## Purpose

DEC-329 binds the actual successful DEC-326 read-only executor-preflight proof to
immutable runtime identities and independently verified artifact/preflight hashes.

It re-runs DEC-327 review and DEC-328 deterministic freezing against the supplied raw
evidence. It does not make an executor available and does not dispatch historical
discovery.

## Concrete proof evidence

The frozen DEC-326 proof is:

- merged head: `a811aacaae82e15b18267b6e4ba659054abb0341`;
- proof workflow run id: `36422936991`;
- run number / attempt: `1 / 1`;
- conclusion: `success`;
- sole job id: `108929843306`;
- sole artifact id: `10970303347`;
- artifact name:
  `exp062-dec326-historical-executor-preflight-a811aacaae82e15b18267b6e4ba659054abb0341`;
- GitHub artifact digest:
  `sha256:fe116a7fff7ffdec27e787d3cd7981ac67772276efb12a5b434b04ee3855c74c`;
- independently recomputed ZIP SHA-256:
  `fe116a7fff7ffdec27e787d3cd7981ac67772276efb12a5b434b04ee3855c74c`;
- raw preflight SHA-256:
  `5dfa7800a8dcbe4537910690a0ba70b3c93467c685d7c5c99898d0b6d111f9d8`;
- canonical preflight SHA-256:
  `9970dcbf44241a3b9ffc6aab01d8a3bab6749813f88d0771dee101ea640aec3d`.

The artifact contains only `historical-executor-preflight.json`.

## Source bindings

DEC-329 pins:

- DEC-327 reviewer blob:
  `da3febc87e69a81f88088c0b34ba0650956d1873`;
- DEC-328 freeze-builder blob:
  `ce37dd70c167182441b503c38b1197223917ff72`.

## Replayed review and freeze

DEC-329 must reproduce:

- DEC-327 reviewed stage:
  `EXP062_HISTORICAL_EXECUTOR_PREFLIGHT_PROOF_REVIEWED_SLOT_AVAILABLE`;
- zero historical-result attempts;
- unconsumed historical slot;
- target run #2 / attempt 1;
- exact frozen discovery command;
- executor source authorization true;
- actual executor availability, dispatch, and execute mode false;
- DEC-328 freeze fingerprint:
  `2e295d03066fcfa4dcea300c3f263bcf6a67cb96d6b356410821af493b2d5675`.

## Safety boundary

DEC-329 keeps false:

- historical executor availability;
- historical-result dispatch;
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

The historical-result slot remains verified empty.

## Next gate

The next safe gate is a separate **source-only one-shot historical executor activation
contract**. It may define the exact prerequisites under which an executor could later
be installed, but must not itself dispatch the workflow.
