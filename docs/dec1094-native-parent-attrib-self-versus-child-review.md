# DEC-1094 — Directory-self versus named-sibling IN_ATTRIB: separate inodes, same one-shot lifetime loss

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict documentation-only single-commit child of DEC-1093/#1314 at `2617ea32168455e2511fb0670c5e2e3a73c6d5a2`. Exactly one Markdown reviewer matrix, **714 source-defined tests unchanged**. No executable, observer runtime, protected annual data, production or trading changes.

## Which inode actually caused the first matching parent watch event?

| Test | First actual disposable PUBLIC change | Original parent one-shot native record | Independently continuing witness | Later sample writes |
| --- | --- | --- | --- | --- |
| DEC-1089/#1310 | chmod the **watched parent directory inode itself**, then restore directory mode | **Unnamed** `IN_ATTRIB | IN_ISDIR`, then `IN_IGNORED` | Two native parent self `IN_ATTRIB | IN_ISDIR` events from change and reversal | Sample source and named-parent `IN_MODIFY` and `IN_CLOSE_WRITE` occur, but removed original sees none |
| DEC-1093/#1314 | chmod an **unrelated regular child public-sibling**, then restore sibling mode | **Named** `IN_ATTRIB` for `public-sibling`, without `IN_ISDIR`, then `IN_IGNORED` | Two native named parent `IN_ATTRIB` events on public-sibling from change and reversal | Genuine writes to **different child sample** are witnessed only by continuous source+parent instance |

The two operations both cause actual metadata mutation, not benign read events. The `IN_ISDIR` modifier and empty name on the self event distinguish the watched parent directory inode from a regular child; the child's basename in the other receipt identifies a different inode. Neither record is evidence of source content mutation, but each consumes the original **test-only** IN_ONESHOT parent watcher, which also subscribed to MODIFY, CLOSE_WRITE, CREATE and DELETE. The native `IN_IGNORED` event indicates automatic watch removal. It does not make the parent or child files read-only.

After a real chmod reversal, a separately initialized continuing source+parent native instance still records two subsequent genuine writes to `sample`, the second restoring original PUBLIC bytes. The original consumed one-shot reports no later write events, despite nominally containing those mutation categories in its initial mask. The unchanged evaluator returns exact `status=BLOCKED`, `can_authorize_dispatch=false`, `independent_os_proof_verified=false` on actual independent sample mutation receipts. Original bytes, modes, directory inventories and dev/inode identity cannot retrospectively prove that intervening events did not occur.

## Implementation and security scope

These examples install **alternative, deliberately unsafe parent IN_ONESHOT masks only inside isolated generated-PUBLIC Linux regressions**. The actual disposable helper `scripts/dec677_disposable_inotify_events.py::_start_watch` remains unmodified and uses continuing full source+parent mutation registrations, with **no IN_ONESHOT**. Do not infer that this intentional test-only watch lifetime loss is a deployed observer vulnerability or that an event-log-only observation satisfies OS-enforced protected no-write.

Every draft requires **both** successful completed exact-head Phase 3 acceptance and complete historical regression, followed by qualified independent security review. At document creation #1309/DEC-1088 was the latest consecutive fully verified draft with **711 source-defined tests**; exact-head historical CI for #1310/#1311/#1313/#1314 and the new child remains separately pending. #1312 has individually passed both suites but does not bypass pending ancestors. Earlier original failed exact commits #1201–#1205, #1212, #1237, and #1261–#1267 remain FAILED regardless of passing later children.

Independently OS-enforced protected no-write DEC-650/#820 and immutable exclusive annual run385 admission DEC-651/#821/#779 remain **BLOCKED**. All drafts stay NEVER MERGE / NEVER PROMOTE. No protected annual source/evidence, run385 execution/test/retry/rerun/dispatch, production refs/workflows/runners/rulesets/permissions, broker/trading actions, merges or promotions.
