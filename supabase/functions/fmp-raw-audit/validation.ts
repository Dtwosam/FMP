const EXPECTED = {
  repository: "Dtwosam/FMP",
  repository_id: "1342321016",
  repository_owner_id: "42391449",
  ref: "refs/heads/main",
  event_name: "workflow_dispatch",
  runner_environment: "github-hosted",
  workflow_ref:
    "Dtwosam/FMP/.github/workflows/phase1-final-cloud-audit.yml@refs/heads/main",
} as const;

const RAW_RE = /^raw\/dukascopy\/v1\/(EURUSD|GBPUSD|USDJPY)\/(\d{4})\/(0[0-9]|1[01])\/([0-2][0-9]|3[01])\/(BID|ASK)_candles_min_1\.bi5$/;
const MANIFEST_RE = /^manifests\/dukascopy\/v1\/(EURUSD|GBPUSD|USDJPY)\/(\d{4})\/(0[0-9]|1[01])\/([0-2][0-9]|3[01])\/(BID|ASK)_candles_min_1\.json$/;

export function assertTrustedGithubAuditClaims(
  claims: Record<string, unknown>,
): true {
  for (const [key, expected] of Object.entries(EXPECTED)) {
    if (claims[key] !== expected) {
      throw new Error(`untrusted GitHub ${key}`);
    }
  }
  return true;
}

export function validateAuditPaths(paths: unknown): string[] {
  if (!Array.isArray(paths) || paths.length < 1 || paths.length > 100) {
    throw new Error("audit paths must contain 1..100 entries");
  }

  const validated: string[] = [];
  const seen = new Set<string>();
  for (const [index, value] of paths.entries()) {
    if (typeof value !== "string") {
      throw new Error(`audit path ${index} must be a string`);
    }
    if (!RAW_RE.test(value) && !MANIFEST_RE.test(value)) {
      throw new Error(`invalid FMP audit object path: ${value}`);
    }
    validateSnapshotDate(value);
    if (seen.has(value)) {
      throw new Error(`duplicate FMP audit object path: ${value}`);
    }
    seen.add(value);
    validated.push(value);
  }
  return validated;
}

export function validateAuditRequest(payload: unknown): string[] {
  if (!payload || typeof payload !== "object" || Array.isArray(payload)) {
    throw new Error("audit request root must be a JSON object");
  }
  const record = payload as Record<string, unknown>;
  if (Object.keys(record).length !== 1 || !("paths" in record)) {
    throw new Error("audit request root must contain exactly paths");
  }
  return validateAuditPaths(record.paths);
}
