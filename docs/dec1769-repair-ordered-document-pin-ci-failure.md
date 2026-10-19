# DEC-1769 — Repair exact-head historical/general CI: preserve packet ordering for SHA pin test

**DRAFT / NEVER MERGE / NEVER PROMOTE**, exact-parent child of PR #2015 at `fa0442c9ba12fdbfc896cc68bdf9d4d7097c927a`.

**Confirmed CI failure** on #2012, #2013, #2014, #2015: the same test, `test_unreviewed_caveat_editorial_edit_cli_exits_two_without_stdout`, expected a SHA-256 pin rejection but used `json.dumps(..., sort_keys=True)`. That changed the iteration order of `downstream_gate_state`, which is also frozen by the source-only schema; the correct earlier rejection `required downstream gates cannot be represented as completed` made that overly specific test assertion fail. These runs completed **FAILURE (1 test)** even though Phase3 acceptance passed. The code was failing **closed**; this is a test-setup defect, not proof of a successful strategy or unsafe execution.

Fix the test to preserve source-document key ordering while changing its caveat so the intended independent SHA-256 pin rejects that exact-byte drift. Add a table-driven regression that checks this for **all five** source packets, and an independent test establishing that deliberate map-order drift continues to be rejected at the earlier gate. No production security, strategy/risk/math semantics, source pins, permissions, broker, or annual workflow changed.

This exact-parent patch adds **2** source-defined tests (**6451 proposed cumulative**) and requires fresh full historical/general and Phase3 CI before declaring green. Prior failed runs must **not** be relabeled passed. Issue #779/#820/#821 remains BLOCKED; no protected 2023 run385, separate current runner authority, StrategyV1 economic evidence, demo, live trading or order placement is permitted by source-only tests.
