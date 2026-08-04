# Phase 1.5 completion report

Date: **2026-08-02 EDT**.

## 1. Critique

Phase 1 code existed, but its evidence overstated two boundaries. The former generated-
client round trip used an HTTPS logical origin over substituted HTTP transport, and the
former direct-SNI probe bypassed normal resolution. Neither proved an installed production
origin. The prior `word-researcher.localhost` candidate then failed normal macOS and Node
resolution, making it a real Phase 1 defect rather than a documentation concern.

Phase 1.5 split protocol, HTTPS bind/certificate, installed production-origin, real Word,
Windows runner, and real Windows Word evidence. It replaced the unreliable origin
consistently with `https://localhost:4179`, separated Windows policy/coordination/platform
mechanics, added fail-closed HTTP and credential handling, and added deterministic static
verification.

The replacement passes normal resolver checks but did not survive real Word testing because
that test could not safely start: Word had an unsaved user document and was not quit. Final
installed trust and production-origin tests also remain incomplete. Windows CI did not run
because no commit/push was authorized. Those are present Phase 1 blockers.

Production signing/notarization, enterprise deployment, upgrade/rollback, and full
certificate lifecycle are later distribution concerns. No Phase 2 feature was implemented.

## 2. Refactored code

### Added

- `companion/src/researcher_companion/api/http_policy.py`
- `companion/tests/test_windows_platform.py`
- `eslint.config.js`
- `installers/windows/platform.ps1`
- `installers/windows/policy.ps1`
- `installers/windows/tests/phase1.tests.ps1`
- `phase1/PHASE1_5_TASK.md`
- `phase1/PHASE1_5_COMPLETION_REPORT.md`
- `phase1/evidence/CI_RESULTS.md`
- `phase1/evidence/CONTRACT_HASHES.md`
- `phase1/evidence/MACOS_REAL_WORD_RESULTS.md`
- `phase1/evidence/PHASE0_OWNER_ACCEPTANCE.md`
- `phase1/evidence/PHASE1_EXIT_DECISION.md`
- `phase1/evidence/WINDOWS_RUNNER_RESULTS.md`
- `pyrightconfig.json`
- `scripts/compute_phase1_hashes.py`
- `scripts/run_generated_client_protocol_roundtrip.py`
- `scripts/run_installed_production_origin_test.py`
- `scripts/run_locked_python.mjs`
- `scripts/verify_architecture.py`
- `scripts/verify_security_surface.py`
- `taskpane/tests/generated-client-roundtrip-support.ts`
- `taskpane/tests/generated-client.production-origin.ts`
- `taskpane/tests/generated-client.protocol.ts`

### Modified

- `.gitignore`
- `.github/workflows/phase1.yml`
- `README.md`
- `companion/src/researcher_companion/api/app.py`
- `companion/src/researcher_companion/api/models.py`
- `companion/src/researcher_companion/platform/credentials.py`
- `companion/src/researcher_companion/settings.py`
- `companion/tests/test_api.py`
- `companion/tests/test_contracts_and_listener.py`
- `companion/tests/test_infrastructure.py`
- `companion/tests/test_session.py`
- `contracts/openapi.json`
- `docs/ARCHITECTURE.md`
- `docs/CONFIG_EXAMPLE.md`
- `docs/ROADMAP.md`
- `docs/VERIFICATION.md`
- `installers/macos/install.sh`
- `installers/macos/repair.sh`
- `installers/windows/common.ps1`
- `installers/windows/install.ps1`
- `installers/windows/repair.ps1`
- `installers/windows/uninstall.ps1`
- `manifest/word-researcher.xml`
- `package-lock.json`
- `package.json`
- `phase1/README.md`
- `phase1/evidence/AUTOMATED_RESULTS.md`
- `phase1/evidence/INSTALLER_RESULTS.md`
- `phase1/evidence/NETWORK_OBSERVATIONS.md`
- `phase1/evidence/PHASE0_AUDIT.md`
- `phase1/evidence/REAL_HOST_MATRIX.md`
- `phase1/evidence/TRUST_ASSUMPTIONS.md`
- `scripts/generate_contracts.py`
- `scripts/run_https_loopback_probe.py`
- `taskpane/src/initialize.tsx`
- `taskpane/tests/initialize.test.tsx`

