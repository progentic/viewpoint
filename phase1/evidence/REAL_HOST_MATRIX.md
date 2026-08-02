# Phase 1 real-host feasibility matrix

Test date: **2026-08-02 EDT**. A `PASS` below means the named operation was directly
observed. `BLOCKED` is not a failure disguised as a pass; it identifies missing real-host
or platform access.

## Test environments

| Field | Windows | macOS |
| :--- | :--- | :--- |
| Operating system | No Windows device available | macOS 26.5.2 (25F84), arm64 |
| Word version | Not available | 16.109.3, bundle build 16.109.26053122 |
| Update channel | Not available | Not exposed by local Microsoft AutoUpdate preferences; unknown |
| Installation type | Not available | Locally installed `/Applications/Microsoft Word.app`; license/deployment source not inspected |
| Spike installation type | Not run | Unsigned local feasibility scripts and development manifest sideload |
| Policy dependencies | Windows trust, Credential Manager, Scheduled Tasks, Office trusted catalogs, WebView2 | Login Keychain, per-user certificate trust, Finder Automation/TCC, LaunchAgents, Word WKWebView |

## Required operations

| Operation | Windows Word Desktop | macOS Word Desktop | Evidence or blocker |
| :--- | :--- | :--- | :--- |
| Fresh companion installation | BLOCKED | PASS | Final macOS install exited 0 and created unique Keychain/TLS material, trust, manifest, and LaunchAgent. No Windows host existed. |
| Manifest availability | BLOCKED | BLOCKED | Finder placed the XML in Word's `wef` folder, but availability inside a freshly restarted Word UI was not safely confirmed. |
| Word launch | BLOCKED | PASS | `open -na 'Microsoft Word'` succeeded and created a separate Word process. |
| Task pane opens | BLOCKED | BLOCKED | The existing Word process held a user document; a safe full restart was not performed, and the separate process exposed no usable window. |
| Office.js initializes | BLOCKED | BLOCKED | No real task pane opened. Static/build tests are not substituted. |
| Loopback TLS is trusted | BLOCKED | BLOCKED | macOS system trust and TLS passed with `ssl_verify_result=0`, but Word WKWebView trust was not observed. |
| Local session is established | BLOCKED | BLOCKED | Authenticated automated tests pass; no real Word cookie trace exists. |
| `/health` succeeds | BLOCKED | BLOCKED | Generated-client integration passes outside Word; no real Word round trip exists. |
| Companion starts predictably | BLOCKED | PASS | LaunchAgent was `state = running`; listener was exactly `127.0.0.1:4179`. |
| Repair behavior works | BLOCKED | PASS | Repair restarted the LaunchAgent and retained root/leaf SHA-256 fingerprints and origin. |
| Uninstall completes | BLOCKED | PASS | LaunchAgent, listener, manifest, trust root, Keychain secret, and temporary install tree were removed. |
| No undocumented installation download occurs | BLOCKED | BLOCKED | macOS installer contains no downloader and made no observed external companion connection; full Word/task-pane network observation was not possible. |

## macOS procedure and sanitized results

1. Built locked assets, validated the manifest, and ran the fresh installer with
   `WORD_RESEARCHER_DATA=/tmp/word-researcher-phase1-install`.
2. Shell access to Word's protected container returned `Operation not permitted`; the
   installer used its Finder-mediated fallback and successfully registered the manifest.
3. `launchctl print gui/501/local.word-researcher.companion` reported `state = running`.
4. `lsof` reported only `TCP 127.0.0.1:4179 (LISTEN)` for the companion.
5. `/usr/bin/curl --resolve word-researcher.localhost:4179:127.0.0.1 ... /taskpane`
   reported `200 127.0.0.1 0` (status, remote address, TLS verification result).
6. Successful repair retained root fingerprint
   `f9576470af7331f863add2a2880de06128310ab17b6da65ea28150efe71b132d`
   and leaf fingerprint
   `0c72e213e5781633336a49f92998e9857c9a42d00689f16ecb69f711c1ce77e7`.
7. A durable-secret scan of source, generated browser assets, manifest, and logs passed.
8. Word launched, but the safe-host limitation described in the table stopped the task-pane
   procedure before any WKWebView claim.
9. Uninstall exited 0; follow-up checks found no service, listener, manifest, certificate,
   installation tree, or Keychain item.

The screenshots used for local UI inspection stayed in `/tmp` and are not product or release
artifacts. No user document was closed or modified for this spike.
