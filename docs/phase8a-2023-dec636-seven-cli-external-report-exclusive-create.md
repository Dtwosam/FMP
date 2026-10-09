# DEC-636 — External audit report exclusive creation for seven stage-3 preview CLIs

**DRAFT, source-only audit hardening. DO NOT MERGE without independent review and the landing sequence.**

## Failure class and scope

This is the same check-to-create gap identified in DEC-635 / PR #805, but on the **seven different audit scripts changed in DEC-629 / PR #798**. On PR #798's raw head, those scripts reject output paths inside their source checkout and avoid rewriting identical outside reports. However, a new external output still followed `target.exists()` with `target.write_text()`, permitting an intervening conflicting leaf file to be overwritten.

The seven affected CLIs are:
- DEC-621 ambiguous-dispatch hold model
- DEC-618 disarmed tag-amendment preview
- DEC-620 lock witness coverage
- DEC-623 pre-access identity topology audit
- DEC-619 ref-race interleaving model
- DEC-622 runtime tag-SHA binding preview
- DEC-624 three-layer admission model

This draft **starts from exact PR #798 head `620626ad66fd85bb85d94c126e7262592c4a499e`**, rather than changing PR #798 itself. The new branch targets its unchanged head. Existing source-checkout checks and pre-import `sys.dont_write_bytecode=True` remain in each CLI. No live workflow, runtime, dispatch, or permission flag changes.

## Proposed implementation

All seven scripts import `fmp.discovery.annual_pattern_catalogue_2023_external_report_create.write_once_external_report`, preserving each original conflict message. The helper's Git blob and the seven existing deterministic leaf-creation tests are **byte-for-byte identical** to those proposed on the separately stacked DEC-635 draft PR #805. There are not two independently diverging implementations.

The helper uses `Path.open('x', encoding='utf-8')` to prevent overwriting a conflicting report created between an initial existence check and opening the output. Identical existing reports are not rewritten; an intervening identical competing file is accepted without writing. A dangling symlink remains an error and no symlink target is populated.

The additional three static integration regression tests verify every one of the seven staged audit script imports and calls the helper exactly once, preserves its source-checkout output guard in front of the write and its Python bytecode suppression, and no longer contains `target.write_text()`. Existing CLI functional/regression tests also remain part of full GitHub CI.

## Review and landing considerations

**PR #805 is based on PR #797. This PR is based on PR #798.** They deliberately contain the *same* new helper and shared test blob. Merging/rebasing both proposals requires reconciliation of the shared paths, not duplicated helper modules. No draft is permission to merge, rebase the original reviewed heads, or bypass the original #796→#797→#798 sequence.

Leaf-file exclusivity does **not** lock parent directories, make publication fully atomic across process termination, or prevent a privileged local actor swapping path components between containment check and file open. Its scope is narrowly preventing accidental/concurrent overwrite of an external report at the target leaf.

The one-shot annual 2023 workflow-dispatch run385 remains **unconsumed and blocked**. This change grants no historical protected-data access, run/retry/dispatch permission, merge authorization, broker or trading authority. See issue #779.
