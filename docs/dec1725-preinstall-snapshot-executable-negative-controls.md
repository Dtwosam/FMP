# DEC-1725 — Executable synthetic negative controls for preinstall snapshot exclusion

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent test/docs-only child of #1971 at `82befadd63294d714e434e01deddf9e985fd49aa`.

Adds **10 methods** (**5,894 proposed source-defined methods**) exercising DEC-1716's real Python unittest loader and assertions without any protected annual workflow file, private data, GitHub API, permissions, runtime installation or runner OS access.

- Imports the test module in a disposable namespace and asserts **exactly 12 skips** only when `FMP_PREINSTALL_SNAPSHOT="1"`. While the workflow path is deliberately nonexistent, a clean loader run with zero errors proves the documented reduced-snapshot exemption is executable.
- With the environment unset and workflow path nonexistent, the loader must produce **one `FileNotFoundError` class setup error**, never a blanket skip.
- Alternate environment values `0`, `true`, `01` and `yes` must not activate the skip.
- In-memory **synthetic job step labels** exercise six actual DEC-1716 ordering assertions. Mutations of checkout position, main-ref literal, job-level guard existence, preflight fetch-before-authorization and cell download timing must each be detected by the test logic.
- The fixture does not touch or claim to authenticate the installed protected workflow; real normal-checkout focused checks must still be completed independently.

The original DEC-1716 source test file is unchanged, as are all workflow/runtime/security and economics sources. These test scenarios demonstrate only the **test harness behavior**, not an actual installed admin lock or readiness to consume 2023 annual run385. External admin/runner review issue #779 and DEC-650/#820 and DEC-651/#821 stay **BLOCKED**. No protected evidence access, annual dispatch/retry, main/tag/ruleset modification, strategy promotion, broker/demo/live or trading.

Own exact-head Phase 3/general-historical CI and qualified independent review mandatory.
