# DEC-1000 — Atomic symlink exchange: watch-inode and resolved-target reviewer matrix

**DRAFT / NEVER MERGE / NEVER PROMOTE.** This is a strict documentation-only one-commit child of DEC-999/#1220. The strict draft test count remains **653 distinct source-defined methods**, with no executable test, observer runtime, CI/workflow, runner, production configuration, protected sources/evidence, or trading code changed.

## Compare native Linux exchange experiments

| Draft | What is exchanged | What the genuine kernel reports | What the unchanged observer must NOT infer |
| --- | --- | --- | --- |
| DEC-997/#1218 | Original link inode moved to another basename; fresh distinct link inode recreated at original name | Original symlink WD retains first inode through rename; new link WD differs despite same pathname | Watch/path spelling equality proves continuous inode identity |
| DEC-998/#1219 | Two distinct no-follow symlink INODEs pointing to the **same** regular-file target, exchanged using `renameat2(RENAME_EXCHANGE)` | Parent emits two pairs of `IN_MOVED_FROM`/`IN_MOVED_TO` with distinct nonzero matching cookies; each symlink WD emits `IN_MOVE_SELF`; neither invalidated by exchange; later unlink of each pathname invalidates its newly positioned inode's original WD | Atomic path exchange is loss of a watched inode, or unchanged pathname means unchanged link inode |
| DEC-999/#1220 | Two symlink pathnames pointing to **different** regular-file targets, exchanged atomically | Same parent rename-cookie-pair behavior; afterwards a write via first alias hits the **other** target WD and parent name `public-other`, while a write via second alias hits original sample WD and parent name `sample` | Inotify parent event names must match user-level symlink spelling, or the original source WD has observed a write to another target inode |

These controls use only generated disposable public `/tmp` paths; native registrations and kernel event buffers; distinct target or symlink inode identities; actual writes and restore; metadata and bounded final directory inventory checks; and explicit FD closure. The kernel checks were separately reproduced in disposable local Linux probes, but still do **not** establish independent protected no-write enforcement, authoritative write-call accounting, immutable provenance or annual admission. A third unexpected watch descriptor must fail closed in the original two-WD parser; real observed writes must produce `BLOCKED`, with exact `can_authorize_dispatch=false` and `independent_os_proof_verified=false`.

## Strict historical CI interpretation

- DEC-979/#1200 is the last **uninterrupted** green checkpoint before the red exact-head series.
- The exact original heads of #1201–#1205 failed historical regression despite passing Phase 3. The first repair #1206 and later descendants may be individually green, but cannot retroactively change those red SHA verdicts.
- The original DEC-991/#1212 exact head likewise failed historical CI on a symlink alias-versus-resolved-target event basename assertion. Its separate new repair DEC-992/#1213 passed both exact-head required suites.
- Every new exact head, including this doc-only child, requires **its own Phase 3 AND full historical CI** before being described as verified. Later passing descendants never heal failed earlier exact SHAs. This matrix is *not* a live CI status certificate; a qualified independent security review is still necessary.

Protected independently OS-enforced no-write DEC-650/#820 and immutable exclusive annual run385 admission DEC-651/#821/#779 remain **BLOCKED**. Do not access protected sources/evidence, run/test/retry/dispatch annual run385, alter production refs/workflows/runners/rulesets/permissions, operate brokers/trading, merge, promote or authorize this draft stack.