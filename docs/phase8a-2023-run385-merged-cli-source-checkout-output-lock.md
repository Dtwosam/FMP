# DEC-630 — Merged DEC-625/626 CLI output containment and no-rewrite guard

**Status: SOURCE-ONLY, UNMERGED, NO DISPATCH OR TRADING.** Based on main at `53e203133bbc141b2f48c7b8b8241d56b35166a3`. Separate from still-open DEC-627 PR #796, DEC-628 PR #797 and DEC-629 PR #798. No installed annual workflow or 2023 runtime amendment.

## Root cause

A follow-up to DEC-629 found that the already-merged assess-only DEC-625 `review_manifest_identity_separation` and DEC-626 `precheckout_job_if_preview` CLIs still relied on `Path.cwd()` when blocking `--out` targets inside the Git checkout. Calling a script from `scripts/` or outside the checkout could resolve an explicit output to a checkout file without being rejected. Both also rewrote an identical existing external report, changing inode timestamps on a checkout-hardlinked external path, even when source byte hashes remained stable. The static tests asserted the weaker caller-cwd guard.

## Scoped repair

For both CLI assess handlers, retain `checkout = Path.cwd().resolve()` as the **offline model computation root only**, and introduce `source_checkout = Path(__file__).resolve().parents[1]` as the output isolation root. Resolve `target = args.out.resolve()` and refuse `target.is_relative_to(source_checkout)` before running the model. If an external existing report differs, retain refusal. If identical, return without recreating or rewriting the file. Preserve import-time `sys.dont_write_bytecode = True` ahead of package imports.

Existing legacy source-only test assertions now require the real script checkout rather than the unsafe caller-cwd guard.

## CI coverage

- Copy the clean `src/fmp` package, two scripts and frozen installed annual workflow into a disposable checkout. Unset `PYTHONDONTWRITEBYTECODE` and `PYTHONPYCACHEPREFIX` in real subprocesses.
- For both CLIs, seven checkout-local output paths (14 total): checkout-root relative, scripts-relative, parent-relative, outside cwd absolute, symlink-aliased checkout, existing checkout sentinel and source script path. Every one must reject with the decision-specific checkout message, preserve the SHA-256 checkout content inventory, preserve the sentinel and create zero `.pyc`.
- Positive subprocess checks for both CLIs must produce valid external offline reports with `dispatch_blocked=true` and `trading_authorized=false`. Each report is hardlinked to a copied checkout file, inode mtime pinned, then re-executed; the identical second report must **not** write or change timestamp. Conflicting existing outside-checkout reports must be rejected unchanged.

## Boundary and authorization

Resolved-path checks are not an atomic adversarial filesystem sandbox against concurrent symlink swaps. No authentication of administrator no-bypass protections, reviewed immutable ref/commit SHA, or live tag-compatible three-job workflow/runtime exists here. No protected history, run385/attempt1 dispatch or retry, future-year research, strategy promotion, brokerage, demo/live order, or trading is authorized. Issue #779 remains open.

This branch targets main independently of PRs #796–#798 because DEC-625/626 were previously merged and their scripts are unaffected by those source-only PRs. **Do not merge without its own exact-head focused/full historical/general regression, compilation, Phase 3 acceptance, acceptable independent review, main drift/rebase inspection, and no outstanding findings.** This branch is not an independent code review of any other PR.
