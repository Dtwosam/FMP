# DEC-1026 — Native inotify FD aliasing, lifetime and mask-mutation reviewer handoff

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict documentation-only one-commit child of DEC-1025/#1246. Source-defined test count remains **671**. No test/runtime code, CI workflow, protected source/evidence, production ref, runner, ruleset, permission, broker or trading change.

## Distinguish native inotify instances from numeric file descriptors

| Control | Real generated-public Linux setup | Native observation | Trust boundary |
| --- | --- | --- | --- |
| DEC-1018/#1239 | `dup(original_inotify_fd)` while original remains open | Duplicate and original share source+parent subscriptions, kernel queue and `IN_IGNORED` invalidations | Distinct FD numbers alone are not independent evidence |
| DEC-1020/#1241 | Two independent native `inotify_init1` instances, source then parent watch registration order | Both may hold the same numeric source WD and parent WD but have entirely separate event queues | Bare WD number is meaningful only within its owning instance |
| DEC-1021/#1242 | Reverse watch registration order on second genuine independent instance | Original source WD's numeric value refers to **parent WD** on second FD; removing via second FD invalidates that second parent only | Reusing another instance's WD integer can remove a different watched inode role |
| DEC-1022/#1243 | Two independent FDs exist, then `dup2(primary_fd, second_fd)` | The second kernel instance is closed and its former numeric FD becomes an alias of the first, collapsing two event queues into one | An unchanged numeric FD does not guarantee an unchanged kernel observer |
| DEC-1024/#1245 | `dup(original_fd)`, then close the **original** numeric FD | The surviving alias preserves original source+parent WDs, still sees real writes, and can remove source watch with native `IN_IGNORED` | Closing a numeric FD does not prove the underlying inotify instance has disappeared |
| DEC-1025/#1246 | Add `IN_MASK_ADD | IN_OPEN` to original source WD **through the dup alias** | Original FD's queue now includes real `IN_OPEN` on source as well as source/parent write events; a separate independent FD's mask remains unchanged. Closing alias does not restore old original mask | A duplicate can mutate its shared instance's registrations; unexpected native records must fail closed |

Every row is a real Linux inotify behavior test on newly generated public disposable `/tmp` paths, never protected annual material. The tests parse actual kernel event buffers, verify source and parent final device/inode/mode, restore public bytes, check bounded directory inventory, and close native descriptors. Local public kernel probes independently confirmed the new duplicate-close and additive-mask semantics before the draft tests were authored.

A complete observation identity needs the owning kernel inotify instance, local WD and verified watched inode. Neither a numeric FD value, a numeric WD, an empty queue, a surviving duplicate, nor a later rewatch constitutes independently OS-enforced no-write policy, an immutable trusted history or annual authorization. Real unsafe writes, missing subscriptions and unknown source event masks must keep the unchanged evaluator **`BLOCKED`**, with `can_authorize_dispatch=false` and `independent_os_proof_verified=false` exactly.

## Exact-head CI and protected-operation ledger

- The last individually fully verified draft before this new series was DEC-1020/#1241, exact SHA `cb9c01dd46bd0d719620622fa00ef89e14c9138e`.
- DEC-1021/#1242, DEC-1022/#1243, DEC-1023/#1244, DEC-1024/#1245, DEC-1025/#1246 and this documentation-only child **each require their own completed successful Phase 3 and full historical CI**. This document is not a live CI pass certificate.
- The original exact SHA for DEC-1016/#1237 `658feef31f5a961366ff3fc8f0cc5157b704a094` passed Phase 3 and **FAILED full historical** (run `38420457581`). Its failed job archive was unavailable (404/BlobNotFound) when checked; there is not enough evidence to assign the cause. The earlier #1201–#1205 and #1212 historical failures also remain failed. No later green descendant rewrites red predecessor SHA results.
- Qualified independent security review is separate from CI. All green drafts remain **DRAFT / NEVER MERGE / NEVER PROMOTE**.

Protected independently OS-enforced no-write DEC-650/#820 and immutable exclusive annual run385 admission DEC-651/#821/#779 remain **BLOCKED**. Do not access protected sources/evidence, execute/test/retry/rerun/dispatch annual run385, alter production refs/workflows/runners/rulesets/permissions, operate broker/trading, merge, promote or authorize.