### Removed

- `scripts/run_generated_client_roundtrip.py`
- `taskpane/tests/generated-client.roundtrip.ts`

The ambiguous round-trip pair was replaced with explicit protocol and installed-origin
drivers. Windows entry points now coordinate pure plans and platform operations rather than
mixing policy with raw PowerShell APIs. HTTP body/cache rules live in middleware; session
policy remains independent of FastAPI composition. The locked Python wrapper makes every npm
verification script select the same `.venv` and Node executable.

## 3. Hierarchy table

| Layer | Function or component | Responsibility |
| ----- | --------------------- | -------------- |
| High | `main.main` | Compose and run the installed companion lifecycle. |
| High | `create_app` | Compose Phase 1 HTTP routes, lifecycle, and middleware. |
| High | `initializeTaskPane` | Wait for Office, gate the host, and coordinate health. |
| High | `Install-Phase1Spike` / `Repair-Phase1Spike` / `Uninstall-Phase1Spike` | Coordinate Windows lifecycle steps. |
| Mid | `LocalSessionManager` | Decide bootstrap/session validity and expiry. |
| Mid | `LocalRequestBoundary` | Decide whether a local request is authorized. |
| Mid | `New-Phase1InstallPlan` | Produce and validate immutable Windows install policy. |
| Low | `ApiHttpPolicyMiddleware` | Bound ASGI bodies and enforce no-store response headers. |
| Low | Keychain/Credential Manager adapters | Read, write, and delete protected installation material. |
| Low | TLS provisioner and installer platform scripts | Perform certificate, trust, ACL, manifest, filesystem, and startup APIs. |
| Low | `SQLiteDatabase`, `LocalContentStore`, `SupervisedWorkerShell` | Implement Phase 1 infrastructure lifecycle. |
| Low | generated `CompanionClient` | Serialize contract-derived bootstrap/health HTTP calls. |

Coordination contains no raw OS mechanics; session policy contains no FastAPI composition;
infrastructure adapters make no business-state decisions; platform selection occurs at
composition/installer boundaries.

## 4. Verification results

| Check | Exact result |
| :--- | :--- |
| Python | 3.12.13 |
| Node | 24.14.0 |
| npm lock installation | 226 packages; 2 transitive deprecation warnings; 0 audit vulnerabilities |
| Python lock installation | Hash-locked install passed; `pip check` passed; cache-disabled warning |
| Python tests | 32 passed, 2 Windows-only skipped, 1 upstream Starlette deprecation warning |
| TypeScript tests | 2 files, 4 tests passed |
| ESLint / TypeScript / Pyright / Ruff | PASS; Pyright 0 errors and 0 warnings |
| Build | PASS; Vite 8.2.0, 19 modules, main JS 193.71 kB |
| Manifest | PASS from Microsoft's acceptance validator |
| OpenAPI hash | `8b6b8e34847705da178f92ce0862e6445518489ea567bfcec9b94d0d06680444` |
| Generated client hash | `980c708d0229ca287b4f0c17a7fd1e2e7593f0226e697f9207aeb521a8d03a9d` |
| Protocol round trip | PASS, health `ok`, error mapping PASS |
| HTTPS bind/certificate | PASS |
| Installed production origin | BLOCKED |
| macOS Word | BLOCKED |
| Windows runner | BLOCKED — not executed |
| GitHub workflow | BLOCKED — no final committed/pushed revision |

`CONTRACT_HASHES.md` records every required lock, manifest, and installer hash.

## 5. macOS real Word evidence

- macOS: 26.5.2 (25F84), arm64.
- Word: 16.109.3, build 16.109.26053122; update channel unknown.
- Final URL: `https://localhost:4179/taskpane`.
- Resolver: `127.0.0.1` and `::1`, both loopback; no hosts-file mapping.
- Certificate creation: PASS in adapter tests with SAN `DNS:localhost`.
- Certificate trust: BLOCKED for final origin; OS authentication is required and was not
  bypassed.
