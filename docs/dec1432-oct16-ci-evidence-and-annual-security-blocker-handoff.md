# DEC-1432 — October 16 dual-CI verified lineage versus independent protected annual gates

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit documentation-only child of #1655 DEC-1431 at efcec311c9bfdbe98c18bbb37c9c4a1b01f7113b; **1,547 proposed source-defined methods** unchanged.

## Read-only exact-head CI evidence (snapshot, not execution consent)

At GitHub PR [#1649](https://github.com/Dtwosam/FMP/pull/1649) exact head **5a322ee18009e5127e8cb3460cf838f396e76b0b**, base **a27209faee57dee1a8718aa60b15bb027873cfa7**, both required independent pull_request workflow runs completed successfully in first attempts:

- [Historical/general CI workflow run 38973051079](https://github.com/Dtwosam/FMP/actions/runs/38973051079): workflow_id 339764246, path .github/workflows/tests.yml, status completed / conclusion success / event pull_request / attempt 1. Exact head and PR head/base association matched. One unit-tests job succeeded (117215797370). The real job listed completed-success DEC-611 immutability audit (step 223), DEC-612 lock readiness (225), DEC-613 administrator handoff (227), DEC-626 precheckout expression rehearsal (240), historical/general unit suite (241), and package compile (242).
- [Phase 3 acceptance run 38973051093](https://github.com/Dtwosam/FMP/actions/runs/38973051093): workflow_id 357768849, path .github/workflows/phase3-acceptance.yml, completed/success, event pull_request, attempt 1. Exact head and PR associations matched. One acceptance job succeeded (117215796850); generation, shape verification and acceptance evidence upload all completed successfully (steps 5, 6, 7).

The previous chain through #1648 also has both required suites successful at each exact corrective head #1645–#1648. Earlier exact-head failures **must stay failed**: #1634–#1636 parser defect, #1641 inline manual event scalar, #1644 wrong initial first-row fixture. Forward repairs exist; none rewrites those original run conclusions.

#1650–#1655 are newer strict draft descendants with Phase3 passes where completed and full historical runs still pending at the last recorded snapshot. **Do not mark them fully green merely because previous heads are green**, and do not mark this handoff doc verified until its own two suites complete. Test-method counts are source-defined draft numbers, not full-suite executed-case counts.

## Independently required annual run385/attempt1 security gates — unchanged BLOCKED

**DEC-650 / [#820](https://github.com/Dtwosam/FMP/pull/820): BLOCKED.** A separately qualified OS/runner/storage custodian must independently attest and witness *real original protected input* no-write isolation across preflight, 18 annual cells and freeze, aliases/mounts/hardlinks, UID/caps/privilege, standard/inherited descriptors, children, external output publication and uploader. Synthetic source test cases, inotify proxies, default checkout permissions or a green CI cannot substitute.

**DEC-651 / [#821](https://github.com/Dtwosam/FMP/pull/821) / [#779](https://github.com/Dtwosam/FMP/issues/779): BLOCKED.** A separately authorized GitHub administrator must prove an exclusive immutable server-side source ref/SHA and a single permitted workflow dispatcher with all bypass principals excluded **before** the irreversible annual **2023 run number 385 / attempt1** is allocated. Prior 2022 freeze run expected is **37663157285**. A late in-job GITHUB_SHA shape check, GitHub concurrency, read-only token scopes, source pin to main, short-lived lock witness, last-second REST ref poll, or post-allocation rejection is not atomic admission.

Current separate read-only GET observations: **main** still at commit 53e203133bbc141b2f48c7b8b8241d56b35166a3, protected=false; repository rulesets list empty; annual workflow source blob **09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1** unchanged. Those observations are neither a complete organization-level privileges inventory nor evidence of all branch/tag bypass paths. A fresh annual history run-385 absence assertion is intentionally **not** made in this packet, because this step did not obtain full authoritative annual workflow run history.

## Authorized scope and no-go

Continue only reviewed source/docs and synthetic fixture work in strict one-commit draft children, no merges or promotions, and exact-head CI verification. No protected annual dispatch, no dry-run, retry or replacement attempt; no original protected archive read/write; no repository security/branch/tag/ruleset/permission mutation; no installed annual workflow/runtime change; no brokerage or trading. An external administrator's **independent documented OS and GitHub admission verdict** remains necessary before any separate future authorization discussion.
