# DEC-1061 — Parent inode versus child-directory IN_ISDIR one-shot review

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict documentation-only child of DEC-1060/#1281. This child adds NO executable test and the stack stays at **694 source-defined methods**. Only one Markdown file; no source observer runtime, protected source/evidence, production workflow/ref/runner/ruleset/permission, broker or trading mutation.

## Different native IN_ISDIR meanings on one parent watcher

| Test | Real disposable public operation | Parent-only IN_ONESHOT kernel buffer | Independent live source+parent watcher | What changes afterward |
| --- | --- | --- | --- | --- |
| DEC-1055/#1276 | Rename sibling **directory** `public-alpha/ → public-beta/` | Named `IN_MOVED_FROM | IN_ISDIR` with positive cookie, then `IN_IGNORED` | Full directory `IN_MOVED_FROM | IN_ISDIR` and `IN_MOVED_TO | IN_ISDIR` with matching positive cookie | One-shot misses the destination half and all later renames |
| DEC-1056/#1277 | Rename sibling directory, but register `IN_MOVED_TO | IN_ONESHOT` | Named `IN_MOVED_TO | IN_ISDIR` with positive cookie, then `IN_IGNORED` | Complete native FROM/TO directory pair with same cookie | One-shot misses the source half and later rename history |
| DEC-1058/#1279 | `chmod` watched **parent directory inode** after actual nonmatching child writes | **Unnamed** `IN_ATTRIB | IN_ISDIR`, then `IN_IGNORED` | True parent inode ATTRIB|ISDIR; child sample writes separately recorded | Original parent permission mode restored, but original one-shot does not observe the restoration |
| **DEC-1059/#1280** | `mkdir` new sibling **directory entry** after two nonmatching sample writes | **Named** `IN_CREATE | IN_ISDIR`, then `IN_IGNORED` | Named CREATE|ISDIR and subsequent DELETE|ISDIR on actual rmdir | One-shot misses rmdir and another real mkdir/rmdir cycle |
| **DEC-1060/#1281** | `rmdir` preexisting disposable sibling **directory entry** after two nonmatching sample writes | **Named** `IN_DELETE | IN_ISDIR`, then `IN_IGNORED` | Named DELETE|ISDIR, plus subsequent CREATE|ISDIR/DELETE|ISDIR/CREATE|ISDIR on later real operations | The same disposable name can be recreated with a NEW inode; initial/final inventory equality does not certify identity or no writes |

A source-only regular-file `IN_MODIFY | IN_ONESHOT` and a source-only `IN_ATTRIB | IN_ONESHOT` remain separate controls: here all first one-shot watches are parent **directory inode** registrations. `IN_ONLYDIR` is a registration option requiring the watched path to be a directory; **`IN_ISDIR` is an event modifier** describing a directory entry for named child namespace operations, or describing the watched directory inode itself for unnamed parent metadata events. None of these event type modifiers proves the independent OS no-write policy.

All controls use only freshly generated PUBLIC disposable Linux `/tmp` fixtures and actual native syscalls and complete event-buffer decoding. The independent full watcher is a *different* native inotify instance, never just `dup()` of the original one-shot FD. Native disposable probes independently confirmed the new genuine mkdir and rmdir event sequences. Test fixtures restore public sample bytes and sample+parent dev/inode/mode, verify bounded directory inventory and close all kernel FDs. DEC-1060 intentionally does NOT assert that a deleted and recreated sibling directory has its earlier inode.

The unchanged evaluator remains `status=BLOCKED` with exact `can_authorize_dispatch=false` and `independent_os_proof_verified=false` for actual independently observed unsafe write and namespace activity. Syntactically valid quiet disposable receipts without protected proof instead have distinct nonauthorizing `LOCAL_DISPOSABLE_WITNESS_UNVERIFIED` status. Neither result constitutes annual authorization, and no runtime implementation changes are proposed.

## Exact-head CI and protected-operation gates

- Last confirmed individually two-suite CI-verified draft before this series: DEC-1054/#1275 at exact SHA `f916bd2830e35819ae0091f619335e4886a9bc74` (**Phase 3 and full historical successful**).
- DEC-1055/#1276, DEC-1056/#1277, DEC-1057/#1278, DEC-1058/#1279, DEC-1059/#1280 and DEC-1060/#1281 **each require their own** successful Phase 3 AND complete historical suites. At document creation, #1276–#1280 had individually passed Phase 3 but still had historical runs in progress. Both suites for #1281 were in progress. This doc-only child also needs its own exact-head two-suite success. Do not classify a running check as green.
- Failed original exact historical commits #1201–#1205, #1212, #1237 and #1261–#1267 remain FAILED regardless of successful descendants or later repairs. Qualified independent security review is an additional gate after CI.

Every PR remains **DRAFT / NEVER MERGE / NEVER PROMOTE**. Independent protected OS-enforced no-write DEC-650/#820 and immutable exclusive annual run385 admission DEC-651/#821/#779 remain **BLOCKED**. No protected annual evidence/source, run385 execution/test/retry/rerun/dispatch, production refs/workflows/runners/rulesets/permissions changes, broker/trading actions, merges or promotion.
