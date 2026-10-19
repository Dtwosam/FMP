# DEC-1681 — Invalid JSON numeric literals inside array-contained evidence objects

**DRAFT / NEVER MERGE / NEVER PROMOTE.** One-commit tests/docs child of #1927 at `170cd6f0df80cf4d8f35d6e44318b07a3693f575`, adding 37 regression methods (**4,742 proposed source-defined methods**).

Six evidence-array paths (runs, CI job rows, PR comparison files, Phase 3 scenarios, Git-tree entries and merge-parent records) each receive one additional numeric member whose value has one of six illegal spellings: `01`, `+1`, `-.`, `.5`, `1.`, `1e`. Plain strict Python JSON must refuse the malformed document; bounded JSON-text and stdin must return `BUNDLE_JSON_GRAMMAR_UNREVIEWED` before any nested evidence or annual approval checks. The path-specific serializer preserves unrelated evidence keys.

Each negative case protects clean source immutability, exact safe verdict fields, no synthetic changed-source-path echo, and false protected original OS, exclusive server dispatch and annual-run flags. One clean nonauthorizing control is retained. The method-name uniqueness check remains active.

Own Phase 3/full general CI and independent qualified review required for the exact new head. Tests/docs only; no production/parser/limit/workflow/security change, protected originals/archive/artifacts, annual execution/retry, merge/deployment/trading. DEC-650/#820 and DEC-651/#821/#779 remain **BLOCKED**.
