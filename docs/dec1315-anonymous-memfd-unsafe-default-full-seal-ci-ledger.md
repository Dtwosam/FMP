# DEC-1315 — Anonymous memfd write protection: corrected CI, COW, splice and unsafe defaults

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit documentation-only child of #1535 DEC-1314 at `519504498708d87f11f8835beb5ae452825b5a5c`, preserving **875 distinct source-defined tests unchanged**. All executable new evidence comes only from disposable generated PUBLIC anonymous Linux memfds and anonymous pipes; nothing installed on or read from protected annual sources or their evidence.

## Original exact-head CI history

- **#1525 DEC-1304**, **869 methods**, passed both Phase3 and full historical tests at its exact head and remains the latest fully verified contiguous draft until later exact-head historical suites complete.
- Original **#1526 DEC-1305** and **#1527 DEC-1306** historical tests FAILED when successful anonymous-memfd in-place pwrites were incorrectly expected to emit `IN_MODIFY`. The same two assertions caused inherited original historical failures at **#1528–#1530**. All those exact SHA conclusions remain **FAILED**.
- **#1531 DEC-1310**, exact original new SHA `97aa822ffd4af2fecdc4b7201989c71941e6d119`, repairs **only five positive in-place pwrite event assertions to strict empty native-event assertions**, while independently confirming actual original file bytes change via `pread` and retaining **two genuine positive IN_MODIFY on ftruncate shrink/regrow**. Four misleading earlier evidence documents were also corrected. Phase3 passed; exact-head full historical suite remains a separate required gate.
- None of the following new drafts may be classified fully verified on Phase3 alone. Each requires completed successful **Phase3 and full historical `tests`** at its own original SHA, plus independent qualified security review.

## Current capability matrix

| Draft | Native operation on generated PUBLIC anonymous inode | What is genuinely protected, allowed, or silent |
| --- | --- | --- |
| #1531 DEC-1310 | Fix pwrite native receipt interpretation | Anonymous memfd in-place pwrite changes actual original inode bytes with **no `IN_MODIFY`**, while resize by ftruncate generates real MODIFY |
| #1532 DEC-1311 | `F_SEAL_WRITE|GROW|SHRINK|SEAL`, create `mmap.ACCESS_COPY`, modify private mapped memory, then read original inode | Full seals deny actual original pwrite/writable shared mapping and size changes; **private COW bytes can still change** while actual original sealed inode stays byte-for-byte intact |
| #1533 DEC-1312 | Full seals; original memfd→anonymous pipe via `splice`, then pipe→original sealed memfd | Read direction **succeeds**, transferring exact original bytes without file mutation; reverse original-file **write direction rejects EPERM**, leaving original source and pending pipe bytes unchanged |
| #1534 DEC-1313 | Documentation-only corrected native event/source provenance review | No executable changes; preserves failing original SHA ledger and avoids attributing named source+parent watches to anonymous data |
| #1535 DEC-1314 | `memfd_create(MFD_CLOEXEC)` without `MFD_ALLOW_SEALING` | Kernel creates an anonymous inode with **F_SEAL_SEAL already set**; later adding WRITE seal is EPERM, yet in-place pwrite and destructive shrink/regrow remain allowed. In-place writes are **IN_MODIFY-quiet**, while actual size changes yield MODIFY |

## Review and safety interpretation

A strict write/size-sealed anonymous inode is not necessarily unreadable: a source→pipe copy is still permitted, and writable private COW memory can exist without changing original backing file data. Conversely a memfd may advertise an **irreversible seal set** while having no original-data write protections, especially when `MFD_ALLOW_SEALING` was omitted during creation. Neither a read denial on one handle, memory-only byte difference, inode-watch silence nor an irreversible seal bit proves comprehensive source integrity. Exact original backing `pread`, syscall return codes, seal bitset, size and independently decoded native receipts remain separate evidence.

The anonymous memfd watch is an **inode-only inotify watch through `/proc/self/fd/<memfd>`**, with no named original-parent directory at all. It is not equivalent to earlier generated named PUBLIC /tmp original source+parent observations, and none of these experiments applies a kernel seal to any existing protected annual file. No local test evidence can authorize annual execution or substitute for independently reviewed OS access-control confinement.

Protected independent OS-enforced no-write **DEC-650/#820** and immutable exclusive run385 annual admission **DEC-651/#821/#779** remain **BLOCKED**. No protected annual source/evidence access or change, annual run/test/retry/rerun/dispatch, installed source monitor/runtime, production refs/workflows/rulesets/permissions, broker/trading, merges or promotions.
