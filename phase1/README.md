# Phase 1 connectivity spike

This directory records the evidence for the smallest Phase 1 vertical slice in
`docs/ROADMAP.md`. The implementation contains no paper, research, AI, review, synthesis,
artifact, or Word-content feature.

## Component hierarchy

| Layer | Component | Responsibility |
| :--- | :--- | :--- |
| Policy | `researcher_companion.main.main` | Loads installed material and owns the HTTPS server lifecycle. |
| Policy | `api.app.create_app` | Composes the Phase 1 HTTP application and its routes. |
| Policy | `initializeTaskPane` | Waits for Office, applies host gates, then performs the health round trip. |
| Policy | macOS and Windows installer entry points | Coordinate private material, trust, manifest, startup, repair, and cleanup. |
| Domain | `LocalSessionManager` | Issues one-time bootstrap material and validates short-lived local sessions. |
| Domain | `LocalRequestBoundary` | Enforces exact host, origin, fetch metadata, and loopback client policy. |
| Domain | `CompanionLifecycle` / `HealthService` | Coordinate readiness and orderly startup or shutdown. |
| Infrastructure | `SQLiteDatabase` | Applies ordered migrations and exposes only Phase 1 readiness. |
| Infrastructure | `LocalContentStore` | Establishes a private local adapter boundary without storing papers. |
| Infrastructure | `SupervisedWorkerShell` | Starts, monitors, and stops an inert worker process. |
| Infrastructure | credential-store adapters | Use macOS Keychain or Windows Credential Manager without browser exposure. |
| Infrastructure | `PerInstallTlsProvisioner` | Generates installation-unique root and leaf material for the stable hostname. |
| Infrastructure | generated `CompanionClient` | Calls the contract-derived bootstrap and health operations. |

## Locked setup

Use Node 24 from `.nvmrc` and Python 3.12 or newer.

```sh
npm ci --ignore-scripts
python3 -m venv .venv
.venv/bin/python -m pip install --require-hashes -r companion/requirements.lock
```

Every direct and transitive Python dependency is exactly pinned in
`companion/requirements.in`; the lock contains every non-yanked release hash. Regenerate it
from immutable, exact-version PyPI metadata with:

```sh
.venv/bin/python scripts/generate_python_lock.py
```

## Contracts and generated client

The FastAPI application is the only contract source. These commands create deterministic
OpenAPI 3.1 JSON and the TypeScript client, then verify that a clean regeneration is
byte-identical:

```sh
.venv/bin/python scripts/generate_contracts.py
.venv/bin/python scripts/check_generated.py
```

The generated outputs are `contracts/openapi.json` and
`taskpane/src/generated/client.ts`. The task pane imports that client directly.

## Verification commands

```sh
.venv/bin/ruff check companion/src companion/tests scripts
(cd companion && ../.venv/bin/pytest)
npm run check
npm test
npm run build
npm run validate:manifest
npm run ci:pins
npm run generate:check
npm run test:integration
npm run test:https
```

`test:integration` uses the generated client over a loopback-only test transport and the
real FastAPI session guard. `test:https` separately performs a real TLS handshake using the
stable SNI/Host, an installation-unique trust root, and `127.0.0.1:4179`. Neither test is
reported as Word Desktop evidence.

## Installer spike commands

The installer scripts consume prebuilt, locked assets and contain no dependency download.

```sh
WORD_RESEARCHER_DATA=/path/to/test-install installers/macos/install.sh
WORD_RESEARCHER_DATA=/path/to/test-install installers/macos/repair.sh
WORD_RESEARCHER_DATA=/path/to/test-install installers/macos/uninstall.sh
```

On Windows, a testing-only UNC catalog must already exist:

```powershell
.\installers\windows\install.ps1 -CatalogPath "\\host\WordResearcherCatalog"
.\installers\windows\repair.ps1 -CatalogPath "\\host\WordResearcherCatalog"
.\installers\windows\uninstall.ps1
```

The macOS script uses Finder only when TCC prevents a shell process from writing Word's
protected `wef` directory. The Windows network-share catalog and macOS `wef` path are
development sideload routes; they are not production organizational deployment evidence.

See `phase1/evidence/PHASE0_AUDIT.md`, `AUTOMATED_RESULTS.md`, `REAL_HOST_MATRIX.md`,
`INSTALLER_RESULTS.md`, `NETWORK_OBSERVATIONS.md`, and `TRUST_ASSUMPTIONS.md` before
interpreting any result.
