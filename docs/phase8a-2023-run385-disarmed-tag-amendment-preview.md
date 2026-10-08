# DEC-618: disarmed immutable-tag workflow amendment preview

**Status:** source-only review proposal. No effective workflow, runtime, tag, or branch settings are modified.

## Context

DEC-616 and DEC-617 are merged. DEC-617 was merged as PR #786 at main `a2a767d5a09a32282722bfb24b98dad96ef27c9c` after full focused/historical/Phase 3 acceptance. Annual research run 385 remains unconsumed, following successful 2022 predecessor run 384 / id 37663157285. Issue #779 remains open.

The frozen installed annual workflow has Git blob `09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1` and each of annual_preflight, annual_cell and annual_freeze contains a main-ref guard. Simply dispatching against a tag fails those existing guards. Runtime authorization also needs a separately reviewed binding from tag identity to the actual dispatched GITHUB_SHA.

## Inert source-only difference preview

DEC-618 builds a unified diff **only in memory** from the frozen installed annual workflow. It checks that all three original guards and their ordering still match DEC-617. It replaces those three lines **only in the preview** with a deliberately unapproved synthetic tag and two hard-stop lines:

```sh
test "$GITHUB_REF" = "refs/tags/fmp/phase8a/2023/run385/dec618-not-authorized"
echo "DEC-618 DISARMED PREVIEW: tag workflow execution is not authorized" >&2
exit 1
```

There is one unconditional `exit 1` per proposed job. The preview includes no permission to remove these stops. It reconstructs the original workflow byte-for-byte after undoing the three synthetic changes. The source-path input is pinned by Git blob hash.

The only output is an offline JSON report containing the annotated unified diff, preview SHA-256, and a deterministic content fingerprint. **Never apply the diff as a live workflow.** A separate source/runtime authorization and independent GitHub runtime testing would be needed first. A user could technically apply the disarmed diff, but doing so would make the current annual workflow reject execution rather than enable it.

Example read-only local command:

```sh
PYTHONPATH=src python scripts/phase8a_annual_pattern_catalogue_2023_disarmed_tag_amendment_preview.py assess --out /tmp/dec618-preview.json
```

## Remaining blockers

- Authenticate the exact prospective immutable tag and reviewed code commit using real no-bypass administrator evidence covering the entire server-side workflow_dispatch request, not only a JSON static candidate.
- Separately approve workflow changes for preflight, all 18 cell jobs and freeze, plus an authoritative 2023 runtime ref/SHA binding before protected reads.
- Preserve historical source evidence, ten-run annual predecessor inventory, exact 2023 run 385 / attempt 1, and strict no-retry semantics.
- Obtain another explicit narrowly scoped one-shot action decision before any workflow_dispatch. Even a successful run requires independent verification of all 18 cells, freeze and artifacts.
- Keep all 2024+ work, cross-year synthesis, Strategy V1 promotion, Phase 8B and broker/demo/live/real-money/trading authority false.

The alternative exclusive-main branch lock still requires the independent administrator witness described in issue #779. DEC-618 does not choose or authorize either execution path.
