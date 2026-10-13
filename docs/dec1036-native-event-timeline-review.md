# DEC-1036 — Native inotify event-timeline boundary and watch-loss reviewer matrix

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit documentation-only child of DEC-1035/#1256. No executable test, observer runtime, CI workflow, protected evidence/source, production ref, runner, ruleset, permission, broker or trading change. The stack remains at **678 source-defined test methods**.

## Compare actual queued-event ordering with later observation gaps

| Regression | Exact sequence on newly generated disposable public `/tmp` paths | Native kernel event evidence | Reviewer failure mode |
| --- | --- | --- | --- |
| DEC-1030/#1251 | Replace original SOURCE mask through dup with `IN_OPEN` only, then perform real changed-byte write | Original source WD stays SAME number and emits `IN_OPEN`, but lacks actual source `IN_MODIFY`/`IN_CLOSE_WRITE`. Parent and independent second instance observe writes | WD continuity is not source write-event coverage |
| DEC-1031/#1252 | Replace original PARENT mask with `IN_ATTRIB` only, then create/unlink a real sibling | Parent WD stays SAME number, first/dup queue empty, independent parent reports `IN_CREATE`/`IN_DELETE` | Empty source-only or parent-only queue and restored final inventory are not complete namespace provenance |
| DEC-1033/#1254 | Queue real source changed-byte write under intact masks; BEFORE draining, remove original SOURCE WD through dup | Original source `IN_MODIFY` and `IN_CLOSE_WRITE` precede native source `IN_IGNORED` in same complete buffer. Later real writes are parent-only | Discarding earlier queued writes because the watch was subsequently removed loses actual evidence |
| DEC-1034/#1255 | Queue real sibling create+unlink before removing original PARENT WD through dup | Parent `IN_CREATE` precedes `IN_DELETE`, both before parent `IN_IGNORED`. Later sibling activity is silent on first instance, visible on separate second observer | Ignoring the queued real parent record history or inferring later no activity from first quiet queue |
| DEC-1035/#1256 | Queue real SOURCE write before replacing SOURCE mask with `IN_OPEN` via dup, write again during reduced mask, then restore full mask | Earlier genuine source `IN_MODIFY`/`IN_CLOSE_WRITE` remain queued with SAME WD and **without `IN_IGNORED`**; during reduced mask later source writes lack those actions, parent/independent remain active. Restoring mask does not replay lost events | Presence of valid old source records and unchanged WD must not imply continuity across a later silent mask interval |
| DEC-1015/#1236 and DEC-1017/#1238 | Explicitly remove original source or parent watch; later re-register same inode | Original WD receives `IN_IGNORED`; replacement WD sees only NEW actions, not the missing interval | Re-registration creates no retroactive immutable provenance |

The test implementation uses actual `inotify_init1`/`inotify_add_watch`/`inotify_rm_watch`, public inode writes or disposable sibling lifecycle and parses whole native event buffers. Both the source+parent original subscriptions and a genuinely independent second inotify instance supply event contrasts; an `os.dup` FD is a shared alias of the original, not an independent observer. Full byte snapshots and source/parent dev/inode/mode and bounded inventory are checked at the end; all native FDs close. Native disposable probes independently reproduced the newly introduced queued-event cases before tests were drafted.

**Kernel event timelines are not protected confinement.** `IN_IGNORED`, its absence, a quiet queue, the same numeric WD, a restored subscription mask, and restored byte content each fail to prove independently OS-enforced protected no-write or exclusive annual admission. The unchanged evaluator must remain `status=BLOCKED`, exact `can_authorize_dispatch=false` and `independent_os_proof_verified=false`, on real unsafe streams. Qualified independent security review is a separate requirement.

## Individually pinned CI, unchanged failures, and protected boundaries

- DEC-1032/#1253 at exact SHA `9844c948ee53919d03ac9e71f520fe72c6d7ab0e` and DEC-1033/#1254 at `67b2569d498678f07340f0f67dc2d6b1570e49fc` each passed both required exact-head **Phase 3** and **full historical regression**.
- DEC-1034/#1255, DEC-1035/#1256 and this documentation-only child **each require their own** successful exact-head Phase 3 AND complete historical suite before being called individually fully verified. Phase 3 success of an ancestor or historical success of a descendant does not certify another exact SHA.
- Original failed exact historical commits #1201–#1205, #1212 and #1237 remain **FAILED** regardless of later green descendants. DEC-1016/#1237's failed historical run `38420457581` returned an unavailable original job log archive; its cause is **not established**.
- Every draft is **DRAFT / NEVER MERGE / NEVER PROMOTE**, even if its own CI is green. Independently OS-enforced protected no-write DEC-650/#820 and immutable exclusive annual run385 admission DEC-651/#821/#779 stay **BLOCKED**.

No protected annual sources/evidence, run385 execution/test/retry/rerun/dispatch, production workflows/refs/runners/rulesets/permissions changes, broker/trading operations, merge, promotion or authorization.
