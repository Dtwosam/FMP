# DEC-1323 — write only seal readonly open trunc

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit child of prior draft at `59f8a8ede48b67e27067293b4fd524cc430c1257`, one new genuine Linux native generated PUBLIC anonymous memfd test and reviewer note, proposed **880 distinct source-defined tests**.

## Genuine disposable Linux operation and expected evidence

F_SEAL_WRITE rejects pwrite EPERM yet a genuinely opened O_RDONLY|O_TRUNC procfd destroys original anonymous source data with native IN_MODIFY and no writer-close event. The original source is an **anonymous** memfd populated with known generated PUBLIC bytes; it is independently watched by a native inode-only inotify descriptor through `/proc/self/fd/<fd>`. The precise `F_GET_SEALS` state and actual kernel errno or success are checked. The successful O_RDONLY|O_TRUNC read-only-description open emits actual original anonymous source IN_MODIFY; closing the read-only description is event-quiet. The original source loses all data and its size becomes zero. This is an intentionally destructive but strictly disposable counterexample, not a protected annual source. Closing the last original memfd holder retires its real inotify witness with IN_DELETE_SELF and IN_IGNORED; all FDs are closed.

## Required security interpretation

Actual `O_RDONLY|O_TRUNC` behavior on this Linux runtime makes it unsafe to infer immutable data from read-only *descriptor flags* alone: the `O_TRUNC` flag is a data-mutating open-time operation on an existing anonymous inode when no GROW/SHRINK seals prevent it. `F_SEAL_WRITE` and `F_SEAL_FUTURE_WRITE` limit direct in-range writes differently from length changes. Complete data/size protection is established **only for tested syscall paths on this distinct disposable anonymous memfd**; the test never touches or authorizes a protected annual filesystem inode.

Every original exact SHA requires independently **completed successful Phase3 and full historical `tests` suites**, plus qualified independent review. A pending or failed original exact SHA stays pending/failed even if a later descendant passes. Protected independently OS-enforced no-write **DEC-650/#820** and exclusive immutable run385 admission **DEC-651/#821/#779** remain **BLOCKED**. No protected annual source/evidence access, annual run/test/retry/rerun/dispatch, installed monitor/production workflow/ruleset/permission, broker/trading, mergers or promotions.
