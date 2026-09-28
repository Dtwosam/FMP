# Phase 8A — EXP-062 Historical Execution Plan Runtime Evidence Freeze

**Date:** 2026-09-28  
**Status:** CONCRETE DEC-314 RUNTIME EVIDENCE BOUND / NO DISPATCH  
**Decision:** DEC-317  
**Experiment:** EXP-20260927-062  
**Predecessors:** DEC-314, DEC-315, DEC-316

## Purpose

DEC-317 binds the actual successful DEC-314 read-only historical execution-plan proof
to immutable runtime identities and independently verified artifact/plan hashes.

It re-runs DEC-315 review and DEC-316 deterministic freezing against the supplied raw
evidence. It does not dispatch historical discovery.

## Concrete proof evidence

The frozen DEC-314 proof is:

- merged head: `ea69e82c9f653facba8ed6589fe4243848187ad3`;
- proof workflow run id: `36414282818`;
- workflow run number / attempt: `1 / 1`;
- conclusion: `success`;
- sole job id: `108901556593`;
- sole artifact id: `10966632240`;
- artifact name:
  `exp062-dec314-historical-execution-plan-ea69e82c9f653facba8ed6589fe4243848187ad3`;
- GitHub artifact digest:
  `sha256:9299ebfd344c0bd2a66ccd6e29339e035840c8b4204cbfc16bb6d3e938a53254`;
- independently recomputed ZIP SHA-256:
  `9299ebfd344c0bd2a66ccd6e29339e035840c8b4204cbfc16bb6d3e938a53254`;
- raw plan SHA-256:
  `594b5bd129a93ad7b07f69e00826251dd693f1bb388e6b4dff64eda0b34a7c72`;
- canonical plan SHA-256:
  `152bbb90efe3941f1338c73cf24f91f10a877cda3ee5c46f08c4f556d653a12f`.

The artifact contains only `historical-execution-plan.json`.

## Source bindings

DEC-317 pins:

- DEC-315 reviewer blob:
  `284789801505b9391be19ebb1a19c4fae28e2444`;
- DEC-316 freeze-builder blob:
  `2867bc05986bf93dc531d152760bbbac604854fe`.

DEC-315 in turn pins the DEC-314/313/312/311 source stack.

## Replayed review and freeze

DEC-317 must reproduce:

- DEC-315 reviewed stage:
  `EXP062_HISTORICAL_EXECUTION_PLAN_PROOF_REVIEWED_SLOT_AVAILABLE`;
- zero historical-result attempts;
- unconsumed slot;
- target run #2 / attempt 1;
- exact future command:
  `gh workflow run phase8a-exp062-discovery.yml --ref main`;
- DEC-316 freeze fingerprint:
  `7c7d99f4c89aac4e11d27536b9f8d2d39322672a9a0332f141d1d86f93b19be3`.

The reviewed plan still authorizes historical execution/result production only inside
the exact future DEC-312 runtime. The proof itself executes nothing.

## Safety boundary

DEC-317 keeps false:

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

The historical-result slot is verified empty.

## Next gate

The next safe gate is a separate **source-only one-shot historical dispatch
authorization contract**. That contract may define the exact conditions under which a
single dispatcher could submit run #2, but must not itself dispatch the workflow.

A later one-shot executor remains a separate gate.
