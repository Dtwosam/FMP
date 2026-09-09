# fmp-raw-ingest

Private ingestion endpoint for immutable Phase 1 raw market-data objects.

Security is based on GitHub Actions OIDC, not a long-lived GitHub secret. The function validates issuer, audience, repository identity, owner identity, main-branch ref, workflow identity, event type, and GitHub-hosted runner environment before using Supabase server credentials internally.


## Raw-only safety

For canonical manifest uploads with `status = "not_found"`, the function checks the matching raw object path first. If immutable raw already exists, the manifest is rejected with HTTP 409. A Storage error is treated as absence only when it is a verified missing-key/not-found response; all other lookup failures fail closed.
