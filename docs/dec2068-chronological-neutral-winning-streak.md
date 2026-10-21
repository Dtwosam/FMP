# DEC-2068 — Chronological close order places neutral before consecutive wins

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2316 `0b41fd307fb9a9103ebe47ceb3b68af3e9cf9ee1`.

A source run realizes a win then flat close at UTC T+1 and a second win at T+2. Its engine equity checkpoints remain W/FLAT/W, but the writer sorts same-time IDs M-FLAT then Z-EARLY-WIN; the last trade A-LATE-WIN must follow both due its later UTC timestamp, irrespective of its alphabetically earlier identifier. Thus canonical trade order is FLAT/WIN/WIN with longest winning streak **two**, win rate **2/3**, and valid null profit factor because neither of the two directional closes loses. This is a separate cross-time ordering witness from equal-UTC DEC-2062.

Four source-defined tests accept that valid mixed chronological/canonical source report and reject a manifest-rehashed realization-order short win streak, a forged full win rate that ignores the breakeven denominator, or a checkpoint timestamp improperly moved before the later winning close. All tampered artifacts pass manifest digest verification before independent semantic audit refuses them. Production unchanged.

**7,343 cumulative proposed methods** (+4). Own exact-head Phase3 and full historical/general CI required, with no pass credit to pending results. Prior failed #2300–#2312 full suites remain failed; #2313 is last fully green parent until descendant suites complete. Phase8A #779/#820/#821 and eight independent security proof packages remain BLOCKED. No protected research, workflow/ref/runner mutation, merge, strategy promotion, broker orders or real capital.
