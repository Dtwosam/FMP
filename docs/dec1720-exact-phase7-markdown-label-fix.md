# DEC-1720 — Preserve the exact Phase 7 published promotion label

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent test/docs correction to #1966 at `5d46432d5bdb2c678bc2288a2ce540f8981c8cc6`.

The Stage 2 historical evidence string is literally `The authoritative Stage 2 status is therefore \`PHASE7_PROMOTE_TO_SHADOW_DESIGN\`.`. The DEC-1718 fixture accidentally introduced Python backslash-escaped Markdown backticks, and the child DEC-1719 deleted the backticks entirely. This second correction uses the **exact published substring including Markdown backticks**, which is required for a test of source-bound decision fidelity. No assertion is weakened and the reference document is untouched.

Maintains the original 10 tests: 5,864 proposed source-defined methods. No production, parser, workflow, protected artifact, annual dispatch/retry, Phase 8B/demo/live, broker or trading changes.

CI on this exact head (historical/general and Phase 3) plus independent qualified review is required. Prior green Phase 3-only runs never establish the correctness of the imported DEC-1718 module. The current execution/admin blocker issue #779 remains **OPEN**.