# DEC-1078 — Native one-shot benign read triggers: source and parent scope review

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict **documentation-only** one-commit child of DEC-1077/#1298 at `6a57ccea406f9eca0b2feb172c86811fa0b32fe4`. **705 source-defined tests unchanged.** No runtime, executable tests, production or protected-environment changes.

## Read-related first events versus later mutation history

| Trigger | Source one-shot case | Parent one-shot case | Event excluded to isolate trigger | One-shot result | Later independent mutation evidence |
| --- | --- | --- | --- | --- | --- |
| `IN_OPEN` | DEC-1069/#1290, sample read-only OPEN | DEC-1071/#1292, unrelated child `public-read` read-only OPEN | None: OPEN deliberately subscribed | Unnamed (source) or named `public-read` (parent) `IN_OPEN` then `IN_IGNORED` | Real subsequent sample MODIFY and CLOSE_WRITE on continuing source+named-parent witness |
| `IN_ACCESS` | DEC-1073/#1294, sample OPEN stays quiet, then actual read | DEC-1076/#1297, unrelated child OPEN stays quiet, then actual read | **IN_OPEN excluded** | Unnamed (source) or named `public-read` (parent) `IN_ACCESS` then `IN_IGNORED` | Real subsequent sample MODIFY and CLOSE_WRITE on continuing source+named-parent witness |
| `IN_CLOSE_NOWRITE` | DEC-1074/#1295, sample OPEN/read stay quiet, then read-only close | DEC-1077/#1298, unrelated child OPEN/read stay quiet, then read-only close | **IN_OPEN and IN_ACCESS excluded** | Unnamed (source) or named `public-read` (parent) `IN_CLOSE_NOWRITE` then `IN_IGNORED` | Real subsequent sample MODIFY and CLOSE_WRITE on continuing source+named-parent witness |

Each original one-shot registration includes `IN_MODIFY | IN_CLOSE_WRITE` and `IN_ONESHOT` together with its isolated benign read mask. The parent registrations additionally cover relevant directory entry actions such as CREATE/DELETE. Each test starts with newly generated **PUBLIC** disposable Linux `/tmp` fixtures and an **independently created, continuously registered native source+parent inotify** witness, never a duplicated/aliased FD. Independent source and named-parent MODIFY/CLOSE_WRITE events demonstrate that missing later mutations on the one-shot are due to **automatic removal on the first matching event**, not because the sample became read-only or those events never occurred.

The source and parent cases do **not** claim equal watch scope: an unrelated sibling's harmless read action affects a parent-wide one-shot registration that would otherwise observe `sample`, while source-only experiments consume the registration for the sample inode itself. `IN_IGNORED` is a positive watch-removal receipt, not a complete protected history. A restored final public digest, source/sibling/parent inode identity and mode, and bounded directory-name inventory cannot recover missed event provenance.

## Delimit actual observer scope and admission

These are deliberately alternative `IN_ONESHOT` registrations inside isolated tests. The actual helper `scripts/dec677_disposable_inotify_events.py::_start_watch` keeps continuing source+parent mutation watches and does **not** subscribe to the benign masks above or set IN_ONESHOT. No runtime defect in that deployed subscription is asserted by these comparisons. The unchanged evaluator stays exactly `status=BLOCKED`, `can_authorize_dispatch=false`, `independent_os_proof_verified=false` on genuinely independent unsafe native events; an otherwise quiet and coherent *local disposable* receipt remains `LOCAL_DISPOSABLE_WITNESS_UNVERIFIED` and is also nonauthorizing.

Every exact child must independently finish successful Phase 3 acceptance and complete historical regression at **its own commit SHA**, with separate qualified independent security review before any change of evidence classification. At this document's preparation #1294/DEC-1073 is the last consecutively confirmed both-suite green checkpoint; later drafts were still pending at their own heads. Earlier original failed exact commits #1201–#1205, #1212, #1237 and #1261–#1267 remain FAILED regardless of descendant CI. Independently OS-enforced protected no-write DEC-650/#820 and immutable exclusive annual run385 admission DEC-651/#821/#779 remain **BLOCKED**.

No protected annual source/evidence, annual run385 execution/test/retry/rerun/dispatch, production refs/workflows/runners/rulesets/permissions, broker/trading operations, merges or promotions.
