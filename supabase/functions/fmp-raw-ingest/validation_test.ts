import {
  assertEquals,
  assertThrows,
} from "jsr:@std/assert@1";
import {
  assertTrustedGithubClaims,
  INGEST_PROTOCOL,
  isStorageObjectNotFound,
  manifestStorageInvariant,
  manifestsEquivalent,
  rawPathForNotFoundManifest,
  validateManifestForStorage,
  validateObjectPath,
} from "./validation.ts";

function canonicalManifest(
  overrides: Record<string, unknown> = {},
): Record<string, unknown> {
  return {
    manifest_version: 1,
    retrieval_method: "dukascopy-public-daily-m1-bi5-v1",
    source: "dukascopy",
    source_url:
      "https://datafeed.dukascopy.com/datafeed/EURUSD/2024/00/02/BID_candles_min_1.bi5",
    pair: "EURUSD",
    side: "BID",
    date_utc: "2024-01-02",
    granularity: "1m",
    source_format: "bi5-lzma-daily-candles",
    record_size_bytes: 24,
    month_indexing: "zero_based_in_source_url",
    status: "complete",
    http_status: 200,
    sha256: "a".repeat(64),
    compressed_size_bytes: 321,
    records: 1440,
    retrieved_at_utc: "2026-09-09T15:00:00+00:00",
    ...overrides,
  };
}

const trustedClaims = {
  iss: "https://token.actions.githubusercontent.com",
  aud: "fmp-supabase-raw-ingest",
  repository: "Dtwosam/FMP",
  repository_id: "1342321016",
  repository_owner_id: "42391449",
  ref: "refs/heads/main",
  event_name: "workflow_dispatch",
  runner_environment: "github-hosted",
  workflow_ref:
    "Dtwosam/FMP/.github/workflows/phase1-full-acquisition.yml@refs/heads/main",
};

Deno.test("ingest protocol is pinned for client preflight", () => {
  assertEquals(INGEST_PROTOCOL, "fmp-raw-ingest-v2");
});

Deno.test("accepts trusted workflow-dispatch identity", () => {
  assertEquals(assertTrustedGithubClaims(trustedClaims), true);
});

Deno.test("accepts trusted main-branch push identity for cloud smoke", () => {
  assertEquals(assertTrustedGithubClaims({ ...trustedClaims, event_name: "push" }), true);
});

Deno.test("rejects other event types", () => {
  assertThrows(() => assertTrustedGithubClaims({ ...trustedClaims, event_name: "schedule" }), Error, "event_name");
});

Deno.test("rejects a token from another repository", () => {
  assertThrows(() => assertTrustedGithubClaims({ ...trustedClaims, repository: "attacker/FMP" }), Error, "repository");
});

Deno.test("rejects a token from a different workflow", () => {
  assertThrows(
    () => assertTrustedGithubClaims({ ...trustedClaims, workflow_ref: "Dtwosam/FMP/.github/workflows/tests.yml@refs/heads/main" }),
    Error,
    "workflow",
  );
});

Deno.test("accepts canonical raw and manifest object paths", () => {
  assertEquals(validateObjectPath("raw/dukascopy/v1/EURUSD/2024/00/02/BID_candles_min_1.bi5"), true);
  assertEquals(validateObjectPath("manifests/dukascopy/v1/USDJPY/2024/00/02/ASK_candles_min_1.json"), true);
});

Deno.test("accepts frozen snapshot boundary object paths", () => {
  for (const path of [
    "raw/dukascopy/v1/EURUSD/2015/00/01/BID_candles_min_1.bi5",
    "manifests/dukascopy/v1/USDJPY/2026/07/20/ASK_candles_min_1.json",
  ]) {
    assertEquals(validateObjectPath(path), true);
  }
});

Deno.test("rejects object paths outside frozen snapshot", () => {
  for (const path of [
    "raw/dukascopy/v1/EURUSD/2014/11/31/BID_candles_min_1.bi5",
    "manifests/dukascopy/v1/USDJPY/2026/07/21/ASK_candles_min_1.json",
    "raw/dukascopy/v1/GBPUSD/2026/08/01/BID_candles_min_1.bi5",
  ]) {
    assertThrows(() => validateObjectPath(path), Error, "frozen");
  }
});

