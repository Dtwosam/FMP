# DEC-1517 — Complete portable Windows reserved source-device spellings

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent, one-commit tests/docs child of #1762 at `af96f87b97ae908a83e3828b7bf824d0332992d8`. Eleven synthetic unittest methods; **2,410 proposed source-defined tests**.

Prior DEC-1494 source-path guards reject standard `CON`, `PRN`, `AUX`, `NUL`, and `COM1`–`COM9` / `LPT1`–`LPT9`, but omitted the superscript-digit Windows device aliases (`COM¹`, `COM²`, `COM³`; `LPT¹`, `LPT²`, `LPT³`) and the Windows console device names `CONIN$` and `CONOUT$`. Reject these case-insensitively with optional filename extensions before Base64 decoding; preserve safe longer filenames such as `COM10.txt` or `CONINPUT.log`. Do not open paths or infer physical filesystem protection.

Eleven synthetic tests cover superscript digits and console names, case variants, controls for similar unreserved names, changed-source/workflow map refusal, safe stdin diagnostics and clean source-only review. Success has no meaning for provider authenticity, OS no-write, exclusive GitHub server admission or annual workflow permission.

Exact-head Phase 3/full historical-general CI and qualified independent review required. DEC-650/#820 protected-original witnessed OS no-write and DEC-651/#821/#779 exclusive immutable protected 2023 run385/attempt1 GitHub server admission remain **BLOCKED**. No protected execution/retry, originals/archive/artifact access, installed workflow/security changes, merges, deployment or trading.
