# DEC-1421 — Reject unparsed first annual matrix row source prefix

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit tests/docs child #1644 DEC-1420 at a158fd051f41d5480cdfc20f050f891c995ca982. Four new tests; **1,449 proposed source-defined methods**.

The DEC-1410 literal matrix text parser split the source at exact `- symbol: ` row markers and discarded the text before the first marker. A malformed first row identifier or unexpected prefix could be silently discarded, turning an unknown-row source change into a missing-combination warning rather than immediate syntax rejection. DEC-1420 also added a negative fixture expecting MATRIX_FIELDS_DRIFT for a renamed first row, but the first-row marker had already been lost before the field inventory check; that expected diagnostic was incorrect.

The forward-only correction fails closed on any non-whitespace prefix before the first recognized row and updates the specific fixture to expect MATRIX_SOURCE_SHAPE_UNREVIEWED. Additional in-memory negative cases pin this behavior and ensure the existing literal source checks never treat the changed prefix as authenticated.

No installed workflow, GitHub security setting, annual code or protected data is changed or accessed. This is not a YAML evaluator, OS no-write proof, GitHub immutable source admission or authorization for run385/attempt1. Own exact-head Phase3 and full historical CI plus qualified review mandatory. DEC-650/#820 real runner original OS protection and DEC-651/#821/#779 exclusive immutable dispatch remain BLOCKED. No annual dispatch/retry, merge, promotion, production or trading.
