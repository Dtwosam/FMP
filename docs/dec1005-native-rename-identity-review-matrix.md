# DEC-1005 — Native rename identity and failure-mode review matrix

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit documentation-only child of DEC-1004/#1225. The draft stack retains **656 distinct source-defined test methods**. No observer runtime, executable test, protected evidence/source, CI workflows, production refs/runners/rulesets/permissions, broker or trading changes.

## Native syscall and watch-identity comparison

| Draft | Real Linux operation on freshly generated public /tmp paths | Kernel result that the regression checks | Guard conclusion |
| --- | --- | --- | --- |
| DEC-997/#1218 | Rename a watched symlink to a different basename, then recreate a distinct symlink at the original pathname | Original link inode and its WD survive the move; new same-name link has a different inode and WD; later unlink invalidates the correct watch | A pathname is not a continuous watch identity |
| DEC-998/#1219 | `renameat2(RENAME_EXCHANGE)` between two symlinks pointing at the same target | Two paired nonzero rename cookies, source-link `IN_MOVE_SELF`, distinct original link WDs surviving the pathname exchange | Atomic exchange does not swap what inode each watch is bound to |
| DEC-999/#1220 | Exchange aliases pointing to two **different** regular-file target inodes | Actual writes through exchanged alias names follow the NEW resolved targets; source/other WDs and parent names identify those targets | User-level symlink spelling does not determine kernel write-event basename |
| DEC-1001/#1222 | `RENAME_NOREPLACE` of one watched symlink over a different **existing** watched symlink | `-1/EEXIST`, no emitted rename event, no changed inode or subscription; after destination unlink, same call succeeds with paired move records and source-link `IN_MOVE_SELF` | A refused namespace operation is not a committed move or independently enforced file-write prevention |
| DEC-1002/#1223 | Two hardlink names refer to the **same regular-file inode**; try NOREPLACE and normal rename between them | NOREPLACE returns `-1/EEXIST` without events; normal rename returns success as a **no-op** without events; both directory entries and inode link count persist | A successful rename syscall does not always imply a move or a new event |
| DEC-1003/#1224 | `RENAME_EXCHANGE` of two real directories with independent self-watch WDs | Parent reports two matched `IN_MOVED_FROM | IN_ISDIR` / `IN_MOVED_TO | IN_ISDIR` pairs; both directory WDs see `IN_MOVE_SELF`; unlink of each swapped directory emits `IN_DELETE | IN_ISDIR` and appropriate inode-watch invalidation | `IN_ISDIR` is native event type evidence and cannot be ignored, fabricated or confused with a regular-file move |
| DEC-1004/#1225 | Supply DEC-1001's **complete actual successful rename kernel buffer** to the unchanged two-WD parser/evaluator | Native parent move records plus the additional symlink-inode WD's `IN_MOVE_SELF` must fail closed: `well_formed=false`, `status=BLOCKED` | Filtering unknown kernel WDs to manufacture a clean observation is forbidden |

These tests only touch newly generated disposable public Linux objects, exercise genuine OS calls, parse actual kernel events, check final regular-file bytes and source/parent dev/inode/mode and bounded inventory, and close all native FDs. None is a trusted independent OS write-confinement mechanism, complete provenance record, or exclusive annual-run admission. A locally quiet queue, a returned success code, or even a known WD is insufficient for authorization. Actual write or unknown-watch evidence must keep the unchanged evaluator fail-closed, with `can_authorize_dispatch=false` and `independent_os_proof_verified=false`.

## Historical CI gates and security boundaries

- DEC-1000/#1221 at `da5a7d1ed8e416e6c8f4360522f995e2439e0945` passed **both** required exact-head CI suites.
- DEC-1001/#1222, DEC-1002/#1223, DEC-1003/#1224, DEC-1004/#1225 and this doc-only child must each pass **their own** exact-head Phase 3 acceptance **and** complete historical regression. Phase 3 success alone is not a historical pass. This matrix does not claim pending jobs have finished.
- Exact original commits #1201–#1205 and #1212 failed full historical regression; later children with passing suites did not and cannot rewrite those red SHA results. Qualified independent security review is separate from CI.

Independent protected OS-enforced no-write DEC-650/#820 and immutable exclusive annual run385 admission DEC-651/#821/#779 remain **BLOCKED**. No protected annual sources or evidence, annual run385 execution/test/dispatch/retry/rerun, production workflow/ref/runners/rulesets/permissions change, broker/trading operation, merge, promotion or authorization.