# DEC-1041 — Full-state restoration is not evidence of continuous inotify observation

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit documentation-only child of DEC-1040/#1261. The source-defined test count remains **681**. No observer runtime, executable test, CI workflow, production ref, protected annual evidence/source, runner, ruleset, permission, broker or trading changes.

## Different native realities with identical final public snapshots

| Draft | Genuine disposable Linux test interval | Original source+parent inotify result | Independent second instance | Final public state and security interpretation |
| --- | --- | --- | --- | --- |
| DEC-1030/#1251 | Original source mask replaced via alias with `IN_OPEN` only; changed-byte source write | Same source WD emits `IN_OPEN`, source `IN_MODIFY` is suppressed; parent still reports named modifications | Genuine source+parent write records | Source WD continuity cannot certify source event mask continuity |
| DEC-1031/#1252 | Parent mask replaced with `IN_ATTRIB`; sibling created then deleted | Same parent WD, **no original parent events** for temporary sibling | Named sibling `IN_CREATE` and `IN_DELETE` | An identical final parent inventory cannot prove no intervening names |
| DEC-1037/#1258 | Queue sibling lifecycle before parent-mask replacement, then create another sibling during reduced mask | Old sibling CREATE/DELETE events remain readable, later sibling silent, no `IN_IGNORED`; same parent WD | Both sibling lifecycles recorded | Earlier valid events cannot guarantee completeness across a later changed mask |
| DEC-1038/#1259 | Replace **both** source and parent masks with `IN_ATTRIB), then WRITE source bytes and transient sibling during blackout; restore masks and finally source bytes afterward | **Empty original native queue** during real activity with same source+parent WDs, no `IN_IGNORED` | Genuine source `IN_MODIFY`, named parent write and sibling lifecycle | Source bytes remain changed until full native masks return; proves two-WD blind spot |
| **DEC-1040/#1261** | Replace **both** masks with `IN_ATTRIB`; real **BEFORE → AFTER → BEFORE** source writes plus create/delete sibling, all before restoring masks | **Empty original native queue** while both source and parent WDs remain unchanged, no `IN_IGNORED`; byte snapshot and inventory both ALREADY equal their starting values inside the blackout | At least two real source `IN_MODIFY`/`IN_CLOSE_WRITE` plus named parent modifications and sibling `IN_CREATE`/`IN_DELETE`; native direct probe observed 16 events | **All of final byte digest, one-name inventory, WD identity and locally quiet event queue can match the start** even though real writes and namespace changes occurred |

The entire experiment uses fresh, generated public disposable `/tmp` files, native Linux inotify instance/watches and real filesystem writes. Independent read-only witness receipts help demonstrate the original observer's blindness but are **not** independently OS-enforced protected write confinement. The controls inspect original dev/inode/mode, restored sample bytes, bounded final inventory and native FD closure.

For the superficially quiet empty buffer the unchanged evaluator returns **`status=LOCAL_DISPOSABLE_WITNESS_UNVERIFIED`**, not `BLOCKED`; genuinely observed unsafe buffers return `BLOCKED`. Both keep exact `can_authorize_dispatch=false` and `independent_os_proof_verified=false`. A trivially well-formed original **empty** event buffer alone cannot meet the missing independent OS no-write proof. Re-registering original watch masks on SAME WD values only resumes future observations; it never recovers earlier history. Do not forge/provide a fake empty receipt as proof, and do not treat test witness observations as protected policy.

## Exact-head CI and non-authorization gates

- The last confirmed fully verified green individual draft before this series was DEC-1039/#1260 at SHA `66fe18449dc56386af6b9a4d8f2162ecd3c50cc0`, which passed both Phase 3 and full historical regression.
- DEC-1040/#1261 at SHA `cc9216da30b8ae65bb94a7e184ec104b2190dd37` and this doc-only child must EACH independently pass completed exact-head Phase 3 and complete historical regression. At document preparation time, #1261 suites were running; **pending is not passed**. Qualified independent security review is a separate gate even if both suites are green.
- Original historical failures #1201–#1205, #1212 and #1237 remain FAILED regardless of descendant success. #1237's original failing job logs were unavailable and its root cause has not been established.
- Every PR remains **DRAFT / NEVER MERGE / NEVER PROMOTE**. Protected OS-enforced independent no-write DEC-650/#820 and exclusive immutable annual run385 admission DEC-651/#821/#779 remain **BLOCKED**.

No protected annual evidence/sources, annual run385 execution/test/retry/rerun/dispatch, production refs/workflows/runners/rulesets/permissions changes, broker/trading actions, merges, promotion or authorization.
