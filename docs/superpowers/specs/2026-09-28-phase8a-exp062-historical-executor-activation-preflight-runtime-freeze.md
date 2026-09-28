# Phase 8A — EXP-062 Executor Activation-Preflight Runtime Evidence Freeze

**Date:** 2026-09-28  
**Status:** CONCRETE RUNTIME EVIDENCE BOUND / EXECUTOR + DISPATCH STILL LOCKED  
**Decision:** DEC-336  
**Experiment:** EXP-20260927-062  
**Predecessors:** DEC-333, DEC-334, DEC-335

## Purpose

DEC-336 binds the actual successful DEC-332 merged-main executor
activation-preflight proof to exact runtime evidence.

It re-runs the DEC-333 reviewer against the downloaded proof bytes, re-runs DEC-335
deterministic freezing, requires the exact DEC-335 fingerprint, and independently
checks that the downloaded artifact ZIP SHA-256 equals GitHub's artifact digest.

## Concrete evidence

The bound proof is:

- merged head: `12d11320ae302902df0a0deb7343408922deee83`;
- workflow run: `36431469794`, run #1 / attempt 1;
- proof job: `108958446980`;
- proof artifact: `10973597441`;
- artifact/ZIP SHA-256:
  `ee6e7ac2e8c18e1f8d276bba14ca942e20615143316ac185f4b814333804c2d5`;
- raw activation-preflight SHA-256:
  `775010a0c3d4afe11191adb53d8ad54e7cf0d5de85b1a0b5adcb28c470e9a4a5`;
- canonical activation-preflight SHA-256:
  `98b9180ae3b438b3c372ba34cbab9473d7f38ba5c1eb1add2dee988df4e09ad8`;
- expected DEC-335 freeze fingerprint:
  `567320a598f245a8e7521281ddde3a1acaa0e3f294aebe12554688d2258f020b`.

DEC-336 also pins the DEC-333 reviewer, DEC-334 terminal-review contract, and DEC-335
freeze-builder source blobs.

## Safety boundary

The historical-result slot is still empty. Target remains run #2 / attempt 1.

DEC-336 keeps false:

- historical executor availability;
- historical-result dispatch authorization;
- execute mode;
- rerun / retry / replacement;
- reserved 2023-2026 access;
- candidate compilation / promotion;
- Phase 8B;
- demo / broker / live / real-money / trading.

The historical discovery command remains frozen evidence only and is not submitted.

## Next gate

The next safe gate is a source-only one-shot historical executor workflow that is
bound to DEC-336 and the predeclared DEC-334 terminal-review criteria.

That gate must still expose no dispatch until its own current-main preflight/proof
sequence is satisfied.
