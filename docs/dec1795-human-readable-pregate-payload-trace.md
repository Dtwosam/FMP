# DEC-1795 — Surface pinned pre-gate command payloads in human handoff

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child of PR #2041 at `c77f072fb6cb67719ca750b7f59224d913297b74`.

The canonical offline six-source JSON packet already carries each historical three-job pre-runtime-gate operation's step index, name and exact command payload. Its human Markdown handoff only listed the names. Reviewers reading Markdown could therefore miss the frozen source's actual pre-gate reads and setup commands unless they also inspected JSON.

Render the reviewed historical payloads after the existing job summary as indented **JSON-escaped literals**, with zero-based step indices and each historical runtime-gate position. Clear labels say **HISTORICAL, NOT CURRENT**, **not a command to run**, and **never proof of early admission**. The existing canonical six-source equality, pinned dual hashes and exact pre-gate trace are validated *before* formatting, so mutating any command must still reject the report. The JSON output schema and both nonzero CLI exit conventions remain unchanged.

Four added tests cover all three jobs and exact payload display, historical non-executable labeling, injected-payload rejection, and Markdown CLI exit status 3 (**6,580 cumulative proposed source-defined test methods** on this lineage). No new authorization, no installed workflow, ref, ruleset or runner modification; no protected 2023/run385/attempt1 read/dispatch, broker/demo/live action, or profit evidence. External #779/#820/#821 proof and distinct human approval remain **MISSING/BLOCKED**. Exact-head Phase 3 and full historical/general CI plus independent qualified review required.
