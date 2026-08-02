# Installer spike results

## macOS

The final fresh install, repair, and uninstall paths passed on macOS 26.5.2 after two
feasibility findings were incorporated:

- The unsigned Python feasibility companion cannot use the data-protection Keychain without
  an entitlement (`OSStatus -34018`). The spike therefore uses the user's legacy login
  Keychain through `SecItem*`; no secret enters process arguments or files. A future signed
  package must retest the entitled data-protection Keychain.
- Codex's shell process was denied direct write access to Word's protected container. A
  Finder Automation fallback implements Microsoft's manual `wef` placement procedure. This
  is interactive development sideload behavior, not production deployment evidence.

The installer generated a unique EC root and leaf, constrained the leaf SAN to
`word-researcher.localhost`, trusted the root for the user, created the installation secret,
registered the manifest, and loaded a LaunchAgent. Repair refused incomplete private
material and did not rotate a healthy install. Uninstall removed exact registered state and
verified credential and trust cleanup.

The operating-system resolver returned `ENOTFOUND` for `word-researcher.localhost` while the
raw TLS probe succeeded with explicit loopback resolution. Browser/WKWebView special handling
for `.localhost` remains a real-host blocker, not an invitation to add an insecure fallback.

## Windows

PowerShell spikes implement the intended boundaries but were not executed because no Windows
host, Word Desktop, WebView2, trusted UNC catalog, or policy context was available. They:

- generate per-install material and use Windows Credential Manager;
- import the per-install root into the current-user root store;
- register a testing-only Office network-share catalog with exact `Id`, `Url`, and `Flags`;
- register an at-logon Scheduled Task;
- preserve private material during repair; and
- remove the exact task, trust thumbprint, credential, catalog key, manifest, and files.

PowerShell syntax and behavior, Windows trust prompts, catalog policy, task startup, WebView2,
repair, and uninstall are all **BLOCKED pending a real Windows device**.

## Unproved lifecycle cases

Certificate renewal, expiry, deliberate rotation, rollback to a prior certificate,
revocation behavior, enterprise prohibition of local roots, and production organizational
manifest deployment were not proved. They remain Phase 1 blockers under the roadmap.