Deno.test("rejects impossible calendar dates in object paths", () => {
  for (const path of [
    "raw/dukascopy/v1/EURUSD/2024/01/31/BID_candles_min_1.bi5",
    "manifests/dukascopy/v1/USDJPY/2023/01/29/ASK_candles_min_1.json",
    "raw/dukascopy/v1/GBPUSD/2024/03/31/BID_candles_min_1.bi5",
  ]) {
    assertThrows(() => validateObjectPath(path), Error, "calendar");
  }
  assertEquals(
    validateObjectPath(
      "raw/dukascopy/v1/USDJPY/2024/01/29/ASK_candles_min_1.bi5",
    ),
    true,
  );
});

Deno.test("rejects path traversal and non-V1 objects", () => {
  for (const path of [
    "../secret",
    "raw/dukascopy/v1/EURUSD/2024/00/02/evil.exe",
    "raw/dukascopy/v1/XAUUSD/2024/00/02/BID_candles_min_1.bi5",
    "raw/dukascopy/v2/EURUSD/2024/00/02/BID_candles_min_1.bi5",
  ]) {
    assertThrows(() => validateObjectPath(path), Error);
  }
});

Deno.test("manifest retries may differ only by retrieval timestamp", () => {
  const first = {
    pair: "EURUSD",
    side: "BID",
    status: "complete",
    sha256: "abc",
    records: 1440,
    retrieved_at_utc: "2026-08-22T01:00:00Z",
  };
  const retry = { ...first, retrieved_at_utc: "2026-08-22T02:00:00Z" };
  assertEquals(manifestsEquivalent(first, retry), true);
});

Deno.test("manifest retry rejects substantive differences", () => {
  const first = {
    pair: "EURUSD",
    side: "BID",
    status: "complete",
    sha256: "abc",
    records: 1440,
    retrieved_at_utc: "2026-08-22T01:00:00Z",
  };
  assertEquals(manifestsEquivalent(first, { ...first, sha256: "changed" }), false);
  assertEquals(manifestsEquivalent(first, { ...first, records: 1439 }), false);
  assertEquals(manifestsEquivalent(first, { ...first, extra: "field" }), false);
});


Deno.test("not_found manifest maps to canonical raw counterpart", () => {
  const manifestPath =
    "manifests/dukascopy/v1/USDJPY/2022/11/17/BID_candles_min_1.json";
  const rawPath = rawPathForNotFoundManifest(manifestPath, {
    status: "not_found",
  });
  assertEquals(
    rawPath,
    "raw/dukascopy/v1/USDJPY/2022/11/17/BID_candles_min_1.bi5",
  );
});

Deno.test("complete manifest does not request raw counterpart absence check", () => {
  assertEquals(
    rawPathForNotFoundManifest(
      "manifests/dukascopy/v1/EURUSD/2024/00/02/BID_candles_min_1.json",
      { status: "complete" },
    ),
    null,
  );
});

Deno.test("storage missing-key errors are distinguished from other 404s", () => {
  assertEquals(
    isStorageObjectNotFound({ statusCode: "404", error: "NoSuchKey" }),
    true,
  );
  assertEquals(
    isStorageObjectNotFound({ status: 404, error: "NotFound" }),
    true,
  );
  assertEquals(
    isStorageObjectNotFound({ statusCode: "404", code: "not_found" }),
    true,
  );
  assertEquals(
    isStorageObjectNotFound({ statusCode: "404", error: "NoSuchBucket" }),
    false,
  );
  assertEquals(
    isStorageObjectNotFound({ statusCode: "500", error: "InternalError" }),
    false,
  );
});


Deno.test("complete manifest requires canonical raw expectation", () => {
  const invariant = manifestStorageInvariant(
    "manifests/dukascopy/v1/GBPUSD/2020/05/01/BID_candles_min_1.json",
    {
      status: "complete",
      sha256: "a".repeat(64),
      compressed_size_bytes: 321,
    },
  );
  assertEquals(invariant, {
    status: "complete",
    rawPath: "raw/dukascopy/v1/GBPUSD/2020/05/01/BID_candles_min_1.bi5",
    sha256: "a".repeat(64),
    sizeBytes: 321,
  });
});

