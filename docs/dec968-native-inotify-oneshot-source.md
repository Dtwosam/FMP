# DEC-968 — Native source inotify IN_ONESHOT auto-removal

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit child of DEC-967/#1188, test + documentation only.

This generated public Linux negative control tests a different registration-loss mechanism from explicit inotify_rm_watch (DEC-959–961) and mask replacement (DEC-965–966). On a real inotify FD, it replaces only the generated `sample` source subscription with `IN_MODIFY | IN_ONESHOT | IN_DONT_FOLLOW`, preserving its numeric watch descriptor and the separate live parent watch.

A real write of distinct public fixture bytes produces an actual source `IN_MODIFY` followed by `IN_IGNORED`: Linux automatically removes the source watch after its first matching event. The parent independently sees named sample modifications. A second real write restores the original bytes, with native records on the parent only and no source-watch records. Exact initial and final source/parent dev, inode and mode plus single-entry inventory match. The FD is always closed.

The first kernel stream is correctly invalidated and `BLOCKED` by the existing evaluator. Even after the ignored record is consumed, a true parent write event and identical restored final bytes must still be `BLOCKED`. Both `can_authorize_dispatch=false` and `independent_os_proof_verified=false` remain exact. This does not assert that unmodified run_demo uses `IN_ONESHOT`, and a reused numeric watch descriptor is not continuous-registration proof.

This adds one distinct Linux source-defined method, bringing the stack to **631**. It does not change observer runtime code, protected annual evidence, production workflow/runners/refs/rulesets/permissions, broker or trading operations. Own exact-head Phase 3/full historical CI plus qualified independent review are necessary; even green CI cannot establish OS-enforced protected no-write (DEC-650/#820) or immutable annual run385 admission (DEC-651/#821/#779). Both remain **BLOCKED**. Never merge, promote, dispatch, test or rerun the annual suite.
