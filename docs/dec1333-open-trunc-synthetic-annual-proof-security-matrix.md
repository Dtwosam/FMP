# DEC-1333 — Native open-time data-destruction evidence and synthetic annual proof fail-closed ledger

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit documentation-only child of #1556 DEC-1332 at `781176c9a08a7d990d235f5b137e4b664459d75c`, **903 source-defined methods unchanged**. This document neither executes nor authorizes protected annual files, workflows, evidence, broker/trading, merges or production changes.

## Native Linux test cases — original generated PUBLIC anonymous inodes only

| Draft | Exact executable claim | Positive/negative true source evidence |
| --- | --- | --- |
| #1547 DEC-1323 | F_SEAL_WRITE alone rejects actual in-range pwrite EPERM but **O_RDONLY|O_TRUNC succeeds** | Original anon inode loses all data at open, size0 and true native IN_MODIFY, no source-name parent |
| #1548 DEC-1324 | F_SEAL_FUTURE_WRITE denies new pwrite and writable mmap but **O_RDONLY|O_TRUNC succeeds** | Original anon inode loses all bytes at open, IN_MODIFY positive, same FUTURE_WRITE bitset |
| #1549 DEC-1325 | F_SEAL_GROW|SHRINK; each O_RDONLY/O_WRONLY/O_RDWR mode with O_TRUNC | Genuine EPERM, content/size/identity intact and IN_MODIFY quiet |
| #1550 DEC-1326 | F_SEAL_WRITE|GROW|SHRINK|SEAL; all three open O_TRUNC modes, direct write and new writable mmap | All tested mutations EPERM, native inotify quiet; actual original content, size and seal bitset unchanged |
| #1551 DEC-1327 | O_PATH|O_TRUNC and O_PATH|O_WRONLY|O_TRUNC compared to real O_RDONLY|O_TRUNC | O_PATH opens **succeed but O_TRUNC is ignored** and pread(O_PATH) EBADF; true O_RDONLY|O_TRUNC destroys weakly sealed data, while full-sealed data rejects |
| #1552 DEC-1328 | F_SEAL_GROW alone, WRITE|GROW, SHRINK alone, WRITE|SHRINK, FUTURE_WRITE|SHRINK | **F_SEAL_SHRINK** is decisive: its absence allows real destructive O_RDONLY|O_TRUNC with original IN_MODIFY; its presence causes EPERM and unchanged actual original bytes |
| #1553 DEC-1329 | Docs-only source/seal/descriptor operation matrix | No test behavior changed; each original SHA requires full exact-head CI |

These cases are **disposable PUBLIC anonymous memory files** via `memfd_create`, with inode-only Linux native watchers. They do not access the real protected annual filesystem inode. No named original-parent watch exists for anonymous memfd; do not misstate its events as regular named-source+parent receipts. A successful native open with `O_PATH` is not evidence of actual truncation; a real `O_RDONLY|O_TRUNC` can be destructive despite nominal read-only access. Presence or absence of MODIFY is diagnostic, not independently enforced OS no-write.

## Source-only review assessment — never an authority source

| Draft | New source-only behavior | Always forbidden |
| --- | --- | --- |
| #1554 DEC-1330 | Pure `assess_synthetic_claims` with 12 `unittest` methods; caller-supplied quiet inotify, PUBLIC memfd seals/tmp fixtures, self-signed SHA, claimed independent admin locks, attempt2 or ambiguous/retry outcome are rejected as protected proof | All synthetic packets return **BLOCKED**, no dispatch/evidence/trading/merge authority; no real protected sources or external IO |
| #1555 DEC-1331 | +3 tests: missing/invalid, equal self-asserted, and mismatched synthetic SHA claims classified separately | Even exact equal strings cannot authenticate immutable ref/SHA or authorize |
| #1556 DEC-1332 | +3 tests: bool, float and exact integer annual run/attempt identities distinguished despite Python equality behavior | Correct `385` and `1` integers are **still nonauthorizing** absent authenticated independent witnesses |

The new synthetic classifier is not a protected execution controller, is **never invoked by the annual runtime**, cannot authenticate external proof or run inventory and deliberately has **no positive authorization branch**. It is strictly a reproducible negative test of review claims. This augments the separately required real Gate A / Gate B acceptance contract in `docs/dec1320-independent-protected-no-write-and-annual-admission-acceptance-contract.md`; it does not discharge either gate.

## Exact-head CI and disposition

At entry into this batch, the last fully verified strict canonical draft was **#1546 DEC-1322 with 879 source-defined methods**, exact Phase3 and full historical suites successful. New #1547–#1556 require **individual completed successful Phase3 AND full historical tests**, this docs-only #1557 as well; incomplete is **PENDING**, failure stays **FAILED** at the original SHA. Earlier failed original heads and closed superseded parallel siblings are immutable history; no retroactive green, merge or production promotion. Qualified independent security review remains separate from CI.

Protected independently OS-enforced no-write **DEC-650/#820** and immutable exclusive annual run385 admission **DEC-651/#821/#779** remain **BLOCKED**. No protected annual source/evidence handling, annual run/test/retry/rerun/dispatch, installed production refs/workflows/rulesets/permissions, broker/trading, merges or promotions.
