# DEC-1329 — Linux open-time truncation is a separate data-destruction channel: source evidence matrix

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit documentation-only child of #1552 DEC-1328 at `97bc8b236990e49daa9fbe8371440138f673fc9a`, with **885 distinct source-defined test methods unchanged**. All executable cases use fresh generated PUBLIC **anonymous Linux memfd** objects with real inode-only inotify kernel receipts, not protected annual sources or installed monitors.

## Directly observed Linux behavior on generated PUBLIC memfd sources

| Exact draft | Descriptor flags on /proc/self/fd of original memfd | Genuine seal state and return | Effect on actual original inode and native event |
| --- | --- | --- | --- |
| #1547 DEC-1323 | O_RDONLY|O_TRUNC | F_SEAL_WRITE only, succeeds | **All original data destroyed**, size 0, true IN_MODIFY; direct pwrite separately rejects EPERM |
| #1548 DEC-1324 | O_RDONLY|O_TRUNC | F_SEAL_FUTURE_WRITE only, succeeds | **All original data destroyed**, size 0, true IN_MODIFY; new writable mmap and pwrite separately reject EPERM |
| #1549 DEC-1325 | Each of O_RDONLY, O_WRONLY, O_RDWR combined with O_TRUNC | F_SEAL_GROW|F_SEAL_SHRINK, each rejects **EPERM** | Original source bytes/length remain exact, native IN_MODIFY quiet |
| #1550 DEC-1326 | Each of O_RDONLY, O_WRONLY, O_RDWR combined with O_TRUNC | F_SEAL_WRITE|GROW|SHRINK|SEAL, each rejects **EPERM** | Original source bytes/length exact, even direct pwrite and new writable shared map EPERM |
| #1551 DEC-1327 | O_PATH|O_TRUNC and O_PATH|O_WRONLY|O_TRUNC | Both F_SEAL_WRITE-only and strong full seals: O_PATH opens succeed | **No truncation** because O_PATH ignores ordinary access and O_TRUNC for byte operations; pread through O_PATH rejects EBADF, no MODIFY. On same weakly sealed original, *true* O_RDONLY|O_TRUNC subsequently destroys data; with full seals that true call rejects EPERM |
| #1552 DEC-1328 | O_RDONLY|O_TRUNC across five separate source inodes | GROW-only, WRITE|GROW **succeed**; SHRINK-only, WRITE|SHRINK, FUTURE_WRITE|SHRINK **EPERM** | Native MODIFY and actual lost bytes in success cases; quiet kernel buffer and unchanged original data in denial cases |

## Security interpretation

1. An open can itself be a **data-mutating syscall**. `O_RDONLY` in an accepted `O_RDONLY|O_TRUNC` combination does **not** mean the protected original was merely read. `F_SEAL_WRITE` and `F_SEAL_FUTURE_WRITE` alone are incomplete data-integrity constraints because file length reduction can destroy original bytes. The tested decisive restriction for opening an existing source with `O_TRUNC` is **F_SEAL_SHRINK**, with or without additional WRITE/FUTURE_WRITE/GROW bits.
2. `O_PATH` changes the meaning of the other open flags: `open(O_PATH|O_TRUNC)` may return success while doing no truncation at all. A successful syscall alone is **not proof of a performed data write**; an actual before/after original inode byte/size comparison and true independent kernel receipt are necessary.
3. In these cases the genuine original anonymous inotify **IN_MODIFY** stream sees the destructive O_TRUNC, but earlier real native tests show mmap and memfd hole-punch/copy operations can change actual data with no MODIFY; **no event receipt alone can ever be elevated to independently enforced no-write**. These anonymous memfd witnesses have **no named original parent**, unlike original PUBLIC pathname+parent negative controls in older tests.
4. Strict kernel seals and errno observations concern only the particular disposable **anonymous PUBLIC** file. They are **not installed OS/storage policy over any existing protected annual source**, do not attest an independently authenticated administrator no-bypass witness, and do not bind a protected annual job to a reviewed immutable SHA.

## Gate separation, exact-head CI and immutable failure records

The prior canonical #1546 DEC-1322 exact head was the fully verified baseline, **879 source-defined tests**, successful completed Phase3 and full historical CI. The six new executable drafts #1547–#1552 and this docs-only child #1553 each require their own independently successful **completed Phase3 AND historical `tests`** at the exact head. A green Phase3 with historical still running is **pending**, not fully verified. Past original failed exact SHA conclusions remain FAILED even if a later forward-only repair passes.

The noninstalled independent review acceptance contract in `docs/dec1320-independent-protected-no-write-and-annual-admission-acceptance-contract.md` remains nonauthorizing: protected original inode identity, OS/storage no-bypass protection and access-time lifetime, job-before-checkout + pre-install + pre-evidence immutable SHA/ref admission, fresh run385 slot proof and separate reviewed **one-shot** authorization are outstanding.

Protected independently OS-enforced no-write **DEC-650/#820** and exclusive immutable annual run385 admission **DEC-651/#821/#779** remain **BLOCKED**. No protected annual source/evidence handling, run/test/retry/rerun/dispatch, installed production refs/workflows/rulesets/permissions, broker/trading, merges or promotions.
