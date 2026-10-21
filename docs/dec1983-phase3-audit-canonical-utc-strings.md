# DEC-1983 — Canonical UTC string timestamps in stored Phase3 audit

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2231 `b3f9006c921c32431cf2e03f89b71eaeea2f749c`.

The stored-evidence auditor checked only that JSON timestamps ended with `Z` and parsed to a UTC datetime. Python's `datetime.fromisoformat` accepts equivalent but noncanonical spellings, such as a space separator instead of `T`, omitted seconds or redundant fractional-zero suffixes. The canonical writer emits only `datetime.isoformat().replace("+00:00", "Z")`.

Roundtrip each parsed timestamp back through precisely that writer serialization and require byte-for-byte equality of the original JSON string. Apply to trade entry/exit, rejection decision/evaluation and equity checkpoint timestamps without weakening the existing chronology checks. Three synthetic tests forge and rehash a space-separated trade date, minute-precision rejection date and redundant-fraction checkpoint date. Each must pass the low-level SHA256 verifier but fail the optional audit.

**7,050 cumulative proposed source-defined tests** (+3), not a claim about passed full CI or profitable trading. Own exact-head Phase3/full historical-general regression plus independent source review required. Historical failures still failed.

Phase8A security issues #779/#820/#821 and eight independent proof packages remain missing. No protected 2023/run385/attempt1, later research, strategy promotion, GitHub installed refs/workflows/runners, broker trades, merges or capital.
