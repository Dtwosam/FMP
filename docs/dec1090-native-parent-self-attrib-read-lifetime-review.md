# DEC-1090 — Parent self-event one-shot removal: read-only operations versus transient metadata mutation

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Documentation-only one-commit child of DEC-1089/#1310 at 9e21f33becdf30d3f60dd7d56f78656e8610d776. Adds one reviewer matrix, **712 source-defined test methods unchanged**. No executable code, observer runtime, protected annual environment, broker/trading or production updates.

## Distinguish harmless reads from metadata changes

| Case | First real operation on watched PUBLIC parent inode | Original alternative one-shot mask | Original one-shot receipt | Continuing independent observation | Later evidence lost by original |
| --- | --- | --- | --- | --- | --- |
| DEC-1082/#1303 | Read-only open of directory | OPEN plus parent write/namespace events with ONESHOT | Unnamed IN_OPEN|IN_ISDIR, then IN_IGNORED | Independent continuing parent OPEN receives same event | Actual later sample MODIFY/CLOSE_WRITE |
| DEC-1085/#1306 | Actual os.scandir directory enumeration | ACCESS plus parent write/namespace events with ONESHOT | Unnamed IN_ACCESS|IN_ISDIR, then IN_IGNORED | Independent continuing parent ACCESS receives same event | Actual later sample MODIFY/CLOSE_WRITE |
| DEC-1084/#1305 | Close a read-only directory FD | CLOSE_NOWRITE plus parent write/namespace events with ONESHOT | Unnamed IN_CLOSE_NOWRITE|IN_ISDIR, then IN_IGNORED | Independent continuing parent CLOSE_NOWRITE receives same event | Actual later sample MODIFY/CLOSE_WRITE |
| DEC-1087/#1308 | Single os.scandir operation, all benign read categories subscribed | OPEN + ACCESS + CLOSE_NOWRITE plus parent write/namespace events with ONESHOT | Only unnamed IN_OPEN|IN_ISDIR, then IN_IGNORED | Another native parent instance captures ordered OPEN, ACCESS, CLOSE_NOWRITE, all with IN_ISDIR | Actual later sample MODIFY/CLOSE_WRITE |
| **DEC-1089/#1310** | Actual chmod of watched directory mode, followed by a second chmod restoring mode | ATTRIB plus parent write/namespace events with ONESHOT | **Unnamed IN_ATTRIB|IN_ISDIR**, then IN_IGNORED, with no original receipt for reversal | Independent continuing source+parent sees **both** parent IN_ATTRIB|IN_ISDIR events, and later child writes | Actual later sample MODIFY/CLOSE_WRITE |

**Do not call chmod a no-write action.** OPEN, ACCESS and CLOSE_NOWRITE cases use non-mutating read workflows. The ATTRIB case performs **real metadata mutation** on a freshly generated disposable PUBLIC parent, then reverses it. The independently witnessed first and second ATTRIB events prove intervening metadata activity even when the final parent mode is identical. All five one-shot registrations are intentionally alternative unsafe test controls, not evidence that a production or actual helper watcher has disappeared.

All cases preserve the distinction between an **unnamed, IN_ISDIR-modified self event** on the watched directory inode and **named child events** on the parent from earlier sibling operations. IN_ISDIR is a modifier, not another primary event or a no-write proof. IN_IGNORED is proof that the **one-shot registration was removed**, not that the watched directory, its children or the filesystem were made immutable.

For DEC-1089, after original parent mode is restored, an independently instantiated continuing full source+parent native watcher captures actual source MODIFY/CLOSE_WRITE and named-parent MODIFY/CLOSE_WRITE for genuinely changed sample contents and for a separate genuine write restoring original PUBLIC sample bytes. Original parent one-shot remains silent; unchanged evaluator remains exactly status=BLOCKED, can_authorize_dispatch=false, independent_os_proof_verified=false. Final bytes/inode/mode/directory inventory cannot reconstruct the lost native event history.

## Scope and evidence admission

The actual unchanged helper scripts/dec677_disposable_inotify_events.py::_start_watch installs **continuing source+parent mutation watches without IN_ONESHOT** or the alternative read-only masks above. The DEC-1089 test creates only a deliberately alternative parent IN_ATTRIB|IN_ONESHOT registration and a separate independent normal watcher. These tests are local negative controls for inference from the lifetime and returned snapshots of an unsafe **hypothetical** registration; do not claim a new installed runtime defect.

Both exact-head Phase 3 acceptance and complete historical regression must finish successfully **on each individual commit**, followed by separate qualified independent security review. At writing #1308/DEC-1087 was the latest consecutive fully verified checkpoint with **711 tests**; historical CI for #1309 and both own suites for #1310/#1311 still require exact-head verification.

Previously failed original exact commits #1201–#1205, #1212, #1237 and #1261–#1267 remain FAILED. Independently OS-enforced protected no-write DEC-650/#820 and immutable exclusive annual run385 admission DEC-651/#821/#779 remain **BLOCKED**. All PRs stay DRAFT / NEVER MERGE / NEVER PROMOTE. No protected annual source/evidence, run385 execution/test/retry/rerun/dispatch, production refs/workflows/runners/rulesets/permissions, broker/trading operations, merges or promotions.
