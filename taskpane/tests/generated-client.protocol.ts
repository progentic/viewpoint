import { CompanionApiError, CompanionClient } from "../src/generated/client"
import {
  CookieFetchSession,
  requireEnvironment,
  requireSecureBootstrapCookie,
  runGeneratedClientRoundTrip,
} from "./generated-client-roundtrip-support"

async function runProtocolTest(): Promise<void> {
  const logicalOrigin = requireEnvironment("PHASE1_PROTOCOL_LOGICAL_ORIGIN")
  const transportOrigin = requireEnvironment("PHASE1_PROTOCOL_TRANSPORT_ORIGIN")
  const session = new CookieFetchSession(logicalOrigin, transportOrigin)
  const result = await runGeneratedClientRoundTrip(session, "Mac")
  requireSecureBootstrapCookie(result.bootstrapCookie)
  await verifyErrorMapping(logicalOrigin, transportOrigin)
  console.log(
    JSON.stringify({
      test: "generated-client-protocol-round-trip-under-test-transport",
      status: "PASS",
      healthStatus: result.healthStatus,
      errorMapping: "PASS",
    }),
  )
}

async function verifyErrorMapping(logicalOrigin: string, transportOrigin: string): Promise<void> {
  const session = new CookieFetchSession(logicalOrigin, transportOrigin)
  await session.fetch("/taskpane")
  const client = new CompanionClient(session.fetch, {
    querySelector: () => ({ content: "incorrect-bootstrap-csrf" }),
  })
  try {
    await client.bootstrapLocalSession({
      officeHost: "Word",
      officePlatform: "Mac",
      wordApi13Supported: true,
    })
  } catch (error) {
    if (error instanceof CompanionApiError && error.code === "bootstrap_replay_rejected") {
      return
    }
    throw error
  }
  throw new Error("Generated client did not map the invalid bootstrap response")
}

await runProtocolTest()
