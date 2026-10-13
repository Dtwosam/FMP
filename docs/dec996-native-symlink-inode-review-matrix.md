# DEC-996 — Native symlink-inode watch identity and exact-head CI handoff

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict documentation-only one-commit child of DEC-995/#1216. Adds **zero tests**, retaining **650 distinct source-defined methods** across the draft stack. No executable test, observer runtime, CI workflow, protected sources/evidence, production ref, runner, ruleset or permission change.

## Distinct kernel identity and observation controls

| Draft | Real disposable Linux event/registration behavior | Security interpretation |
| --- | --- | --- |
| DEC-974/#1195 | Default symlink watch follows a regular-file target; `IN_DONT_FOLLOW` watches the link inode itself | Path spelling and watched inode identity are separate |
| DEC-980/#1201 and DEC-985/#1206 | A directory-symlink watch without `IN_DONT_FOLLOW` attaches to the parent inode and sees deletion of its own alias entry as named `IN_DELETE` | An empty-queue expectation there was wrong; the repaired test must require the kernel event |
| DEC-986/#1207 | Followed parent survives alias unlink and continues reporting sibling entry activity; no-follow symlink watch emits `IN_DELETE_SELF` plus `IN_IGNORED` | Alias pathname loss does not invalidate a watch on the directory target |
| DEC-991/#1212 and DEC-992/#1213 | Create-only following the symlink clashes with the already-watched target (`EEXIST`); create-only no-follow selects the distinct link inode | A subsequent write via the alias is reported on the *resolved target* name `sample`, not on alias name |
| DEC-993/#1214 | Separate source+parent and link-inode inotify FDs independently confirm write-through-alias names `sample` while link watch is quiet | This rejects a false assertion about the parent event basename without sharing or silently filtering native WDs |
| DEC-994/#1215 | Dangling symlink default-follow create-only returns `ENOENT`; no-follow create-only succeeds on the existing symlink inode | A missing target and present symlink are different kernel inode facts |
| DEC-995/#1216 | A target file is created **after** a no-follow symlink watch was registered; parent reports target creation and write while link WD stays quiet | A link-inode watch cannot silently retarget when its formerly missing target materializes |

All controls create **public, generated, disposable files** in private `/tmp` directories, parse actual Linux inotify events and check watch identity, final filesystem state and FD closure. An inotify FD, WD number, correct native event parser, quiet queue, or later target creation is never independent OS-enforced write prevention or continuous provenance proof. The evaluator remains nonauthorizing: `status=BLOCKED` on real observed writes/invalidation, `can_authorize_dispatch=false`, and `independent_os_proof_verified=false` exactly.

## Exact commit results: no history rewriting

- **#1200 DEC-979** at `28ca006e2dc9fe4d91db28c1106a2e06e855b37e` was the last uninterrupted fully verified historical checkpoint before the failed series.
- **#1201–#1205 DEC-980–984** all have exact-head **FAILED** historical runs due to the original directory-alias unlink assertion. Their own Phase 3 success does **not** make them fully green.
- **#1206–#1211 DEC-985–990** passed both Phase 3 and full historical suites at their individual exact commits, but their success does not rewrite the earlier failed SHA history.
- **#1212 DEC-991** at `0bcc31e4168cb34136512f56c8a0625c9d9cc7f7` also **FAILED** full historical regression at its original incorrect alias-name assertion, despite Phase 3 success.
- **#1213 DEC-992** at `ab2a1318e707e61d4edc83c85eaa65b30337e5e9` is a new strict one-commit correction; it must pass its own exact-head suites. **#1214–#1216** and this doc-only child also require their own exact-head Phase 3 and complete historical regression; this document makes no claim that pending jobs have finished.
- Qualified independent security review remains a separate requirement even if all CI passes.

Protected independent OS-enforced no-write DEC-650/#820 and immutable exclusive annual run385 admission DEC-651/#821/#779 remain **BLOCKED**. No protected sources/evidence, annual run385 execution, test, dispatch, retry or rerun, production workflows/refs/runners/rulesets/permissions, broker/trading operations, merge, promotion or authorization.