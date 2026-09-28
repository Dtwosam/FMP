# Phase 8A — EXP-062 One-Shot Historical Executor Source-Proof Runtime Freeze

**Date:** 2026-09-28  
**Status:** CONCRETE RUNTIME EVIDENCE BOUND / EXECUTOR + DISPATCH STILL LOCKED  
**Decision:** DEC-341  
**Experiment:** EXP-20260927-062  
**Predecessors:** DEC-334, DEC-338, DEC-339, DEC-340

## Purpose

DEC-341 binds the actual successful DEC-338 one-shot historical executor source proof
to immutable runtime evidence.

It re-runs the DEC-339 reviewer against the downloaded source-contract bytes, replays
the DEC-340 deterministic freeze, requires the exact DEC-340 freeze fingerprint, and
verifies the downloaded artifact ZIP independently against GitHub's artifact digest.

## Concrete evidence

DEC-341 binds:

- merged proof head:
  `e9dfbf034614b54598d31653da3868ed66aa90ba`;
- proof run:
  `36442399041`;
- proof job:
  `108995955292`;
- proof artifact:
  `10979242048`;
- artifact / ZIP SHA-256:
  `7dff775fc559cf9dbd754f45c24fbc814035b1602b59ca5eb9f82678af4e8b88`;
- raw source-contract SHA-256:
  `484ad49fa3b3e925ae4a3576af840a8736c9b25ef439b619e8b60e8011f94d63`;
- canonical source-contract SHA-256:
  `cb650b81c2549bfb5bfa62f6609bec9b39e4ed118f3e54c302a48a3a27a11616`;
- DEC-340 freeze fingerprint:
  `e340394fb987c68d9203a57c9cd363f255729b3424a9600ec03533ff421960a8`.

The source also pins the exact DEC-339 reviewer, DEC-340 freeze builder, and DEC-334
terminal-review contract Git blobs.

## Safety boundary

DEC-341 keeps false:

- historical executor availability;
- historical-result dispatch authorization;
- execute mode;
- rerun / retry / replacement;
- reserved 2023-2026 access;
- candidate compilation / promotion;
- Phase 8B;
- demo / broker / live / real-money / trading.

The historical-result slot remains empty and target run #2 / attempt 1 remains the
only future historical attempt.

## Next gate

The next safe gate is a source-only one-shot historical executor workflow contract.
That future source gate may define the workflow shape, but it must not make the
historical executor available or dispatch the workflow without a later explicit gate.
