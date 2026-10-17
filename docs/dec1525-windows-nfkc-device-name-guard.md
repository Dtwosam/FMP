# DEC-1525 — Windows device-name checks under Unicode compatibility normalization

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent, one-commit tests/docs child of #1770 at `fe89ebd9328bdb40c90b4402a491bc1151145dc8`. Eleven synthetic methods; **2,489 proposed source-defined tests**.

Earlier portable path checks excluded ordinary Windows reserved device names and superscript-digit variants. Compatibility-form Unicode letters/numbers still allowed labels such as `ＣＯＮ.txt`, `ＣＯＭ１.txt` or `COM①.txt` whose NFKC forms are Windows device names. Extend **only** the reserved-name lexical comparison to use NFKC-normalized path components; never replace the original source label or perform filesystem access. Keep existing NFC, byte budgets, invisible Unicode and casefold/NFKC collision rules. Safe longer names such as `ＣＯＭ１０.txt` remain valid labels.

Eleven tests cover fullwidth CON/PRN/AUX/COM/LPT and console names, circled digits, non-reserved controls, changed-source and workflow maps, safe CLI non-disclosure and permanently false protected annual authorization.

Own exact-head Phase 3/full historical/general CI and qualified independent review required. DEC-650/#820 independently witnessed protected original OS no-write and DEC-651/#821/#779 immutable exclusive protected 2023 run385/attempt1 GitHub server admission remain **BLOCKED**. No protected dispatch/retry, originals/archives/artifacts, installed workflow/security changes, merges, deployment or trading.
