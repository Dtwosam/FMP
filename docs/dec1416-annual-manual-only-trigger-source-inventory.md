# DEC-1416 — Manual-only annual workflow trigger source inventory

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit test/docs child #1639 DEC-1415 at fd25773fb89268756b27e54614932a109a83ac73; +12 source-only methods, **1,427 proposed methods**.

The installed annual source is explicitly workflow_dispatch-triggered and has exactly two declared inputs: annual_segment_label and previous_annual_freeze_run_id. The segment choice list remains the checked-in 2015–2025 years plus 2026 YTD segment. This pure source fixture rejects newly added push, pull_request, schedule, workflow_call or duplicate/inline event triggers; extra inputs; widened years; or changed predecessor required/type flags. All edits are in-memory source counterexamples, never applied to the installed workflow.

A manual-only source trigger does not establish a one-shot server-side run385/attempt1 allocation, immutable reviewed SHA, protection from Actions-write principals or OS-original no-write. This limited shape audit is not a YAML evaluator, source-of-truth authorization, or promise that unknown GitHub settings have been assessed. Neither runtime nor protected data are opened.

Requires exact-head Phase 3 and full historical CI plus independent review. DEC-650/#820 independently OS-enforced original no-write and DEC-651/#821/#779 exclusive immutable one-shot 2023 annual dispatch remain **BLOCKED**. No annual execution/retry, original/archive read, installed workflow/permission/ruleset change, merge, production or trading action.
