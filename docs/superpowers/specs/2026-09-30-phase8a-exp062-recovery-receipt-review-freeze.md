# Phase 8A — EXP-062 Recovery Receipt Review and Freeze

**Date:** 2026-09-30  
**Status:** SOURCE-ONLY REVIEW + DETERMINISTIC FREEZE  
**Decisions:** DEC-437, DEC-438  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-436

## DEC-437

DEC-437 strictly reviews a future successful DEC-436 recovery executor receipt.

A valid recovery run must be:

- workflow `phase8a-exp062-one-shot-historical-executor-recovery`;
- event `workflow_dispatch`;
- branch `main`;
- recovery run #1 / attempt 1;
- completed successfully;
- exactly one successful recovery job;
- exactly one non-expired DEC-436 receipt artifact.

The receipt must preserve the failed original executor provenance
(`36702494195`, job `109844958600`, run #2 / attempt 1, failure), prove that
failed run never dispatched the historical result, and bind the historical target
to discovery run #2 / attempt 1 on the exact same head SHA as the recovery run.

All rerun/retry/replacement, reserved-data, Phase 8B, demo/live, real-money, and
trading fields must remain false.

## DEC-438

DEC-438 deterministically freezes a valid DEC-437 review and emits one canonical
SHA-256 fingerprint.

The freeze preserves:

- exact recovery run/job/artifact identities;
- raw/canonical receipt hashes;
- DEC-436 recovery authorization identity;
- failed original executor provenance;
- historical result run #2 / attempt 1 identity;
- exact recovery/discovery head SHA equality;
- all broad authority locks.

## Authority boundary

DEC-437 and DEC-438 add no workflow dispatch surface and do not wait for or evaluate
the historical discovery result itself.

## Next gate

After a real successful DEC-436 recovery run, bind its concrete run/job/artifact
evidence to DEC-437/438 while discovery run #2 completes.
