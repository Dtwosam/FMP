# fmp-raw-ingest

Private ingestion endpoint for immutable Phase 1 raw market-data objects.

Security is based on GitHub Actions OIDC, not a long-lived GitHub secret. The function validates issuer, audience, repository identity, owner identity, main-branch ref, workflow identity, event type, and GitHub-hosted runner environment before using Supabase server credentials internally.
