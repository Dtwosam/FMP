# Phase 8A — EXP-062 Active Install-Authorization Preflight Proof Runtime Freeze

**Date:** 2026-09-29  
**Status:** CONCRETE RUNTIME EVIDENCE BOUND / INSTALL + EXECUTOR STILL LOCKED  
**Decision:** DEC-377  
**Experiment:** EXP-20260927-062  
**Predecessors:** DEC-334, DEC-374, DEC-375, DEC-376

## Purpose

DEC-377 binds the actual successful DEC-374 merged-main active workflow
install-authorization-preflight proof to immutable runtime evidence.

It re-runs DEC-375 against the downloaded DEC-373 preflight bytes, replays DEC-376,
requires the exact DEC-376 freeze fingerprint, and verifies the downloaded artifact
ZIP SHA-256 against GitHub's artifact digest.

## Concrete evidence

DEC-377 binds:

- merged proof head: `c23ba694fcf60e2a73280f59fe0bf13d90ffa229`;
- proof run: `36542684978`;
- proof job: `109321600936`;
- proof artifact: `11020419084`;
- artifact / ZIP SHA-256:
  `f7829f71c481143517b918c7d54b1cb43136edcd50ea9076e3795935bd994384`;
- raw install-authorization-preflight SHA-256:
  `e5de1145a6f39ca42413fb5ce1eed297d8bdcf572923e296d2b6d773e945e45f`;
- canonical install-authorization-preflight SHA-256:
  `994b96d76cf50cfae019d21b4b478d6e0b6ffc0c99fda9efa7c7aa4bf50263dc`;
- DEC-376 freeze fingerprint:
  `fb4c445610884db868a516f9a2086c8d0a6f22d397cb7e8d39806548101c1595`.

It also pins the exact DEC-375 reviewer, DEC-376 freeze builder, and DEC-334
terminal-review contract Git blobs.

## Safety boundary

The active executor workflow path remains absent. Historical-result attempts remain
zero and target run #2 / attempt 1 remains the only future historical attempt.

DEC-377 keeps false:

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

The next safe gate is a source-only active workflow install-decision contract. It may
define the next review boundary, but cannot install the workflow or authorize
historical dispatch without a later explicit gate.
