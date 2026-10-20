# DEC-1815 — Repair Git blob NUL terminator and adversarial text fixture

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child of #2061 `ee7c2a0704d5ba66eaea6a31a5fb4bf0d7eb9341`.

The DEC-1814 worksheet validator initially constructed a byte sequence with the *printable* backslash-plus-zero string instead of the single required NUL byte separating the Git blob header from file bytes. That incorrectly disagreed with GitHub's frozen worksheet blob. Fix the source-only formula to `b"blob " + len + bytes((0,)) + raw`, using an unambiguous integer-byte constructor. Also ensure the adversarial approval-message test adds real newlines via `bytes((10,))`, instead of escaped printable characters.

The reviewed worksheet and its exact Git blob SHA-1 `c594c97ad9dbbff1a0265256818df25300b45f4b` are unchanged. Production validity remains an **always BLOCKED** outcome (exit 3) and a mismatched/forged document remains invalid (exit 2/no stdout). There are **no new test methods** (6,638 cumulative proposed source-defined). This repairs **source-only evidence integrity**, not security approval.

No protected 2023/run385/attempt1 research, installed GitHub workflow/ref/ruleset changes, broker/demo/live operations, money or strategy profitability. The eight external independent proof packages and #779/#820/#821 remain MISSING/BLOCKED. Exact-head Phase3/full CI and qualified independent review required.
