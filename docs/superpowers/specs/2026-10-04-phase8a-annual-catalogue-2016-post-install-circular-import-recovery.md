# Phase 8A — 2016 Post-Install Circular-Import Recovery

**Date:** 2026-10-04  
**Status:** SOURCE-READY RECOVERY / RUN 378 UNCONSUMED  
**Decisions:** DEC-531 / DEC-532

## Live failure

Explicit successor installer run `37205170186` / run number 2 applied,
committed, and pushed the exact DEC-518 two-file runtime installation. Main
advanced to install commit
`525386dd68955e9f02909f9692987968ab15e516`.

The same job then failed while constructing DEC-508. Importing the receipt
source traversed DEC-507 → DEC-506 → DEC-504 → DEC-503 → annual runtime. The
installed annual runtime imports the new DEC-505 gate, and that gate imported
DEC-504 at module load time, creating a circular import.

No annual run 378 was dispatched. The annual inventory remains failed run 1,
failed run 376, and successful 2015 run 377.

## DEC-531 — Post-install runtime repair

The active DEC-505 gate defers its DEC-504 constant import until
`require_2016_execution_authorized` is actually called. The installed runtime
remains unchanged. The historical dormant gate template remains unchanged and
continues to represent the exact DEC-507 install source.

DEC-531 validates:

- the exact successful install commit;
- failed installer workflow run `37205170186`;
- successful apply, commit, and push steps;
- failure specifically at DEC-508 receipt construction;
- repaired active gate, installed runtime, and annual workflow blobs.

DEC-531 grants no dispatch authority.

## DEC-532 — Exact run-378 dispatch recovery

The recovery executor downloads the exact successful DEC-514 run-2 artifact
(`11304088642`, SHA-256
`cd455bfae7a1c91f114d9a4e35b81fcd46d7921740f0c04ff27d79978ab93231`).
It reconstructs DEC-508 from the frozen DEC-507 action and the historical
install commit rather than rerunning the install.

DEC-532 then requires:

- current main to be the repair landing;
- valid DEC-531 and reconstructed DEC-508 evidence;
- the concrete 2015 runtime binding for successful annual run 377;
- exactly annual runs 1, 376, and 377, with no run 378 or later.

Only then may it submit one fresh 2016 annual run 378 / attempt 1. The immutable
dispatch receipt records both the historical install commit and the repaired
run head.

DEC-522 accepts the original DEC-521 dispatch receipt or this exact DEC-532
recovery receipt. Its result remains read-only and 2017-locked.

## Authority boundary

No installer rerun, annual rerun/retry, run 379+, 2017+ execution, strategy
synthesis or promotion, broker mutation, order placement, real-money action, or
trading authority is added.
