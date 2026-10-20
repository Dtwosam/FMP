# DEC-1948 — Exact-head historical full regression repair and Phase8A no-go handoff

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Documentation-only exact-parent child of PR #2196 at `7da52cace02e4f7e92d6a8cd7da5b929558f1077`. GitHub confirms it is **23 ahead, zero behind** PR #2173; current source-defined proposed method count **6,978** (+47 from #2173). No merges.

## Historical exact-SHA checks

- #2174–#2177: exact-head Phase3 **PASSED** and full historical/general **PASSED**.
- #2178–#2191: exact-head Phase3 **PASSED** but full historical/general **FAILED**. Every failed run stays failed, even when a later child repairs the implementation.
- #2178 full [39496009035](https://github.com/Dtwosam/FMP/actions/runs/39496009035), job 118881110892: `test_artifact_writer_rejects_nonfinite_metrics_before_directory_creation` expected `non-finite`; writer rejected NaN/inf with misleading finite-ledger conflict classification.
- #2189 full [39498469623](https://github.com/Dtwosam/FMP/actions/runs/39498469623) and #2190 full [39498712521](https://github.com/Dtwosam/FMP/actions/runs/39498712521), job 118890389345: after nonfinite-error repair, full suite still failed due uncontrolled integer-to-float conversion while adding source financing subtotal to zero float costs. #2191 full [39498992560](https://github.com/Dtwosam/FMP/actions/runs/39498992560) failed on the same cost path. None relabeled.

## Later candidate repair lineage

| Draft | Exact head SHA | Change | Own Phase3 | Own full historical/general |
|---|---|---|---|---|
| [#2192](https://github.com/Dtwosam/FMP/pull/2192) | `75bd82002f358317f654f2541c8561b9e19d3168` | Prevalidate cost subtotals (+2) | [39501782854](https://github.com/Dtwosam/FMP/actions/runs/39501782854) PASS | [39501782804](https://github.com/Dtwosam/FMP/actions/runs/39501782804) IN_PROGRESS |
| [#2193](https://github.com/Dtwosam/FMP/pull/2193) | `fa2e96760a582873a2d1e43c11f66afd9a49c7d3` | Control derived metric overflow (+1) | [39502130716](https://github.com/Dtwosam/FMP/actions/runs/39502130716) PASS | [39502130668](https://github.com/Dtwosam/FMP/actions/runs/39502130668) IN_PROGRESS |
| [#2194](https://github.com/Dtwosam/FMP/pull/2194) | `d457922f8a647f476f549d5cd49b595840e4e281` | Exact native UTC metric checkpoint (+2) | [39502353776](https://github.com/Dtwosam/FMP/actions/runs/39502353776) PASS | [39502353783](https://github.com/Dtwosam/FMP/actions/runs/39502353783) IN_PROGRESS |
| [#2195](https://github.com/Dtwosam/FMP/pull/2195) | `3164bfd67ad22fd80fb7de879531759bcaa9c05f` | Invalidate stale manifest on rewrite (+2) | [39502595104](https://github.com/Dtwosam/FMP/actions/runs/39502595104) PASS | [39502595040](https://github.com/Dtwosam/FMP/actions/runs/39502595040) IN_PROGRESS |
| [#2196](https://github.com/Dtwosam/FMP/pull/2196) | `7da52cace02e4f7e92d6a8cd7da5b929558f1077` | Exit-ordered metric streaks (+2) | [39502995411](https://github.com/Dtwosam/FMP/actions/runs/39502995411) PASS | [39502995497](https://github.com/Dtwosam/FMP/actions/runs/39502995497) IN_PROGRESS |

All five Phase3 runs are **COMPLETED SUCCESS**; all five full regressions are **IN_PROGRESS** at the checkpoint. Their future final conclusions must be checked against the exact own SHA; source fixes are not proof of a full pass until then.

**External security no-go:** #779/#820/#821 and all eight independently authenticated administrator/ref/installed workflow/real privileged OS isolation/frozen DEC609–610 provenance/fresh complete 2023 attempt inventory/separate human decision proof packages missing. Accepted annual catalogue ends 2022/run384, protected 2023/run385/attempt1 and future annual research, Strategy V1 economics, shadow/demo/Phase10/11, installed GitHub workflow/refs/ruleset/runner changes, real broker orders and capital remain BLOCKED. No protected research execution or earned profit. The dry-run synthetic tests do not prove market profitability or real-world OS isolation.

**Next source-only step:** Review exact full-suite conclusions for #2192–#2196 and investigate any independent failure; preserve source lineage and historical FAILED statuses. Seek separate qualified review and independent security proofs before any protected action.
