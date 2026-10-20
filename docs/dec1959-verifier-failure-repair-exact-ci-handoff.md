# DEC-1959 — Pinned Phase3 artifact verifier and exact-commit CI security no-go handoff

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Documentation-only exact-parent child of PR #2207 `9f1cb47584300bffdccf3440cd18b47d5a5ced0e`, 34 commits ahead/0 behind #2173. **6,996 cumulative proposed source-defined test methods** (+12 since #2200). All PRs on this dependency line are source-only open draft and unmerged.

## Exact-commit CI outcome audit

- #2174–#2177 and #2192–#2197: **own Phase3 PASS and own full historical/general PASS**, separately observed.
- #2178–#2191: own Phase3 PASS, own full historical/general **FAIL**. Do not erase earlier negative outcomes just because later lineage repaired the underlying code.
- [#2198](https://github.com/Dtwosam/FMP/pull/2198) full [39503736058](https://github.com/Dtwosam/FMP/actions/runs/39503736058) **FAIL**: synthetic duplicate-path test reused already first sorted `metrics.json`, incorrectly expecting invalid input when unchanged.
- [#2199](https://github.com/Dtwosam/FMP/pull/2199) full [39503910878](https://github.com/Dtwosam/FMP/actions/runs/39503910878) **FAIL**: same fixture plus two duplicate JSON key tests expected `"duplicate JSON key"`, but the verifier's overbroad `except ValueError` rewrote precise errors to `"valid JSON"`. Both defects have narrow later repairs; failures stay failed.
- #2200 own Phase3 SUCCESS, own full historical/general **IN_PROGRESS** at observation.

## Later draft lineage (all Phase3 successful; full suites still running)

| Draft | Exact head SHA | Implemented source/tests change | Own Phase3 | Own full |
|---|---|---|---|---|
| [#2201](https://github.com/Dtwosam/FMP/pull/2201) | `95c5c0bd4a254d860964e99afba44b93beaa2d72` | Stream SHA256 / 1MiB (+2) | [39505766356](https://github.com/Dtwosam/FMP/actions/runs/39505766356) PASS | [39505766213](https://github.com/Dtwosam/FMP/actions/runs/39505766213) IN_PROGRESS |
| [#2202](https://github.com/Dtwosam/FMP/pull/2202) | `e22ed4d51bf92a054710df18e1cf3b9b7659353c` | No-follow descriptor leaves (+2) | [39506008380](https://github.com/Dtwosam/FMP/actions/runs/39506008380) PASS | [39506008372](https://github.com/Dtwosam/FMP/actions/runs/39506008372) IN_PROGRESS |
| [#2203](https://github.com/Dtwosam/FMP/pull/2203) | `198233bc901e5a99cc3aefa82eff47b5c2f99ab5` | Fix duplicate-path test fixture (+1) | [39506202495](https://github.com/Dtwosam/FMP/actions/runs/39506202495) PASS | [39506202032](https://github.com/Dtwosam/FMP/actions/runs/39506202032) IN_PROGRESS |
| [#2204](https://github.com/Dtwosam/FMP/pull/2204) | `2ab5e6802259aac29304affbca4c06981ba16095` | Preserve duplicate key error (+1) | [39506448039](https://github.com/Dtwosam/FMP/actions/runs/39506448039) PASS | [39506447976](https://github.com/Dtwosam/FMP/actions/runs/39506447976) IN_PROGRESS |
| [#2205](https://github.com/Dtwosam/FMP/pull/2205) | `0f40d1ce465b3b85718b3ee6965f6cfeddec9253` | Deny symlink ancestors (+2) | [39506700092](https://github.com/Dtwosam/FMP/actions/runs/39506700092) PASS | [39506700052](https://github.com/Dtwosam/FMP/actions/runs/39506700052) IN_PROGRESS |
| [#2206](https://github.com/Dtwosam/FMP/pull/2206) | `fc07146651e42776d67707f3a709b94eb45f37d2` | Require canonical file order (+2) | [39506920063](https://github.com/Dtwosam/FMP/actions/runs/39506920063) PASS | [39506920103](https://github.com/Dtwosam/FMP/actions/runs/39506920103) IN_PROGRESS |
| [#2207](https://github.com/Dtwosam/FMP/pull/2207) | `9f1cb47584300bffdccf3440cd18b47d5a5ced0e` | Pinned O_DIRECTORY dir_fd opens (+2) | [39507178576](https://github.com/Dtwosam/FMP/actions/runs/39507178576) PASS | [39507178945](https://github.com/Dtwosam/FMP/actions/runs/39507178945) IN_PROGRESS |

DEC-1954 corrects the false duplicate input. DEC-1955 fixes classification without silently ignoring malformed JSON. All five fixed leaf opens are now pinned to a no-follow O_DIRECTORY root fd with fixed basename and no-follow regular-file checks; hash streams have bounded memory and writer's canonical filename order is required. Lexical parent checks and directory fd pinning mitigate some ordinary redirection but do not prove race-free ancestor traversal, bind mount invariants, independent privileged runner OS security, external quote provenance or real trading performance. New tests require own exact full-suite conclusions before repairs are credited.

**Independent external Phase8A no-go:** #779/#820/#821 and all eight independently attested administrator/no-bypass server ref/installed 3-job early workflow/real privileged OS isolation/frozen DEC609–610 provenance/fresh 2023 attempt inventory/separate human authorization packages MISSING/BLOCKED. Accepted annual catalogue through 2022/run384. Protected 2023/run385/attempt1, later annual research, Strategy V1 economics, shadow/demo/live broker funds and installed GitHub workflows/refs/rulesets/runner changes forbidden. No protected research dispatch, no merge, orders, real capital or verified profit.

**Next source-only work:** Check exact-head full historical/general suites for #2200–#2207 and any subsequent drafts. Any failure must remain explicitly recorded and have a separate narrow dependent source-only repair. Security and protected 2023 authorization require independent external proof owners and a separate human action decision.
