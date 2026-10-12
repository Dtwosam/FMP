# DEC-983 — Native directory-follow, additive parent mask and per-instance creation review

**DRAFT / NEVER MERGE / NEVER PROMOTE.** This is a documentation-only strict one-commit child of DEC-982/#1203, retaining **642 distinct source-defined test methods**. No runtime, executable tests, workflows or protected assets are changed.

## Reviewer separation of identity, registration and observed events

| Control | Genuine disposable Linux operation | Native conclusion | Unsupported escalation |
| --- | --- | --- | --- |
| DEC-976/#1197 | IN_ONLYDIR and IN_DONT_FOLLOW reject a source regular file and directory-pointing symlink with ENOTDIR | A refused registration does not implicitly replace the existing two watch masks | Any claim that no writes can occur on those targets |
| DEC-980/#1201 | IN_ONLYDIR without IN_DONT_FOLLOW follows a directory symlink; a follow-up no-follow attempt rejects ENOTDIR | A live watch on the **directory target** sees sibling create and delete despite symlink spelling | That the symlink entry itself was watched or the parent write stream was exhaustive |
| DEC-970/#1191 | IN_OPEN | IN_MASK_ADD on a source WD preserves source MODIFY and CLOSE_WRITE | Additive source mask is distinct from replacement; unknown IN_OPEN records are rejected by the narrow observer | Filtering unknown events to produce a locally clean stream |
| DEC-981/#1202 | IN_OPEN | IN_MASK_ADD on a parent WD preserves CREATE, DELETE and named source write events | Opening the parent emits IN_OPEN | IN_ISDIR, and opening children emits named IN_OPEN; these are not accepted observer action masks | Treating unknown directory or child open events as no events |
| DEC-972/#1193 | IN_MASK_CREATE against already registered source/parent inodes returns EEXIST | Exclusivity applies when a watch already exists **in that instance** | Global ownership or kernel no-write protection |
| DEC-977/#1198 | First IN_MASK_CREATE on a fresh second instance succeeds, second attempt on that same inode fails EEXIST | A new source-only FD has a valid own WD but still lacks a parent watch | Retrospective observation or full dual watch coverage |
| DEC-982/#1203 | Two completely independent instances each first-create a watch on the SAME source inode with IN_MASK_CREATE; both then refuse their second attempt | The create-only constraint is per inotify instance, not global to an inode, and draining one FD does not consume the other | Exclusive independent OS admission, write denial or a global registration guarantee |

These controls use genuine kernel registrations/events on newly generated public samples under private /tmp directories. Watch descriptor equality, successful watch creation, a rejected watch request, a correctly parsed event stream, or a locally empty queue are not standalone proof of continuous event history or OS-enforced confinement. The unchanged evaluator must not grant authority; it returns BLOCKED for true write events, unsupported native masks or missing required watch coverage. Both can_authorize_dispatch=false and independent_os_proof_verified=false remain exact.

Each draft head, including this document-only child, must have its own successful exact-head Phase 3 and complete historical regression. Successful downstream CI never rewrites an earlier failed head. Qualified independent security review and actual OS-enforced protected no-write are separate requirements, not satisfied by these public Linux experiments.

Protected OS no-write DEC-650/#820 and immutable exclusive annual run385 admission DEC-651/#821/#779 remain **BLOCKED**. No protected source/evidence access, annual run385 dispatch/test/retry/rerun, production refs/workflows/runners/rulesets/permissions, broker/trading operations, merges, promotions or authorization.