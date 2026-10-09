# DEC-628 — Legacy annual audit report output isolation

**Status:** SOURCE-ONLY / stacked behind DEC-627 PR #796 / no live workflow, no research dispatch, no tag or administrator change, no trading.

## Concrete defect

Four older Phase 8A **offline** 2023 audit CLIs used `args.out.parent.mkdir(...)` and `args.out.write_text(...)` without first verifying the target was outside the repository checkout:

| Existing CLI | Decision | Requested report |
| --- | --- | --- |
| `phase8a_annual_pattern_catalogue_2023_main_lock_readiness.py` | DEC-612 | main lock readiness |
| `phase8a_annual_pattern_catalogue_2023_immutable_tag_feasibility.py` | DEC-615 | immutable tag feasibility |
| `phase8a_annual_pattern_catalogue_2023_tag_ruleset_static_review.py` | DEC-616 | ruleset/ref static review |
| `phase8a_annual_pattern_catalogue_2023_tag_ref_guard_rehearsal.py` | DEC-617 | proposed ref guard rehearsal |

Each could create/overwrite a report inside the checkout if its arguments pointed there. That violates the source-only auditing discipline even though their report contents continue to deny research or trading.

DEC-627 PR #796 independently fixes import-time Python bytecode writes in these and seven other scripts, with no-bytecode and content-hash-based regression checks. This DEC-628 change addresses the **separate, previously unguarded explicit output-path side effect**; it intentionally stacks on DEC-627 without merging or changing its review requirements.

## Smallest change

For each of the four audited CLIs, immediately on entry to its assess handler:

1. Resolve the **actual source checkout** using `Path(__file__).resolve().parents[1]` (never the caller's mutable working-directory choice), and resolve the requested output path using `args.out.resolve()`.
2. If the fully resolved target `is_relative_to(checkout)`, raise a decision-specific `ValueError` **before reading any supplied JSON input or evaluating its security claims**.
3. Use the resolved target consistently for conflict checks, parent creation and report write. Preserve the existing refusal to overwrite conflicting outside-checkout output.

There is no new permission flag, GitHub API call, active workflow change, tag mutation, dispatch path, network access, broker action or historical artifact read.

## Adversarial execution tests

The focused DEC-628 CI test launches all four actual CLI assess commands from a temporary copied checkout, with no upstream Python bytecode suppression and deliberately **missing input files**. For each CLI, nine output cases must fail before any input-file read: checkout-relative, checkout-absolute, parent-relative, symlink-aliased checkout, an existing checkout file, two subdirectory-to-repository paths, an absolute path launched from a working directory outside the checkout, and an existing checkout file launched from a subdirectory. In all **36** combinations, the expected decision-specific checkout denial is emitted and the SHA-256 content inventory of the copied checkout is identical; the original sentinel is untouched; no `.pyc` or input file appears.

Static tests also ensure the checks occur before any audit computation and the output uses the resolved target.

**Scope limitation:** `Path.resolve` protects against paths/symlinks as resolved during validation. It is not an atomic filesystem confinement primitive against an actor that can swap filesystem path components concurrently *after* the check; these offline scripts are not privileged security sandboxes. A later dedicated sandboxed output mechanism would need separate review if a hostile concurrent filesystem actor becomes part of the threat model.

## Still locked

The installed annual catalogue workflow remains bound to `refs/heads/main` and its existing Git blob. The installed 2023 runtime retains its existing Git blob and format-only commit check. Issue #779 stays open: no independent continuous administrator no-bypass immutable-ref proof, externally authenticated reviewed ref/SHA tuple, separately approved live three-job workflow/runtime change, new one-shot dispatch authority, protected history reads, retries, next year, strategy promotion, brokerage, demo/live or real-money trading. Research run 385 remains reserved; DEC-628 cannot dispatch it.
