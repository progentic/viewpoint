/* This file is generated. Run `npm run generate`; do not edit it directly. */

export interface ComponentHealth {
  contentStore: "ready";
  database: "ready";
  worker: "ready";
}

export interface ErrorResponse {
  code: string;
  message: string;
}

export interface HTTPValidationError {
  detail?: Array<ValidationError>;
}

export interface HealthResponse {
  components: ComponentHealth;
  schemaVersion?: 1;
  status?: "ok";
  version: string;
}

export interface SessionBootstrapRequest {
  officeHost: "Word";
  officePlatform: "PC" | "Mac";
  wordApi13Supported: true;
}

export interface SessionBootstrapResponse {
  csrfToken: string;
  expiresAt: string;
}

export interface ValidationError {
  ctx?: unknown;
  input?: unknown;
  loc: Array<unknown>;
  msg: string;
  type: string;
}

export type FetchImplementation = (
  input: string,
  init?: RequestInit,
) => Promise<Response>;

export interface BootstrapDocument {
  querySelector(selector: string): { content: string } | null;
}

export class CompanionApiError extends Error {
  constructor(
    public readonly status: number,
    public readonly code: string,
    message: string,
  ) {
    super(message);
  }
}

export class CompanionClient {
  private sessionCsrf: string | null = null;

  constructor(
    private readonly fetchImplementation: FetchImplementation = globalThis.fetch.bind(globalThis),
    private readonly documentSource: BootstrapDocument = globalThis.document,
  ) {}

  async bootstrapLocalSession(request: SessionBootstrapRequest): Promise<SessionBootstrapResponse> {
    const bootstrapCsrf = readBootstrapCsrf(this.documentSource);
    const response = await this.fetchImplementation("/api/v1/session/bootstrap", {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        "X-Bootstrap-CSRF": bootstrapCsrf,
      },
      body: JSON.stringify(request),
    });
    const payload = await readResponse<SessionBootstrapResponse>(response);
    this.sessionCsrf = payload.csrfToken;
    return payload;
  }

  async getHealth(): Promise<HealthResponse> {
    if (this.sessionCsrf === null) {
      throw new CompanionApiError(0, "session_not_bootstrapped", "Local session is not established");
    }
    const response = await this.fetchImplementation("/api/v1/health", {
      method: "GET",
      credentials: "include",
      headers: { "X-Session-CSRF": this.sessionCsrf },
    });
    return readResponse<HealthResponse>(response);
  }
}

function readBootstrapCsrf(documentSource: BootstrapDocument): string {
  const value = documentSource.querySelector('meta[name="word-researcher-bootstrap"]')?.content;
  if (!value || value === "__BOOTSTRAP_CSRF__") {
    throw new CompanionApiError(0, "bootstrap_missing", "Reload the task pane to start locally");
  }
  return value;
}

async function readResponse<T>(response: Response): Promise<T> {
  const payload = (await response.json()) as T | ErrorResponse;
  if (!response.ok) {
    const error = payload as ErrorResponse;
    throw new CompanionApiError(response.status, error.code, error.message);
  }
  return payload as T;
}
