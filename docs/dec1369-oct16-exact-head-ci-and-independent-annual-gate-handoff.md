# DEC-1369 — Oct 16 actual-source and exact-head CI reviewer handoff

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict docs-only one-commit child of #1592 DEC-1368 at `cb476143a71c0879e0b9d58fe5dfcf76a38d088f`; **1,042 proposed source-defined unittest methods unchanged**. No production/runtime/trading, protected annual artifacts or GitHub workflow/ruleset/permission change. This is a timestamped CI observation, not an assertion that pending runs later passed.

## Exact-head CI facts observed October 16, 2026

| PRs | Phase 3 | Full historical suite | Source-defined tests |
| --- | --- | --- | ---: |
| #1578 DEC-1354 | completed SUCCESS | completed SUCCESS | 972 |
| #1579–#1585 (each **original exact SHA**) | completed SUCCESS | completed **FAILURE** | 976–1,000 |
| #1586 DEC-1362 `9adfbb63b20b07b6090b3f0ef891e0e61a4cd2f6` | completed SUCCESS | completed SUCCESS: 5,901 executions, 702 skipped, zero failures | 1,000 |
| #1587 DEC-1363 `29e84e5ce668ec93e4d4df7f4ed7b2f09544bb6b` | completed SUCCESS | completed SUCCESS: 5,907 executions, 702 skipped, zero failures | 1,006 |
| #1588 DEC-1364 | completed SUCCESS | still IN PROGRESS at this snapshot | 1,011 |
| #1589 DEC-1365 | completed SUCCESS | still IN PROGRESS at this snapshot | 1,023 |
| #1590 DEC-1366 | completed SUCCESS | still IN PROGRESS at this snapshot; one source test has a **known incorrect indentation expectation** | 1,032 |
| #1591 DEC-1367 | completed SUCCESS | still IN PROGRESS at this snapshot; forward-only indentation repair | 1,032 |
| #1592 DEC-1368 | completed SUCCESS | still IN PROGRESS at this snapshot | 1,042 |

**Preserve original test verdicts.** The #1579–#1585 historical failures come from tests authored for the synthetic runner key guard which invoked hostile dictionary equality during fixture insertion, plus source audit tests reading mutable checkout YAML after another historical test had removed that file from the working tree. The committed YAML blob was present in Git. #1586 forward-repairs fixture construction and reads source from local `git show HEAD:path`. #1586 and #1587 are independently green for both CI suites. Their success cannot rewrite original failed commits.

The #1590 2015 predecessor test used a literal 15-space assertion for an existing 14-space line. #1591 fixes that error in a **new** commit; do not retroactively classify #1590 until its original exact-head historical CI completes, and never rewrite its failure if observed.

## Traceability of new source-only coverage

- **#1586:** forward-only tests-only repair (1,000 methods unchanged).
- **#1587:** +6 methods exposing preflight snapshot metadata reads and `if: always()` upload attempt after failure of the later execution gate.
- **#1588:** +5 methods pin exact committed Git blobs for current YAML, CLI, 2023 runtime gate and read-only source order audit.
- **#1589:** +12 methods parsing the 18-cell symbol/timeframe/horizon matrix and archive ID/digest pair bindings.
- **#1590:** +9 methods for predecessor 2022 freeze metadata, artifact digest, run ID and CLI evidence binding.
- **#1591:** forward-only fixture adjustment, no new methods.
- **#1592:** +10 methods for four cell archives, SHA check before extraction, distinct staging paths, root discovery and checkout-relative outputs.

Source-only observations **are not an installation, an end-to-end independent OS denial proof or a verified production GitHub admission**. They do not measure any protected annual results.

## External acceptance still missing and outside authority of this draft

1. **DEC-650/#820 — genuine original protected no-write: BLOCKED.** Independent OS/storage custodian must attest actual protected source object aliases, read-only bind/mount/policy before first access, inherited write-capability closure (open FD / mmap / dirfd / procfd / stdio), UID/caps/sudo/no-new-privileges, dedicated writable scratch and trusted external uploader, positive nonprotected report publication, authenticated cleanup and lifecycle, real malicious-write denial on the intended runner (not root-skipped synthetic CI). Existing CLI and workflow write checkout-relative scratch; they have **not** been restructured here.
2. **DEC-651/#821/#779 — immutable exclusive 2023 run385/attempt1 dispatch: BLOCKED.** Independent GitHub administrator and reviewer must establish either a completely audited server-enforced exclusive freeze of mutable main through the actual single-authority dispatch, or separately amend and independently approve an immutable tag pathway with retested main-only workflow gates. Must externally bind approved installed workflow/ref/resolved SHA **before** checkout, dependency installation, metadata access or run allocation. Current in-job `GITHUB_REF` and `GITHUB_SHA` plus 2023 runtime 40-hex syntax check cannot supply this.
3. **Fresh one-shot decision — BLOCKED.** Reauthenticate protected predecessor/run history and no-385+ inventory with independent authorized custodian; only after both external security gates and qualified review could a *separate explicit* one-shot action decision even be considered. Never test a dispatch or retry a possibly allocated run to verify this condition. Failure, ambiguity and incomplete evidence mean terminal hold.

**Not authorized:** protected annual data/evidence reading; 2023 annual run, retry, replacement or dispatch; workflow, tag, ruleset, permission and installed runner changes; Phase 8B, strategy synthesis/promotion, demo/live orders, broker mutation, trading, merges or promotions. No claim that even a fully green 1,042-test draft makes DEC-650 or DEC-651 PASS.
