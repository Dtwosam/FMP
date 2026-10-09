# DEC-645 — Non-authorizing checkout mount-boundary observations

**DRAFT / NEVER MERGE.** This is an offline, read-only diagnostic stacked on [PR #814](https://github.com/Dtwosam/FMP/pull/814). It does not import or change the 23 audit CLI wrappers, shared report writer, annual workflows, repository permissions, protected artifacts, broker APIs or trading systems.

## Why

DEC-644 established that a pinned directory FD cannot by itself guarantee checkout integrity: an actor permitted to rename the already-open output directory into checkout can still cause report publication inside checkout. Real mount and ownership enforcement matter. Linux documents that rename() fails with EXDEV across distinct mounts even if backed by the same filesystem. This does NOT mean different device IDs or read-only flags alone prove immutable checkout.

References:
- https://man7.org/linux/man-pages/man2/rename.2.html
- https://man7.org/linux/man-pages/man5/proc_pid_mountinfo.5.html
- https://man7.org/linux/man-pages/man3/statvfs.3.html
- https://man7.org/linux/man-pages/man8/mount.8.html

## Usage (local/test namespace only)

    python -B scripts/dec645_mount_boundary_diagnostic.py --checkout /path/to/checkout --output-parent /path/to/external/reports

The tool reads the process's mountinfo and metadata for TWO pre-existing directories. It outputs observations for mount IDs, distinct st_dev, VFS read-only mount flag, statvfs read-only flag, and whether the requested report parent resolves into checkout. A mountinfo source (default /proc/self/mountinfo) is read nonblocking, nofollow and length-bounded; FIFO, non-regular, malformed, oversized, unavailable or ambiguous input cannot grant approval. The CLI neither creates directories nor writes report files.

**Every single result sets authorized=false and classification=NOT_AN_AUTHORIZATION, and the CLI intentionally exits status 2.** An observation of separate mounts and a read-only checkout is NOT itself a permission to dispatch, merge, trade or assert checkout immutability. Mount namespace changes, alternate bind aliases, privilege and concurrent rename remain outside this observational tool.

## Regression evidence and scope

The initial isolated test suite passed **13/13 local tests**: identical/distinct mount advisory, observed read-only checkout still unauthorized, output already inside checkout, output alias symlink, escaped mountinfo path, prefix-confusion prevention, ambiguous stacked mounts, missing directories, corrupt and oversize mountinfo, CLI exit 2 with JSON, nonblocking FIFO mountinfo, and absence of network/order/dispatch/write primitives. Exact-head GitHub CI must be independently verified.

## Never-merge gate

Independent review must define and verify the actual checkout namespace, mount isolation, owner/group write privileges and whether adversaries can reparent directories into checkout. This diagnostic is NOT enforcement. Legitimate symlinked parent usability, mode-0600 output, crash/orphan cleanup and cross-platform behavior remain unresolved in the ancestor proposals. Original #796–800 lack independent review, main was unprotected with no rulesets at last live check, run385 remains unconsumed and prohibited, and all preview drafts #809–815 remain NEVER MERGE.