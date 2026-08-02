# Phase 1 automated verification results

Final local verification date: **2026-08-02 EDT**.

| Check | Exact result |
| :--- | :--- |
| Python lock | Hash-locked requirements installed successfully; `pip check` reported no broken requirements. |
| Python lint | `ruff` reported all checks passed. |
| Python tests | 18 passed; one upstream `StarletteDeprecationWarning` from FastAPI's `TestClient`. |
| Node lock | Clean `npm ci --ignore-scripts` under Node 24.14.0 installed 145 packages; no engine mismatch and zero vulnerabilities. |
| TypeScript | `tsc --noEmit` passed. |
| Task-pane tests | 2 files and 4 tests passed. |
| Task-pane build | Vite built 19 modules successfully. |
| Manifest | Microsoft's validator completed its acceptance check and reported the XML manifest valid. |
| OpenAPI/client drift | Repeated generation retained SHA-256 `f0d443926c5ef9b034b91a13cdf1f6fc910db9286ba6fb73e2a185aa66bf0d1b` for OpenAPI and `980c708d0229ca287b4f0c17a7fd1e2e7593f0226e697f9207aeb521a8d03a9d` for the TypeScript client. |
| Generated-client integration | Authenticated bootstrap plus `/api/v1/health` returned `generated-client-roundtrip: PASS`. |
| HTTPS probe | Real TLS handshake at the stable SNI/Host and loopback listener returned `https-loopback-probe: PASS`. |
| CI policy | Action-pin check passed; workflow YAML parsed successfully; every third-party action uses a full commit SHA. |
| macOS installer syntax | `zsh -n` passed for install, repair, and uninstall. |
| Windows installer syntax | BLOCKED: PowerShell was unavailable; scripts require a real Windows verification host. |

Commands:

```sh
.venv/bin/ruff check companion/src companion/tests scripts phase1/evidence/tools
.venv/bin/python -m pytest companion
.venv/bin/python -m pip check
npm ci --ignore-scripts
npm run check
npm test
npm run build
npm audit --audit-level=high
npm run validate:manifest
.venv/bin/python scripts/check_generated.py
.venv/bin/python scripts/check_ci_action_pins.py
.venv/bin/python scripts/run_generated_client_roundtrip.py
.venv/bin/python scripts/run_https_loopback_probe.py
zsh -n installers/macos/install.sh installers/macos/repair.sh installers/macos/uninstall.sh
```

These results prove local components and transports only. They are not evidence that Word
Desktop opened or executed the task pane.
