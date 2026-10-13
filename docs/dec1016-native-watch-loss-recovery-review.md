# DEC-1016 — Manual inotify watch loss, re-registration and non-recoverable gap

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict documentation-only one-commit child of DEC-1015/#1236. This keeps **664 distinct source-defined test methods** unchanged and makes no executable observer, test, CI workflow, protected evidence/source, production configuration, runner, ruleset, permission or trading change.

## Reviewer distinction: explicit watch loss is not source write prevention

| Control | Native generated-public Linux action | Actual expected event evidence | What must not be inferred |
| --- | --- | --- | --- |
| DEC-968/#1189 | Real source `IN_ONESHOT` auto-removal after first subscribed event | Source watch eventually auto-generates `IN_IGNORED` | One-shot queue silence after disarm means the source stayed unwritten |
| DEC-969/#1190 | Real parent `IN_ONESHOT` auto-removal | Parent `IN_IGNORED` while source and external activity can continue | Parent directory census is still complete after auto-disarm |
| DEC-1014/#1235 | Native `inotify_rm_watch(source_wd)` on first of two independent source+parent instances, followed by real write | First FD: source `IN_IGNORED`, then genuine named parent `IN_MODIFY` but no source record; second FD: genuine dual source/parent writes | Source subscription was live throughout because parent remained live |
| DEC-1014/#1235 | Remove first FD's remaining parent WD and write source again | First FD: parent `IN_IGNORED` then **empty queue**. Second independent FD: real source/parent write records | Empty first queue proves no file activity or no-write enforcement |
| DEC-1015/#1236 | Remove source WD, write during gap, and re-add watch to **same inode on same FD** | Actual source `IN_IGNORED`, parent-only named write during gap, **new source WD** after re-add, new source plus parent events on a later restore | New WD registration retroactively fills an earlier observation gap or proves continuous historical watch identity |

The tests create only disposable generated-public files under private `/tmp`, exercise actual native inotify operations and event buffers, and check restored source bytes, final source/parent dev/inode/mode, bounded directory inventory and FD closure. A local kernel probe separately reproduced explicit `IN_IGNORED`, actual parent-only writes during the missing-source gap and distinct newly registered WD. Those facts are direct kernel observations but are not independently OS-enforced protected no-write guarantees, retrospective audit proof, exclusive annual admission or broker/trading approval.

The unchanged observer must reject missing/invalidated/unknown original WDs or real write evidence: `status=BLOCKED`, `can_authorize_dispatch=false`, `independent_os_proof_verified=false` exactly. A later valid subscription does not turn its earlier unattested interval into proof.

## Exact-head CI and protected boundaries

DEC-1013/#1234 at `87842d56f1abcea9c6fdb618e0dd0032935a7d86`, DEC-1014/#1235 at `e2a1fa663d14fd7b523791749593517daf3b9cb0`, DEC-1015/#1236 at `b68105557a7993b3839274d2d89264731b8721be`, and this documentation-only child must each pass **their own Phase 3 AND complete historical regression at their exact SHA** before a fully verified label. Do not credit a descendant's success to an unverified ancestor. Prior original exact heads #1201–#1205 and #1212 retain their FAILED historical results regardless of later successful descendants. Qualified independent security review remains mandatory even for CI-green experiments.

Protected OS-enforced independent no-write DEC-650/#820 and immutable exclusive annual run385 admission DEC-651/#821/#779 remain **BLOCKED**. No protected sources/evidence access, annual run385 execution/test/retry/rerun/dispatch, production workflows/refs/runners/rulesets/permissions, broker/trading operation, merge, promotion or authorization.