- Menu path, task pane, Office.js, Word host, `WordApi 1.3`, bootstrap, session, `/health`,
  restart, two repairs, and final uninstall: BLOCKED because Word could not be safely quit.
- Final cleanup state: no listener, LaunchAgent/plist, manifest, app-data directory,
  credential, or relevant trust certificate.

No user document was modified or closed. Full details are in
`evidence/MACOS_REAL_WORD_RESULTS.md`.

## 6. Windows validation

### Windows GitHub runner

The final job targets `windows-2025` and includes parser, PSScriptAnalyzer, locked Python and
Node installs, all code/contract tests, native path/Credential Manager tests, certificate
store and loopback checks, dry-run, installed production-origin, two repairs, and cleanup.
It was not executed against final source and is **BLOCKED**. Configuration is not a result.

### Windows real host

**BLOCKED.** No supported Windows host with Word Desktop was available. Nothing in the
runner configuration is reported as WebView2, Word catalog, prompt, restart, reboot, or
enterprise-policy evidence.

## 7. Network observations

- Loopback: temporary tests listened only on `127.0.0.1:4179`; no application-content route
  exists.
- Microsoft platform: production Office.js is the only task-pane external asset; the real
  request was not captured. Manifest validation contacted Microsoft. Prior AutoUpdate
  behavior is classified as Office platform traffic, not add-in traffic.
- Installer: static scan found no downloader; macOS system `curl` is restricted to exact
  local readiness. npm, PyPI, GitHub, advisory, and manifest-validator requests were
  documented development traffic.
- Unexplained: none observed in the limited window, but final real Word traffic capture is
  incomplete, so the complete network gate is BLOCKED.

## 8. Limitations and assumptions

Present feasibility blockers are final macOS Word execution/trust, final Windows CI, and
real Windows Word. Same-user native malware remains outside the loopback browser boundary.
Enterprise root-certificate policy may prohibit the design and requires explicit testing.

Production signing/notarization, organizational deployment, upgrade/rollback, and full
certificate renewal/rotation/revocation are later distribution work. They were not
implemented or mislabeled as current feasibility evidence.

## 9. Phase 1 exit decision

**BLOCKED**

The implementation is locally reproducible, but conditional closure requires complete
macOS real Word evidence, a final tracked commit, and passing Windows/noninteractive CI.
All are incomplete. The original two-platform roadmap exit gate remains unchanged.

## 10. Authorization boundary

No Phase 2 route, model, database entity, paper workflow, AI behavior, review/synthesis
logic, artifact generation, Word insertion, backup/restore, signing, notarization, or
distribution feature was implemented.

Phase 2 may not begin under the conditional-closure exception because the decision is
BLOCKED.

## 11. Repository handoff

| Field | Value |
| :--- | :--- |
| Root | `/Users/godzilla/Documents/Projects/MicrosoftWord Researcher` |
| Repository | `progentic/viewpoint` |
| Branch | `main` |
| Baseline commit | `12284945619764d3270a657e202f3cd2343bcc20` |
| Final commit | None; not authorized |
| Working tree | Intentionally dirty: 36 modified, 24 untracked paths, and 2 removals |
| Workflow run | None for final source |
| Generated artifacts | OpenAPI and TypeScript client updated deterministically; task-pane `dist` remains ignored |
| Untracked runtime/private artifacts | None detected; `.venv`, `node_modules`, `dist`, databases, logs, and runtime evidence are ignored |

GitHub CLI access is active as `progentic` with repository ADMIN visibility. No commit,
push, pull request, tag, release, signing, notarization, publication, or distribution
occurred.

## 12. Continuation result — 2026-08-02 EDT

This section preserves and supersedes the earlier safe-stop result above. The user fully
quit Word, so the final-origin macOS sequence resumed from a clean pre-install state.

### Critique and defect correction

