# DEC-987 — Exact-head historical failure ledger and native alias-event repair handoff

**DRAFT / NEVER MERGE / NEVER PROMOTE.** One-commit documentation-only child of DEC-986/#1207. No observer runtime, executable tests, workflows, protected assets or production code changed; **644 distinct source-defined methods** remain.

## Failure chronology: do not erase red exact SHAs

The following exact historical `tests` workflow runs **completed with failure**, even though the respective `phase3-acceptance` runs completed successfully. This is not a transient queue state, and downstream success must never rewrite these failures.

| Draft | Exact commit | Historical CI run | Finding |
| --- | --- | --- | --- |
| DEC-980/#1201 | `adae3f1364d76b781af631573f48ec4928a78475` | `38320037012` | Failed at `test_dec980_native_onlydir_symlink_follow.py:156` |
| DEC-981/#1202 | `ea5c6d2fbb22b1b8642f843bd0334e10d9b426d5` | `38320145357` | Same inherited assertion failure |
| DEC-982/#1203 | `87a1bac5c3a2a455063de4b3049de1a830f4ae54` | `38320241625` | Same inherited assertion failure |
| DEC-983/#1204 | `764c5f98bda7b9c2765b751804e380a4eee168f2` | `38320323176` | Same inherited assertion failure |
| DEC-984/#1205 | `0a43d8d86e1711ed6fc16967ca7174cd1a6ff09b` | `38320484237` | Same inherited assertion failure |

The common failed assertion expected an empty inotify queue after removing the temporary symlink used to register a *followed parent directory* watch. A watch created with `IN_ONLYDIR` but without `IN_DONT_FOLLOW` follows the alias to the actual parent directory inode. Deleting the alias removes a directory entry **inside that still-watched directory**, so Linux correctly emits a named `IN_DELETE` record. This was a mistaken test expectation, not a reason to silence a real event or modify the production/runtime guard.

## Strict draft repair lineage and acceptance gates

- **#1200 DEC-979**, `28ca006e2dc9fe4d91db28c1106a2e06e855b37e`: last verified *contiguous* checkpoint, both required suites passed.
- **#1206 DEC-985**, `51a9070fd944e39b5b5dce757f77517b9bf0aa9b`: repairs the historical assertion to require the native followed-parent `IN_DELETE` named `public-parent-alias`; retains existing checks. This SHA must itself pass **both** exact-head Phase 3 and full historical regression.
- **#1207 DEC-986**, `0c1b80728d81bec3232ece86a552133f82d0f3f9`: distinct public Linux control comparing (a) followed parent survival and post-alias-unlink sibling events with (b) true no-follow symlink inode `IN_DELETE_SELF` plus `IN_IGNORED`. It needs its **own** two-suite exact-head CI.
- **This doc-only child**: equally requires both its own suites. Documentation is not OS evidence and does not heal any failed historical ancestor.

Real kernel write and invalidation evidence must remain fail-closed, with `status=BLOCKED`, `can_authorize_dispatch=false`, and `independent_os_proof_verified=false` wherever evaluated. Qualified independent security review is a separate gate; green CI alone never authorizes protected annual execution.

Independent protected OS-enforced no-write DEC-650/#820 and immutable exclusive annual run385 admission DEC-651/#821/#779 remain **BLOCKED**. No protected annual evidence/sources or run385 test, execution, dispatch, retry, rerun; no production refs/workflows/runners/rulesets/permissions changes, broker/trading operations, merge or promotion.
