# DEC-1497 — Raw CI log text type and volume bounds

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent one-commit tests/docs child of #1742 at `53042b371af2475bd92caff65ce945a5bc8cd88a`. Eight new synthetic unittest methods; **2,217 proposed source-defined tests**.

The in-memory offline CI evidence reviewer accepts a `raw_ci_runner_logs` map, which can bypass JSON/stdin text length bounds when called directly. The run-map index is already capped, but its values were not independently size-limited. Enforce plain `str` log values, a maximum of 2,000,000 characters per run and 4,000,000 characters across all run logs before converting run IDs or invoking nested composite checks. Reject invalid types with `BUNDLE_RAW_LOG_TEXT_UNREVIEWED`, per-entry oversize with `BUNDLE_RAW_LOG_TEXT_OVERSIZE`, and aggregate oversize with `BUNDLE_TOTAL_RAW_LOG_OVERSIZE`. Never emit input contents as diagnostic text.

Eight tests cover too-large individual/aggregate inputs, bytes/null/subclass string types, deterministic diagnostic precedence, source non-disclosure and unchanged positive offline consistency. The total is an in-memory resource bound, not authentication of CI provider records or authorization of protected research.

Own exact-head Phase 3 and historical/general CI, plus qualified independent review, required. DEC-650/#820 independently witnessed original-file OS no-write and DEC-651/#821/#779 exclusive immutable protected 2023 run385/attempt1 GitHub server admission remain **BLOCKED**. No protected runs, dispatch/retry, originals/artifacts, installed workflow/security changes, merges, deployments or trading.
