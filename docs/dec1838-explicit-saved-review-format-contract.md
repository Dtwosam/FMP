# DEC-1838 — Explicit saved-input format contract, no silent reinterpretation

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child of #2084 `b5197985c91ed668327ee9612911261fe92d3551`.

The new saved Markdown verifier was first added with `--format json` as the argument parser's default, so an explicit incompatible `--verify-markdown FILE --format json` request would silently produce Markdown. Set the format default to absent, infer the correct output for each saved verification mode and reject **explicit contradictory** formats with controlled BLOCKED exit 2 and no stdout. Full seven-source `--verify-report` continues to permit deliberate JSON, human Markdown or compact request output, always from independently re-derived pinned inputs.

Saved compact requests accept only requests format, saved Markdown accepts only Markdown; both still require exact canonical evidence. Three tests (6,709 cumulative proposed source-defined) cover contradictory format denial and matching explicit formats remaining BLOCKED/nonzero exit 3. No live admin/OS attestation, signed evidence, protected 2023/run385/attempt1 read/dispatch, ref/ruleset/workflow mutation, broker/demo/live order, capital or profit. External #779/#820/#821 and eight independent proof packages remain MISSING/BLOCKED. Exact-head Phase3/full CI and qualified review required.
