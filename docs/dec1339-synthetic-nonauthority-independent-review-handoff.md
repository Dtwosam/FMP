# DEC-1339 — Synthetic rejection tests versus independently verified protected admission: reviewer handoff

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit documentation-only child of #1562 DEC-1338 at `eb4e0bfd54eccd3637d1b6ce1a61e59b941f01ce`. **924 distinct source-defined test methods unchanged**. No protected annual source/evidence, run385 execution/attempt/retry/dispatch, production deployment, workflow/ruleset/permission modification, brokerage or trading.

## Scope of the current implementation

The recently added `scripts/dec1330_synthetic_annual_gate_proof_nonauthorizing.py` and its two `tests/test_dec1330_*.py` and `tests/test_dec1335_*.py` / `tests/test_dec1338_*.py` groups are an **inert source-only negative diagnostic**. They deliberately examine only synthetic Python dictionaries; there is no authenticated proof provider, no true protected-source path, no actual OS no-write policy binding, no runner/admission integration, and no network, GitHub, broker or annual inventory access. Even an all-green synthetic claim is always blocked and cannot become execution authority.

| Draft | Concrete addition | Persistent hard stop |
| --- | --- | --- |
| #1554 DEC-1330 | Source-only pure negative classifier and 12 test methods | Every packet permanently status BLOCKED, all protected/dispatch/trading flags false |
| #1555 DEC-1331 | +3 tests: nonempty SHA identity vs missing/equal/mismatch | Equal caller-supplied expected/observed strings never authenticate an immutable ref |
| #1556 DEC-1332 | +3 tests: exact integer run385 and attempt1 identity | `True == 1` or `385.0 == 385` cannot spoof syntactic slot identity; proper integers still nonauthorizing |
| #1557 DEC-1333 | Reviewer matrix for native O_TRUNC and synthetic claims | Documentation only, no installed execution controller |
| #1558 DEC-1334 | +4 tests: reject dict subclasses/custom Mapping getters | Plain dict checks prevent inherited caller-defined `get` behavior from controlling review |
| #1559 DEC-1335 | +5 tests: AST import/call boundary, patched host I/O, fresh result isolation, forged all-green packet | Static spellings/runtime mocks are defense in depth, **not formal side-effect or security proofs** |
| #1560 DEC-1336 | +4 tests: require exact built-in strings before proof, outcome and SHA equality checks | Caller-defined scalar `__eq__` cannot be asked to decide evidence or outcome |
| #1561 DEC-1337 | +4 tests: reject colliding nonstring keys even in plain dicts | Custom dictionary-key `__eq__` never consulted on known-field lookup |
| #1562 DEC-1338 | +4 tests: 128 flag combinations, proof/independence, outcome/attempt and SHA cross-products | Every permutation remains BLOCKED and all authority flags remain FALSE |

## Deliverables still required for an authorized *future* protected admission decision

| Independent owner / action | Concrete authenticated evidence required | Current disposition |
| --- | --- | --- |
| Protected source custodian | Identity of real protected original annual source(s), exact bytes/content attestations, all filesystem aliases and mount/namespace coverage | **NOT SUPPLIED — BLOCKED** |
| OS/storage security owner | Independently installed, verified and time-scoped policy enforcing actual no-write against executor and approved threat-model bypasses, including preexisting descriptors, mappings, O_RDONLY|O_TRUNC, fallocate hole-punch, procfd aliases, administrative and mount bypasses | **NOT INSTALLED / NOT VERIFIED — BLOCKED** |
| Repository/workflow administrator | Independently enforced exclusive immutable approved workflow/ref/SHA identity gate *before checkout, dependencies and any protected evidence bytes*, across all three required job paths | **NOT INSTALLED / NOT VERIFIED — BLOCKED** |
| Authorized run inventory owner | Fresh independently attested annual slot inventory proving one legitimate run385 attempt1 remains available and no race or replacement is possible | **NOT ATTESTED — BLOCKED** |
| Qualified independent security reviewer | Signed complete packet linking exact protected original identity, OS policy and no-bypass scope, admission timing, ref/SHA binding, deployment provenance and all negative controls | **NOT APPROVED — BLOCKED** |
| Separately empowered action authority | New narrowly scoped one-shot decision *after* all independent gates pass, with terminal no-retry/no-attempt2 behavior on ambiguity/failure | **NO AUTHORIZATION — BLOCKED** |

The repository's existing `docs/dec1320-independent-protected-no-write-and-annual-admission-acceptance-contract.md` is the noninstalled reviewer proof contract, and older DEC-624/run385 three-layer ref/SHA and immutable-tag feasibility documents are source-only architectural history. The installed three-job workflow's tag-ref limitation cannot be solved by merely providing an unverified tag or an SHA in a chat/test. Neither the local generated PUBLIC original-source+parent inotify tests nor anonymous memfd seal tests can be relabeled as independent protected OS no-write.

## Verification policy

Each draft and every exact commit in its strict one-commit lineage must independently complete **both Phase3 acceptance and the entire full historical `tests`** successfully before its own head is called fully CI-verified. A new passing descendant cannot retroactively change failed historical exact-head results. Closed superseded unmerged siblings are not silently counted as verified canonical ancestors. CI-successful source-only negative tests **never** imply qualified independent security review or any permission to handle protected annual evidence. All PRs remain **DRAFT / NEVER MERGE / NEVER PROMOTE**.

Hard gates: independent protected no-write **DEC-650/#820 BLOCKED**; exclusive immutable annual run385 admission **DEC-651/#821/#779 BLOCKED**; run/test/retry/rerun/dispatch, protected source/evidence access, production/runner/workflow changes, broker/trading, merge/promotion all forbidden.
