# DEC-1807 — Lossless nested historical workflow comparison in JSON compiler

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child of PR #2053 at `b49e241d98d1285d195b347efafc94a0f1a3b3b1`.

DEC-1806 re-derives job, matrix and command-trace observations from the pinned historic fixture. Python container equality can still equate **60.0 and 60** or **1 and True** in nested, not individually typed matrix members, allowing a numeric/Boolean alias to reach JSON while appearing equal to frozen source.

Use strict sorted JSON serialization with `allow_nan=False` for the complete re-derived versus received `jobs/matrix/trace` object. Reject unsupported/nonfinite types with a controlled `InvalidHandoff`, reject any numeric alias or altered source-only Boolean with source equality failure. No schema expansion or current installed workflow access occurs; all pinned bytes and BLOCKED output remain unchanged.

Four adversarial methods (6,620 cumulative proposed source-defined) cover float nested horizon, numeric alias for a static denial indicator, nonfinite NaN and infinite metadata failing JSON+Markdown with code 2/no stdout. Normal offline reports remain code 3. None proves current GitHub runtime/rulesets, independent OS protection, fresh one-shot inventory or broker permissions. Protected 2023/run385/attempt1, shadow/demo/live, orders, real money and profitability remain BLOCKED. #779/#820/#821 external evidence unresolved; independent qualified review and full exact-head CI required.
