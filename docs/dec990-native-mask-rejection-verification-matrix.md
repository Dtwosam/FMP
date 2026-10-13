# DEC-990 — Invalid native registration flags: kernel evidence and CI handoff

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Documentation-only strict one-commit child of DEC-989/#1210. The source-defined test count remains **646**; no executable tests, observer runtime, CI workflow, protected assets, production settings or trading operations are changed.

## Distinct native Linux controls

| Draft | Original inotify state | Native operation | Observed kernel result | Follow-up that rejects a false watch-history conclusion |
| --- | --- | --- | --- | --- |
| DEC-972/#1193 | Source and parent already watched | `IN_MASK_CREATE` on either registered inode | `-1/EEXIST` | Original source/parent masks retain real write and namespace events |
| DEC-977/#1198 | Fresh second inotify FD | First `IN_MASK_CREATE` on source, then duplicate create-only | First succeeds; second `-1/EEXIST` | Source-only observer still lacks the separate parent census |
| DEC-982/#1203 | Two distinct empty inotify FDs | First `IN_MASK_CREATE` on same source inode in both | Both succeed; duplicate attempts in each fail EEXIST | Registration uniqueness is **per FD instance**, not global to the inode |
| DEC-984/#1205 | Watched source inode then a second hardlink pathname | Create-only watch on alias in same instance | `-1/EEXIST`, even though pathname differs | Real alias writes still reach original source WD; kernel identity is inode-based |
| DEC-988/#1209 | Source and parent watches already active | `IN_MASK_ADD | IN_MASK_CREATE` on either | `-1/EINVAL` | Original source/parent registrations still report actual public writes and sibling create/delete |
| DEC-989/#1210 | Completely fresh inotify FD, zero watch registrations | Both incompatible flags on source and parent, then valid create-only registrations | Invalid calls `-1/EINVAL`; subsequent separate first create-only calls succeed | The initial invalid request created no watch; only later valid watches report new writes/namespace events |

`IN_MASK_CREATE` and `IN_MASK_ADD` are registration-only modifiers, not native action masks. EINVAL and EEXIST are distinct rejection reasons; neither must be interpreted as kernel write denial or continuous event coverage. Watch descriptor values are local to inotify instances and can be reused. A later success does not retrospectively observe prior writes.

All native controls use newly generated nonprotected public temporary Linux files, real inotify operations and event queues, actual write/restore checks, final inode/parent metadata and inventory checks, and explicit FD closure. They never provide independently OS-enforced no-write proof or a trusted annual admission mechanism. When a raw write stream is supplied, the unchanged evaluator remains `BLOCKED` with exact `can_authorize_dispatch=false` and `independent_os_proof_verified=false`.

## Honest exact-head verification status

The contiguous verified green checkpoint was DEC-979/#1200. DEC-980/#1201 through DEC-984/#1205 each passed Phase 3 but **failed** full historical at its own exact commit because DEC-980 incorrectly expected an empty followed-parent directory queue after symlink unlink. Native `IN_DELETE` on the followed parent is correct. DEC-985/#1206 repairs only that assertion on a **new** strict draft head. DEC-986/#1207 adds the follow/no-follow symlink watch-lifetime comparison, and DEC-987/#1208 preserves the exact historical failure ledger.

DEC-985 through DEC-990 are **not** retroactive CI repairs of the failed exact commits. Each must independently complete exact-head Phase 3 and full historical regression before being described as green. This handoff is not a live CI-completion certificate. Qualified independent security review is a separate gate; passing CI is not dispatch approval.

Independently OS-enforced protected no-write DEC-650/#820 and immutable exclusive annual run385 admission DEC-651/#821/#779 remain **BLOCKED**. Do not access protected evidence/source, test/dispatch/retry/rerun run385, alter production refs/workflows/runners/rulesets/permissions, operate broker/trading systems, merge or promote any draft.
