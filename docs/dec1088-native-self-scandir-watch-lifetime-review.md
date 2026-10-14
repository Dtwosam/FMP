# DEC-1088 — Directory self-event mask and lifetime evidence review

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict documentation-only one-commit child of DEC-1087/#1308 at 568c507efde12bc86ac79724b7ef7db6c8998648. Adds one Markdown reviewer matrix; **711 source-defined test methods unchanged**. No runtime, new executable, protected annual, production, broker or trading changes.

## Watch lifetime versus selected read masks on the same watched parent inode

| Test case | Deliberately subscribed benign events | Actual first successful PUBLIC operation | One-shot original queue | Independent *continuing* parent benign-event queue | Subsequent sample activity |
| --- | --- | --- | --- | --- | --- |
| DEC-1082/#1303 | **OPEN**, with parent mutation actions and IN_ONESHOT | Read-only O_DIRECTORY opening watched parent | Unnamed IN_OPEN|IN_ISDIR then IN_IGNORED | Unnamed IN_OPEN|IN_ISDIR | Genuine sample MODIFY + CLOSE_WRITE captured by separate full source+named-parent mutation watcher |
| DEC-1084/#1305 | **CLOSE_NOWRITE**, without OPEN or ACCESS, with mutation actions and IN_ONESHOT | Read-only O_DIRECTORY opening (initially quiet), then closing watched parent | Unnamed IN_CLOSE_NOWRITE|IN_ISDIR then IN_IGNORED | Unnamed IN_CLOSE_NOWRITE|IN_ISDIR | Same independent actual sample writes after removal |
| DEC-1085/#1306 | **ACCESS**, without OPEN or CLOSE_NOWRITE, with mutation actions and IN_ONESHOT | Enumerating watched parent's directory entries with os.scandir | Unnamed IN_ACCESS|IN_ISDIR then IN_IGNORED | Unnamed IN_ACCESS|IN_ISDIR | Same independent actual sample writes after removal |
| **DEC-1087/#1308** | **OPEN + ACCESS + CLOSE_NOWRITE**, with mutation actions and IN_ONESHOT | One real os.scandir of watched parent | **Only unnamed IN_OPEN|IN_ISDIR, then IN_IGNORED** | All three unnamed IN_OPEN|IN_ISDIR, IN_ACCESS|IN_ISDIR, IN_CLOSE_NOWRITE|IN_ISDIR in order | Same independent actual sample writes after removal |

All original one-shot watches also deliberately include parent-level CREATE, DELETE, MODIFY and CLOSE_WRITE subscriptions, none of which continue after the kernel emits IN_IGNORED for that watch identity. The continuing benign read watcher is created on a **separate native inotify_init1 descriptor** and reveals which actions really occurred. A **third separate full source+parent** native inotify instance confirms real sample changes by receiving source MODIFY and CLOSE_WRITE plus named-parent MODIFY and CLOSE_WRITE. Final restored PUBLIC bytes, unchanged inode/mode, and a stable bounded inventory do not recover native events that a destroyed one-shot never received.

**Directory self versus child scope.** Each event in this table has an **empty name** and an IN_ISDIR modifier, because the watched parent directory inode itself was opened, enumerated or closed. The modifier IN_ISDIR is not a second action. Contrast earlier **named child events** (unrelated public-read OPEN/ACCESS/CLOSE_NOWRITE on #1292/#1297/#1298, combined child read on #1301), which address the parent observer from a different inode but also destroy parent one-shot lifetime. The one-shot removal is not a read-only filesystem guarantee and is not a complete mutation provenance record.

**Keep actual implementation separate.** The deliberately unsafe alternative IN_ONESHOT masks in these regressions are NOT installed by the unchanged actual disposable observer scripts/dec677_disposable_inotify_events.py::_start_watch. It continues monitoring source+parent mutation events without IN_ONESHOT or these benign read masks. The unchanged evaluator stays exact status=BLOCKED, can_authorize_dispatch=false, independent_os_proof_verified=false for independently witnessed unsafe activity; a locally quiet result remains LOCAL_DISPOSABLE_WITNESS_UNVERIFIED and cannot authorize protected dispatch.

## Verification and immutable security boundary

Each descendant must pass **both** its own exact-head Phase 3 acceptance and full historical regression, followed by qualified independent security review. At this note's preparation #1304/DEC-1083 was the latest consecutively fully CI-verified checkpoint; later drafts need individually completed successes before the consecutive checkpoint can advance. Earlier original failed exact commits #1201–#1205, #1212, #1237 and #1261–#1267 remain FAILED even if descendants pass.

Independently OS-enforced protected no-write DEC-650/#820 and immutable exclusive annual run385 admission DEC-651/#821/#779 remain **BLOCKED**. All PRs stay DRAFT / NEVER MERGE / NEVER PROMOTE. No protected annual source/evidence, run385 execution/test/retry/rerun/dispatch, production refs/workflows/runners/rulesets/permissions, broker/trading operations, merges or promotions.
