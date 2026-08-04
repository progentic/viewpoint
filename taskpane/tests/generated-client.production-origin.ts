import {
  CookieFetchSession,
  requireEnvironment,
  requireSecureBootstrapCookie,
  runGeneratedClientRoundTrip,
} from "./generated-client-roundtrip-support"

const EXPECTED_ORIGIN = "https://localhost:4179"

async function runProductionOriginTest(): Promise<void> {
  const origin = requireEnvironment("PHASE1_PRODUCTION_ORIGIN")
  if (origin !== EXPECTED_ORIGIN) {
    throw new Error("Installed-origin test requires the exact production origin")
  }
  const session = new CookieFetchSession(origin, origin)
  const result = await runGeneratedClientRoundTrip(session, currentPlatform())
  requireSecureBootstrapCookie(result.bootstrapCookie)
  console.log(
    JSON.stringify({
      test: "installed-production-origin-generated-client-round-trip",
      status: "PASS",
      origin,
      healthStatus: result.healthStatus,
      healthVersion: result.healthVersion,
    }),
  )
}

function currentPlatform(): "Mac" | "PC" {
  return process.platform === "win32" ? "PC" : "Mac"
}

await runProductionOriginTest()
