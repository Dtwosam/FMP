# DEC-1722 — Explicit preinstall-snapshot scope for installed-workflow contract tests

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent one-commit test/docs child of #1968 at `0ff1daa062286778b244b15970e9029db5dfa1ff`.

## Verified failure, not a change in installed security

Full historical/general CI for previous head #1966 (job `118104345150`, run `39265631364`) reported **10,747 tests / 1 failure / 1 error / 702 skipped**. The failure was the literal Stage2 published Markdown label, corrected by DEC-1720/#1967. The error was this source-bound test's `setUpClass` raising `FileNotFoundError` for `.github/workflows/phase8a-annual-pattern-catalogue.yml` in the environment `FMP_PREINSTALL_SNAPSHOT=1`. That mode deliberately excludes the installed protected annual workflow source; another existing historical DEC-613 test suite explicitly guards the same mode.

## Narrow repair

Add only `os` import and **`@unittest.skipIf(os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1", ...)`** on the DEC-1716 installed-workflow class. The behavior is exact:

- In the documented reduced preinstall snapshot mode: its 12 source-dependent tests are **SKIPPED**, not presented as an installed-workflow proof.
- In a normal source checkout: all 12 tests are still run against the exact original workflow blob `09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1`, with assertions of the dangerous post-checkout/post-install guard ordering and preflight metadata-first access.
- In any other environment where the workflow unexpectedly goes missing: **fail closed** through ordinary `FileNotFoundError`. There is no generic existence skip or silent fallback to fabricated workflow bytes.

The skip means historical/general CI under `FMP_PREINSTALL_SNAPSHOT=1` cannot independently certify the 12 focused DEC-1716 tests; a future separately reviewed normal-checkout focused validation remains necessary. Phase 3 tests alone are not substitute certification. The historical security finding and all external administrator blocker requirements remain unchanged.

New source-defined methods **0**; proposed total **5,876**. Source and doc only, no production/parser/workflow/security/source-of-truth modification, annual dispatch or protected-history access. Issue #779, DEC-650/#820, DEC-651/#821 remain **BLOCKED**, and no demo, broker, live or trading action is authorized. Exact-head CI and independent qualified review required.
