# Phase 8A — EXP-062 Workflow-Install Preflight Proof Runtime Freeze

**Date:** 2026-09-28  
**Status:** CONCRETE RUNTIME EVIDENCE BOUND / INSTALL + EXECUTOR STILL LOCKED  
**Decision:** DEC-353  
**Experiment:** EXP-20260927-062  
**Predecessors:** DEC-334, DEC-350, DEC-351, DEC-352

## Purpose

DEC-353 binds the actual successful DEC-350 merged-main workflow-install-preflight
proof to immutable runtime evidence.

It re-runs DEC-351 against the downloaded DEC-349 preflight bytes, replays DEC-352,
requires the exact DEC-352 freeze fingerprint, and verifies the downloaded artifact
ZIP SHA-256 against GitHub's artifact digest.

## Concrete evidence

DEC-353 binds:

- merged proof head: `bef60cd8656f0db48293570c13f91e2e09fe5be8`;
- proof run: `36461898040`;
- proof job: `109062250103`;
- proof artifact: `10987972547`;
- artifact / ZIP SHA-256:
  `60a723a55502ee9b8145258c5482ce71b82b2331c572378536b14d78f6ef2f91`;
- raw install-preflight SHA-256:
  `ee754581b87576c3c23228a2371b88b3b8a38fdcd9c20ebd2c222c18f7c65e0d`;
- canonical install-preflight SHA-256:
  `5c1893ea24a627ea421f05564d6d0cc490215201c01162fbe0b6ab519a323c8b`;
- DEC-352 freeze fingerprint:
  `75fad6795f4046d83f5ae29f08475c969e29d3fe3af0e3448dde46292a959f4a`.

It also pins the exact DEC-351 reviewer, DEC-352 freeze builder, and DEC-334
terminal-review contract Git blobs.

## Safety boundary

The expected future executor workflow path remains absent. The historical-result slot
remains empty and target run #2 / attempt 1 remains the only future historical attempt.

DEC-353 keeps false:

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

The next safe gate is a source-only one-shot historical executor workflow-installation
source contract. It may define installation source, but cannot install the workflow,
make the executor available, or dispatch historical discovery without a later
explicit gate.
