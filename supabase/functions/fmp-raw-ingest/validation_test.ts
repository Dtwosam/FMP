import {
  assertEquals,
  assertThrows,
} from "jsr:@std/assert@1";
import {
  assertTrustedGithubClaims,
  validateObjectPath,
} from "./validation.ts";

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

Deno.test("accepts trusted workflow-dispatch identity", () => {
  assertEquals(assertTrustedGithubClaims(trustedClaims), true);
});

Deno.test("accepts trusted main-branch push identity for cloud smoke", () => {
  assertEquals(
    assertTrustedGithubClaims({ ...trustedClaims, event_name: "push" }),
    true,
  );
});

Deno.test("rejects other event types", () => {
  assertThrows(
    () => assertTrustedGithubClaims({ ...trustedClaims, event_name: "schedule" }),
    Error,
    "event_name",
  );
});

Deno.test("rejects a token from another repository", () => {
  assertThrows(
    () => assertTrustedGithubClaims({ ...trustedClaims, repository: "attacker/FMP" }),
    Error,
    "repository",
  );
});

Deno.test("rejects a token from a different workflow", () => {
  assertThrows(
    () =>
      assertTrustedGithubClaims({
        ...trustedClaims,
        workflow_ref: "Dtwosam/FMP/.github/workflows/tests.yml@refs/heads/main",
      }),
    Error,
    "workflow",
  );
});

Deno.test("accepts canonical raw and manifest object paths", () => {
  assertEquals(
    validateObjectPath(
      "raw/dukascopy/v1/EURUSD/2024/00/02/BID_candles_min_1.bi5",
    ),
    true,
  );
  assertEquals(
    validateObjectPath(
      "manifests/dukascopy/v1/USDJPY/2024/00/02/ASK_candles_min_1.json",
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
