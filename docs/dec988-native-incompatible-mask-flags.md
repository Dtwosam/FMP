# DEC-988 — Native IN_MASK_ADD and IN_MASK_CREATE are mutually exclusive

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit test/documentation child of DEC-987/#1208.

On a genuine Linux inotify FD with both source and parent subscriptions already registered, calling native `inotify_add_watch` with **both** registration-only options `IN_MASK_ADD | IN_MASK_CREATE` must return `-1/EINVAL` for either the public source or its containing directory. Both bits control registration semantics and are never accepted event-record action masks.

The new generated-public regression checks actual native `EINVAL` and unchanged event queue, then exercises real sibling creation/deletion and a distinct-byte source write followed by restoration. The original parent still reports named `IN_CREATE`, `IN_DELETE` and source `IN_MODIFY`; the original source WD still reports content writes. The unchanged evaluator remains `BLOCKED`, with exact `can_authorize_dispatch=false` and `independent_os_proof_verified=false`. Public sample/parent device, inode, mode and one-name bounded inventory match, and the native FD is explicitly closed.

This is **one additional Linux source-defined method**, for **645 total** on the stack. It neither alters observer runtime nor proves no-write OS enforcement or uninterrupted watch history. Historical runs for the exact heads #1201–#1205 remain recorded **failed**, owing to the separate inherited DEC-980 alias-unlink assertion; DEC-985/#1206 is the dedicated repair and must itself pass both required suites. DEC-988 likewise requires its own Phase 3 and full historical CI and qualified independent security review.

Protected OS-enforced no-write DEC-650/#820 and exclusive immutable annual run385 admission DEC-651/#821/#779 remain **BLOCKED**. No protected source/evidence access, annual test/dispatch/retry/rerun, production refs/workflows/runners/rulesets/permissions changes, broker/trading, merge or promotion.