# DEC-1962 — Full-manifest preflight regression repair and Phase8A no-go handoff

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Documentation-only exact-parent child of PR #2210 `2fbf505004e7ccaef9224307ae0138587446db05`, GitHub compare **37 commits ahead/zero behind #2173**. Source-defined proposed method count **6,998**, +14 since #2200; source-only drafts remain unmerged.

## Exact historical CI facts — never rewrite failure outcomes

| PR / exact check | Full historical/general outcome | Finding |
|---|---|---|
| #2174–#2177 and #2192–#2197 | **SUCCESS on each own SHA** | Fully verified repairs/ancestry only at their exact commits |
| #2178–#2191 | **FAIL on each own SHA** | Historical financial artifact message and cost-aggregate regressions |
| [#2198 run 39503736058](https://github.com/Dtwosam/FMP/actions/runs/39503736058) | **FAIL** | Test forged path `metrics.json` for already first sorted `metrics.json`; not a real duplicate |
| [#2199 run 39503910878](https://github.com/Dtwosam/FMP/actions/runs/39503910878) | **FAIL** | Same false duplicate fixture plus two duplicate JSON keys whose hook errors were overbroadly masked |
| [#2200 run 39504137726](https://github.com/Dtwosam/FMP/actions/runs/39504137726) | **FAIL** | Same three verifier-regression test signatures confirmed by logs |
| [#2203 run 39506202032](https://github.com/Dtwosam/FMP/actions/runs/39506202032) | **FAIL** | Real duplicate-path fixture now triggers mismatched original SHA256 before path rejections in four cases; two inherited masked duplicate-key cases |

## Independent candidate repairs and improved verifier

#2201 limits memory via 1 MiB SHA256 chunks. #2202 opens no-follow regular file descriptors for fixed artifacts. #2203 repairs false duplicate test inputs; #2204 narrows parser error trapping to preserve exact duplicate JSON key refusals. #2205 denies lexical linked ancestors, #2206 enforces canonical manifest path order, and #2207 pins every artifact open to the same no-follow O_DIRECTORY root fd. #2208 and #2209 are documentation-only security/CI and independent proof-intake checkpoints.

**#2210 DEC-1961**, `2fbf505004e7ccaef9224307ae0138587446db05`, changes the verifier from one mixed validate-and-hash loop into two passes: **complete manifest schema, path uniqueness and fixed canonical order admission first, then file descriptor reads and streaming byte hash checks**. Two regression methods assert no payload is opened when an early duplicate path or later malformed digest exists. Own [Phase3 run 39508334492](https://github.com/Dtwosam/FMP/actions/runs/39508334492) **PASS**. Own [full run 39508334574](https://github.com/Dtwosam/FMP/actions/runs/39508334574) **IN_PROGRESS** at snapshot, therefore no claim this repair is fully green. Every newer draft needs its own exact-SHA full historical/general result and qualified review; older failures remain FAILED.

**Unchanged external safety stop:** Phase8A #779/#820/#821 and all eight independent administrator/no-bypass server-ref/installed three-job early workflow/privileged runner OS isolation/frozen DEC609–610 provenance/fresh 2023 one-shot inventory/separate human action authorization proof packages are MISSING. The DEC-1960 source-only intake worksheet is merely a collection guide and cannot supply or approve any external proof. Accepted annual-first research catalogue ends at 2022/run384. Protected 2023/run385/attempt1 and future annual research, Strategy V1 economic qualification, shadow/demo/Phase10/11, installed GitHub refs/workflows/rulesets/runners, brokers/orders/live funds remain BLOCKED. No protected research, merge, capital, trading or earned profit.

**Next source-only continuation:** Read exact own full CI for #2201–#2210, investigate and preserve any additional failure signatures, and revise only through narrowly scoped dependent drafts. Security owner evidence and a separate human decision govern protected run admission, not synthetic test counts or documentation.
