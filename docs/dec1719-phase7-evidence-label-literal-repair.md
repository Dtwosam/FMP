# DEC-1719 — Correct Phase 7 evidence-label literal in historical audit

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent one-commit tests/docs correction to #1965 at `cf37471e7a5fcb3675fa09d75288ebb2109ced5d`.

The new DEC-1718 regression accidentally included backslash-escaped Markdown backticks in a Python source string; those are literal backslashes, not the accepted Stage 2 evidence text. The test now matches the exact frozen `PHASE7_PROMOTE_TO_SHADOW_DESIGN` label without extra escapes. This is **test-fixture-only**, changes no history, calculations, parser, runtime, workflow, risks or phase gates, and adds **zero new methods**. Cumulative proposed source-defined test count remains **5,864**.

The economic facts remain: +0.757266% at 0.2-pip, +0.262176% at 0.5-pip, -0.562118% at 1.0-pip in retrospective independent windows; none are current earnings or a real-money approval. Phase 8A 2023 run385 is still blocked by #779. Own exact-head Phase3/full historical-general CI and independent qualified review required. No protected evidence, dispatch/retry, production or broker mutation, deployment, merge or trading.