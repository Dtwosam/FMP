# DEC-1293 — Linux native read/write provenance and persistent mmap write-capability review

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit documentation-only child of #1513 DEC-1292 at `0e7c27842f7938f8499df20aa3f9e1b3480d614c`. **861 distinct source-defined Linux regression methods unchanged**. All tests generate only disposable **PUBLIC /tmp** data and use native Linux kernel calls and inotify; nothing protected, annual, broker/trading, production or installed source-monitor runtime was touched.

## Evidence matrix — map access is not one global write switch

| Draft | Original source descriptor / operation | Exact native source+named-parent evidence | Negative security implication |
| --- | --- | --- | --- |
| #1506 DEC-1285 | `mmap(PROT_READ,MAP_SHARED)` on original O_RDONLY, then `mprotect(PROT_READ|PROT_WRITE)` | Native **EACCES** on upgrade, mutation queues quiet; separate independent original O_WRONLY writer causes two true source+named-parent MODIFY | EACCES denies **that MAP_SHARED mapping's upgrade**, not writes through other descriptions |
| #1507 DEC-1286 | `mmap(PROT_READ,MAP_PRIVATE)` on original O_RDONLY, then `mprotect(PROT_READ|PROT_WRITE)` and actual COW memory store | mprotect succeeds, private memory changes while independent original inode pread remains unchanged and source+parent MODIFY silent; later real writer positive MODIFY | MAP_PRIVATE can permit writable **private COW**, without independently modifying the original source inode |
| #1512 DEC-1291 | `mmap(PROT_READ|PROT_WRITE,MAP_SHARED)` on original O_RDWR; mprotect downgrade PROT_READ, re-upgrade PROT_READ|PROT_WRITE, actual mapped stores/restoration | mprotect both directions succeeds and **actual original inode data changes twice** with no native MODIFY; eventual FD-close source+parent CLOSE_WRITE | Temporary mapping permission downgrade does not permanently revoke ability to re-upgrade a previously writable shared map |
| #1513 DEC-1292 | Same original O_RDWR shared mapping, but **close original O_RDWR FD while map only PROT_READ**, then call mprotect write-upgrade and change/restore source bytes | Closing FD is **CLOSE_WRITE quiet** while map retains file; mprotect re-upgrade succeeds **after FD already closed**; genuine original inode changes with no MODIFY; **final munmap** emits source+parent CLOSE_WRITE | Closing all known ordinary write descriptors and temporarily PROT_READ-mapping is **not** independent file no-write confinement |

## Evidence matrix — kernel transfer direction determines the source event

| Draft | Genuine source and destination operations | Independent read-witness receipt | Continuous source+parent mutation receipt |
| --- | --- | --- | --- |
| #1508 DEC-1287 | Precreated PUBLIC original `sample` O_RDONLY → distinct precreated PUBLIC `dest` O_WRONLY via `copy_file_range` | Original source + named-parent **IN_ACCESS(sample)** | **Parent named MODIFY(dest)**, no original source MODIFY; later separate real original source writes positive MODIFY |
| #1509 DEC-1288 | Original `sample` O_RDONLY → anonymous pipe via `sendfile` | Original source + named-parent **IN_ACCESS(sample)** | **No original source/parent MODIFY**, no named destination exists |
| #1510 DEC-1289 | Original `sample` O_RDONLY → pipe via `splice`, then pipe → same original source O_WRONLY via `splice(offset_dst=0)`, with restoration | Source + named-parent IN_ACCESS on read direction | Original source/parent quiet on source→pipe; **source+named-parent MODIFY twice** on pipe→original source changing/restoring, then CLOSE_WRITE |
| #1511 DEC-1290 | Documentation-only comparison of mprotect and kernel-copy original/destination event provenance | No executable change | No source mutation from reviewer document |

## Why this is still BLOCKED

A real original-source IN_ACCESS can coexist with no source mutation; source-to-destination transfers can modify a **different inode**; private mapped-memory writes may never modify original inode, whereas MAP_SHARED mapped-memory writes can genuinely modify original inode **without native IN_MODIFY**. Even a real shared mapping held at PROT_READ can sometimes be later upgraded to writable if its original file-description capability authorized such pages; closing the original O_RDWR descriptor does not necessarily revoke that mapping. Presence or absence of **inotify**, source file mode or a currently open write FD is an observation about one dimension of the system, not independent kernel-enforced prohibition of all writes.

Each executable test asserts genuine original source-inode and named-original-parent watch identities, original PUBLIC bytes and backing-source device/inode, exact native event-buffer records, generated fixture inventory and FD cleanup. Separate read-witness subscriptions are used where access provenance matters. Original **source MODIFY|CLOSE_WRITE|IN_ONESHOT** is an **intentionally unsafe isolated test-only negative control**, never deployed for authorization. All unchanged `scripts/dec677_disposable_inotify_events.py::_evaluate` verdicts remain **can_authorize_dispatch=false**, **independent_os_proof_verified=false**; every actual source change/restoration case is **BLOCKED**. No disposable Linux diagnostic observation proves independent OS enforcement.

## Exact-head CI and annual boundaries

The latest independently completed **fully green contiguous baseline** before new drafts was #1505 DEC-1284, **854 source-defined tests**, both Phase3 and historical suites passing at its exact commit. New #1506–#1513 drafts need their own **completed successfully** Phase3 and full historical `tests` suites before they are called fully verified; pending is not green. Historic originally FAILED exact SHAs from earlier batches remain FAILED forever, with forward repairs classified only under their new exact commits. Qualified independent security review is required separately and cannot be replaced by test count or CI success.

Protected independently OS-enforced no-write **DEC-650/#820** and exclusive immutable annual run385 admission **DEC-651/#821/#779** remain **BLOCKED**. No protected annual source/evidence access or changes, annual run/test/retry/rerun/dispatch, installed monitor/production refs/workflows/rulesets/permissions, broker/trading, merges or promotions.
