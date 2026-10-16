# DEC-1322 — Anonymous source integrity, mutable metadata, fork reconciliation and independent protected gates

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit docs-only child of #1545 DEC-1321 at `664210d65ddb2a954956f5718d838a15b60f9794`, **879 distinct source-defined tests unchanged**. No protected annual source/evidence access, installed runtime/runner/workflow/ruleset/permission change, production, broker/trading, merge or promotion.

## Canonical recent lineage and actual evidence

| Canonical draft | Tested or reviewed boundary | Narrow Linux outcome | Security interpretation |
| --- | --- | --- | --- |
| #1531 DEC-1310 | Original generated PUBLIC anonymous memfd direct pwrite did not emit inotify MODIFY | Five original test assertions were **repaired forward only** to require genuine event silence while retaining true changed/restored byte proof and **positive native ftruncate MODIFY** | The formerly failed historical original exact SHAs **#1526–#1530 remain FAILED** and must never be relabeled |
| #1532 DEC-1311 | Fully sealed anonymous original, writable MAP_PRIVATE COW | Real original source data/size remains unchanged, private mapped memory can still change; strong write/size seals deny tested source mutations | Source immutability is different from memory-view immutability |
| #1533 DEC-1312 | Fully sealed original source→pipe native splice, versus pipe→sealed source | Kernel allows original read/transfer, but denies original data write EPERM | No-write does not imply no-read; operation direction matters |
| #1534 DEC-1313 | Initial source-only sealed-inode and CI review | Documentation-only | Non-authorizing review; each exact SHA requires its own finished CI |
| #1535 DEC-1314 | memfd without MFD_ALLOW_SEALING | Defaults to F_SEAL_SEAL, prevents adding missing seals but **does not deny actual data writes or truncation** | Immutable seal *list* is not protected data immutability |
| #1536 DEC-1315 | Sealing-mode and CI audit | Documentation-only | Keeps previous failures and evidence scopes distinct |
| #1537 DEC-1316 | Fully sealed original reopened via procfd O_RDWR after initial handle | Original seals still reject write/truncate/mmap even after original FD closes | Full data seals survive new writable descriptions of the **same anonymous inode** |
| #1539 DEC-1317 | Canonical review child of #1537 | Documentation-only | Disposition and reviewer notes, not a new executable authority |
| #1541 DEC-1318 | Fully sealed source memfd→different unsealed memfd destination via native copy_file_range; seal destination and repeat | Source data stays unchanged, **destination original inode bytes change without IN_ACCESS or IN_MODIFY on either anonymous watch**; subsequent sealed-destination copy rejects EPERM | A completely sealed **source** does not freeze a distinct destination or deny source reads; inotify quiet can accompany actual destination mutation |
| #1543 DEC-1319 | Full-sealed original memfd, fchmod mode0444 and restore | Two true native **IN_ATTRIB**, no IN_MODIFY or data changes; pwrite, writable shared mmap and grow/shrink remain denied EPERM | Full memfd data/length sealing does **not** freeze permission metadata |
| #1544 DEC-1320 | Independent protected no-write and run385 admission acceptance contract | Documentation-only conditions for actual protected source identity, OS/storage control/lifetime/bypass witness and separately immutable SHA/ref admission | No controls installed; real DEC-650/#820 and DEC-651/#821/#779 both remain BLOCKED |
| #1545 DEC-1321 | Full-sealed original reopened via independent procfd O_RDWR, original FD closed; fchmod via surviving description | Original anonymous inode remains alive; two native **IN_ATTRIB** mode transitions despite original FD closure, while direct source writes/truncate/new shared mmap remain EPERM | Metadata remains writable via alternate legitimate file description even when actual backing data/size are sealed |

## Reconciled fork audit

Parallel drafting briefly produced native copy proposals #1538 (DEC-1314), #1540 (DEC-1317) and #1542 (DEC-1318) from older heads while #1535–#1539 were also advancing. To preserve a reviewer-readable **single strict one-commit canonical lineage**, those three duplicate sibling PRs were **closed, unmerged, as SUPERSEDED**; their commits and original CI observations were *not rewritten or erased*. The canonical test occupies **#1541 DEC-1318**, one commit after canonical review #1539, followed by #1543, #1544, #1545. Their exact SHA results remain individually reviewable. Closing a superseded proposal grants no promotion/merge/execution authority.

## Mandatory assurance boundary

**Actual original data, mapping bytes, different destination data, file size, inode metadata, descriptor identity and native event receipts must be distinguished individually.** Anonymous memfd cases use real native original inode-only inotify watches through `/proc/self/fd`, and do **not** claim the named-parent `_start_watch` or `_evaluate` witness from disposable regular-file tests. A genuinely denied native write on a fully sealed **anonymous PUBLIC object** is not proof that any existing protected annual filesystem inode is under the same independently owned policy. An empty original source/parent inotify MODIFY queue cannot prove absence of real mapped/copy data changes.

Each draft remains **DRAFT / NEVER MERGE / NEVER PROMOTE** and needs its exact-head completed **Phase3 acceptance AND full historical tests** plus qualified independent review. A Phase3-green/historical-pending draft remains pending, and an original historical FAILED exact SHA stays failed forever. No future decision shall infer `independent_os_proof_verified=true`, `can_authorize_dispatch=true` or annual run385 authorization from these PUBLIC fixtures.

Protected independently OS-enforced no-write **DEC-650/#820** and immutable exclusive annual run385 admission **DEC-651/#821/#779** remain **BLOCKED**. The DEC-1320 checklist is a noninstalled reviewer contract only. No protected annual source/evidence operations, annual run/test/retry/rerun/dispatch, installed production refs/workflows/rulesets/permissions, broker/trading, merges or promotions.
