import { CompanionClient } from "../src/generated/client"

export interface RoundTripResult {
  bootstrapCookie: string[]
  healthStatus: string
  healthVersion: string
}

export class CookieFetchSession {
  private readonly cookies = new Map<string, string>()
  private readonly cookieAttributes = new Map<string, string[]>()

  public constructor(
    private readonly logicalOrigin: string,
    private readonly transportOrigin: string,
  ) {}

  public readonly fetch = async (input: string, init: RequestInit = {}): Promise<Response> => {
    const headers = this.createHeaders(init.headers)
    const response = await fetch(new URL(input, this.transportOrigin), {
      ...init,
      headers,
      redirect: "manual",
    })
    this.storeResponseCookies(response)
    if (isRedirect(response.status)) {
      throw new Error(`Unexpected local redirect: ${response.status}`)
    }
    return response
  }

  public attributes(name: string): string[] {
    return this.cookieAttributes.get(name) ?? []
  }

  private createHeaders(initial: HeadersInit | undefined): Headers {
    const headers = new Headers(initial)
    headers.set("Origin", this.logicalOrigin)
    headers.set("Sec-Fetch-Site", "same-origin")
    headers.set("Sec-Fetch-Mode", "cors")
    headers.set("Sec-Fetch-Dest", "empty")
    if (this.cookies.size > 0) {
      headers.set("Cookie", serializeCookies(this.cookies))
    }
    return headers
  }

  private storeResponseCookies(response: Response): void {
    for (const header of response.headers.getSetCookie()) {
      this.storeCookie(header)
    }
  }

  private storeCookie(header: string): void {
    const [pair, ...attributes] = header.split(";")
    const separator = pair.indexOf("=")
    const name = pair.slice(0, separator)
    const value = pair.slice(separator + 1)
    const normalized = attributes.map((attribute) => attribute.trim().toLowerCase())
    this.cookieAttributes.set(name, normalized)
    if (value === "" || normalized.includes("max-age=0")) {
      this.cookies.delete(name)
      return
    }
    this.cookies.set(name, value)
  }
}

export async function runGeneratedClientRoundTrip(
  session: CookieFetchSession,
  officePlatform: "Mac" | "PC",
): Promise<RoundTripResult> {
  const document = await loadTaskPane(session)
  const bootstrapCookie = session.attributes("wr_bootstrap")
  const client = createClient(session, extractBootstrapCsrf(document))
  await client.bootstrapLocalSession({
    officeHost: "Word",
    officePlatform,
    wordApi13Supported: true,
  })
  const health = await client.getHealth()
  return {
    bootstrapCookie,
    healthStatus: health.status ?? "unknown",
    healthVersion: health.version,
  }
}

export function requireSecureBootstrapCookie(attributes: string[]): void {
  const required = ["secure", "httponly", "samesite=strict"]
  if (!required.every((attribute) => attributes.includes(attribute))) {
    throw new Error("Bootstrap cookie security attributes are incomplete")
  }
}

export function requireEnvironment(name: string): string {
  const value = process.env[name]
  if (!value) {
    throw new Error(`Missing ${name}`)
  }
  return value
}

async function loadTaskPane(session: CookieFetchSession): Promise<string> {
  const response = await session.fetch("/taskpane")
  const document = await response.text()
  if (!response.ok) {
    throw new Error(`Task pane request failed with ${response.status}`)
  }
  return document
}

function createClient(session: CookieFetchSession, csrf: string): CompanionClient {
  return new CompanionClient(session.fetch, {
    querySelector: () => ({ content: csrf }),
  })
}

function extractBootstrapCsrf(document: string): string {
  const match = document.match(/name="word-researcher-bootstrap" content="([^"]+)"/)
  if (!match) {
    throw new Error("Task pane did not contain bootstrap material")
  }
  return match[1]
}

function serializeCookies(cookies: Map<string, string>): string {
  return Array.from(cookies)
    .map(([name, value]) => `${name}=${value}`)
    .join("; ")
}

function isRedirect(status: number): boolean {
  return status >= 300 && status < 400
}
