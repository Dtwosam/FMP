# DEC-1075 — Benign read event types consume native one-shot lifetime before later mutations

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict **documentation-only** one-commit child of DEC-1074/#1295 at `6dae4224fa5d69dce2ab4bfc62a54efdaaac6667`. **703 source-defined tests unchanged.** No executable, observer runtime, production, protected annual data or broker/trading changes.

## Source one-shot: three different non-mutating first matches

| Experiment | Native source one-shot subscription | Real initial harmless action | Original native watch queue | Subsequent independent source+parent evidence |
| --- | --- | --- | --- | --- |
| DEC-1069/#1290 | `IN_OPEN | IN_MODIFY | IN_CLOSE_WRITE | IN_ONESHOT` | Open source for read | unnamed `IN_OPEN`, then `IN_IGNORED` | Actual later sample changed-byte MODIFY+CLOSE_WRITE, source and named parent |
| DEC-1073/#1294 | `IN_ACCESS | IN_MODIFY | IN_CLOSE_WRITE | IN_ONESHOT`, **without IN_OPEN** | Open for read (still armed), then read bytes | After actual read: unnamed `IN_ACCESS`, then `IN_IGNORED` | Actual later sample changed-byte MODIFY+CLOSE_WRITE, source and named parent |
| DEC-1074/#1295 | `IN_CLOSE_NOWRITE | IN_MODIFY | IN_CLOSE_WRITE | IN_ONESHOT`, **without IN_OPEN or IN_ACCESS** | Open and read source (still armed), then close read-only handle | After actual close: unnamed `IN_CLOSE_NOWRITE`, then `IN_IGNORED` | Actual later sample changed-byte MODIFY+CLOSE_WRITE, source and named parent |

Each experiment independently creates a real native inotify source-only one-shot instance and a separate, **non-duplicated**, continuously registered native source+parent instance. All paths and content are generated disposable **PUBLIC** Linux `/tmp` fixtures. Every alternative one-shot mask nominally includes the subsequent mutation categories `IN_MODIFY` and `IN_CLOSE_WRITE`. Nevertheless the first subscribed read-related event removes the entire watch for the remainder of its lifetime. This is **watch removal**, not proof that the file became immutable, and not a demonstration that ordinary IN_MODIFY/IN_CLOSE_WRITE subscriptions omit genuine events while their watch remains active.

## Parent scope and evaluation boundary

DEC-1071/#1292 demonstrates an even broader **parent** one-shot failure: read-only opening an **unrelated public sibling** triggers named `IN_OPEN` then `IN_IGNORED`, destroying later write coverage for the watched sample because the parent subscription is gone. Source-only OPEN/ACCESS/CLOSE_NOWRITE read cases and cross-child parent OPEN cases differ in trigger and watch scope, but share the first-match `IN_ONESHOT` loss.

The actual unchanged helper `scripts/dec677_disposable_inotify_events.py::_start_watch` registers continuing source+parent mutation watches **without IN_ONESHOT** or benign read event masks. The experiments deliberately install different **test-only, unsafe alternative registrations**; do not attribute these masks to the existing observer runtime or claim they are a deployed vulnerability. The unchanged evaluator responds to genuinely independently witnessed sample writes with exact `status=BLOCKED`, `can_authorize_dispatch=false`, `independent_os_proof_verified=false`. Even an apparently quiet, locally coherent receipt remains a distinct nonauthorizing `LOCAL_DISPOSABLE_WITNESS_UNVERIFIED`.

## Admission and verification limits

Independent native disposable kernel probes reproduced the distinct benign-event records. A final restored public source digest, unchanged source+parent inode/mode, and stable bounded directory inventory cannot retrospectively recover events missing from a destroyed watcher or establish independently OS-enforced protected no-write.

Every draft must pass **both** the Phase 3 acceptance and complete historical regression **at its own exact commit**, followed by qualified independent security review. At matrix creation, #1292/DEC-1071 was the latest consecutive fully verified checkpoint; #1293's historical suite and #1294–#1295's own historical suites had not yet been individually verified complete. Earlier original failed exact commits #1201–#1205, #1212, #1237 and #1261–#1267 must stay FAILED regardless of descendant status. Independently OS-enforced protected no-write DEC-650/#820 and immutable exclusive annual run385 admission DEC-651/#821/#779 remain **BLOCKED**.

No protected annual source/evidence, annual run385 execution/test/retry/rerun/dispatch, production refs/workflows/runners/rulesets/permissions, broker/trading operations, merge or promotion.
