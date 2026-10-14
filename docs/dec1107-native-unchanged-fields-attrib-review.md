# DEC-1107 — IN_ATTRIB when supplied permissions or timestamps already match

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict documentation-only one-commit child of DEC-1106/#1327 at `eb1216c3a40ce3091b0664f2cae9fb80f7884583`. One new Markdown reviewer matrix and **721 source-defined tests unchanged**. No executable observer, production, protected annual evidence, broker/trading or helper runtime changes.

## Which originally equal inode fields are explicitly re-submitted?

| Case | Actual first PUBLIC Linux syscall | Equality asserted in test | Original intentionally unsafe IN_ONESHOT receipt | Independent continuing source+parent native witness | Subsequent true sample content change |
| --- | --- | --- | --- | --- | --- |
| DEC-1102/#1323 | `chmod(sample, current_mode)` on watched regular-file **source** | Source permission bits remain original; bytes unchanged | **Unnamed source IN_ATTRIB**, then **IN_IGNORED** | Unnamed source IN_ATTRIB + named parent IN_ATTRIB(sample), including a second same-mode call | Real source MODIFY/CLOSE_WRITE and named parent MODIFY/CLOSE_WRITE occur but are missed by original source one-shot |
| DEC-1104/#1325 | `chmod(parent, current_mode)` on watched **directory inode** | Parent permission bits remain original; child bytes unchanged | **Unnamed parent IN_ATTRIB|IN_ISDIR**, then **IN_IGNORED** | Unnamed parent IN_ATTRIB|IN_ISDIR for each of two same-mode calls | Real child source and named-parent MODIFY/CLOSE_WRITE occur but are missed by original parent one-shot |
| **DEC-1106/#1327** | `utime(sample,ns=(old_atime_ns,old_mtime_ns))` on watched regular-file **source** | **Both nanosecond atime and mtime** remain exactly original immediately after call; bytes unchanged | **Unnamed source IN_ATTRIB**, then **IN_IGNORED** | Unnamed source IN_ATTRIB + named parent IN_ATTRIB(sample) for each of two same-timestamps calls | Real source and named-parent MODIFY/CLOSE_WRITE occur but are missed by original source one-shot |

**Do not overclaim no metadata mutation.** Although the target permission bits or atime/mtime values match the pre-call values, a real chmod or utime can update ctime or other kernel-managed metadata. These tests prove the behavior of native inotify on actually executed syscalls with **selected original values preserved**, not overall metadata neutrality. A native IN_ATTRIB event is not itself proof of byte mutation; a native IN_CLOSE_WRITE is not itself proof that a write() changed bytes. Actual changed-byte calls and independent source+parent MODIFY+CLOSE_WRITE receipts are used to demonstrate later mutations.

The `IN_ISDIR` modifier identifies the watched directory **self** event, not a second action or a named child. Both regular source inode cases generate **unnamed** events on the original source-only watch and **named** IN_ATTRIB(sample) on the continuing independent parent watch. Each original one-shot ends with IN_IGNORED; preserving final selected field values or restoring original PUBLIC bytes does not rearm it or reconstruct intervening file event history.

## Exact-head evidence versus protected authorization

The actual unchanged helper `scripts/dec677_disposable_inotify_events.py::_start_watch` uses **continuing source+parent mutation watches**, not the deliberately unsafe alternative IN_ONESHOT event subscriptions installed only by these generated-PUBLIC Linux tests. They do **not** demonstrate an installed runtime defect or independently OS-enforce protected no-write.

The unchanged evaluator on genuinely witnessed unsafe source mutation returns exact `status=BLOCKED`, `can_authorize_dispatch=false`, `independent_os_proof_verified=false`. Each distinct draft needs both its own exact-head `phase3-acceptance` and full historical `tests` workflow `completed/success`, plus qualified independent security review. At review preparation #1320/DEC-1099 remained the last **consecutive** both-suite fully CI-verified head with **717 source-defined tests**, while #1323 individually passed both and #1321/#1322 historical CI remained pending.

Failed original exact commits #1201–#1205, #1212, #1237 and #1261–#1267 remain FAILED irrespective of later descendants. Independently OS-enforced protected no-write DEC-650/#820 and immutable exclusive annual run385 admission DEC-651/#821/#779 stay **BLOCKED**. All PRs remain DRAFT / NEVER MERGE / NEVER PROMOTE. No protected annual source/evidence, run385 execution/test/retry/rerun/dispatch, production refs/workflows/runners/rulesets/permissions, broker/trading, merges or promotions.
