# DEC-1081 — Combined native read masks: source and parent one-shot scope and evidence review

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict **documentation-only**, one-commit child of DEC-1080/#1301 at `0c5aa2bdc7b148061d4ba01dd353002223b4db5a`. Exactly one new Markdown file; **707 source-defined test methods unchanged**. No executable, observer runtime, protected annual, broker/trading or production changes.

## Nominal combined mask does not guarantee surviving subscriptions

| Experiment | One-shot watched inode | Initial ordinary PUBLIC read | One-shot native receipt | Separately initialized benign-read witness | Independently initialized mutation witness |
| --- | --- | --- | --- | --- | --- |
| DEC-1079/#1300 | Source `sample` inode | Read-only `open`, actual byte `read`, then `close` of **same sample** | Unnamed `IN_OPEN` then `IN_IGNORED`; no subscribed ACCESS/CLOSE_NOWRITE | Continuing **source** read watch captures unnamed OPEN → ACCESS → CLOSE_NOWRITE | Continuing source + parent captures later genuine source MODIFY/CLOSE_WRITE and named-parent MODIFY/CLOSE_WRITE |
| DEC-1080/#1301 | Parent directory inode | Read-only `open`, actual byte `read`, then `close` of **unrelated sibling public-read** | **Named public-read** `IN_OPEN` then `IN_IGNORED`; no subscribed ACCESS/CLOSE_NOWRITE | Continuing **parent** read watch captures named OPEN → ACCESS → CLOSE_NOWRITE on public-read | Continuing source + parent captures later genuine **different child sample** MODIFY/CLOSE_WRITE and named-parent MODIFY/CLOSE_WRITE |

Both original one-shot watchers explicitly include `IN_OPEN | IN_ACCESS | IN_CLOSE_NOWRITE | IN_MODIFY | IN_CLOSE_WRITE | IN_ONESHOT`. The parent case additionally subscribes to `IN_CREATE | IN_DELETE` and uses `IN_ONLYDIR`. Both witnesses for the one-shot and continuing read events are separate native `inotify_init1` instances: shared kernel watch identity or shared queue cannot explain why one loses records while the other receives them. The third continuous source+parent mutation instance is separately initialized and does not subscribe to read-open-access-close events. Neither combined-mask one-shot reaches later WRITE events after automatic watch removal; an independent native witness observes real writes and subsequent restoration of original PUBLIC bytes.

**Read filters versus lifetime:** A missing event due to a registration never subscribing to its bit must not be confused with a subscribed event being missed after `IN_ONESHOT` consumes the watch. Both DEC-1079 and DEC-1080 specifically address the latter. `IN_IGNORED` proves native watch removal, **not** future immutability. Restored final file content, inode/mode and final bounded directory inventory are snapshots, not a complete history of protected filesystem writes.

**Production scope:** These intentionally alternative unsafe one-shot configurations are used for generated-PUBLIC disposable regressions only. The unchanged actual disposable source+parent watcher `scripts/dec677_disposable_inotify_events.py::_start_watch` does not set `IN_ONESHOT` or use these benign read event subscriptions. The unchanged evaluator stays `status=BLOCKED`, `can_authorize_dispatch=false`, and `independent_os_proof_verified=false` on independently witnessed genuine source modifications. Even a locally coherent quiet receipt remains `LOCAL_DISPOSABLE_WITNESS_UNVERIFIED`, never an authorization.

## Exact-head CI and blocked security gates

At creation, DEC-1079/#1300 (706 source-defined tests) was the latest consecutively verified both-suite green draft; DEC-1080/#1301 needed its own exact-head successful Phase 3 and complete historical regression. This documentation-only child likewise requires BOTH exact-head CI suites to complete successfully, followed by qualified **independent** security review. None of the above observational regressions establishes OS-enforced protected no-write or immutable annual admission.

Earlier original failed exact commits #1201–#1205, #1212, #1237 and #1261–#1267 retain FAILED status regardless of passing descendants. Independently OS-enforced protected no-write DEC-650/#820 and immutable exclusive annual run385 admission DEC-651/#821/#779 stay **BLOCKED**.

All descendants stay DRAFT / NEVER MERGE / NEVER PROMOTE. No protected annual source/evidence, run385 execution/test/retry/rerun/dispatch, production refs/workflows/runners/rulesets/permissions, broker/trading operations, merges or promotions.
