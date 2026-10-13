# DEC-1019 — Inotify FD independence, subscription loss and gap coverage handoff

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict documentation-only one-commit child of DEC-1018/#1239. No runtime, executable test, CI workflow, production refs, protected source/evidence, runner, ruleset, permission or broker/trading action. The draft stack remains at **666 distinct source-defined test methods**.

## Native Linux evidence and independence boundary

| Control | Native disposable Linux mechanism | Observed real evidence | Reviewer limitation |
| --- | --- | --- | --- |
| DEC-982/#1203 | Two truly separate `inotify_init1` instances register the SAME source inode with create-only `IN_MASK_CREATE` | Both initial registrations independently succeed and each FD retains a separate native queue; duplicate create-only registration within each FD returns EEXIST | Per-FD registration exclusivity is not global file ownership or OS-enforced write prevention |
| DEC-1014/#1235 | Two independent dual source+parent FDs, explicitly removing source then parent on one FD | Source and parent `IN_IGNORED` on removed FD; the untouched independent FD still witnesses real public source writes when removed FD's queue becomes empty | A quiet queue on a watchless FD is not evidence that the source had no writes |
| DEC-1015/#1236 | Native source removal and re-registration on same original inode and same FD | Parent-only named write evidence during gap; new source WD receives later modifications but not earlier ones | Reinstalling a watch cannot reconstruct missing event history |
| DEC-1017/#1238 | Native parent watch removal and re-registration on same directory inode | A real transient sibling create/delete is invisible to the primary FD with missing parent watch, yet separately reported by intact independent second FD. New parent WD sees only later namespace activity | Re-registering the parent cannot retroactively make an earlier unseen sibling interval complete |
| DEC-1018/#1239 | `os.dup(primary_inotify_fd)` and separately `inotify_init1` on the SAME source/parent inodes | Reads via duplicated FD drain primary's **shared** queue; `inotify_rm_watch(dup_fd, wd)` invalidates the same original watch with `IN_IGNORED` on primary FD. Unrelated instance retains its own records | Two FD integers do not establish two independent inotify observers when they alias one kernel instance |

The controls use genuinely generated, disposable public files in private `/tmp` directories, real kernel inotify syscalls and byte/event snapshots, bounded source+parent stat/inventory verification and native FD cleanup. No test has permission to touch protected annual sources or evidence, access a broker, or operate trading systems.

Independence requires *different inotify instances*, not merely different FD integers or WD integer values; a duplicated descriptor also shares the original kernel queue, subscriptions and invalidation. An `IN_IGNORED` event or a later rewatch cannot authenticate prior missing coverage. Even correctly observed writes or no-op file operations are not independently OS-enforced protected write confinement.

The unchanged observer must remain fail-closed when handed actual unsafe writes or watch invalidation, with `status=BLOCKED`, `can_authorize_dispatch=false` and `independent_os_proof_verified=false` exactly. This document is a reviewer matrix, not operational authorization or a live CI certificate.

## Required exact-head CI separation

The last previously confirmed fully CI-green individual checkpoint before these new developments was DEC-1015/#1236 at `b68105557a7993b3839274d2d89264731b8721be`. DEC-1016/#1237, DEC-1017/#1238, DEC-1018/#1239 and this documentation-only child each require **their own exact-head Phase 3 AND complete historical regression**, followed by a separate qualified independent security review. A running historical job is not a success, and a successful descendant does not change a failed or unverified ancestor. Historical original red exact commits #1201–#1205 and #1212 remain failed.

Independent protected OS-enforced no-write DEC-650/#820 and immutable exclusive annual run385 admission DEC-651/#821/#779 remain **BLOCKED**. No protected annual source/evidence, run385 execution/test/retry/rerun/dispatch, production workflows/refs/runners/rulesets/permissions changes, broker/trading operations, merges, promotions or authorization.