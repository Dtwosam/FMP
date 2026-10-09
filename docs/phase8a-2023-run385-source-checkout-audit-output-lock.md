# DEC-629 — Anchor remaining audit report output guards to source checkout

**SOURCE-ONLY / STAGED / NOT MERGED.** Stacked on DEC-628 PR #797, which itself depends on DEC-627 PR #796. No annual research dispatch, tag/ruleset/protection edit, installed workflow or 2023 runtime change, historical protected read or trading authority.

## Observed defect

The assess-only DEC-618 through DEC-624 CLI scripts used `Path.cwd()` as their read-only output containment boundary. Running a CLI with its cwd in `scripts/` or outside the actual checkout could allow an explicitly requested `--out` target to resolve to a file **inside the source checkout**. This is distinct from DEC-627 bytecode import hygiene and DEC-628's four older CLI output guards and hard-link metadata idempotency.

## Scoped amendment

All seven handlers resolve `source_checkout = Path(__file__).resolve().parents[1]` from the running script and `target = args.out.resolve()`, then reject `target.is_relative_to(source_checkout)` before reading inputs or building a report. Keep the prior `Path.cwd().resolve()` variable for report computation to avoid changing research or audit semantics. DEC-618 uses its resolved target consistently for conflict/read/write handling. No Python package logic or installed research workflow is modified.

## Test contract

- Copy `src/fmp`, the seven real scripts and the unchanged installed annual workflow to a temporary checkout. Explicitly unset external bytecode-suppression variables.
- Run each CLI with seven checkout-local output attempts: repo-root relative, `scripts/` relative, `scripts/` parent-relative, absolute output from outside cwd, symlink-aliased checkout from outside, existing checkout sentinel from outside, and source script as target. All **49** real subprocess calls must deny the target with decision-specific checkout errors and preserve source filename/SHA-256 inventory, sentinel bytes, and zero `.pyc` files.
- DEC-620 and DEC-621 use deliberately missing input JSON files; a checkout refusal must occur first, before input access. All seven real `assess` positive cases (DEC-618 through DEC-624, using external synthetic unauthenticated fixture JSON for DEC-620/621) must emit legitimate outside-checkout reports with `dispatch_blocked=true` and `trading_authorized=false`. Each script must now return without rewriting an identical existing report. The test hard-links its external report into a disposable checkout, pins the shared inode's mtime, repeats the report and demands unchanged mtime and source SHA-256 inventory; file hashes alone miss metadata-only writes.

## Remaining limitations and sequence

Resolved-path containment does not solve concurrent adversarial filesystem symlink retargeting or constitute a privileged sandbox. There is still no authenticated no-bypass immutable-ref administrator proof, independently approved external ref/SHA tuple, installed tag-compatible workflow/runtime change, authorized unique annual run 385, or trading permission.

PR #796 must first pass independent exact-head review and merge on unchanged main; PR #797 must then be retargeted/retested/reviewed/merged independently; DEC-629 will require its own retarget, focused and full historical/general regression, compilation, Phase 3 acceptance, and acceptable independent exact-head review before any merge. Issue #779 remains open.
