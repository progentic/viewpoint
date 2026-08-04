# Phase 0 owner acceptance

Acceptance date: **2026-08-02 EDT**
Accepting owner or role: **Project owner**, recorded through the explicit Phase 1.5 closure
authorization in the repository task history.

## Accepted contract

- Supported Office target: Microsoft Word Desktop on Windows and macOS.
- Architecture: local-only add-in and installed loopback companion, with no hosted
  application backend.
- Ownership: the companion owns its stable loopback API, static task-pane assets, session
  boundary, durable local state, and supervised workers.
- Authority: SQLite owns local metadata and state; the addressed local content store owns
  local content bytes.
- Worker boundary: local workers own later extraction, OCR, embeddings, indexing, and
  queued execution mechanics; none are Phase 1 features.
- Egress boundary: `MicrosoftAiGateway` is the only later application-data egress adapter.
- Human authority: the researcher alone accepts evidence and approves decisions or claims.
- Audit semantics: suggestions are immutable and review decisions are append-only.
- Provenance: accepted evidence must resolve to an exact Unicode code-point source span in
  immutable extraction text through the recorded checksum and paper hash chain.
- API contract: Pydantic-generated deterministic OpenAPI 3.1 is authoritative and produces
  the TypeScript client; handwritten cross-stack mirrors are forbidden.
- Office platform: task-pane HTML loads production Office.js from Microsoft's production
  CDN before application initialization.
- Requirement baseline: stable `WordApi 1.3`, with runtime host/platform/capability gates.

## Scope of acceptance

Acceptance covers the eight Phase 0 governing documents, their disclosed local-only and
managed-deployment limitations, and authorization to complete the Phase 1/1.5 feasibility
spike. It does not approve Phase 2 functionality, a release, or a cross-platform support
claim.

## Unresolved feasibility items at acceptance

- Normal stable-hostname and trust behavior in Word WKWebView and WebView2.
- Real Word task-pane discovery, Office.js readiness, cookies, Fetch Metadata, CSP, and
  generated-client health on both platforms.
- macOS and Windows fresh install, restart, repeated repair, and uninstall lifecycle.
- Windows Credential Manager, certificate store, Scheduled Task, and catalog behavior.
- Production-candidate organizational manifest deployment.
- Certificate renewal, rotation, rollback, revocation, enterprise trust policy, and port
  ownership under installed-package conditions.

These items remain evidence gates. This artifact does not rewrite the architecture to fit
an implementation defect or convert an unproved item into acceptance.
