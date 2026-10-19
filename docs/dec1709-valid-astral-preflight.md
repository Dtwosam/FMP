# DEC-1709 — Valid paired supplementary Unicode reaches nested evidence review

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent tests/docs-only child of #1955 at `f245fc78283382c5e1d20285951830535539bdea`.

Adds **25 source-defined methods** (**5,753 proposed**): four valid supplementary Unicode scalar values in each of six array-contained nested evidence dictionaries, plus a clean synthetic control. JSON is serialized with `ensure_ascii=True` so supplementary scalars take paired `\uXXXX\uXXXX` escape form. Strict JSON-text and stdin review must equal direct-memory review, must not report Unicode or grammar refusal, and **must invoke the nested reviewer twice** (once for each parse route), as observed through a wrapped reviewer mock. This is the positive boundary counterpart to DEC-1708's lone-surrogate refusal.

The original synthetic input remains immutable; exact safe verdict keys, no path/marker echo, and protected annual, independent-original-OS and exclusive-server-dispatch authority false. Own exact-head Phase 3/full historical/general CI and independent qualified review required. No parser/production/limits/workflow/security changes, protected originals/archive/artifacts, annual execution/dispatch/retry, merging/deployment/trading. DEC-650/#820 and DEC-651/#821/#779 **BLOCKED**.
