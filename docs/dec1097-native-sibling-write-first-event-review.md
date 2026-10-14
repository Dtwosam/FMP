# DEC-1097 — Sibling first MODIFY versus first CLOSE_WRITE: parent one-shot witness boundary

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict documentation-only single-commit child of DEC-1096/#1317 at `5340ba3c2f0b1a3ba4873d3b636303c40b0984df`. Exactly one reviewer document and **716 source-defined tests unchanged**. No runtime, executable, protected annual, production or broker/trading changes.

## Compare first matching native events on one real sibling write

| Test | Original unsafe parent-only IN_ONESHOT mask | First real activity | Original parent one-shot records | Independent continuing full parent witness | Events missed afterward |
| --- | --- | --- | --- | --- | --- |
| DEC-1095/#1316 | IN_CLOSE_WRITE plus CREATE/DELETE, **IN_MODIFY absent** | Real changed-byte write and writable close to unrelated PUBLIC sibling | **Named IN_CLOSE_WRITE(public-sibling)**, then **IN_IGNORED** | Named sibling **IN_MODIFY and IN_CLOSE_WRITE** on same actual operation | Subsequent sibling restoration plus both actual sample changed-byte/restoration writes |
| DEC-1096/#1317 | **Both IN_MODIFY and IN_CLOSE_WRITE** plus CREATE/DELETE | Same kind of real changed-byte write and writable close to unrelated PUBLIC sibling | **Named IN_MODIFY(public-sibling)**, then **IN_IGNORED** | Named sibling **IN_MODIFY and IN_CLOSE_WRITE** on same actual operation | **Even the first sibling write's CLOSE_WRITE**, subsequent sibling restoration, and both actual sample writes |

Both tests create a new independent one-shot parent inotify instance alongside the real unchanged continuing source+parent mutation watcher, on disposable PUBLIC Linux /tmp files. A true source changed-byte write and restoration each produce independent unnamed source MODIFY/CLOSE_WRITE and named parent MODIFY/CLOSE_WRITE. This provides genuine positive mutation provenance despite the removed original one-shot's empty queue.

**Critical temporal distinction:** The event masks describe what *would trigger* a live watch, not a promise that all subscribed actions from a single kernel operation are captured. With IN_MODIFY subscribed, the first genuine sibling MODIFY ends the one-shot lifetime *before the corresponding writable close*. Without IN_MODIFY, first matching event is CLOSE_WRITE at the end of that write. Either original parent one-shot loses all future cross-child writes. IN_IGNORED is native watch removal, not evidence of a read-only filesystem or a complete historical log. Final original sibling/sample bytes and bounded inventory cannot prove no intervening mutations.

## Evidence admission and production scope

These are intentionally alternative unsafe **IN_ONESHOT** masks installed in isolated test code only. The unchanged actual helper `scripts/dec677_disposable_inotify_events.py::_start_watch` instead installs continuing full source and parent mutation watches and does not use IN_ONESHOT. Do not claim the experimental first-event behavior is an installed runtime defect or independently OS-enforced protected no-write.

The unchanged evaluator on independently witnessed real sample writes stays exact `status=BLOCKED`, `can_authorize_dispatch=false`, and `independent_os_proof_verified=false`. A locally quiet disposable observer also cannot authorize protected annual dispatch.

Every individual draft requires its own exact-HEAD successful Phase 3 acceptance **and** complete historical regression plus separate qualified independent security review. At document writing, #1313/DEC-1092 was the most recent consecutively both-suite verified draft (713 source-defined methods); later exact heads are still pending. Earlier failed originals #1201–#1205, #1212, #1237 and #1261–#1267 retain FAILED status, irrespective of descendant checks.

Independently OS-enforced protected no-write DEC-650/#820 and immutable exclusive annual run385 admission DEC-651/#821/#779 remain **BLOCKED**. All descendants remain DRAFT / NEVER MERGE / NEVER PROMOTE. No protected annual source/evidence, annual run385 execution/test/retry/rerun/dispatch, production refs/workflows/runners/rulesets/permissions, broker/trading operations, merges or promotions.
