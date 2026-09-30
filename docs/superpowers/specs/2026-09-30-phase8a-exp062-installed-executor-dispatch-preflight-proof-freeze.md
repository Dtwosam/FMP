# Phase 8A — EXP-062 Installed Executor Dispatch-Preflight Proof Freeze

**Date:** 2026-09-30  
**Status:** DETERMINISTIC PROOF FREEZE / DISPATCH STILL LOCKED  
**Decision:** DEC-428  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-427

DEC-428 deterministically freezes a valid DEC-427 review.

The frozen object preserves the DEC-426 run/job/artifact identities, artifact
digest, raw/canonical DEC-425 hashes, exact source map, installed executor state,
zero executor runs, unused historical-result slot, and target run #2 / attempt 1.

It emits one canonical `freeze_fingerprint_sha256` for later concrete runtime
binding.

DEC-428 does not authorize the one-shot executor run. Historical-result dispatch,
execute mode, rerun/retry/replacement, reserved-data access, Phase 8B, demo/live,
real-money, and trading remain false.

Next gate: concrete DEC-426 runtime-evidence binding before any dispatch
authorization.
