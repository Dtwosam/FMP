# Phase 8A — EXP-062 Dormant Executor Source Proof Runtime Freeze

**Date:** 2026-09-28  
**Status:** CONCRETE RUNTIME EVIDENCE BOUND / ACTIVE INSTALL + DISPATCH STILL LOCKED  
**Decision:** DEC-359  
**Experiment:** EXP-20260927-062  
**Predecessors:** DEC-334, DEC-356, DEC-357, DEC-358

## Purpose

DEC-359 binds the actual successful DEC-356 merged-main dormant executor source proof
to immutable runtime evidence.

It re-runs DEC-357 against the downloaded DEC-355 source artifact, replays DEC-358,
requires the exact DEC-358 freeze fingerprint, and verifies the downloaded artifact
ZIP SHA-256 against GitHub's artifact digest.

## Concrete evidence

DEC-359 binds:

- merged proof head: `67337de4b21efab0cbafb3c9237397f0a98d524e`;
- proof run: `36473192632`;
- proof job: `109100293950`;
- proof artifact: `10991479562`;
- artifact / ZIP SHA-256:
  `092e1daebf889560d27ebe57242772c3806322627dab03e64a2ff400d9b4b1d1`;
- raw dormant-source SHA-256:
  `1dfae5078e400fc2dbf0b10ef6d4297dc4d3c0660386ebb8c46b63c6dbe69060`;
- canonical dormant-source SHA-256:
  `4d6cf8999ecb5346a10ecb31cdc1b669736d4d466e6b31c503b3fbf1a5e633a7`;
- DEC-358 freeze fingerprint:
  `8ba4411b8c7468a1f0eecc0352490e00577452ce96a81710fca6457e779e9897`.

It also pins the exact DEC-357 reviewer, DEC-358 freeze builder, and DEC-334
terminal-review contract Git blobs.

## Safety boundary

The dormant template remains source only. The active executor workflow path remains
uninstalled. The historical-result slot remains empty and target run #2 / attempt 1
remains the only future historical attempt.

DEC-359 keeps false:

- active workflow-install authorization;
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
install contract. It may define the future installation boundary but cannot install
the workflow, make the executor available, or dispatch historical discovery without
a later explicit gate.
