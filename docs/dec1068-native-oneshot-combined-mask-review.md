# DEC-1068 — One-shot combined masks: first matching event removes future category coverage

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit documentation-only child of DEC-1067/#1288, with **699 source-defined test methods unchanged**. One Markdown document; no runtime, executable test, production ref/workflow/runner/ruleset/permission, protected data/evidence or broker/trading change.

## Distinguish included event masks from sustained kernel event history

| Disposable native Linux control | Actual subscribed one-shot categories | First native one-shot buffer | Separate independent source+parent instance | Missed real activity |
| --- | --- | --- | --- | --- |
| DEC-1062/#1283 | Parent **`IN_CREATE | IN_DELETE | IN_ONESHOT`** | Actual public `mkdir` yields named **`IN_CREATE | IN_ISDIR`**, then `IN_IGNORED` | Real CREATE|ISDIR then DELETE|ISDIR on immediate `rmdir` | DELETE is missing **despite mask inclusion**, not because of an excluded category |
| DEC-1063/#1284 | Parent **`IN_CREATE | IN_DELETE | IN_ONESHOT`** | Actual public `rmdir` yields named **`IN_DELETE | IN_ISDIR`**, then `IN_IGNORED` | Real DELETE|ISDIR then CREATE|ISDIR on immediate recreation | CREATE is missing **despite mask inclusion**; re-created name is not inode-identity proof |
| DEC-1064/#1285 (metadata first) | Source **`IN_MODIFY | IN_ATTRIB | IN_ONESHOT`** | Actual public `chmod` yields `IN_ATTRIB`, then `IN_IGNORED` | Real original source+parent ATTRIB, followed by MODIFY from a later content write | First attribute trigger removes watch before genuine later content write |
| DEC-1064/#1285 (content first) | Fresh source instance with **same MODIFY+ATTRIB mask** | Actual public write yields `IN_MODIFY`, then `IN_IGNORED` | Real source+parent MODIFY, followed by later ATTRIB from mode restoration | First content trigger removes watch before genuine later chmod |
| **DEC-1066/#1287** | Source **`IN_MODIFY | IN_CLOSE_WRITE | IN_ONESHOT`** | Real write produces `IN_MODIFY`, then `IN_IGNORED` | Real source and named-parent **MODIFY and CLOSE_WRITE** from the same successful writable open/write/close | **CLOSE_WRITE is missing although explicitly subscribed**, because watch is removed on MODIFY before close |
| **DEC-1067/#1288** | Parent **`IN_MOVED_FROM | IN_MOVED_TO | IN_ONESHOT`** | First half of real same-parent rename yields named **`IN_MOVED_FROM`** with positive rename cookie, then `IN_IGNORED` | Full native **FROM and TO** rename pair with same positive cookie and original/destination names | **MOVED_TO is missing although explicitly subscribed**, because source half removed watch during the same operation |

These are real native Linux `inotify_init1` and `inotify_add_watch` registrations observing successful actual public filesystem operations on generated disposable `/tmp` fixtures. The companion independent inotify instance is created separately rather than through `dup`, and therefore has its own receipt queue and continuing event subscriptions. Successful Linux disposable kernel probes independently reproduced the two new source-close and combined-rename cases before drafting the regression tests.

Two distinct mechanisms can produce a partial inotify history: (1) a registration filter omits an event category in the first place (earlier DEC-1052/#1273, DEC-1054/#1275), and (2) `IN_ONESHOT` destroys a watch **after the first matching event** even when the mask includes *every relevant category* (the table above). The `IN_IGNORED` auto-removal record is retained and must not be dropped. A complete nominal watch mask, an event-count or `FIONREAD` counter, a real nonzero rename cookie, returned original bytes/permissions or restored final directory-name inventory cannot independently enforce protected no-write or retrospectively supply missing history.

The unchanged public evaluator remains **`status=BLOCKED`**, exact **`can_authorize_dispatch=false`** and **`independent_os_proof_verified=false`** on actual native unsafe records. A well-formed but otherwise quiet disposable receipt returns distinct **`LOCAL_DISPOSABLE_WITNESS_UNVERIFIED`** and remains nonauthorizing too. No source observer runtime change is proposed.

## Exact-head verification and immutable historical failures

- Latest individually **both-suite successful** exact-head checkpoint at document preparation: DEC-1062/#1283 at `ca27651cba97e014e254126d1a34f572e75e9762`, source-defined count **695** there. Both `phase3-acceptance` and full historical `tests` finished successfully at that SHA.
- DEC-1063/#1284, DEC-1064/#1285, DEC-1065/#1286, DEC-1066/#1287, DEC-1067/#1288 and **this doc-only child** each require their own completed successful Phase 3 **AND** full historical regression at their exact SHA, followed by separate qualified independent security review. At the last CI inspection, Phase 3 had passed #1284–#1287 but their historical runs remained active; #1288 had both suites in progress. Pending is not passed.
- Earlier original failed exact historical heads #1201–#1205, #1212, #1237 and #1261–#1267 remain permanently FAILED. A passing corrected descendant must not be used to rewrite any failed original.
- Every child stays **DRAFT / NEVER MERGE / NEVER PROMOTE**. The independently OS-enforced protected no-write gate DEC-650/#820 and immutable exclusive annual run385 admission gate DEC-651/#821/#779 remain **BLOCKED**.

No protected annual evidence/source, annual run385 execution/test/retry/rerun/dispatch, production workflows/refs/runners/rulesets/permissions changes, broker/trading operations, merges or promotions.
