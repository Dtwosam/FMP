# FMP Supabase Raw Storage

Phase 1 may persist immutable Dukascopy source chunks and acquisition manifests in a dedicated Supabase Storage bucket.

## Project

- Supabase project: `FMP`
- Project ref: `htjqqzlezyguveuajuat`
- Region: `eu-central-1`
- Bucket: `fmp-raw`
- Bucket visibility: private
- Development cost: $0/month at creation

## Security boundary

The bucket is not directly writable by public clients.

Uploads flow through the `fmp-raw-ingest` Edge Function. The function accepts only GitHub Actions OIDC tokens issued by `https://token.actions.githubusercontent.com` for the canonical `Dtwosam/FMP` full-acquisition workflow on `main`. It additionally pins repository ID `1342321016` and owner ID `42391449`.

Supabase secret/admin keys stay inside the Supabase Edge Function environment and must never be committed to GitHub.

Objects are immutable: a second upload to the same canonical path is accepted only if the existing bytes have the same SHA-256. A checksum conflict fails closed.

## Intended contents

- `raw/dukascopy/v1/.../*.bi5`
- `manifests/dukascopy/v1/.../*.json`

Normalized Phase 2+ research datasets remain outside this bucket unless a later approved decision changes the storage architecture.
