# Phase 8A — EXP-062 One-Shot Executor Dispatch Authorization

**Date:** 2026-09-30  
**Status:** ONE-SHOT DISPATCH AUTHORIZED / RUN NOT STARTED  
**Decision:** DEC-430  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-429

DEC-430 records explicit operator authorization for exactly one invocation of the
installed EXP-062 historical executor.

It pins:

- DEC-429 runtime-freeze blob
  `98fbb04a78efeef0a9a1fc919b5e5d61093c09de`;
- DEC-429 runtime-freeze fingerprint
  `a561a4a66111c5c2edc3183e68a978b01ead42f9b8f8c8c061244b50fc751dac`;
- active executor workflow blob
  `51ce87584369be957482460d81649adb1cb9f05d`.

The authorization scope is exact:

- executor workflow run #1 / attempt 1;
- historical result run #2 / attempt 1;
- executor run count must still be zero before action;
- historical-result attempt count must still be zero before action.

DEC-430 sets one-shot executor dispatch authorization and historical-result dispatch
authorization true. It does not itself invoke the workflow.

General execute mode, rerun/retry/replacement, reserved-data access, candidate
compilation/promotion, Phase 8B, demo/live, real-money, and trading remain false.

## Next gate

A read-only current-main dispatch-action preflight must recheck repository identity
and both one-shot inventories before the executor may be triggered.
