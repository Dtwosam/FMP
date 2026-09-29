# Phase 8A — EXP-062 Workflow-Install Source-Preflight Recovery Proof Review

**Date:** 2026-09-29  
**Status:** SOURCE-ONLY RECOVERY-EVIDENCE REVIEWER / NO INSTALL OR DISPATCH  
**Decision:** DEC-408  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-407

DEC-408 reviews a successful DEC-407 recovery proof without rewriting the failed
DEC-404 run.

A valid reviewed proof requires:

- the corrected DEC-407 workflow blob
  `2adfc7bd1ccacd158a78532d31ff38f4f175229f`;
- workflow run #2 / attempt 1;
- exactly one successful read-only proof job;
- one non-expired DEC-407 recovery artifact;
- exact DEC-403 preflight JSON bytes;
- all six source-only gates true;
- all install/dispatch/trading authority fields false.

The review output carries immutable provenance for failed DEC-404 run
`36613664506`, failed head
`0db04ae49b3533778b08afa31e9ef9a26576b80c`, and failed job
`109561121322`.

The next safe gate is deterministic freezing of the reviewed recovery evidence.
