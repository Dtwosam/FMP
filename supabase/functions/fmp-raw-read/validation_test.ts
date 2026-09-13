import {
  assertEquals,
  assertThrows,
} from "https://deno.land/std@0.224.0/assert/mod.ts";
import {
  assertTrustedGithubReadClaims,
  deriveReadPaths,
  READ_PROTOCOL,
  validateManifestForRead,
  validateReadRequest,
} from "./validation.ts";

const trustedClaims = {
  repository: "Dtwosam/FMP",
  repository_id: "1342321016",
  repository_owner_id: "42391449",
  ref: "refs/heads/main",
  event_name: "workflow_dispatch",
  runner_environment: "github-hosted",
  workflow_ref:
    "Dtwosam/FMP/.github/workflows/phase2-cloud-golden.yml@refs/heads/main",
};

Deno.test("read protocol and trusted GitHub claims are pinned", () => {
  assertEquals(READ_PROTOCOL, "fmp-raw-read-v1");
  assertEquals(assertTrustedGithubReadClaims(trustedClaims), true);
  for (const key of Object.keys(trustedClaims)) {
    assertThrows(() =>
      assertTrustedGithubReadClaims({ ...trustedClaims, [key]: "wrong" })
    );
  }
});

Deno.test("full-history workflow identity is trusted", () => {
  assertEquals(
    assertTrustedGithubReadClaims({
      ...trustedClaims,
      workflow_ref:
        "Dtwosam/FMP/.github/workflows/phase2-full-history.yml@refs/heads/main",
    }),
    true,
  );
});

Deno.test("unlisted raw-read workflow identity is rejected", () => {
  for (const workflow_ref of [
    "Dtwosam/FMP/.github/workflows/other.yml@refs/heads/main",
    "Dtwosam/FMP/.github/workflows/phase2-full-history.yml@refs/heads/feature",
    "Dtwosam/FMP/.github/workflows/phase2-full-history.yml@refs/pull/1/merge",
  ]) {
    assertThrows(() =>
      assertTrustedGithubReadClaims({ ...trustedClaims, workflow_ref })
    );
  }
});

Deno.test("request accepts exactly pair side date_utc", () => {
  assertEquals(
    validateReadRequest({ pair: "EURUSD", side: "BID", date_utc: "2015-01-01" }),
    { pair: "EURUSD", side: "BID", date_utc: "2015-01-01" },
  );
  assertEquals(
    validateReadRequest({ pair: "USDJPY", side: "ASK", date_utc: "2026-08-20" }),
    { pair: "USDJPY", side: "ASK", date_utc: "2026-08-20" },
  );

  for (const invalid of [
    null,
    [],
    {},
    { pair: "EURUSD", side: "BID" },
    { pair: "EURUSD", side: "BID", date_utc: "2015-01-01", path: "raw/x" },
    { pair: "AUDUSD", side: "BID", date_utc: "2015-01-01" },
    { pair: "EURUSD", side: "MID", date_utc: "2015-01-01" },
    { pair: "EURUSD", side: "BID", date_utc: "2014-12-31" },
    { pair: "EURUSD", side: "BID", date_utc: "2026-08-21" },
    { pair: "EURUSD", side: "BID", date_utc: "2024-02-30" },
    { pair: "EURUSD", side: "BID", date_utc: 20260820 },
  ]) {
    assertThrows(() => validateReadRequest(invalid));
  }
});

Deno.test("canonical paths use zero-based Dukascopy month", () => {
  assertEquals(
    deriveReadPaths({ pair: "GBPUSD", side: "ASK", date_utc: "2026-08-20" }),
    {
      manifestPath: "manifests/dukascopy/v1/GBPUSD/2026/07/20/ASK_candles_min_1.json",
      rawPath: "raw/dukascopy/v1/GBPUSD/2026/07/20/ASK_candles_min_1.bi5",
    },
  );
});

function manifest(overrides: Record<string, unknown> = {}) {
  return {
    manifest_version: 1,
    retrieval_method: "dukascopy-public-daily-m1-bi5-v1",
    source: "dukascopy",
    source_url:
      "https://datafeed.dukascopy.com/datafeed/EURUSD/2020/00/02/BID_candles_min_1.bi5",
    pair: "EURUSD",
    side: "BID",
    date_utc: "2020-01-02",
    granularity: "1m",
    source_format: "bi5-lzma-daily-candles",
    record_size_bytes: 24,
    month_indexing: "zero_based_in_source_url",
    status: "complete",
    http_status: 200,
    sha256: "a".repeat(64),
    compressed_size_bytes: 123,
    records: 1440,
    retrieved_at_utc: "2026-08-20T12:00:00Z",
    ...overrides,
  };
}

const request = { pair: "EURUSD" as const, side: "BID" as const, date_utc: "2020-01-02" };

Deno.test("manifest validator accepts exact complete and not_found contracts", () => {
  assertEquals(validateManifestForRead(request, manifest()), {
    status: "complete",
    sha256: "a".repeat(64),
    compressedSizeBytes: 123,
    records: 1440,
  });
  assertEquals(
    validateManifestForRead(request, manifest({ retrieved_at_utc: "2026-08-20T12:00:00+00:00" })),
    {
      status: "complete",
      sha256: "a".repeat(64),
      compressedSizeBytes: 123,
      records: 1440,
    },
  );
  assertEquals(
    validateManifestForRead(
      request,
      manifest({
        status: "not_found",
        http_status: 404,
        sha256: null,
        compressed_size_bytes: null,
        records: null,
      }),
    ),
    { status: "not_found" },
  );
});

Deno.test("manifest validator rejects provenance and type drift", () => {
  for (const invalid of [
    manifest({ manifest_version: true }),
    manifest({ source_url: "https://example.com/x" }),
    manifest({ pair: "GBPUSD" }),
    manifest({ retrieved_at_utc: "2026-08-20T12:00:00+01:00" }),
    manifest({ sha256: "abc" }),
    manifest({ compressed_size_bytes: 0 }),
    manifest({ records: 1441 }),
    manifest({ status: "not_found", http_status: 404, sha256: "a".repeat(64), compressed_size_bytes: null, records: null }),
    { ...manifest(), extra: true },
  ]) {
    assertThrows(() => validateManifestForRead(request, invalid));
  }
});
