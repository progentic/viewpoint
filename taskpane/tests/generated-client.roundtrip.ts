import { CompanionClient } from "../src/generated/client"

const origin = requireEnvironment("PHASE1_ORIGIN")
const transportOrigin = requireEnvironment("PHASE1_TRANSPORT_ORIGIN")
const cookies = new Map<string, string>()

async function runRoundTrip(): Promise<void> {
  const taskpane = await browserFetch("/taskpane")
  const document = await taskpane.text()
  if (!taskpane.ok) {
    throw new Error(`Task pane request failed with ${taskpane.status}: ${document}`)
  }
  const csrf = extractBootstrapCsrf(document)
  const client = new CompanionClient(browserFetch, {
    querySelector: () => ({ content: csrf }),
  })
  await client.bootstrapLocalSession({
    officeHost: "Word",
    officePlatform: "Mac",
    wordApi13Supported: true,
  })
  const health = await client.getHealth()
  if (health.status !== "ok") {
    throw new Error("Generated client did not receive a healthy companion response")
  }
  console.log("generated-client-roundtrip: PASS")
}

async function browserFetch(input: string, init: RequestInit = {}): Promise<Response> {
  const headers = new Headers(init.headers)
  headers.set("Origin", origin)
  headers.set("Sec-Fetch-Site", "same-origin")
  if (cookies.size > 0) {
    headers.set("Cookie", Array.from(cookies).map(([name, value]) => `${name}=${value}`).join("; "))
  }
  const response = await fetch(new URL(input, transportOrigin), { ...init, headers })
  storeResponseCookies(response)
  return response
}

function storeResponseCookies(response: Response): void {
  for (const header of response.headers.getSetCookie()) {
    const [pair, ...attributes] = header.split(";")
    const separator = pair.indexOf("=")
    const name = pair.slice(0, separator)
    const value = pair.slice(separator + 1)
    const expired = attributes.some((attribute) => attribute.trim().toLowerCase() === "max-age=0")
    if (expired || value === "") {
      cookies.delete(name)
    } else {
      cookies.set(name, value)
    }
  }
}

function extractBootstrapCsrf(document: string): string {
  const match = document.match(/name="word-researcher-bootstrap" content="([^"]+)"/)
  if (!match) {
    throw new Error("Task pane did not contain bootstrap material")
  }
  return match[1]
}

function requireEnvironment(name: string): string {
  const value = process.env[name]
  if (!value) {
    throw new Error(`Missing ${name}`)
  }
  return value
}

await runRoundTrip()