Deno.test("complete manifest rejects missing or invalid raw metadata", () => {
  const path =
    "manifests/dukascopy/v1/EURUSD/2024/00/02/BID_candles_min_1.json";
  for (const manifest of [
    { status: "complete", compressed_size_bytes: 123 },
    { status: "complete", sha256: "not-a-sha", compressed_size_bytes: 123 },
    { status: "complete", sha256: "a".repeat(64), compressed_size_bytes: 0 },
    { status: "complete", sha256: "a".repeat(64), compressed_size_bytes: 12.5 },
  ]) {
    assertThrows(
      () => manifestStorageInvariant(path, manifest),
      Error,
      "complete manifest",
    );
  }
});

Deno.test("manifest storage invariant rejects unknown status", () => {
  assertThrows(
    () =>
      manifestStorageInvariant(
        "manifests/dukascopy/v1/USDJPY/2024/00/02/ASK_candles_min_1.json",
        { status: "mystery" },
      ),
    Error,
    "status",
  );
});


Deno.test("canonical complete manifest schema is accepted for its path", () => {
  assertEquals(
    validateManifestForStorage(
      "manifests/dukascopy/v1/EURUSD/2024/00/02/BID_candles_min_1.json",
      canonicalManifest(),
    ),
    true,
  );
});

Deno.test("canonical not_found manifest schema is accepted", () => {
  assertEquals(
    validateManifestForStorage(
      "manifests/dukascopy/v1/EURUSD/2024/00/06/ASK_candles_min_1.json",
      canonicalManifest({
        source_url:
          "https://datafeed.dukascopy.com/datafeed/EURUSD/2024/00/06/ASK_candles_min_1.bi5",
        side: "ASK",
        date_utc: "2024-01-06",
        status: "not_found",
        http_status: 404,
        sha256: null,
        compressed_size_bytes: null,
        records: null,
      }),
    ),
    true,
  );
});

Deno.test("manifest schema rejects path/body identity mismatches", () => {
  const path =
    "manifests/dukascopy/v1/EURUSD/2024/00/02/BID_candles_min_1.json";
  for (const manifest of [
    canonicalManifest({ pair: "GBPUSD" }),
    canonicalManifest({ side: "ASK" }),
    canonicalManifest({ date_utc: "2024-01-03" }),
    canonicalManifest({
      source_url:
        "https://datafeed.dukascopy.com/datafeed/EURUSD/2024/00/03/BID_candles_min_1.bi5",
    }),
  ]) {
    assertThrows(
      () => validateManifestForStorage(path, manifest),
      Error,
      "identity",
    );
  }
});

Deno.test("manifest schema rejects missing and extra fields", () => {
  const path =
    "manifests/dukascopy/v1/EURUSD/2024/00/02/BID_candles_min_1.json";
  const missing = canonicalManifest();
  delete missing.records;
  assertThrows(
    () => validateManifestForStorage(path, missing),
    Error,
    "fields",
  );
  assertThrows(
    () =>
      validateManifestForStorage(path, {
        ...canonicalManifest(),
        extra: "not-canonical",
      }),
    Error,
    "fields",
  );
});

Deno.test("manifest schema rejects invalid retrieval timestamp", () => {
  assertThrows(
    () =>
      validateManifestForStorage(
        "manifests/dukascopy/v1/EURUSD/2024/00/02/BID_candles_min_1.json",
        canonicalManifest({ retrieved_at_utc: "2026-09-09T15:00:00" }),
      ),
    Error,
    "retrieved_at_utc",
  );
});

Deno.test("manifest schema rejects inconsistent status metadata", () => {
  const path =
    "manifests/dukascopy/v1/EURUSD/2024/00/02/BID_candles_min_1.json";
  assertThrows(
    () =>
      validateManifestForStorage(
        path,
        canonicalManifest({
          status: "not_found",
          http_status: 404,
          sha256: "a".repeat(64),
          compressed_size_bytes: null,
          records: null,
        }),
      ),
    Error,
    "not_found",
  );
  assertThrows(
    () =>
      validateManifestForStorage(
        path,
        canonicalManifest({ http_status: 404 }),
      ),
    Error,
    "complete",
  );
});
