# DEC-1810 — October 20 read-only FMP public main control-plane observation

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child of #2056 `dcbd8363603a1dd235acc64fae6e9e4f71fc4406`. This report describes API observations obtained by a read-only integration on October 20, **not** independent effective administration/security attestation or an approval of any action.

| Read-only endpoint | Observed result | Unverified requirement |
| --- | --- | --- |
| `GET /repos/Dtwosam/FMP/branches/main` | SHA `53e203133bbc141b2f48c7b8b8241d56b35166a3`; `protected:false` | Durable exclusive server-side lock, bypass and writer inventory |
| `GET /repos/Dtwosam/FMP/rulesets?includes_parents=true` | `[]` | Independently authenticated full effective repo/org/enterprise ruleset scope and bypass actors |
| `GET /repos/Dtwosam/FMP/branches/main/protection` | **HTTP 403 — Resource not accessible by integration** | Authoritative effective branch-protection configuration from a properly privileged, independent administrator |

**Interpretation:** no protected research run may be dispatched based on these observations. The API read is only a current snapshot and does not guarantee main ref continuity between SHA review and future run time; absence of listed rulesets with insufficient permissions is **not** proof of absent inherited policy, admin bypass or exclusive publisher authority. It does not verify the actual runner, OS isolation, DEC-609/610 provenance, fresh full one-shot run inventory, or separately scoped human execution approval.

**Next external steps:** independent effective privileged administrator and inherited-policy review under issue #779, separate installed runner/OS proof under #820, a reviewed no-race exclusive lock or immutable-ref amendment under #821, independent fresh inventory, and **separate human 2023/run385/attempt1 decision** only after evidence is accepted. Eight proof packages remain MISSING and the protected action is BLOCKED.

No source policy, workflow/ref/branch/ruleset, credentials, protected market data, broker/demo/live order, trade, or capital was mutated. This documentary work is not an installed security mechanism or profitability evidence. Latest cumulative proposed source-defined test methods remain **6,624**.
