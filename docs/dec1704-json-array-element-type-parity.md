# DEC-1704 — Legal JSON types in array-element evidence slots

**DRAFT / NEVER MERGE / NEVER PROMOTE.** One-commit exact-parent tests/docs child of #1950 at `77950205a323a575790f5f2cb053c398e2d65ff7`.

Adds **37 source-defined methods** (**5,610 proposed total**): six JSON-legal replacement values (`null`, `true`, `false`, a synthetic string, empty array and integer zero) in the first element of each of six required nested evidence arrays, plus clean control. Each replacement is valid JSON but not an expected evidence object; strict JSON-text/stdin review must reach the same nested evidence validation outcome as direct-memory review. Such values must not be falsely classified as JSON grammar or Unicode failures, and must never grant protected authority.

A deep copy of synthetic evidence is changed; original caller fixture remains immutable. Exact safe stdout verdict keys, no synthetic marker or path echo and false independent-original-OS, exclusive-server-dispatch and annual-run authority flags. Own exact-head Phase3/full historical-general CI and qualified independent review required. Tests/docs only, no parser/production/limits/workflow/security changes, protected originals/archive/artifacts, annual dispatch/retry, merge/deployment/trading. DEC-650/#820 and DEC-651/#821/#779 **BLOCKED**.
