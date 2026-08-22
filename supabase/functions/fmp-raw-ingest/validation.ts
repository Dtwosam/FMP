const EXPECTED = {
  repository: "Dtwosam/FMP",
  repository_id: "1342321016",
  repository_owner_id: "42391449",
  ref: "refs/heads/main",
  event_name: "workflow_dispatch",
  runner_environment: "github-hosted",
  workflow_ref:
    "Dtwosam/FMP/.github/workflows/phase1-full-acquisition.yml@refs/heads/main",
} as const;

export function assertTrustedGithubClaims(
  claims: Record<string, unknown>,
): true {
  for (const [key, expected] of Object.entries(EXPECTED)) {
    if (claims[key] !== expected) {
      throw new Error(`untrusted GitHub ${key}`);
    }
  }
  return true;
}

const RAW_RE = /^raw\/dukascopy\/v1\/(EURUSD|GBPUSD|USDJPY)\/(\d{4})\/(0[0-9]|1[01])\/([0-2][0-9]|3[01])\/(BID|ASK)_candles_min_1\.bi5$/;
const MANIFEST_RE = /^manifests\/dukascopy\/v1\/(EURUSD|GBPUSD|USDJPY)\/(\d{4})\/(0[0-9]|1[01])\/([0-2][0-9]|3[01])\/(BID|ASK)_candles_min_1\.json$/;

export function validateObjectPath(path: string): true {
  if (!RAW_RE.test(path) && !MANIFEST_RE.test(path)) {
    throw new Error("invalid FMP storage object path");
  }
  return true;
}
