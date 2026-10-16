# DEC-1364 — Pin Git blobs used by the annual source-only security audit

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit child of #1587 DEC-1363 at `29e84e5ce668ec93e4d4df7f4ed7b2f09544bb6b`; proposed **1,011 source-defined unittest methods** (+5). Source audit only; no protected annual reads, GitHub dispatch, production changes, workflow/CLI/runtime modification or trading.

The 2026-10-16 draft source-only characterization was previously based on visible YAML and Python text; it must not silently treat a changed Git blob as the same reviewed source. This draft adds local `git rev-parse HEAD:path` negative-fidelity checks for:

| Tracked source | Exact expected Git blob |
| --- | --- |
| `.github/workflows/phase8a-annual-pattern-catalogue.yml` | `09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1` |
| `scripts/phase8a_annual_pattern_catalogue.py` | `030bf98df2d5ffb50821bd0403f205c7c09f20f3` |
| `src/fmp/discovery/annual_pattern_catalogue_2023_runtime_authorization.py` | `cb4d32507dc93fa8a7a1296e630ce3bc9ee9c191` |
| `scripts/dec1356_annual_workflow_source_order_audit.py` | `348dce13adf26734ed6139f11d7ba46d6c145546` |

The fifth negative control requires an absent tracked path to raise rather than fall back silently to a mutable working tree. Exact Git blob matches prove only **local committed-source identity** under CI checkout. They **do not authenticate the installed server-side workflow, its future dispatch ref/resolved SHA, an externally approved SHA, OS-enforced original-source no-write, or 2023 run385 exclusive admission**. GitHub PR test checkouts may be synthetic merge commits; any variation affecting one pinned blob is a source-review invalidation, not automatically a security fix. New authorized future source changes will require independent review and updated source-bound expectations, rather than silently passing the old findings.

Each exact SHA must pass Phase 3 and full historical CI and receive independent qualified review. Prior exact-head CI failures remain failures. Real DEC-650/#820 and DEC-651/#821/#779 blockers remain **BLOCKED**. No protected input/artifact access, annual run/retry/rerun/dispatch, workflow/ruleset/permission install, broker/trade, promotion or merge.
