# DEC-1682 — Finite valid JSON numerics inside array-contained evidence retain source-review parity

**DRAFT / NEVER MERGE / NEVER PROMOTE.** One-commit tests/docs child of #1928 at `f39ba2895d356d5f1b4ec689f645895df59f57e5`, adding 31 synthetic regression methods (**4,773 proposed**).

The companion to DEC-1681's malformed numeric literals places one extra finite numeric member inside each of six array-containing evidence categories. Five strictly valid spellings (`0`, `-0`, `1.0`, `1e+0`, `1E-0`) must parse and produce the same source-only verdict from direct in-memory review, bounded JSON text, and stdin. An extra unreviewed field may still be semantically rejected; these tests do not assert the extra field is admissible or grant independent/protected annual-run proof.

Each case checks no false JSON grammar/Unicode refusal, no mutation of the original clean source fixture, exactly the safe verdict fields, no sample source-path echo and false independent-original OS, exclusive dispatch or annual-run flags. One clean synthetic control remains.

Own exact-head Phase 3/full general CI and qualified independent review required. Tests/docs only; no production/parser/limit/workflow/security change, protected originals/archive/artifacts, annual execution/retry, merging/deployment or trading. DEC-650/#820 and DEC-651/#821/#779 remain **BLOCKED**.
