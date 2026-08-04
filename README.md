# Viewpoint — Researcher for Microsoft Word Desktop

**Viewpoint** is the project codename and is not the final product name.

Architecture contract for a local-only research assistant add-in.

Status: **DISCONTINUED**. The selected Word add-in and native companion architecture did
not pass the cross-platform session feasibility gate within the available budget. See
[PROJECT_STATUS.md](PROJECT_STATUS.md) for the final decision. Do not continue
implementation on the current architecture.

## Product flow

Import papers → extract evidence locally → human review → compare studies → test
candidate gaps → develop research questions → insert approved artifacts into Word.

## V1 product model

V1 runs entirely on the user's Windows or macOS computer:

- An XML add-in-only manifest loads a task pane in Microsoft Word Desktop.
- A packaged local companion serves the task-pane assets and API over trusted HTTPS
  loopback. No application server is hosted on the internet or an institutional network.
- SQLite is authoritative. PDFs, page previews, indexes, and artifacts live in the local
  application-data directory.
- Local worker processes perform PDF extraction, OCR, indexing, and analysis outside
  Word's task-pane process.
- The only later application-data egress is an explicit, researcher-initiated `analysis`
  or `research` operation through `MicrosoftAiGateway`. It receives only the approved,
  previewed disclosure payload.

Word on the web, mobile Word, multi-user collaboration, tenants, Postgres, S3, hosted
workers, and Marketplace distribution are not v1 targets.

Office.js is loaded from Microsoft's production CDN as a Word platform dependency. That
request hosts no application code or research data.

## Non-negotiable boundaries

- The companion binds to loopback only and rejects untrusted origins and sessions.
- PDF bytes, extracted text, indexes, and the local database never leave the device.
- Microsoft AI validation is optional, advisory, and cannot accept evidence.
- AI suggestions are immutable. Humans create append-only review decisions.
- Every accepted finding resolves to an exact span in a versioned PDF text layer.
- Synthesis claims link several findings with typed evidentiary relationships.
- Gap tests describe only the recorded local corpus; they do not prove a universal gap.
- Word insertion uses stable `WordApi 1.3` APIs and immutable artifact snapshots.

## Document map

- [Architecture](docs/ARCHITECTURE.md)
- [Domain model](docs/SYNTHESIS_DOMAIN_MODEL.md)
- [Workflows](docs/SYNTHESIS_WORKFLOW.md)
- [Invariants](docs/INVARIANTS.md)
- [Coding style](docs/CODING_STYLE.md)
- [Configuration](docs/CONFIG_EXAMPLE.md)
- [Roadmap](docs/ROADMAP.md)
- [Verification](docs/VERIFICATION.md)

Phase 1 implementation and evidence live in [phase1](phase1/README.md). Phase 1 remains
blocked, and Phase 2 did not start. The repository is preserved for reference only.
