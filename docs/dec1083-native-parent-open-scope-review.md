# DEC-1083 — Parent one-shot OPEN source: distinguish watched directory self-event from child activity

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict documentation-only one-commit child of DEC-1082/#1303 at 26d9237973b87c3b4745df6d6448f7edb614766b. One new Markdown reviewer matrix; **708 source-defined tests unchanged**. No source code, executable tests, observer runtime, production, protected environment, broker/trading or annual runner changes.

## Native parent OPEN first-trigger scope

| Case | Real first filesystem operation | Original parent one-shot record | Independent continuing OPEN witness | Real activity missing afterwards |
| --- | --- | --- | --- | --- |
| DEC-1071/#1292 | Read-only open of *unrelated public child* public-read | **Named child IN_OPEN**, then IN_IGNORED | Earlier regression independently confirms benign operation and continuously registered full source+parent later mutations | Subsequent real sample writes and writable closes |
| DEC-1080/#1301 | Read-only open, read and close of unrelated public child under a **combined OPEN+ACCESS+CLOSE_NOWRITE** one-shot mask | **Named child IN_OPEN**, then IN_IGNORED; subscribed ACCESS and CLOSE_NOWRITE lost | Separate continuing parent read instance records all **named** OPEN, ACCESS, CLOSE_NOWRITE | Subsequent genuine sample MODIFY and CLOSE_WRITE, recorded by third independent source+parent instance |
| **DEC-1082/#1303** | Read-only **O_DIRECTORY open of the watched parent inode itself**, not any child | **Unnamed IN_OPEN with IN_ISDIR modifier**, then IN_IGNORED | Separate continuing parent OPEN instance records the same **unnamed IN_OPEN|IN_ISDIR** | Subsequent genuine child sample MODIFY and CLOSE_WRITE, recorded by third independent source+parent instance |

**Watch identity matters.** The parent inode generates an unnamed IN_OPEN record flagged IN_ISDIR when its own directory file descriptor is opened. Opening a child generates a named IN_OPEN for that entry. Both trigger the first-match automatic removal of an alternative parent IN_ONESHOT watch. The IN_ISDIR bit is a *directory modifier* on the real OPEN event, not an extra action, an actual child directory creation, or an authorization token. Do not relabel an unnamed self-event as a named child event, or use the subsequent IN_IGNORED to imply future no-write confinement.

**Observed mutations are independent.** In each test, a full continuing source+parent native inotify witness records successful changed-byte sample MODIFY and writable close events after the original one-shot has been removed. Returning to identical original PUBLIC bytes, source and parent dev/inode/mode, and stable final bounded inventory cannot recover missing event history. All operations are isolated to freshly generated disposable PUBLIC Linux /tmp fixtures.

**Do not overstate production scope.** These alternative native one-shot experiments explicitly include benign read event subscriptions to stress unsafe *hypothetical* coverage inference. The real, unchanged disposable observer scripts/dec677_disposable_inotify_events.py::_start_watch uses continuing full source+parent mutation watches without IN_ONESHOT or these read event subscriptions. The real evaluator remains exact status=BLOCKED, can_authorize_dispatch=false, independent_os_proof_verified=false for independently witnessed unsafe records; coherent quiet local receipts remain LOCAL_DISPOSABLE_WITNESS_UNVERIFIED and also nonauthorizing.

## CI provenance and protected admission

At this document's preparation, #1300/DEC-1079 was the latest consecutively fully verified exact-head draft, with 706 source-defined tests. #1301–#1303 require their individual exact-head completed successful Phase 3 and complete historical regression, and **this** docs-only child requires both as well. Passing a draft's CI is not a substitute for a qualified independent security review or OS enforced confinement.

Earlier original failed exact commits #1201–#1205, #1212, #1237, and #1261–#1267 must remain FAILED. Independently OS-enforced protected no-write DEC-650/#820 and immutable exclusive annual run385 admission DEC-651/#821/#779 remain **BLOCKED**.

All PRs stay DRAFT / NEVER MERGE / NEVER PROMOTE. No protected annual source/evidence, run385 execution/test/retry/rerun/dispatch, production refs/workflows/runners/rulesets/permissions, broker/trading actions, merges or promotions.
