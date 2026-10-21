# DEC-1987 — Canonical summary and metrics JSON evidence

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent successor to PR #2235 at `07bf3324870e21cab415a80208651ea0c1a92629`.

The writer emits summary.json and metrics.json with stable sorted-key, indented UTF-8 JSON followed by exactly one LF. The optional audit verifies manifest digests, semantic record values and counts but previously accepted a self-rehashed summary or metrics file with equivalent values and noncanonical whitespace or key ordering. It now saves the bytes read from each manifest-matched file and, **only after all existing semantic rejections**, checks their bytes match `_stable_json_bytes` of the parsed dictionary. This preserves specific error reasons for forged economic claims and changes neither canonical writer nor low-level checksum verifier.

Three synthetic tests cover normal canonical output, a compact self-rehashed summary and a re-ordered self-rehashed metrics JSON. Projected cumulative source-defined methods **7,059** (+3). Own Phase3 and full historical/general regression must validate the exact commit. Older CI PASS/FAIL snapshots remain unchanged.

Phase8A #779/#820/#821 and eight independent external security proofs outstanding. No protected annual research, strategy promotion, broker, capital, merge or installed runner/ref/workflow mutation. **DRAFT NEVER MERGE NEVER PROMOTE.**
