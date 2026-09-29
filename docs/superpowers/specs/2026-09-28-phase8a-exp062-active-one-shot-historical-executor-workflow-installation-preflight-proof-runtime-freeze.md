# Phase 8A — EXP-062 Active Workflow-Installation Preflight Proof Runtime Freeze

**Date:** 2026-09-28  
**Status:** CONCRETE RUNTIME EVIDENCE BOUND / INSTALL + EXECUTOR STILL LOCKED  
**Decision:** DEC-371  
**Experiment:** EXP-20260927-062  
**Predecessors:** DEC-334, DEC-368, DEC-369, DEC-370

## Purpose

DEC-371 binds the actual successful DEC-368 merged-main active workflow-installation
preflight proof to immutable runtime evidence.

It re-runs DEC-369 against the downloaded DEC-367 preflight bytes, replays DEC-370,
requires the exact DEC-370 freeze fingerprint, and verifies the downloaded artifact
ZIP SHA-256 against GitHub's artifact digest.

## Concrete evidence

DEC-371 binds:

- merged proof head: `035c0ee8190a7eb1e2c8ac80771e6eeb19d1e8e1`;
- proof run: `36484309283`;
- proof job: `109137344254`;
- proof artifact: `10997847720`;
- artifact / ZIP SHA-256:
  `d122e474752f1ec8127eb610b55321dbf94cc7dcb339eca43eafb7e429ef4a07`;
- raw installation-preflight SHA-256:
  `5bf7760c7ad36e642eeeaf9e29b5fb0e5108a4059207ff2d7d75bd4c9f6bcf3b`;
- canonical installation-preflight SHA-256:
  `30de670f8483139b23fbd51bd05444677278fd7d1ba1f1eb8f0cc33409cf3a74`;
- DEC-370 freeze fingerprint:
  `51e47a3d6d2876b52e2090714e6f89b4c2ce0ae2d869d79e5b2cd4586c774af6`.

It also pins the exact DEC-369 reviewer, DEC-370 freeze builder, and DEC-334
terminal-review contract Git blobs.

## Safety boundary

The active executor workflow path remains absent. Historical-result attempts remain
zero and target run #2 / attempt 1 remains the sole future historical attempt.

DEC-371 keeps false:

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

The next safe gate is a source-only active one-shot historical executor workflow
install-authorization contract. It may define future install authorization criteria,
but cannot install the workflow, make the executor available, or dispatch historical
discovery without a later explicit gate.
