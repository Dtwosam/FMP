# Phase 8A — EXP-062 Install-Decision Preflight Proof Runtime Freeze

**Date:** 2026-09-29  
**Status:** CONCRETE RUNTIME EVIDENCE BOUND / INSTALL + EXECUTOR STILL LOCKED  
**Decision:** DEC-383  
**Experiment:** EXP-20260927-062  
**Predecessors:** DEC-334, DEC-380, DEC-381, DEC-382

## Purpose

DEC-383 binds the actual successful DEC-380 merged-main install-decision-preflight
proof to immutable runtime evidence.

It re-runs DEC-381 against the downloaded DEC-379 preflight bytes, replays DEC-382,
requires the exact DEC-382 freeze fingerprint, and independently verifies the
downloaded artifact ZIP SHA-256 against GitHub's artifact digest.

## Concrete evidence

- merged proof head: `fa96bc731ed8d21cec883451f7ec5e984b74df40`;
- proof run: `36553935570`;
- proof job: `109358450875`;
- proof artifact: `11025737149`;
- artifact / ZIP SHA-256:
  `f863ea57b45e2c0e12892732747094f8f4f63793cf212be018d7d6cbade6555b`;
- raw install-decision-preflight SHA-256:
  `05bb0e78cd14d22ba84a2bd46bc2fde894e088ad4e96fdd463a040ea91718ed0`;
- canonical install-decision-preflight SHA-256:
  `27e6ef7221062844b1f4b12f6fae55c9de2d933c4f606411cd676e982201487f`;
- DEC-382 freeze fingerprint:
  `be15d3ffe0a66befeec91694e5c412e0d7678818835774361258edf06b06b6f8`.

DEC-383 also pins the exact DEC-381 reviewer, DEC-382 freeze builder, and DEC-334
terminal-review contract Git blobs.

## Safety boundary

The active executor workflow path remains absent. Historical-result attempts remain
zero and target run #2 / attempt 1 remains the only future historical attempt.

Install-authorization and install-decision source contracts remain source-only.
Actual workflow installation, executor availability, historical dispatch, execute
mode, rerun/retry/replacement, reserved 2023-2026 access, candidate compilation /
promotion, Phase 8B, demo / broker / live / real-money / trading remain false.

## Next gate

The next safe gate is a source-only workflow install-execution authorization
contract. It may define a later installation boundary but cannot install the workflow
or dispatch historical discovery by itself.
