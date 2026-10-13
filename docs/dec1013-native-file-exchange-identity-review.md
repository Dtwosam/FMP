# DEC-1013 — Equal bytes, hardlink aliasing and atomic regular-file exchange review

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict documentation-only one-commit child of DEC-1012/#1233. Source-defined test methods remain **662**; no executable test, observer runtime, workflow, production ref, protected source/evidence, runner, ruleset, permissions or trading code changes.

## Real native Linux observations and non-equivalent identity cases

| Draft | Generated-public inode identity | Native rename and event outcome | Implication for independent review |
| --- | --- | --- | --- |
| DEC-1002/#1223 | Two different hardlink pathnames to **one inode** | `RENAME_NOREPLACE` to occupied name returns `EEXIST` with no events; ordinary rename between same-inode entries succeeds as no-op with no events | A successful syscall does not always mean a directory entry or inode moved |
| DEC-1010/#1231 | Two names of **one regular-file inode**, link count two | Native `renameat2(RENAME_EXCHANGE)` succeeds but the inotify queue is empty; both names, inode identity and link count survive unchanged | Exchange is not always evidence of two moves, and a quiet queue does not prove later writes are impossible |
| DEC-1011/#1232 | Two names pointing to **different regular-file inodes** | Actual `RENAME_EXCHANGE` emits two paired nonzero rename cookies and `IN_MOVE_SELF` for both inode WDs. During swapped interval, writes through path `sample` reach the other file WD, and writes through path `public-other` reach the original source WD | Pathname identity and the original watched-source inode must be checked independently; unfamiliar additional WDs must fail closed |
| DEC-1012/#1233 | Two **different** regular-file inodes holding **exactly equal public bytes** | Native exchange emits paired rename records and both inode `IN_MOVE_SELF` events, but no `IN_MODIFY` or `IN_CLOSE_WRITE`; `sample.read_bytes()` and inventory appear unchanged while the pathname points at another inode until swapped back | Byte equality and unchanged final name inventory are not evidence of continuous watched inode identity or uninterrupted write-prevention |
| DEC-1006/#1227 and DEC-1007/#1228 | Watched regular file and watched directory of opposite inode types | Mixed-type atomic exchange temporarily makes pathname `sample` a directory and writes to original source inode arrive under directory's former name, with `IN_ISDIR` on actual directory rename records | File-kind and path identity also must not be conflated with inode-bound WD identity |

All controls use real native Linux syscalls and inotify event buffers on newly generated public files in disposable `/tmp` directories. They check original/final bytes, source+parent dev/inode/mode, directory inventories, exact native event identities, and FD closure. A no-move queue, a source-only quiet interval, an unchanged byte snapshot, or matching final stat values must never be treated as a trusted full-history or independently OS-enforced no-write attestation.

The observer evaluator remains nonauthorizing on the actual native unsafe streams, requiring `status=BLOCKED`, `can_authorize_dispatch=false` and `independent_os_proof_verified=false` exactly. This document is a reviewer aid, not a security approval or a CI-completion certificate.

## CI lineage and protected controls

DEC-1009/#1230 at exact SHA `20319e9fa1c532891a8ac9e132d7bac6ba189b2f` passed both required CI suites. DEC-1010/#1231, DEC-1011/#1232, DEC-1012/#1233 and this documentation-only child each require **their own exact-head Phase 3 and full historical regression** before being called fully verified. Phase 3 alone does not meet the historical gate. Qualified independent security review remains separately required. Earlier failed historical exact commits #1201–#1205 and #1212 remain FAILED, even though later descendants passed.

Independent protected OS-enforced no-write DEC-650/#820 and immutable exclusive annual run385 admission DEC-651/#821/#779 remain **BLOCKED**. No protected annual source/evidence, execution/test/retry/rerun/dispatch, production workflows/refs/runners/rulesets/permissions, broker/trading action, merge, promotion or authorization.