The first real Word load exposed an abstraction mismatch in the installer: the LaunchAgent
was installed, but late-bound task-pane files still came from the project checkout under
`Documents`. macOS TCC denied that background read and Word received HTTP 500. The corrected
install/repair policy now stages companion source, migrations, and built task-pane assets in
the installer-owned application runtime. LaunchAgent and Windows Scheduled Task launchers
resolve runtime paths there. The project checkout remains only the source of the locked
Python executable for this unsigned feasibility spike.

The next real Word run loaded the pane, production Office.js completed, `Office.onReady()`
resolved, Word Desktop/macOS and `WordApi 1.3` passed, and the generated client attempted
bootstrap. The companion then failed closed. Safe categorical logging proved this actual
WKWebView request context:

```text
Host: exact localhost:4179 (authority check passed)
client: loopback (client check passed)
Origin: missing
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: cors
Sec-Fetch-Dest: empty
```

ROADMAP.md requires exact Origin enforcement. No absent-Origin exception, browser secret,
TLS bypass, or other security weakening was introduced. The task pane therefore rendered
`Local companion unavailable`; no local session was established and Word did not call
authenticated `/health`.

### Continuation changes

- Staged installed runtime assets on macOS and Windows instead of serving late-bound files
  from the checkout.
- Re-rendered macOS LaunchAgent and Windows launcher paths against that runtime boundary.
- Removed copied development bytecode caches during staging and removed the staged runtime
  during uninstall.
- Added safe rejection-category logging containing no header values, cookies, CSRF values,
  secrets, URLs, document content, or user identity.
- Added path/launcher and safe-log tests. Python verification is now 34 passed and 2
  Windows-only skipped.

| Layer | Function or component | Continuation responsibility |
| :--- | :--- | :--- |
| High | macOS install/repair entry points | Stop, stage, register, start, and verify the installed runtime. |
| High | Windows install/repair coordinators | Stage the runtime before trust, catalog, and startup registration. |
| Mid | `LocalRequestBoundary` | Decide exact authority, loopback, Origin, and Fetch Metadata acceptance. |
| Low | runtime staging functions | Copy only Phase 1 runtime assets and remove copied bytecode caches. |
| Low | `log_rejection` | Emit categorical rejection reasons without request material. |

### Final continuation verification

| Check | Result |
| :--- | :--- |
| Node | 24.14.0 explicit runtime |
| Python tests | 34 passed, 2 Windows-only skipped, 1 upstream warning |
| TypeScript tests | 2 files, 4 tests passed |
| Ruff / Pyright / ESLint / TypeScript | PASS; Pyright 0 errors and 0 warnings |
| Architecture / security / CI action pins | PASS |
| Build | PASS; Vite 8.2.0, 19 modules, main JS 193.71 kB |
| Manifest | PASS from Microsoft acceptance validator |
| Deterministic OpenAPI/client | PASS twice; hashes unchanged |
| Protocol / HTTPS certificate | PASS under Node 24 |
| Exact-source installed production origin | PASS, normal `localhost`, verified TLS, generated-client health `ok` |
| macOS real Word | **FAIL** at strict Origin boundary; task pane rendered unavailable |
| Restart / two-repair acceptance | BLOCKED; the initial Word-host sequence did not pass |
| Full uninstall | PASS; no active process, listener, plist, manifest, credential, trust, or app data remained |
| Windows runner | BLOCKED; no final commit or workflow run |

The final Phase 1 decision remains **BLOCKED**. macOS real-host verification is a genuine
security/host compatibility failure, not an unavailable-host result. Final source is also
uncommitted, Windows CI has not run, and real Windows Word remains unavailable. No Phase 2
functionality was implemented.

Repository handoff at continuation end: branch `main`; HEAD and `origin/main`
`12284945619764d3270a657e202f3cd2343bcc20`; 41 modified paths, 31 untracked paths, and 2
tracked removals. No commit, staging, push, workflow, pull request, tag, release, or
publication occurred. Runtime/private artifacts are absent; the similarly named untracked
`* 2.md` files predated this continuation and were preserved.
