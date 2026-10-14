# DEC-1103 — Snapshot equality versus native first-event provenance

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit **documentation-only** child of DEC-1102/#1323 at `cc12b023142a691d5cbd5010d817a8ee55093c12`. Exactly one Markdown reviewer matrix, **719 source-defined test methods unchanged**. No executable regression, helper runtime, protected annual, production, broker or trading changes.

## Different first events can leave the reviewed fields apparently unchanged

| Regression | Real first operation on generated PUBLIC fixture | Fields intentionally unchanged | Original test-only one-shot receipt | Independently continuing source+parent witness | Later real events original misses |
| --- | --- | --- | --- | --- | --- |
| DEC-1098/#1319 | O_WRONLY open+close of **unrelated sibling**, no O_TRUNC/write/fsync | **Sibling bytes/size**, final inode/mode | **Named parent IN_CLOSE_WRITE(public-sibling)**, then IN_IGNORED; no MODIFY | Named parent CLOSE_WRITE without sibling MODIFY | Genuine later **different child sample** source and named-parent MODIFY+CLOSE_WRITE |
| DEC-1100/#1321 | O_WRONLY open+close of **watched sample source**, no O_TRUNC/write/fsync | **Source bytes/size**, final inode/mode | **Unnamed source IN_CLOSE_WRITE**, then IN_IGNORED; no MODIFY | Unnamed source and named-parent CLOSE_WRITE(sample) without MODIFY | Genuine later **same source inode** source and named-parent MODIFY+CLOSE_WRITE |
| **DEC-1102/#1323** | Actual chmod of **watched sample source**, explicitly passing already existing permission bits | **Source permission bits**, source bytes/size, final inode/mode | **Unnamed source IN_ATTRIB**, then IN_IGNORED; no MODIFY | Unnamed source and named-parent IN_ATTRIB(sample) for first and second same-mode chmod | Genuine later **same source inode** source and named-parent MODIFY+CLOSE_WRITE |

**Precision about what did not change:** An opened-for-writing file descriptor can close with IN_CLOSE_WRITE even when no content bytes were written. IN_CLOSE_WRITE alone does **not** establish a content mutation. A same-mode chmod can generate native IN_ATTRIB despite leaving the **permission bits** unchanged; it may change ctime or other metadata. Do **not** claim that the same-mode chmod is metadata-neutral or that the first event is an actual content write. Distinguish the event category, watched inode, modified fields, and complete native operations.

For each regression, the **original alternative IN_ONESHOT registration** is removed by its first matching event, confirmed by IN_IGNORED. A completely independent continuously registered native source+parent watcher records the genuine first event and later real changed-byte sample writes and writable closes, including a real write restoring the original PUBLIC bytes. The unchanged evaluator on actual independent unsafe source write receipts remains `status=BLOCKED`, `can_authorize_dispatch=false`, `independent_os_proof_verified=false`. A final original digest, file mode and directory-name inventory cannot prove no intervening writes or reconstitute the removed watch.

## Scope and admission

The real `scripts/dec677_disposable_inotify_events.py::_start_watch` remains unchanged and uses **continuing source+parent mutation watches without IN_ONESHOT**. All one-shot configurations above are deliberately **alternative unsafe registrations used only in disposable tests**. These examples cannot establish a deployed helper defect, independently OS-enforced protected no-write confinement, or immutable annual admission.

Both required exact-head workflows, **phase3-acceptance and tests**, must finish `completed/success` on each individual commit, followed by qualified independent security review. At writing #1320/DEC-1099 was the latest consecutive both-suite successful draft (717 source-defined tests); #1321–#1324 require their own exact-head CI. Previously failed original commits #1201–#1205, #1212, #1237 and #1261–#1267 stay FAILED regardless of later successes.

Independently OS-enforced protected no-write DEC-650/#820 and immutable exclusive annual run385 admission DEC-651/#821/#779 remain **BLOCKED**. Keep every child DRAFT / NEVER MERGE / NEVER PROMOTE. No protected annual source/evidence, run385 execution/test/retry/rerun/dispatch, production refs/workflows/runners/rulesets/permissions, broker/trading operations, merges or promotions.
