# Phase 8A — EXP-062 Adapter Proof Review Contract

**Date:** 2026-09-27  
**Status:** SOURCE-ONLY PREDECLARED REVIEW / NO PROOF RESULT YET  
**Decision:** DEC-295  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-294

DEC-295 freezes how the DEC-294 merged-main adapter proof will be judged before that proof runs.

A successful proof must be the exact `phase8a-exp062-adapter-proof` push-to-main workflow, attempt 1, at the caller-supplied merged head. Success requires exactly ten completed jobs: nine named pair/timeframe adapter probes plus `exp062-adapter-probe-aggregate`. Every job must conclude `success`.

Success also requires exactly ten non-expired commit-scoped artifacts: nine `exp062-dec294-adapter-probe-<symbol>-<timeframe>-<head>` artifacts plus one `exp062-dec294-adapter-proof-<head>` aggregate artifact.

Any unexpected job or artifact fails closed. A terminal non-success can be reviewed as proof failure but grants no execution authority.

Review source: `src/fmp/discovery/exp062_adapter_proof_review.py` blob `d3f1283cffae4e7aa6c6a9bd2b8403743cc3709d`.

Focused tests: `tests/test_phase8a_exp062_adapter_proof_review.py` blob `3ce8157054e04ef88b47624404c31b9a187fe6fa`.

Bound DEC-294 workflow blob: `c4c0a980e2675b1cc696ca02294a15f079874ada`.

Regardless of proof outcome, historical discovery execution/result production, reserved 2023-2026 access, candidate compilation, promotion, Phase 8B, demo, broker/live, real-money, and trading remain locked.

After a complete successful proof, a later decision must bind and inspect the exact ten artifacts and aggregate proof contents before any EXP-062 historical execution governance is considered.
