# DEC-1105 — Same-mode chmod one-shot scope: watched file versus watched directory

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict documentation-only one-commit child of DEC-1104/#1325 at `66219762e689f2cf057503a4e07d1119f19db450`. Adds one reviewer matrix, leaves **720 source-defined tests unchanged**. No observer runtime, source code, protected annual evidence, production, broker or trading changes.

## Identical permission bits; different native event identity

| Case | Actual first action on generated PUBLIC /tmp fixture | Alternative original IN_ONESHOT watch | Original event before removal | Independent continuing source+parent observation | Later genuine writes original misses |
| --- | --- | --- | --- | --- | --- |
| DEC-1102/#1323 | `os.chmod(sample, stat.S_IMODE(os.lstat(sample).st_mode))` on **source regular-file inode** | Source-only IN_ATTRIB+MODIFY+CLOSE_WRITE | **Unnamed source IN_ATTRIB**, then **IN_IGNORED** | **Unnamed source IN_ATTRIB** and **named parent IN_ATTRIB(sample)** for both original and a second same-mode chmod | Real source MODIFY/CLOSE_WRITE and named-parent MODIFY/CLOSE_WRITE on changed and restoring sample writes |
| DEC-1104/#1325 | `os.chmod(parent, stat.S_IMODE(os.lstat(parent).st_mode))` on **watched parent directory inode** | Parent-only IN_ATTRIB+MODIFY+CLOSE_WRITE+CREATE+DELETE+ONLYDIR | **Unnamed parent IN_ATTRIB|IN_ISDIR**, then **IN_IGNORED** | **Unnamed parent IN_ATTRIB|IN_ISDIR** for both original and a second same-mode chmod; source-file observer remains quiet | Real source MODIFY/CLOSE_WRITE and named-parent MODIFY/CLOSE_WRITE on changed and restoring sample writes |

Both actual chmod calls supply permission bits already present before the call. **Do not claim full metadata neutrality**: ctime or other metadata may change, and `IN_ATTRIB` is a genuine kernel event even when mode bits remain equal. They are not byte-changing content writes. The source event carries no name, and its parent counterpart carries the **regular child name**. The directory self event is unnamed and carries the `IN_ISDIR` modifier, which is not an additional primary action. Both original intentionally unsafe IN_ONESHOT registrations lose all later coverage after `IN_IGNORED`, even though the watched inode still exists and file modes appear unchanged.

The full normal source+parent observer is independent from each original one-shot. It positively witnesses the attribute event(s) and later real sample writes. The unchanged evaluator on independent genuine sample content modification stays exactly `status=BLOCKED`, `can_authorize_dispatch=false`, and `independent_os_proof_verified=false`. Final identical original PUBLIC file bytes, modes and directory inventory cannot establish a complete event history or an independently OS-enforced no-write guarantee.

## Runtime distinction, exact-head CI, and immutable admission

The deliberate alternative unsafe IN_ONESHOT masks are installed in disposable regression code only. The actual unchanged helper `scripts/dec677_disposable_inotify_events.py::_start_watch` uses continuing source+parent mutation watches, **not IN_ONESHOT**. Neither control proves a deployed observer runtime defect, protected OS confinement, or immutable annual authorization.

Each PR needs its own successful completed **exact-head** Phase 3 acceptance and full historical regression plus separate qualified independent security review. At document preparation #1320/DEC-1099 was the last consecutive fully green draft, with **717 source-defined tests**, while #1323 was individually green but intervening #1321–#1322 were still pending. This new docs-only head likewise must pass both suites and must not inherit status from ancestors or descendants.

Earlier original FAILED commits #1201–#1205, #1212, #1237 and #1261–#1267 stay FAILED. Independently OS-enforced protected no-write DEC-650/#820 and immutable exclusive annual run385 admission DEC-651/#821/#779 remain **BLOCKED**. Keep every draft DRAFT / NEVER MERGE / NEVER PROMOTE. No protected annual source/evidence, annual run385 execution/test/retry/rerun/dispatch, production refs/workflows/runners/rulesets/permissions, broker/trading operations, merges or promotions.
