# DEC-1029 — Native descriptor flags, aliases and instance provenance review

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict documentation-only child of DEC-1028/#1249. The source-defined test count stays **673**. No observer runtime, executable test, CI workflow, protected source/evidence, production ref, runner, ruleset, permission, broker or trading change.

## Descriptor-level and instance-level evidence are different

| Control | Real disposable-public Linux action | Kernel boundary proved | Forbidden inference |
| --- | --- | --- | --- |
| DEC-1018/#1239 | `os.dup(inotify_fd)` | Original and alias share the original inotify queue and subscriptions, even with different FD integers | Different FD numbers imply independent write-history evidence |
| DEC-1022/#1243 | `os.dup2(primary_fd, second_fd)` when second FD initially owns another independent inotify instance | Previous second instance is closed and its preserved numeric FD becomes an alias of the first, sharing the first instance's queue | Stable numeric FD identity implies stable watcher independence |
| DEC-1024/#1245 | Close original numeric FD while `dup` stays alive | The duplicate still retains the same kernel inotify instance and original source/parent WDs | Closing the original number necessarily destroys its actual watched subscriptions |
| DEC-1025/#1246 | Call `inotify_add_watch(dup_fd, sample, IN_MASK_ADD | IN_OPEN)` | The watch mask changes on the original **shared instance**, producing native unexpected source `IN_OPEN`; independent second instance's mask does not change | An alias is incapable of mutating another FD's observed event stream |
| DEC-1027/#1248 | `fcntl(F_SETFL)` on duplicate, and `fcntl(F_SETFD)` separately | `O_NONBLOCK` is a **shared open-file-description** status flag; `FD_CLOEXEC` is an **individual descriptor** flag. Independent instance keeps its own status | All flags share the same aliasing scope, or different close-on-exec flags imply independent queues |
| DEC-1028/#1249 | `fcntl(F_DUPFD)` and `fcntl(F_DUPFD_CLOEXEC)` on original | Both new descriptors share native source+parent watches and queue, but the new `F_DUPFD` alias initially lacks `FD_CLOEXEC` while the `F_DUPFD_CLOEXEC` alias has it | Close-on-exec policy decides kernel watch ownership or guarantees protected file-write prevention |
| DEC-1020/#1241 and DEC-1021/#1242 | Two independent native inotify instances with matching or reversed watch registration | Numeric WD values may match across instances even while mapping to different source/parent roles | Bare WD integer gives global identity of watched inode |

Every test operates on new public disposable `/tmp` source/parent data and actual native inotify syscalls or `fcntl` descriptor flags. For the brief status-flag check, DEC-1027 restores `O_NONBLOCK` inside `finally` **before any queue read**. DEC-1028 verifies `F_DUPFD`'s initial non-CLOEXEC bit and immediately restores `FD_CLOEXEC`, without running or spawning any process. Every event-stream assertion remains read-only observation of generated public fixture activity. Native source/parent device, inode, mode, original bytes, bounded inventory and FD closure remain independently checked.

No duplicated numeric FD, per-descriptor CLOEXEC flag, shared open-file-description nonblocking bit, native `IN_IGNORED` receipt, or queue silence is independently OS-enforced protected no-write or complete write provenance. The unchanged observer's evaluator must stay **`BLOCKED`**, with `can_authorize_dispatch=false` and `independent_os_proof_verified=false` exactly, for the observed native write and invalidation cases.

## Exact-head CI gate, not a retroactive approval

DEC-1026/#1247 at exact SHA `60fbd8fbaf2b98f360ac4c6a58019cef97b79794` passed both required Phase 3 and complete historical CI suites. DEC-1027/#1248, DEC-1028/#1249 and this documentation-only child each need **their own successful exact-head Phase 3 and full historical regression**. The source-defined count is **673**, independent of the doc-only child. Passing descendants do not change earlier failed SHAs. In particular, the original DEC-1016/#1237 exact SHA `658feef31f5a961366ff3fc8f0cc5157b704a094` failed historical run `38420457581`; its unavailable log archive was not sufficient to establish a failure cause. Original historical failures #1201–#1205 and #1212 also remain failed. Qualified independent security review is a distinct gate even after CI.

Independent protected OS-enforced no-write DEC-650/#820 and immutable exclusive annual run385 admission DEC-651/#821/#779 remain **BLOCKED**. Do not access protected source/evidence, execute/test/dispatch/retry/rerun run385, change production refs/workflows/runners/rulesets/permissions, operate brokers or trading, merge, promote or authorize this stack.
