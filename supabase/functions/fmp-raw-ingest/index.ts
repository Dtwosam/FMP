import { createClient } from "npm:@supabase/supabase-js@2";
import { createRemoteJWKSet, jwtVerify } from "npm:jose@5";
import {
  assertTrustedGithubClaims,
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
      if (downloadError || !existing) {
        throw error;
      }
      const existingSha = await sha256Hex(new Uint8Array(await existing.arrayBuffer()));
      if (existingSha !== expectedSha) {
        return Response.json({ error: "immutable_object_conflict" }, { status: 409 });
      }
      return Response.json({ status: "already_verified", path: objectPath, sha256: actualSha });
    }

    return Response.json({ status: "stored", path: objectPath, sha256: actualSha }, { status: 201 });
  } catch (error) {
    console.error(error);
    return Response.json({ error: "unauthorized_or_invalid_request" }, { status: 401 });
  }
});
