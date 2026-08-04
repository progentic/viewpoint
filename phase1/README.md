# Phase 1 connectivity spike

This directory records the smallest Phase 1 vertical slice in `docs/ROADMAP.md`. The
implementation contains no paper, research, AI, review, synthesis, artifact, or Word-content
feature. The final Phase 1.5 decision is **BLOCKED**; see
`evidence/PHASE1_EXIT_DECISION.md` before interpreting individual checks.

## Component hierarchy

| Layer | Component | Responsibility |
| :--- | :--- | :--- |
| Policy | `researcher_companion.main.main` | Loads installed material and owns the HTTPS server lifecycle. |
| Policy | `api.app.create_app` | Composes the Phase 1 HTTP application and routes. |
| Policy | `initializeTaskPane` | Waits for Office, applies host gates, then performs health. |
| Policy | installer entry points | Coordinate provisioning, trust, manifest, startup, repair, and cleanup. |
| Domain | `LocalSessionManager` | Issues one-time bootstrap material and validates local sessions. |
| Domain | `LocalRequestBoundary` | Enforces exact host, origin, fetch metadata, and loopback policy. |
| Domain | `CompanionLifecycle` / `HealthService` | Coordinate readiness and orderly lifecycle. |
| Infrastructure | `SQLiteDatabase` | Applies ordered Phase 1 migrations. |
| Infrastructure | `LocalContentStore` | Establishes a private adapter boundary without paper storage. |
| Infrastructure | `SupervisedWorkerShell` | Starts, monitors, and stops an inert worker process. |
| Infrastructure | credential-store adapters | Use macOS Keychain or Windows Credential Manager. |
| Infrastructure | `PerInstallTlsProvisioner` | Generates installation-unique trust for `localhost`. |
| Infrastructure | generated `CompanionClient` | Calls bootstrap and health from the OpenAPI contract. |

## Locked setup

Use Node 24 from `.nvmrc` and Python 3.12 or newer.

```sh
npm ci
python3 -m venv .venv
.venv/bin/python -m pip install --require-hashes -r companion/requirements.lock
.venv/bin/python -m pip check
```

Every direct and transitive Python dependency is exactly pinned. Regenerate the lock from
the exact versions in `companion/requirements.in` with:

```sh
.venv/bin/python scripts/generate_python_lock.py
```

## Contracts and generated client

FastAPI is the only contract source. The npm wrappers deliberately require the repository
`.venv` and propagate the locked Node executable:

```sh
npm run generate
npm run verify:generated
npm run hashes
```

Outputs are `contracts/openapi.json` and `taskpane/src/generated/client.ts`. Repeated
generation must be byte-identical.

## Verification commands

```sh
npm ci
npm run lint
npm run typecheck
npm run test
npm run build
npm run pyright
npm run verify:architecture
npm run verify:security
npm run verify:generated
npm run ci:pins
npm run validate:manifest
npm run test:protocol
npm run test:https-bind
.venv/bin/python -m ruff check companion/src companion/tests scripts phase1/evidence/tools
.venv/bin/python -m pytest companion
```

`test:protocol` is the **generated-client protocol round trip under test transport**. It
uses substituted HTTP transport and is not production HTTPS evidence.

`test:https-bind` is the **HTTPS bind and certificate test**. It verifies a temporary
loopback listener, certificate chain, SNI, authority, and production Office.js reference;
it is not normal installed-origin or Word evidence.

With a complete installed companion, `npm run test:production-origin` uses normal hostname
resolution and the exact `https://localhost:4179` origin. It does not use `--resolve`, a
bind-address substitution, or disabled TLS verification.

## Installer spike commands

The installers consume prebuilt locked assets and contain no dependency download.

```sh
installers/macos/install.sh
installers/macos/repair.sh
installers/macos/uninstall.sh
```

On Windows, a testing-only shared catalog must already exist:

```powershell
.\installers\windows\install.ps1 -CatalogPath "\\host\WordResearcherCatalog"
.\installers\windows\repair.ps1 -CatalogPath "\\host\WordResearcherCatalog"
.\installers\windows\uninstall.ps1
```

Each Windows entry point also accepts `-DryRun`. The emitted plan validates the exact
hostname, port, bind address, required inputs, and paths without credential, certificate,
manifest, task, or filesystem mutation.

The macOS `wef` directory and Windows trusted catalog are development sideload routes, not
production organizational deployment evidence.
