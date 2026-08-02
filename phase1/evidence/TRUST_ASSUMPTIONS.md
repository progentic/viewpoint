# Local trust and security assumptions

## Implemented session boundary

1. The companion retrieves a random installation secret from the operating-system credential
   store at startup. It fails closed with a repair instruction if the item is missing.
2. `GET /taskpane` issues a 30-second, signed, one-time bootstrap cookie with `Secure`,
   `HttpOnly`, and `SameSite=Strict`, plus a separate one-time CSRF value in page metadata.
3. The task pane waits for `Office.onReady()`, confirms Word Desktop on PC or Mac, and checks
   `WordApi 1.3` before calling the generated bootstrap operation.
4. Bootstrap requires the exact Host, Origin, loopback client, same-origin Fetch Metadata,
   valid cookie signature/expiry, matching CSRF value, and supported Office fields.
5. A successful bootstrap replaces the challenge with an opaque 15-minute `Secure`,
   `HttpOnly`, `SameSite=Strict` session cookie. `/health` also requires a separate in-memory
   CSRF value.

The durable installation secret never enters HTML, JavaScript, a URL, or logs. The short-lived
CSRF values are intentionally browser-visible and are not installation credentials.

## Assumptions that remain unproved

- Office.js host/platform fields are runtime gating, not cryptographic Word attestation. A
  malicious process running as the same user can connect to loopback, forge browser headers,
  and acquire its own task-pane challenge. The design protects against remote and ordinary
  cross-site browser requests; it does not establish a security boundary against a fully
  compromised local user session.
- Real WKWebView/WebView2 handling of `.localhost`, exact Origin and Fetch Metadata headers,
  cookies, CSP, and the per-user trust root is unproved.
- macOS currently uses the legacy login Keychain because the unsigned spike has no
  data-protection Keychain entitlement. Windows Credential Manager code is untested.
- Private CA keys are file-protected (`0600` on macOS) but remain on disk so repair can retain
  the stable origin. Windows ACL behavior is unproved.
- Sessions are process-memory state and intentionally expire or disappear on companion
  restart. Multi-process service operation is unsupported.
- The fixed-port availability check is fail-closed but has a small bind-check-to-server-bind
  race. No random-port or HTTP fallback exists.
- Certificate expiry, rotation, rollback, revocation, enterprise trust-root policy, signed
  packaging, and production organizational deployment are not proved.
- Safe logs contain lifecycle event names and exit codes only; operating-system and Uvicorn
  framework logs must be re-audited in the eventual signed package.
