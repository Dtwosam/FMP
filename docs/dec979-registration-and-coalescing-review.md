# DEC-979 — Native watch-registration and event-count review handoff

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict documentation-only, one-commit child of DEC-978/#1199. **639 distinct source-defined test methods**; no executable observer, test assertion, CI configuration, protected asset or production code changes.

## Reviewer matrix: a kernel watch can be present without the claimed meaning

| Draft | Native kernel control | What the control establishes | What it does not establish |
| --- | --- | --- | --- |
| DEC-972/#1193 | `IN_MASK_CREATE` on already watched source and parent yields native `-1/EEXIST` | The first registrations survive; source and parent event masks remain usable | Continuous integrity of every watch or no-write protection |
| DEC-973/#1194 | Ordinary and `IN_EXCL_UNLINK` independent parent watches compare writes to a still-open, already unlinked child | Both saw creation and deletion; the filtered instance can later have an empty queue while ordinary parent reports writes/close | No child writes after unlink or a complete namespace audit from the filtered queue |
| DEC-974/#1195 | Native `IN_DONT_FOLLOW` changes a symlink-path watch from the target to the symlink inode itself | A target write can be invisible to the symlink WD; unlinking the link invalidates it but not the followed target watch | That matching path spelling means matching watched inode |
| DEC-976/#1197 | `IN_ONLYDIR | IN_DONT_FOLLOW` applied to a regular file or directory-pointing symlink fails native `-1/ENOTDIR` | These invalid subscriptions are refused; already established source and parent WDs still detect file writes | Existing registration continuity outside the observed interval |
| DEC-977/#1198 | On a fresh independent inotify FD `IN_MASK_CREATE` succeeds once then yields native `-1/EEXIST` for the same source inode | A source-only registration was created and still sees subsequent real writes | Retrospective visibility before creation, or full parent census when only a source watch exists |
| DEC-978/#1199 | Two distinct unbuffered write syscalls to the same public inode precede one drain of source-only `IN_MODIFY | IN_CLOSE_WRITE` | The kernel merges successive identical unread `IN_MODIFY` events, so one modification record can represent multiple writes | Exact write-call count or continuous attested history from an inotify event count |

All controls are Linux-native, using only newly generated public files under a disposable private `/tmp` directory, genuine inotify calls and kernel event buffers, bounded inode/parent/inventory checks, and explicit FD cleanup. The ordinary source/parent observer is never elevated into an independent trusted kernel guard. Conflating subscription rejection, event filtering, symlink-follow semantics, watch availability and event coalescing would create unsound security conclusions. These checks never attest to every write or to continuous registration.

## Non-authorization and CI are separate gates

The unchanged evaluator must remain nonauthorizing on observed native writes and incomplete watch evidence. Only `BLOCKED` or `LOCAL_DISPOSABLE_WITNESS_UNVERIFIED` are possible local statuses, with `can_authorize_dispatch=false` and `independent_os_proof_verified=false` exactly.

Every draft head, including this documentation-only child, requires its **own exact-commit Phase 3 acceptance and full historical regression**; Phase 3 success never substitutes for historical success, and passing downstream checks never makes an earlier failure green. Qualified independent security review is also separate. This handoff is not a live claim that any pending CI has passed.

DEC-650/#820 independently OS-enforced protected no-write and DEC-651/#821/#779 immutable exclusive annual run385 admission remain **BLOCKED**. No protected evidence or sources, annual dispatch/test/retry/rerun, production refs/workflows/runners/rulesets/permissions, broker/trading action, merge, promotion or authorization.