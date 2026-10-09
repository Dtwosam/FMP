# DEC-631 — Output isolation for ten older 2023 source-only report CLIs

**SOURCE-ONLY / UNMERGED / NO RESEARCH DISPATCH OR TRADING.** Based on independently checked `main` `53e203133bbc141b2f48c7b8b8241d56b35166a3`. The installed annual workflow and 2023 runtime remain exactly unchanged. Issue #779 remains OPEN.

## Concrete defect in the remaining 2023 entry points

A full inventory of the 23 `scripts/phase8a_annual_pattern_catalogue_2023_*.py` Python scripts found **ten** older report-writing entry points with no source-checkout output containment and no pre-import Python bytecode guard. They would accept `--out` paths pointing at source files, and the Python interpreter could create `__pycache__` during `fmp` imports. They also rewrote an identical external report. These are report-only commands, including those whose *names* refer to plan/authorization/install; modifying them does not install or authorize anything.

| Command | Decision | CLI action |
| --- | --- | --- |
| `admin_lock_handoff` | DEC-613 | `prepare` |
| `dispatch_action_preflight` | DEC-610 | `plan` |
| `dispatch_authorization` | DEC-609 | `authorize` (report construction only) |
| `dispatch_immutability_audit` | DEC-611 | `audit` |
| `dispatch_preflight` | DEC-608 | `plan` |
| `execution_preflight` | DEC-602 | `plan` |
| `runtime_authorization_install_action` | DEC-606 | `compile` (report construction only) |
| `runtime_authorization_install_preflight` | DEC-605 | `plan` |
| `runtime_authorization_install_receipt` | DEC-607 | `review` |
| `runtime_authorization_plan` | DEC-604 | `plan` |

## Implementation constraints

1. Set `sys.dont_write_bytecode = True` **before** the first `fmp.discovery` import in each entry script.
2. On entry to the CLI handler, resolve `source_checkout = Path(__file__).resolve().parents[1]` independently from caller cwd, then `target = args.out.resolve()`. Reject `target.is_relative_to(source_checkout)` with the exact decision ID **before** any input JSON read, builder or validator. Existing cwd-based model calculations are unchanged.
3. Pass only the resolved outside-checkout `target` through existing report writers; retain the previous refusal to overwrite conflicting report bytes. Identical external reports return without writing, preserving inode metadata. The report schemas/permissions, original `fmp` package, installed workflow, and 2023 runtime are untouched.

## Adversarial test contract

The focused CI copies clean `src/fmp`, all ten real scripts, and the existing annual workflow to a disposable checkout. Both bytecode suppression environment variables are removed. It runs each `--help` in an actual process, requiring no new source bytes or Python caches. For each of the ten scripts, seven denied output targets are executed with deliberately missing user JSON inputs: relative from repo root, relative from `scripts/`, parent-relative from `scripts/`, absolute from unrelated cwd, symlink alias, existing sentinel, and output over the Python script itself. All **70** real subprocess cases must fail on a decision-specific checkout message **before input access**, leaving source filenames and SHA-256 inventory identical, sentinel unchanged, zero `.pyc`, and no synthetic input file materialization.

A separate real-subprocess positive writer test invokes each of the **eight** existing `_write_json` helper implementations directly (without creating any actual domain authorization report): it writes a deliberately labeled test-only external JSON object, hard-links the file into the copied checkout, pins the shared inode mtime, repeats the helper, and requires unchanged inode timestamps and SHA-256 source inventory. It also asserts that a conflicting existing outside report is rejected without overwrite. The DEC-613 and DEC-611 inline report handlers are covered by early-denial tests and existing model regression tests, not by this eight-helper writer probe. This test proves output-writer hygiene, **not end-to-end authorization/report authenticity**. Full historical CLI/model regression and compilation remain mandatory; green focused checks alone do not authorize merging.

## Limits and downstream authority

`Path.resolve()` is not an atomic sandbox against a concurrent hostile filesystem actor swapping directory/symlink components. This does not validate an administrator's no-bypass immutable ref, independently reviewed external tag/SHA tuple, live annual three-job and 2023 runtime admission guards, or permission to dispatch run 385. No protected-history read, research dispatch/retry, tag/ruleset/protection change, strategy promotion, brokerage mutation, order or trading is performed or authorized.

Separate PRs DEC-627/628/629/630 (#796-799) remain under their own independent review gates; this new branch has a separate **exact-head** focused/full historical/general regression, compilation, Phase 3 and acceptable independent review requirement. No merge before those checks, no silent bypass of review quota or main drift. A future one-shot research action is a different explicitly gated operation entirely.
