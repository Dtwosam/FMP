# DEC-1383 — Fail-closed review for unknown jobs and duplicate event keys

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit test/docs child #1606 DEC-1382 at `fa7dea1ae6008402bf987ec40cce56beba0a3468`; adds two negative tests and tightens only that earlier source-review parser. **1,144 proposed source-defined unit-test methods**.

The initial read-only token/trigger source diagnostic extracted *only known annual job names*, so adding an unexpected fourth job could be silently invisible, while splitting the first top-level `on:` block would not reject a second `on:` block. New source-only tests mutate **in-memory** committed YAML text, adding an extra job or a duplicate top-level event declaration, and require the diagnostic to record an explicit review failure. The diagnostic now parses every two-space job heading and demands the complete ordered three-job inventory, and rejects more than one event block before admitting source shape. No actual YAML was changed and no workflow was executed.

These checks do not claim to be a general YAML parser, nor do they grant dispatch even for compliant source. The non-authorizing token scope cannot enforce immutable ref admission or read-only filesystem semantics. Real GitHub `main` remains unprotected under the latest GET snapshot; OS original no-write DEC-650/#820 and exclusive 2023 run385/attempt1 DEC-651/#821/#779 remain **BLOCKED**.

Requires independent qualified review, successful exact-head Phase 3 and full historical suite. No protected annual data/evidence access, workflow dispatch/retry, GitHub settings/installed workflows/rulesets, broker/trading, merge or promotion.
