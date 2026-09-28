# Phase 8A — EXP-062 Workflow-Preflight Proof Runtime Freeze

**Date:** 2026-09-28  
**Status:** CONCRETE RUNTIME EVIDENCE BOUND / EXECUTOR + DISPATCH STILL LOCKED  
**Decision:** DEC-347  
**Experiment:** EXP-20260927-062  
**Predecessors:** DEC-334, DEC-344, DEC-345, DEC-346

## Purpose

DEC-347 binds the actual successful DEC-344 merged-main workflow-preflight proof to
immutable runtime evidence.

It re-runs DEC-345 against the downloaded DEC-343 preflight bytes, replays DEC-346,
requires the exact DEC-346 freeze fingerprint, and verifies the downloaded artifact
ZIP SHA-256 against GitHub's artifact digest.

## Concrete evidence

DEC-347 binds:

- merged proof head: `c43a1701cadd57c25903d3b637f2af70b28d1065`;
- proof run: `36455684780`;
- proof job: `109041310360`;
- proof artifact: `10984953455`;
- artifact / ZIP SHA-256:
  `eec64c9bb1f6688dca010825e83e191c6a423d21bf6522396d7f650ec2db675f`;
- raw workflow-preflight SHA-256:
  `56981ba62638129f39693239d22b76c65cb3a8e0b236741b3a80984137c2c0d7`;
- canonical workflow-preflight SHA-256:
  `d6bf96a73b1377ad65887c6ba001c2c2d39812d58205e59e304c1c88e3ef22dc`;
- DEC-346 freeze fingerprint:
  `3ba4b6aba0cafab3989c1f20536ad36603786efdcef49964a31bc99b73a79988`.

It also pins the exact DEC-345 reviewer, DEC-346 freeze builder, and DEC-334
terminal-review contract Git blobs.

## Safety boundary

The historical-result slot remains empty and target run #2 / attempt 1 remains the
only future historical attempt.

DEC-347 keeps false:

- historical executor availability;
- historical-result dispatch authorization;
- execute mode;
- rerun / retry / replacement;
- reserved 2023-2026 access;
- candidate compilation / promotion;
- Phase 8B;
- demo / broker / live / real-money / trading.

## Next gate

The next safe gate is a source-only one-shot historical executor workflow-install
contract. It may define installation source, but cannot make the executor available or
dispatch the historical workflow without a later explicit gate.
