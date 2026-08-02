# Network observations

## Observed local behavior

- The installed macOS companion exposed one listener: `127.0.0.1:4179`. `lsof` showed no
  established external socket for that process.
- A trusted HTTPS request to the stable SNI/Host returned HTTP 200 from `127.0.0.1` with TLS
  verification result 0.
- The HTTPS probe loaded a page containing the production Office.js URL
  `https://appsforoffice.microsoft.com/lib/1/hosted/office.js`.
- Cross-origin, missing-session, invalid-session, expired-session, and invalid-bootstrap
  tests were rejected. A valid session completed `/api/v1/health`.
- The installed-secret scan found no durable secret in the manifest, source, generated
  JavaScript, generated HTML, request URLs, or companion logs.
- Installer source contains no `curl`, `wget`, package installation, or other download step.

## Identified non-runtime development requests

- Dependency setup contacted npm and PyPI before installer execution. Those requests build
  the prebuilt spike and are not hidden installer/runtime dependencies.
- Manifest validation contacted Microsoft's
  `validationgateway.omex.office.net` service.
- Word launch displayed a Microsoft AutoUpdate request that reported updates temporarily
  unavailable. It was identified as Microsoft platform behavior; no endpoint-level packet
  trace was retained.
- Production Office.js is an explicit Microsoft CDN dependency and is allowed by the task
  pane CSP. Its load was not observed in Word WKWebView.

## Evidence limits

No packet capture covered a successful Word task-pane startup because the real task pane did
not open. Windows was unavailable. Therefore the complete installation/Word/session/health
network requirement is **BLOCKED**, even though the installer and companion observations
above passed. A future run must capture WebView2 and WKWebView navigation, redirects,
certificate evaluation, cookies, fetch metadata, CSP/CORS, and all Microsoft platform
requests without recording document content or secrets.
