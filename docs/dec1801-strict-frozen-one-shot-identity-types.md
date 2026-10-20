# DEC-1801 — Require exact types for the frozen one-shot identity in JSON

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Source-only exact-parent child of #2047 at `42cdb7cc7c5d3a839ee91dace548ca963fae6910`.

The consolidated compiler previously compared the documentary one-shot identity dictionary to `{"segment": "2023", "run_number": 385, "attempt_number": 1, "authorization": "BLOCKED"}` with Python equality. Python considers `True == 1` and `385.0 == 385` true, so a tampered documentary reporter could leak a Boolean/float numeric alias into the consolidated **JSON** even though the human Markdown canonical comparer may later reject it. Frozen irreversible run identifiers must not silently change type.

Require the one-shot record to be an ordinary dict with exactly four known fields; exact `str`, `int`, `int`, `str` types respectively; and the original BLOCKED values. Boolean aliases, floating run values, nonobjects, missing and extra approval fields are rejected *before* either format is produced. No new permission path or research action is introduced.

Adds four adversarial tests (6,600 cumulative proposed source-defined methods), including both CLI formats exit 2 with empty stdout for a Boolean attempt alias. Valid BLOCKED CLI remains exit 3. No protected 2023/run385/attempt1 dispatch, no altered main/workflow/security, no broker/demo/live trading, no money/profit claim. Eight external independent proofs and #779/#820/#821 remain MISSING/BLOCKED. Exact-head Phase3/full regression CI and independent qualified review required.
