# DEC-1775 — Published Phase 7 calendar partition audit (documentation-only)

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent child of PR #2021 at `adeee76a59eb5ce8e3848cbd4acbf49279d32aa8`. The frozen source-document SHA-1, SHA-256 and historical Stage 2 artifact lineage remain unchanged.

The Phase 7 Stage 2 USDJPY 15m `session_breakout` replay now checks all seven **published scored date intervals** against the exact 2025-01-01 through 2026-08-21-exclusive sequence. It rejects missing, swapped, gapped, overlapping or lengthened windows. Each window's *documented* warm-up is the immediately preceding seven calendar days, ending at the scored interval's inclusive start and excluded from that window's scored dates. The last window is explicitly **partial 2026 Q3**, not a completed quarter.

This is **not independent verification that actual bars obeyed the documented partition, that training/labels did not leak, or that the original runner was isolated**. It reads only the original 6,100-character published historical Markdown and does not download source artifacts, access protected 2023 annual data, or run any model. The output marks actual bar-level non-leakage **NOT REAUTHENTICATED**.

Adds **7** adversarial chronology, cutoff, warm-up and no-authority tests (**6479 proposed cumulative source-defined**). Ordinary retrospective output continues exit 3, invalid source exit 2, with no broker or workflow path. Protected annual 2023/run 385/attempt 1, #779/#820/#821 admin/runner/review blockers, Strategy V1 profitability, prospective shadow, demo/live/real-money orders remain BLOCKED. Exact-head Phase 3/full historical-general CI and independent qualified review required.
