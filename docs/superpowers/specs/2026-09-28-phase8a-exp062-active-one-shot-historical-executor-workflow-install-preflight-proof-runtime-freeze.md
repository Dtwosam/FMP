# Phase 8A — EXP-062 Active Workflow-Install Preflight Proof Runtime Freeze

**Date:** 2026-09-28  
**Status:** CONCRETE RUNTIME EVIDENCE BOUND / INSTALL + EXECUTOR STILL LOCKED  
**Decision:** DEC-365  
**Experiment:** EXP-20260927-062  
**Predecessors:** DEC-334, DEC-362, DEC-363, DEC-364

## Purpose

DEC-365 binds the actual successful DEC-362 merged-main active workflow-install-
preflight proof to immutable runtime evidence.

It re-runs DEC-363 against the downloaded DEC-361 preflight bytes, replays DEC-364,
requires the exact DEC-364 freeze fingerprint, and verifies the downloaded artifact
ZIP SHA-256 against GitHub's artifact digest.

## Concrete evidence

DEC-365 binds:

- merged proof head: `8e74ca94237963253b4fd6e42c42965cabec3ab1`;
- proof run: `36478916362`;
- proof job: `109119455390`;
- proof artifact: `10996155764`;
- artifact / ZIP SHA-256:
  `5554cabdf72e87c6c860746f1d76d0816a3dd3ebdf2b443b911b5027e81f070a`;
- raw active-install-preflight SHA-256:
  `c70cbdb3f593de110a21d6501d867ed23f6be70b7815993ef1b62fea1d2477fc`;
- canonical active-install-preflight SHA-256:
  `010f1bcdd595de78ebe55ad3729e641345f3c486e3a46e38a60a7072555ad30b`;
- DEC-364 freeze fingerprint:
  `2e8c36e891b20dc1811301a4b461d51c9fa46e34b098cbe5af1e3a27bc129932`.

It also pins the exact DEC-363 reviewer, DEC-364 freeze builder, and DEC-334
terminal-review contract Git blobs.

## Safety boundary

The active executor workflow path remains absent. The historical-result slot remains
empty and target run #2 / attempt 1 remains the only future historical attempt.

DEC-365 keeps false:

- workflow-install authorization;
- workflow installed state;
- historical executor availability;
- historical-result dispatch authorization;
- execute mode;
- rerun / retry / replacement;
- reserved 2023-2026 access;
- candidate compilation / promotion;
- Phase 8B;
- demo / broker / live / real-money / trading.

## Next gate

The next safe gate is a source-only active one-shot historical executor workflow-
installation contract. It may define installation source, but cannot install the
workflow, make the executor available, or dispatch historical discovery without a
later explicit gate.
