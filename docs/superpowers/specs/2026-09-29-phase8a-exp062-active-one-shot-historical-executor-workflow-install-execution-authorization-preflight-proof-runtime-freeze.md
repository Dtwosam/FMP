# Phase 8A — EXP-062 Install-Execution Authorization Preflight Proof Runtime Freeze

**Date:** 2026-09-29  
**Status:** CONCRETE RUNTIME EVIDENCE BOUND / INSTALL + EXECUTOR STILL LOCKED  
**Decision:** DEC-389  
**Experiment:** EXP-20260927-062  
**Predecessors:** DEC-386, DEC-387, DEC-388

## Purpose

DEC-389 binds the real successful DEC-386 merged-main proof of the active one-shot
historical executor workflow install-execution-authorization preflight to concrete
immutable runtime evidence.

## Bound runtime evidence

- merged head: `cdbef40d1c9908650155933ae5073909ad9be24d`;
- proof run: `36558750341`, run #1 / attempt 1, success;
- proof job: `109374198795`;
- proof artifact: `11029316948`;
- artifact / downloaded ZIP SHA-256:
  `5908aff795243b98d8dc0f2b15b603df77ec1b1313c03d76b63452c181bf8d02`;
- raw DEC-385 preflight SHA-256:
  `ff645bc0c6742cf05f1edbbb8438b2659ccbf00cd6d40edef284acf1e03c8dd2`;
- canonical DEC-385 preflight SHA-256:
  `6fe2e118136351ffd4d72d6aad7093e83758905378c654a6df0eb927d7ab43e6`;
- deterministic DEC-388 freeze fingerprint:
  `594b2db3aa50b5c09d7f53a4635cea40b4e566fddd0d16a6574e1322ef8a48af`.

DEC-389 re-runs the DEC-387 reviewer, replays DEC-388 deterministic freezing, and
requires the downloaded artifact ZIP hash to match GitHub's artifact digest.

## Authority boundary

The install-authorization, install-decision, and install-execution-authorization
source-only gates remain true. Actual workflow-install authorization remains false.

The active executor workflow path remains absent. Historical executor availability,
historical-result dispatch, execute mode, rerun/retry/replacement, reserved
2023-2026 access, candidate compilation/promotion, Phase 8B, demo, broker/live,
real-money, and trading remain locked.

Historical-result attempts remain zero; target run #2 / attempt 1 remains the only
future historical-result attempt.

## Next gate

The next safe gate is a source-only active workflow install-execution contract. It
must not install the workflow or dispatch historical discovery.
