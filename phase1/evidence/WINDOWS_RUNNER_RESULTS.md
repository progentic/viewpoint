# Windows GitHub-runner results

Final source date: **2026-08-02 EDT**.

## Execution status

The final workflow is configured for GitHub's `windows-2025` image, Node 24, Python 3.12,
and PSScriptAnalyzer 1.24.0. GitHub's official `actions/runner-images` catalog lists
`windows-2025` as a supported YAML label. The job did **not execute** because the Phase 1.5
changes are not committed or pushed and the task does not authorize either operation.

| Field | Result |
| :--- | :--- |
| Repository | `progentic/viewpoint` |
| Intended job | `Windows noninteractive checks` |
| Intended runner | `windows-2025` |
| Actual runner image/version | BLOCKED — no run |
| Actual Node/Python/PowerShell versions | BLOCKED — no run |
| Elevated privileges | Unknown; no run |
| Workflow run URL/ID | None for final source |
| Final result | BLOCKED |

## Required check inventory

| Check | Configured command or mechanism | Result | Would prove | Does not prove |
| :--- | :--- | :--- | :--- | :--- |
| PowerShell parser | `Parser.ParseFile` over `installers/windows/**/*.ps1` | BLOCKED | Syntax on runner PowerShell | Real installer/Word behavior |
| PSScriptAnalyzer | `Invoke-ScriptAnalyzer -Severity Error,Warning` | BLOCKED | Selected static rules | Runtime OS policy |
| Python lock install | `.venv\\Scripts\\python.exe -m pip install --require-hashes ...` | BLOCKED | Windows lock selection and hashes | Word integration |
| Python tests | `pytest companion` | BLOCKED | Cross-platform and Windows-marked tests | Real Word/WebView2 |
| Ruff | `ruff check ...` | BLOCKED | Python lint on Windows checkout | Runtime behavior |
| Pyright | `npm run pyright` | BLOCKED | Python type surface | Native API success |
| Node lock | `npm ci` under `.nvmrc` | BLOCKED | Node 24 lock reproducibility | Browser host behavior |
| ESLint | `npm run lint` | BLOCKED | TypeScript lint | Word readiness |
| TypeScript | `npm run typecheck` | BLOCKED | Strict compilation | WebView2 runtime |
| Vitest | `npm run test` | BLOCKED | Office readiness/unsupported-state units | Actual Office.js |
| Vite | `npm run build` | BLOCKED | Windows frontend build | Task-pane discovery |
| OpenAPI determinism | `npm run verify:generated` | BLOCKED | No generated drift on Windows | HTTP/TLS runtime |
| Manifest validator | `npm run validate:manifest` | BLOCKED | Microsoft schema acceptance | Word catalog discovery |
| Action pins | `npm run ci:pins` | BLOCKED | Full-SHA workflow policy | Third-party action behavior |
| Windows paths | `test_windows_default_app_data_uses_local_app_data` | BLOCKED | `LOCALAPPDATA` adapter | Installed-file permissions |
| Credential Manager | unique safe target in `test_windows_credential_manager_round_trip` | BLOCKED | Native read/write/delete | Interactive target-user profile |
| Certificate generation | companion TLS tests | BLOCKED | Unique SAN/key generation | OS trust consumption by WebView2 |
| Certificate store | isolated lifecycle import/count/remove | BLOCKED | Current-user root operations if permitted | Enterprise trust policy |
| Loopback binding | companion tests plus installed lifecycle | BLOCKED | IPv4 loopback listener | Real WebView2 navigation |
| Session boundary | companion tests and protocol client | BLOCKED | Host/origin/session rejection on Windows runtime | Cryptographic Word attestation |
| Installer dry-run | `phase1.tests.ps1` without `-RunLifecycle` portion | BLOCKED | No mutation and deterministic plan | Actual installation |
| Isolated installation | `phase1.tests.ps1 -RunLifecycle` | BLOCKED | Temp catalog/app-data lifecycle | Word shared-catalog UI |
| Production origin | installed Python/Node production-origin script | BLOCKED | Normal DNS, TLS, exact authority, generated client | Real Word task pane |
| Repair idempotency | repair twice, retain TLS hashes, count one root/task | BLOCKED | Script/store idempotency | Reboot persistence |
| Uninstall cleanup | app-data/manifest/task/root/credential assertions | BLOCKED | Exact cleanup on runner | Interactive enterprise policy |
| Secret scan | `npm run verify:security` | BLOCKED | Source/bundle/storage markers and HTTP-client policy | Memory forensics |
| External HTTP-client scan | `npm run verify:security` | BLOCKED | No installer/companion downloader | Microsoft platform traffic |

## Real-host boundary

Even a passing runner cannot prove Microsoft Word Desktop, add-in discovery, shared-catalog
behavior inside Word, WebView2 trust/navigation/cookies, interactive sign-in startup,
enterprise policy, prompts, or reboot persistence. Real Windows Word remains a separate
mandatory acceptance matrix.
