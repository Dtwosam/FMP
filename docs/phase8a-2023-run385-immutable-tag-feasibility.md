# Protected 2023 annual run 385: immutable-tag alternative feasibility

**Decision:** DEC-615. **Scope:** offline source inspection only. **Disposition:** CURRENT WORKFLOW INCOMPATIBLE; NO TAG DISPATCH AUTHORIZED.

## Why consider this?

GitHub workflow-dispatch REST accepts a branch or tag name, not an immutable raw commit SHA. For workflow_dispatch, GITHUB_REF is the fully qualified branch or tag ref and GITHUB_SHA is the last commit on that ref. These facts do not make a mutable tag immutable.

Official documentation:
- https://docs.github.com/en/rest/actions/workflows#create-a-workflow-dispatch-event
- https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#workflow_dispatch
- https://docs.github.com/en/actions/reference/workflows-and-actions/variables

Original DEC-611 dispatcher PR #777 closed without merge over a mutable-main check/dispatch race. An independently enforced exclusive main lock remains one potential solution (issue #779). A tag with separately reviewed enforced tag protection is another *possible future architecture*; neither option is authorized for execution now.

## Frozen source incompatibility

The installed annual pattern catalogue workflow (.github/workflows/phase8a-annual-pattern-catalogue.yml) is Git blob 09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1. These jobs each explicitly require GITHUB_REF to equal refs/heads/main:

| Current workflow job | Consequence for a tag ref |
| --- | --- |
| annual_preflight | Rejects the tag before protected 2023 execution |
| annual_cell | Each of 18 catalogue cells would reject the tag |
| annual_freeze | The yearly freeze would reject the tag |

GitHub would use refs/tags/<tagname> for a tag, which fails all three main-ref shell guards. Runtime authorization and artifacts are also tied to GITHUB_SHA. The protected 2023 runtime gate blob is cb4d32507dc93fa8a7a1296e630ce3bc9ee9c191; installed runtime blob is 0fb5cf4d5de1355ff8faffcff565cbbabaf1d7a3. Any new workflow/runtime design must independently re-review previous source and artifact pins. Changing only the dispatch input cannot fix this.

DEC-615's offline feasibility assessor pins DEC-614's successful artifact source and these workflow/runtime blobs. It checks all three job guards and fails closed on unexpected source changes, rather than issuing an outdated feasibility judgment.

## Requirements for a separate future tag approach

1. Separate source-only design review for the intended *enforced immutable tag* namespace, exact commit-object binding, deletion/update prevention, inherited rules and authorized bypass actors. An ordinary tag is mutable and not by itself sufficient.
2. Separately authorize and test a narrowly gated annual-workflow and 2023 runtime amendment accepting only the verified ref and matching GITHUB_SHA. Preserve source/freeze pins, single-run attempt, protected-history access and no-trading boundaries. The currently installed workflow is not changed by DEC-615.
3. Negative tests for changed refs, retargeted tags, bypass writers, source drift, unknown or consumed annual run 385, failed/ambiguous submission and prohibited rerun/retry/replacement.
4. Only after review and installation, have an authorized operator create/lock the exact approved tag at the reviewed commit, prove its immutability with independently inspected rules/witnesses, and get a separate *one-shot run-385* action decision.
5. Hold immutability while GitHub processes any future separately approved workflow dispatch and verify the exact run/commit, 18 cell jobs, preflight/freeze artifacts and hashes afterward. No cross-year research, strategy promotion, Phase 8B or trading follows automatically.

## Comparison and current frozen evidence

- An **exclusive main-lock window** keeps the current main-ref workflow and requires admin proof that no writer/bypass can move main during the dispatch request.
- A **verified immutable-tag design** would avoid dispatching a mutable main branch, but the frozen active workflow rejects it in preflight, cell and freeze jobs; an independent workflow/runtime amendment is required.

DEC-614 succeeded as first-push run 37799674451 on main commit ab7c5b34889e666ce14b8a00d572bcd0a07fb2cf. Artifact 11559788794, ZIP SHA-256 52f2c02a3ac8002c2f8b7d043080bcf47292e36f9574e9d37bcce2fb93d4f11d, internal canonical SHA-256 7e470b83d4b9a04017955835ff412aa07a0a7dc91b2193b350354bbbf659a267, fingerprint 6376c28695301ff68e44d2c353c47421c5f2a0b1574310ccf39e5508ae5ca3c0. The original prior annual workflow_dispatch history remains exactly ten runs {1,376,377,378,379,380,381,382,383,384}, ending with successful 2022 predecessor run 384 / id 37663157285. Run 385 is unconsumed.

**DEC-615 verdict:** Current tag path incompatible, tag immutability unproven, alternative ref execution unauthorized, annual dispatch blocked, and trading authorization false. No tag creation, runtime mutation, workflow execution, broker order or real-money action is permitted.
