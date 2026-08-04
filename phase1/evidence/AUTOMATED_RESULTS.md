# Phase 1.5 automated verification results

Final local verification date: **2026-08-02 EDT**.

## Toolchain

| Item | Exact result |
| :--- | :--- |
| macOS | 26.5.2 (25F84), arm64 |
| Python | 3.12.13 from repository `.venv` |
| Node | 24.14.0 |
| Python lock | `--require-hashes` installation succeeded; `pip check` reported no broken requirements. |
| Node lock | `npm ci` installed 226 packages from `package-lock.json`; `npm audit --audit-level=high` found 0 vulnerabilities. |
| Installation warnings | npm reported deprecated transitive packages `@types/strip-bom@4.0.1` and `node-domexception@1.0.0`; pip reported its user cache was unwritable and disabled. Neither changed installed versions or test correctness. |

## Checks

| Check | Exact result | Evidence category |
| :--- | :--- | :--- |
| Ruff | PASS, all selected Python files | Static/local |
| Pyright | PASS, 0 errors, 0 warnings | Static/local |
| Python tests | PASS, 32 passed, 2 Windows-only skipped, 1 upstream warning | Unit/integration |
| Python warning | `StarletteDeprecationWarning`: FastAPI `TestClient` currently uses deprecated `httpx` integration and recommends `httpx2` | Non-failing upstream deprecation |
| ESLint | PASS with `--max-warnings=0` | Static/local |
| TypeScript | PASS, `tsc --noEmit` | Static/local |
| Task-pane tests | PASS, 2 files and 4 tests | Unit |
| Task-pane build | PASS, Vite 8.2.0 built 19 modules; main JavaScript 193.71 kB (61.27 kB gzip) | Build |
| Architecture boundary | PASS | Static/local |
| Security surface | PASS after build; bundle/storage/URL/secret patterns and installer HTTP clients checked | Static/local |
| Manifest | PASS, Microsoft acceptance validator reported the XML valid | Remote validator, not Word |
| Action pins | PASS; all actions use full 40-character SHAs and workflow permission is `contents: read` | Static/local |
| Workflow syntax | PASS; Ruby YAML parsing and local `actionlint` reported no errors | Static/local |
| OpenAPI/client determinism | PASS; two generations produced identical hashes | Generated contract |
| Stable resolver | PASS for final `localhost`: `127.0.0.1` and `::1`, both loopback; no hosts-file change | Normal local resolution |
| Rejected origin candidate | `word-researcher.localhost` failed five locked-Python lookups plus system Python, Node, and `dscacheutil` | Feasibility finding |
| Generated client protocol | PASS: health `ok` and error mapping PASS | Protocol test under substituted transport |
| HTTPS bind/certificate | PASS on temporary `127.0.0.1:4179` listener | Direct bind/certificate test |
| Installed production origin | BLOCKED: no complete installed final-origin companion/trust state | Production-origin test |
| macOS installer syntax | PASS, `zsh -n` | Static/local |
| Windows scripts and adapters | BLOCKED locally: PowerShell and Windows APIs unavailable; intended Windows job has not run | Windows runner required |

## Exact commands

```sh
npm ci
.venv/bin/python -m pip install --require-hashes -r companion/requirements.lock
.venv/bin/python -m pip check
npm run lint
npm run typecheck
npm run test
npm run build
npm run pyright
npm run verify:architecture
npm run verify:security
npm run generate
npm run generate
npm run verify:generated
npm run ci:pins
npm run validate:manifest
npm audit --audit-level=high
.venv/bin/python -m ruff check companion/src companion/tests scripts phase1/evidence/tools
.venv/bin/python -m pytest companion
.venv/bin/python scripts/run_generated_client_protocol_roundtrip.py \
  --node /Users/godzilla/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node
.venv/bin/python scripts/run_https_loopback_probe.py
zsh -n installers/macos/install.sh installers/macos/repair.sh installers/macos/uninstall.sh
```

The protocol and HTTPS probe required permission to bind local port 4179 in the Codex
workspace sandbox. They opened no non-loopback listener. These checks are not real Word
Desktop evidence.

## Continuation verification — superseding local results

Run date: **2026-08-02 EDT**. These results supersede the counts and installed-origin status
above while preserving the prior run history.

| Check | Final exact result |
| :--- | :--- |
| Node | 24.14.0, invoked explicitly from the bundled Node 24 LTS runtime |
| Python | 34 passed, 2 Windows-adapter tests skipped, 1 upstream Starlette deprecation warning |
| TypeScript | 2 files, 4 tests passed |
| Ruff | PASS |
| Pyright | PASS, 0 errors, 0 warnings, 0 information messages |
| ESLint | PASS with zero warnings |
| TypeScript type check | PASS |
| Vite build | PASS, 19 modules, main JavaScript 193.71 kB / 61.27 kB gzip |
| Architecture verification | PASS |
| Security-surface verification | PASS |
| Full-SHA action check | PASS |
| Manifest | PASS through Microsoft's remote acceptance validator under Node 24 |
| Protocol test | PASS; health `ok`, invalid-bootstrap error mapping PASS |
| HTTPS test | PASS; `127.0.0.1:4179`, SAN `DNS:localhost`, verified chain |
| Installed production-origin | PASS against exact final source; normal resolution, TLS verified, generated-client health `ok` |
| OpenAPI generation | Two consecutive generations identical |

The first sandboxed manifest attempt failed DNS resolution and the first sandboxed protocol
and HTTPS attempts were denied bind permission. The same commands passed when granted their
documented remote-validation or loopback-listener access. Those preliminary environment
denials are not represented as test failures.

The preliminary shell Node 26 run was discarded. The final JavaScript, build, manifest,
protocol, HTTPS, architecture, security, action-pin, generated-file, and hash results above
were rerun through Node 24.14.0.

Final deterministic hashes:

- OpenAPI: `8b6b8e34847705da178f92ce0862e6445518489ea567bfcec9b94d0d06680444`
- generated client: `980c708d0229ca287b4f0c17a7fd1e2e7593f0226e697f9207aeb521a8d03a9d`

The real Word failure is intentionally separate from these automated PASS results.
