import { createClient } from "npm:@supabase/supabase-js@2";
import { createRemoteJWKSet, jwtVerify } from "npm:jose@5";
import {
  assertTrustedGithubClaims,
  isStorageObjectNotFound,
  manifestStorageInvariant,
  manifestsEquivalent,
  validateObjectPath,
} from "./validation.ts";

const BUCKET = "fmp-raw";
const AUDIENCE = "fmp-supabase-raw-ingest";
const GITHUB_ISSUER = "https://token.actions.githubusercontent.com";
const GITHUB_JWKS = createRemoteJWKSet(
  new URL("https://token.actions.githubusercontent.com/.well-known/jwks"),
);

async function sha256Hex(bytes: Uint8Array): Promise<string> {
  const digestInput = bytes.buffer.slice(
    bytes.byteOffset,
    bytes.byteOffset + bytes.byteLength,
  ) as ArrayBuffer;
  const digest = await crypto.subtle.digest("SHA-256", digestInput);
  return [...new Uint8Array(digest)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

function parseJsonObject(bytes: Uint8Array): Record<string, unknown> | null {
  try {
    const parsed = JSON.parse(new TextDecoder().decode(bytes));
    if (parsed && typeof parsed === "object" && !Array.isArray(parsed)) {
      return parsed as Record<string, unknown>;
    }
  } catch {
    // Malformed manifests are never treated as equivalent.
  }
  return null;
}

Deno.serve(async (req: Request) => {
  try {
    if (req.method !== "PUT") {
      return Response.json({ error: "method_not_allowed" }, { status: 405 });
    }

    const auth = req.headers.get("authorization") ?? "";
    if (!auth.startsWith("Bearer ")) {
      return Response.json({ error: "missing_oidc_token" }, { status: 401 });
    }

    const token = auth.slice("Bearer ".length);
    const { payload } = await jwtVerify(token, GITHUB_JWKS, {
      issuer: GITHUB_ISSUER,
      audience: AUDIENCE,
    });
    assertTrustedGithubClaims(payload as Record<string, unknown>);

    const objectPath = req.headers.get("x-fmp-object-path") ?? "";
    validateObjectPath(objectPath);

    const expectedSha = (req.headers.get("x-fmp-sha256") ?? "").toLowerCase();
    if (!/^[0-9a-f]{64}$/.test(expectedSha)) {
      return Response.json({ error: "invalid_sha256" }, { status: 400 });
    }

    const body = new Uint8Array(await req.arrayBuffer());
    if (body.length === 0 || body.length > 1_000_000) {
      return Response.json({ error: "invalid_body_size" }, { status: 400 });
    }

    const actualSha = await sha256Hex(body);
    if (actualSha !== expectedSha) {
      return Response.json({ error: "checksum_mismatch" }, { status: 400 });
    }

    const secretKeys = JSON.parse(Deno.env.get("SUPABASE_SECRET_KEYS") ?? "{}");
    const secretKey = secretKeys.default;
    if (!secretKey) throw new Error("missing Supabase secret key");
    const supabase = createClient(Deno.env.get("SUPABASE_URL")!, secretKey);

    if (objectPath.endsWith(".json")) {
      const incomingManifest = parseJsonObject(body);
      if (!incomingManifest) {
        return Response.json({ error: "invalid_manifest_json" }, { status: 400 });
      }

      let invariant;
      try {
        invariant = manifestStorageInvariant(objectPath, incomingManifest);
      } catch (error) {
        console.error(error);
        return Response.json({ error: "invalid_manifest" }, { status: 400 });
      }

      const { data: rawData, error: rawError } = await supabase.storage
        .from(BUCKET)
        .download(invariant.rawPath, {}, { cache: "no-store" });

      if (invariant.status === "not_found") {
        if (!rawError && rawData) {
          return Response.json(
            {
              error: "raw_present_for_not_found_manifest",
              path: objectPath,
              raw_path: invariant.rawPath,
            },
            { status: 409 },
          );
        }
        if (!rawError || !isStorageObjectNotFound(rawError)) {
          throw rawError ?? new Error(
            "raw counterpart lookup returned neither object nor not-found error",
          );
        }
      } else {
        if (rawError) {
          if (isStorageObjectNotFound(rawError)) {
            return Response.json(
              {
                error: "raw_missing_for_complete_manifest",
                path: objectPath,
                raw_path: invariant.rawPath,
              },
              { status: 409 },
            );
          }
          throw rawError;
        }
        if (!rawData) {
          throw new Error("raw counterpart lookup returned no object");
        }

        const rawBytes = new Uint8Array(await rawData.arrayBuffer());
        const rawSha = await sha256Hex(rawBytes);
        if (
          rawSha !== invariant.sha256 ||
          rawBytes.length !== invariant.sizeBytes
        ) {
          return Response.json(
            {
              error: "raw_manifest_mismatch",
              path: objectPath,
              raw_path: invariant.rawPath,
            },
            { status: 409 },
          );
        }
      }
    }

    const contentType = objectPath.endsWith(".json")
      ? "application/json"
      : "application/octet-stream";

    const { error } = await supabase.storage.from(BUCKET).upload(objectPath, body, {
      contentType,
      upsert: false,
    });

    if (error) {
      const { data: existing, error: downloadError } = await supabase.storage
        .from(BUCKET)
        .download(objectPath);
      if (downloadError || !existing) throw error;

      const existingBytes = new Uint8Array(await existing.arrayBuffer());
      const existingSha = await sha256Hex(existingBytes);
      if (existingSha === expectedSha) {
        return Response.json({ status: "already_verified", path: objectPath, sha256: actualSha });
      }

      if (objectPath.endsWith(".json")) {
        const firstManifest = parseJsonObject(existingBytes);
        const retryManifest = parseJsonObject(body);
        if (firstManifest && retryManifest && manifestsEquivalent(firstManifest, retryManifest)) {
          return Response.json({
            status: "already_verified",
            path: objectPath,
            sha256: existingSha,
            equivalence: "retrieved_at_utc_ignored",
          });
        }
      }

      return Response.json({ error: "immutable_object_conflict" }, { status: 409 });
    }

    return Response.json({ status: "stored", path: objectPath, sha256: actualSha }, { status: 201 });
  } catch (error) {
    console.error(error);
    return Response.json({ error: "unauthorized_or_invalid_request" }, { status: 401 });
  }
});
