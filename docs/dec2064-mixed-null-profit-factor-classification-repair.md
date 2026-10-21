# DEC-2064 — Mixed-profit-factor null error-classification repair

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent #2312 `d56bbfa003ee6878b2c5eeda3a2cdab88169db0f`.

The #2301 exact-head historical/general suite [39635164574](https://github.com/Dtwosam/FMP/actions/runs/39635164574) finished **FAILED** with two test assertion mismatches in 12,174 executed tests (714 skipped). First: the preexisting DEC-2051 loss-only null-profit-factor test failed with the classification corrected later by DEC-2059/#2308. Second: DEC-2052's mixed-win/loss same-timestamp null-profit-factor test expected `metric profit_factor conflicts with trade ledger`, but the established read-only audit instead raised `artifact report metric profit_factor must be finite numeric`, which correctly rejects the forged `null` value when a nonzero gross-loss denominator makes a finite ratio mandatory.

This narrow repair changes **only** the second test assertion's expected message. It does not alter the engine, the read-only verifier, or the fixture's tampering behavior. The #2300 and #2301 completed failures remain FAILED forever; descendant pending outcomes are not silently credited. The latest full-green base is still #2299 until a post-repair head completes its own full suite.

**7,322 cumulative proposed test methods** (+0). Own exact-head Phase3 and complete historical/general regression required. Phase8A #779/#820/#821 and eight independent security proof packages remain BLOCKED. No protected research, installed workflow/ref/runner changes, merging, strategy promotion, broker orders or real capital.
