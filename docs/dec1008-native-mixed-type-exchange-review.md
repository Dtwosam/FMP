# DEC-1008 — Mixed-type atomic exchange and transient-write review handoff

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit documentation-only child of DEC-1007/#1228. Source-defined test methods remain **658**. No executable observer, unit test, CI workflow, production ref, protected source/evidence, runner, ruleset, permission, broker or trading changes.

## Kernel evidence: inode type, pathname and active watch are distinct

| Draft | Public native Linux experiment | Meaningful verified property | Forbidden security inference |
| --- | --- | --- | --- |
| DEC-998/#1219 | `renameat2(RENAME_EXCHANGE)` swaps two symlinks targeting the same sample | Symlink link-inode WDs remain attached through the pathname exchange, and parent move records form two cookie pairs | A symlink pathname is permanently bound to one watched inode |
| DEC-999/#1220 | Atomic exchange of symlinks targeting two different regular files, followed by writes | Writes resolve to each swapped alias's new target: inotify regular-file WDs and named parent records identify the actual target inode | The user-entered alias basename must appear in the parent's resolved-target write event |
| DEC-1003/#1224 | Atomic exchange of two watched directories | Parent emits `IN_MOVED_FROM | IN_ISDIR` and `IN_MOVED_TO | IN_ISDIR` paired cookies; both native directory WDs emit `IN_MOVE_SELF` | Dropping or conflating `IN_ISDIR` is a valid way to simplify directory-move evidence |
| DEC-1006/#1227 | Atomic exchange and exchange-back between a **regular file** and a **directory**, both watched | The pathname `sample` temporarily identifies a directory and `public-other-dir` temporarily identifies the original source-file inode; two typed rename-cookie pairs and each WD's self-move are observed per exchange | Watched-source pathname spelling is a durable proxy for watched-file inode type |
| DEC-1007/#1228 | A **real source write while pathnames are still inverted** after file-directory exchange | Original source inode WD emits `IN_MODIFY` even under the temporarily directory-named pathname `public-other-dir`; parent names that new entry instead of `sample` | Restoring original bytes, inode/path layout and final inventory erases the transient write or retroactively establishes no-write |

The native controls use only newly generated public, disposable `/tmp` paths; real Linux `renameat2`, inotify registrations and kernel event buffers; explicit matching inode identities, source and parent stat information, bounded inventories, restored public bytes and native FD cleanup. The real kernel actions were reproduced in independent disposable probes. The unchanged evaluator must fail closed for real write events and unexpected watch identities: `status=BLOCKED`, `can_authorize_dispatch=false`, `independent_os_proof_verified=false`.

## Strict draft CI and non-authorization gates

DEC-1005/#1226 at exact commit `c0eb411a56b7c2d3d2fc04892263f66a1548bb85` passed both Phase 3 and full historical regression. DEC-1006/#1227, DEC-1007/#1228 and this documentation-only child each require **their own** exact-head Phase 3 and complete historical regression. Neither native test nor this handoff is a trusted OS-enforced protected no-write policy or an annual dispatch approval. Qualified independent security review is still a separate gating requirement.

Previous original exact heads #1201–#1205 and #1212 have **failed** historical results preserved, regardless of later green descendant results. Every success or failure must be attributed only to the SHA actually tested.

Independent OS-enforced protected no-write DEC-650/#820 and immutable exclusive annual run385 admission DEC-651/#821/#779 remain **BLOCKED**. No protected sources/evidence access, annual run385 execution/test/retry/rerun/dispatch, production workflows/refs/runners/rulesets/permissions changes, broker/trading operations, merges, promotions or authorization.