# DEC-1789 — Pin the full human-facing pre-gate workflow step trace

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent child of PR #2035 at `c9732dbffabeb90550b817ac6d5919c8e4192d6a`.

DEC-1786's Markdown renderer verified the source hashes, eight missing proof roles, non-authorizing flags and approximate historical runtime gate positions, but not the **entire pre-gate trace**. A caller modifying a parsed report dictionary could replace a step's displayed name, command payload or index—or delete its preflight metadata read—while retaining the expected names, proof count and top-level BLOCKED flags. A malicious newline in an unchecked step name could also inject a fake Markdown table row.

The updated formatter reconstructs the exact three-job trace by **re-reading the dual hash-pinned inert historical workflow fixture** through the existing no-follow, bounded offline audit, then requires exact equality for every step record (name, payload and position) before displaying Markdown. It denies tampered names, command labels, positions, missing metadata fetches and injected table markup. This compares six local pinned documentary sources only; it **does not** prove any control is actually installed on the runner or control a real dispatch ref.

Adds 5 tests (6559 proposed cumulative source-defined methods). PR #2035 already fixes the #2034 numeric formatting failure; new exact-head Phase3 and full historical/general regression required. All external admin/runner packages and one-shot 2023/run385/attempt1 approvals stay MISSING/BLOCKED (#779/#820/#821); no market data, workflow/ref/ruleset mutation, broker/demo/live orders or real-money trading.
