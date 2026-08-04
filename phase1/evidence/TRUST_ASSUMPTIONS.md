# Local trust and security assumptions

## Implemented session boundary

1. The companion retrieves a random installation secret from macOS Keychain or Windows
   Credential Manager at startup. Missing, invalid, or too-short material fails closed with
   an installer/repair action rather than entering browser or database state.
2. `GET /taskpane` issues a 30-second signed, one-time bootstrap cookie with `Secure`,
   `HttpOnly`, and `SameSite=Strict`, plus a separate one-time CSRF value in page metadata.
3. The task pane waits for `Office.onReady()`, confirms Word Desktop on PC or Mac, and checks
   `WordApi 1.3` before calling the generated bootstrap operation.
4. Bootstrap requires exact authority `localhost:4179`, exact Origin
   `https://localhost:4179`, loopback client, same-origin Fetch Metadata, valid signature and
   expiry, matching CSRF, and strict Office request fields.
5. Successful bootstrap consumes the challenge and issues an opaque 15-minute `Secure`,
   `HttpOnly`, `SameSite=Strict` session cookie plus an in-memory session CSRF value.
6. `/api/v1/health` repeats the request-boundary check and requires both session cookie and
   session CSRF. API and task-pane responses are non-cacheable; redirects are not used.

The durable installation secret never enters HTML, JavaScript, URLs, SQLite, browser
storage, source-controlled evidence, or logs. Short-lived CSRF values are intentionally
browser-visible and are not installation credentials.

## Explicit threat-boundary assumptions

- Office host/platform fields are runtime gates, not cryptographic Word attestation. A
  malicious process running as the same user may connect to loopback and forge browser
  headers. This design addresses remote and ordinary cross-site requests, not fully
  compromised same-user native execution.
- Real WKWebView/WebView2 handling of `localhost`, exact Origin and Fetch Metadata headers,
  cookies, CSP, and the per-user root remains unproved.
- The companion binds only IPv4 `127.0.0.1`; `localhost` also resolves to IPv6 `::1` on the
  tested Mac. System and real Word clients must demonstrate predictable IPv4 fallback. No
  IPv6 listener is silently enabled.
- macOS uses the legacy login Keychain because the unsigned spike has no data-protection
  Keychain entitlement. Installing user trust requires the visible OS authentication
  dialog. Windows Credential Manager fail-closed logic exists but awaits runner execution.
- Private CA keys are file-protected (`0600` on macOS; per-user ACL policy on Windows) and
  remain on disk so repair can retain the origin. Windows ACL behavior is unproved.
- Sessions are in process memory and intentionally disappear on companion restart.
  Multi-process service operation is unsupported.
- The fixed-port availability check fails closed but has a small
  bind-check-to-server-bind race. There is no random-port, plaintext HTTP, certificate-
  warning, or proxy fallback.

## Later distribution assumptions

Enterprise certificate policy, production signing/notarization, organizational deployment,
upgrade/rollback, certificate renewal/rotation/revocation, and reboot persistence require
later packaging evidence. They remain distinct from the present blockers: final macOS Word
execution, final Windows CI, and real Windows Word acceptance.

## macOS continuation observation

The real Word/macOS WKWebView boundary is now observed rather than unproved for the initial
bootstrap request. Exact authority and loopback client checks passed. Word supplied
`Sec-Fetch-Site: same-origin`, `Sec-Fetch-Mode: cors`, and `Sec-Fetch-Dest: empty`, but
omitted `Origin`. The exact-Origin invariant therefore rejected bootstrap with 403 before
cookie/session validation.

No missing-Origin exception was added. The open security question is whether a different
Word-to-companion bootstrap can preserve the normative exact-Origin contract. Changing that
contract requires Phase 0/security review and a full affected-gate rerun.
