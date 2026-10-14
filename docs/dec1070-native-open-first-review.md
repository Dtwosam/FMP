# DEC-1070 — Reviewer matrix: OPEN-triggered one-shot loss is not a write-safe receipt

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit documentation-only child of DEC-1069/#1290 at `bc172bb814d69a2c6b13f2f3da35d0d43b2fd6cb`. **700 source-defined tests unchanged.** This commit also corrects literal escaped Markdown backticks in its parent review document without changing the test or observer runtime.

## Distinguish the first event that destroys a source one-shot

| Native PUBLIC Linux control | One-shot subscribed categories | One-shot queue | Truly independent source + parent queue | Security meaning |
| --- | --- | --- | --- | --- |
| DEC-1064/#1285, mode first | `IN_MODIFY | IN_ATTRIB | IN_ONESHOT` | Genuine chmod `IN_ATTRIB` then `IN_IGNORED` | Later genuine changed-byte `IN_MODIFY` | Initial metadata operation destroys source content coverage |
| DEC-1064/#1285, write first | Same MODIFY/ATTRIB one-shot mask, fresh registration | Genuine write `IN_MODIFY` then `IN_IGNORED` | Later genuine chmod `IN_ATTRIB` | Initial content operation destroys subsequent metadata coverage |
| DEC-1066/#1287 | `IN_MODIFY | IN_CLOSE_WRITE | IN_ONESHOT` | Changed-byte `IN_MODIFY` then `IN_IGNORED` | Real source + named-parent MODIFY and CLOSE_WRITE | Initial write mutation destroys subsequent writable-close coverage |
| **DEC-1069/#1290, benign read first** | **`IN_OPEN | IN_MODIFY | IN_CLOSE_WRITE | IN_ONESHOT`** | Genuine **read-only** OPEN then `IN_IGNORED` | Later independently witnessed source + named-parent MODIFY and CLOSE_WRITE | **A non-mutating read** permanently disarms source write coverage |
| **DEC-1069/#1290, writable open first** | Fresh same fully combined mask on original one-shot FD | Genuine **writable** OPEN then `IN_IGNORED` | Same write handle generates independent source + named-parent MODIFY and CLOSE_WRITE | Even the write's own later mutation and CLOSE_WRITE are invisible to the one-shot |

DEC-1069 uses a genuinely separately initialized inotify descriptor with independent native queues; the second native one-shot registration is after the first watch was removed. The writer uses real `open/write/fsync/close` on a disposable PUBLIC sample. Restoring exact original public sample bytes and source/parent dev/inode/mode does not prove uninterrupted observation. The source one-shot emits **native** `IN_IGNORED` in both orderings; never misclassify that removal record as a continuous watch.

Every real independently witnessed write is evaluated by the **unchanged** `dec677_disposable_inotify_events.py` evaluator as exact `BLOCKED`, with `can_authorize_dispatch=false` and `independent_os_proof_verified=false`. No locally coherent disposable read/write test can independently OS-enforce protected annual no-write or admit immutable annual run385.

Each exact draft head independently needs passed Phase 3 **and** completed full historical regression, followed by qualified independent security review; no child inherits a green status or cures an earlier failed original. At review preparation, #1284–#1286 and #1288 had both suites green; #1287, #1289, #1290 historical remained pending. Earlier failed original exact commits #1201–#1205, #1212, #1237 and #1261–#1267 remain FAILED. Independently OS-enforced protected no-write DEC-650/#820 and immutable exclusive annual run385 admission DEC-651/#821/#779 remain **BLOCKED**.

No runtime/test modification in this doc-only child. No protected annual sources/evidence, run385 execution/test/retry/rerun/dispatch, production refs/workflows/runners/rulesets/permissions changes, broker/trading, merges or promotions.
