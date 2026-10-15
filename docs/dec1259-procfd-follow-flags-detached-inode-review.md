# DEC-1259 — Native procfs FD access-mode, follow-policy and inode-retirement review

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit documentation-only child of #1479 DEC-1258 at `981df4313dfeac9b2ec292e7cdb9b39767183f6d`; **838 source-defined test methods unchanged**. These are actual Linux-native observations on generated disposable **PUBLIC /tmp files**, not proof of independent OS-enforced protected no-write and never authorization to execute an annual run.

## Actual native cases and meanings

| PR / DEC | Linux descriptor and namespace condition | Observed native source and original-parent event transition | Crucial security distinction |
| --- | --- | --- | --- |
| #1470 DEC-1249 | Original **O_RDONLY** holder after deleting last pathname; procfs **O_RDWR** reopen | Source ATTRIB+parent DELETE at unlink, then source+named parent MODIFY(sample) on real zero range; original holder's final close source DELETE_SELF/IGNORED | A read-only holder can still permit writable independent procfs reopen under Linux permissions |
| #1472 DEC-1251 | Original **O_PATH** holder after unlink; original ftruncate EBADF; procfs O_RDWR reopen | Rejected original O_PATH operation event quiet; procfs new writable description emits actual source+named-parent MODIFY | Path-only descriptor's access mode does not constrain a different file description |
| #1473 DEC-1252 | O_PATH holder; procfs O_RDONLY reopen fails four libc fallocate modes EBADF; separate O_RDWR reopen succeeds | No native MODIFY while readonly call rejects; first actual writable fallocate consumes isolated unsafe ONESHOT and both source+parent MODIFY visible | Rejected readonly operation is not proof that other reopen modes are blocked |
| #1474 DEC-1253 | O_PATH holder; procfs **O_RDWR|O_TRUNC** reopen | **Open-time** source+named parent MODIFY(sample) destroys bytes, then two further real ZERO_RANGE MODIFY receipts | An open syscall can mutate before any later write or fallocate |
| #1475 DEC-1254 | O_PATH holder; procfs **O_RDWR|O_APPEND** reopen, fixed ZERO_RANGE then pwrite(offset0) | First source+parent MODIFY zeroes prefix, next source+parent MODIFY appends X to EOF | O_APPEND controls Linux pwrite placement, not explicit fallocate fixed offset |
| #1476 DEC-1255 | O_PATH holder; procfs **O_RDONLY|O_TRUNC** reopen then four fallocate EBADF rejections and another O_RDWR reopen | Destructive open-time MODIFY, rejected operations event-quiet, later writable ZERO_RANGE positive MODIFY | Readonly and CLOSE_NOWRITE after the fact do not prove non-destructive open |
| #1477 DEC-1256 | Original O_PATH holder **closes before** procfs-opened O_RDWR writer | O_PATH holder close quiet; surviving procfs writer still emits source+parent MODIFY; final **writer close** CLOSE_WRITE then DELETE_SELF/IGNORED | Original holder close does not retire inode while another independent description is open |
| #1478 DEC-1257 | Documentation-only event/access provenance matrix | No executable changes | Separates current inode identity from original pathname and watch lifecycle |
| #1479 DEC-1258 | O_PATH holder; procfs **O_RDONLY|O_NOFOLLOW** and **O_RDWR|O_NOFOLLOW** data opens | Both reject ELOOP, no native source/parent MODIFY; **O_PATH|O_NOFOLLOW** instead opens **S_IFLNK magic-link inode**, not detached regular file | Follow-policy and O_PATH alter which inode is opened, not universal no-write proof |
| #1479 DEC-1258 continued | Same original O_PATH holder; later procfs O_RDWR **without O_NOFOLLOW** | Two successful real ZERO_RANGE source+named-parent MODIFY(sample); original unsafe ONESHOT expires on first; actual continuing helper sees both | Absence of O_NOFOLLOW guard can still admit independent writable reopening |

## Review-critical invariants

- Real source/parent watch IDs originate in native kernel `inotify_add_watch` on generated disposable PUBLIC source inode and original parent. Unlink of original last pathname causes source **IN_ATTRIB** and named parent **IN_DELETE(sample)**; `st_nlink=0` and the original directory inventory is empty. This **does not imply inode retirement**, because O_PATH/O_RDONLY/O_RDWR file descriptions may still reference it.
- Linux can report native original source **IN_MODIFY** and named original-parent **IN_MODIFY(sample)** for a formerly linked dentry operated through a surviving or procfs-reopened FD, even when `sample` no longer exists in directory inventory.
- Every executable draft uses an isolated **deliberately unsafe test-only source IN_ONESHOT** expiring on first genuine MODIFY→IGNORED; unchanged actual continuous `scripts/dec677_disposable_inotify_events.py::_start_watch` remains the source+original-parent witness for later operations, with native raw event buffers and accurate generated PUBLIC source byte states passed to unchanged `_evaluate`.
- All unchanged evaluator verdicts stay **status=BLOCKED, can_authorize_dispatch=false, independent_os_proof_verified=false**. When the **last** live description is released, source **IN_DELETE_SELF and IN_IGNORED** retire the original inode watch, regardless of which original holder or reopened description was closed last.
- `O_PATH|O_NOFOLLOW` on a procfs FD magic link can return a descriptor to the **link itself** (S_IFLNK) rather than the original regular-file inode. Contrasting `O_RDONLY/O_RDWR|O_NOFOLLOW` **ELOOP** and unguarded writable reopening demonstrates why exact flags and exact inode identities matter. A rejected operation is a bounded observation, never a general permission denial proof.

## Remaining mandatory gates

Each exact draft SHA requires separately completed successful **Phase 3 acceptance** and **full historical `tests` CI**. A green descendant does not retroactively change an earlier originally FAILED SHA; a Phase3-only green draft is **pending** full historical verification. Each also requires **qualified independent security review**; public disposable syscall tests do not implement nor verify independent protected no-write enforcement.

Protected **DEC-650/#820 independently OS-enforced no-write** and **DEC-651/#821/#779 immutable exclusive annual run385 admission** remain **BLOCKED**. No protected annual source/evidence access or edits, annual execution/test/retry/rerun/dispatch, installed watcher production changes, CI workflow/ruleset/permission changes, broker/trading, merges or promotions.
