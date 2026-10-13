# DEC-1023 — Native inotify instance identity and exact-head CI failure ledger

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit documentation-only child of DEC-1022/#1243. No runtime, executable test, CI workflow, protected source/evidence, production ref, runner, ruleset, permission, broker or trading changes. The source-defined test count remains **669**.

## FD, WD and inode identities are three different coordinates

| Control | Actual disposable native Linux setup | Kernel observation | False security conclusion forbidden |
| --- | --- | --- | --- |
| DEC-1014/#1235 | Two genuinely independent source+parent instances; remove watches from one | `IN_IGNORED` and later quiet first queue, while second intact instance still reports writes | Silence means no writes occurred |
| DEC-1015/#1236 | Remove source WD and reinstall on same inode/instance | New WD observes later writes but cannot recover parent-only gap history | Same inode plus rewatch authenticates continuous previous coverage |
| DEC-1017/#1238 | Remove parent WD on one instance while independent second remains subscribed | Real transient sibling create/delete is absent from the first queue but present in the second; new parent WD sees only subsequent siblings | Re-registering parent reconstructs previously missing directory census |
| DEC-1018/#1239 | `dup(primary_fd)` to create another numeric FD | Both descriptors share the **same** kernel instance, native queue and watch removals | Two FD numbers mean two independent audit histories |
| DEC-1020/#1241 | Two **independent** instances, same registration order | They may assign exactly equal numeric source and parent WDs to the same watched inodes | Equal WD numbers prove one shared inotify instance |
| DEC-1021/#1242 | Two independent instances with REVERSED registration order | `primary_source_wd == second_parent_wd`; using primary's bare WD number with second FD removes second **parent** watch with `IN_IGNORED` | A WD number reliably identifies an inode's role without the owning instance |
| DEC-1022/#1243 | Two independent instances initially; then `dup2(primary_fd, second_fd)` | The original second kernel instance is closed and the second numeric FD becomes a shared alias of the first. Writes now enter one queue; removing watch via alias invalidates the first instance | Retaining an FD integer means the underlying observer and its history remain independent |

A valid inotify watch identity therefore includes at least the owning inotify **instance** and its instance-local WD, together with a separately checked observed device/inode. FD integer equality/inequality, WD equality/inequality, pathname equality, re-registration and quiet queues are not sufficient for independent OS write confinement. All native controls above use **new, generated public disposable `/tmp` files only**, real native kernel event buffers, public source/parent metadata/inventory restoration, and explicit FD closure.

The unchanged observer must reject real writes, unexpected WD records or invalidation and remain `status=BLOCKED`, `can_authorize_dispatch=false`, `independent_os_proof_verified=false`. These tests cannot supply protected OS-enforced no-write evidence or immutable annual-runner admission.

## CI results must remain attached to each original SHA

| Draft exact head | Phase 3 acceptance | Full historical regression | Interpretation |
| --- | --- | --- | --- |
| #1236 `b68105557a7993b3839274d2d89264731b8721be` | Success | Success | Fully verified individual draft |
| **#1237 `658feef31f5a961366ff3fc8f0cc5157b704a094`** | **Success** | **Failure** (run `38420457581`) | **Red exact head; do not infer cause** |
| #1238 `351ceb979774834b5151517aa4331d7803f337e8` | Success | Success | Individually green; cannot heal #1237 |
| #1239 `d417a7be95b60d68f1f183c950aa0549b453658e` | Success | Success | Individually green |
| #1240 `ef0e3ded80db897c4b0ae250b327d3293af64bb0` | Success | Success | Individually green |
| #1241 `cb9c01dd46bd0d719620622fa00ef89e14c9138e` | Success | Success | Last independently fully verified at the time of this handoff |
| #1242 `8fa6c309b04ff9a0f86f39346b4ba994ad807450` | Success | Pending at time of writing | Do not claim full green yet |
| #1243 `8a943e0a2d95ed43c0b7815e08344e8cc3d7e784` | Pending at time of writing | Pending at time of writing | Do not claim either suite yet |

The original #1237 historical `unit-tests` check completed with **failure**, but the available GitHub job-log archive returned **BlobNotFound/404**, and no reliable failed assertion was retrievable. That means the exact cause remains **unverified**; do NOT rewrite, dismiss as flaky, or mark green. The original #1201–#1205 and #1212 failed exact historical commits also remain failed. Passing descendants cannot change failed ancestors. This document is not a live CI-status certificate: each exact SHA must pass **both** required suites, then qualified independent security review is still a separate gate.

Protected independently OS-enforced no-write DEC-650/#820 and immutable exclusive annual run385 admission DEC-651/#821/#779 remain **BLOCKED**. No protected evidence/sources, annual run385 execution, tests, retry, rerun, dispatch, production refs/workflows/runners/rulesets/permissions, broker/trading, merge, promotion or authorization.
