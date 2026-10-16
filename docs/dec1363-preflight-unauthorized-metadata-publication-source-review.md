# DEC-1363 — Source-risk audit: preflight `if: always()` publication after failed authorization

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit child of #1586 DEC-1362 at `9adfbb63b20b07b6090b3f0ef891e0e61a4cd2f6`; **1,006 proposed source-defined unittest methods** (+6). New tests inspect only a local Git committed YAML blob. No protected annual inputs, GitHub artifact retrieval or workflow dispatch takes place.

## Confirmed checked-in annual source ordering

- The `annual_preflight` job checks out code, installs Python, then uses `GH_TOKEN` and `gh api` to fetch four EXP-044 run/artifact metadata JSON files under checkout-relative `.preflight`.
- It runs the `preflight` validation command writing `.preflight/preflight.json` **before** the separate `require-execution` authorization command.
- Its final preflight artifact-upload step has **`if: always()`**, `path: .preflight` and `include-hidden-files: true`. When execution authorization fails *after* metadata has been fetched, the source still permits an upload **attempt**; successful publication depends on artifacts and runner state. This is a potential preauthorization metadata publication boundary, **not** a claim of an observed protected annual data leak.
- The cell and freeze upload steps do not share `if: always()`; that distinction is source-backed, not a claim of independently protected execution.

Six tests pin this ordering and output behavior from `git show HEAD:.github/workflows/phase8a-annual-pattern-catalogue.yml` so they remain deterministic if a separate unit test mutates the checkout. They are historical-source characterization, **not** an approval or a production workflow remediation. Future separately reviewed staging/upload policy must address what metadata may be read or published **before** independent gate admission. This draft does not edit installed workflow YAML or annual CLI/runtime.

Source-only green CI never proves OS-enforced no-write or immutable server-side run385 admission. DEC-650/#820 and DEC-651/#821/#779 remain **BLOCKED**; independent external custodians and qualified review are still required. Each exact SHA requires completed successful Phase 3 plus full historical CI and a separate qualified review. Existing failed exact SHA statuses remain failed. No protected annual source/evidence, run/retry/rerun/dispatch, workflow/ruleset/permission mutation, broker/trading, merge or promotion.
