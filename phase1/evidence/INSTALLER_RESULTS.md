# Installer spike results

Test date: **2026-08-02 EDT**.

## macOS final-origin result

The final production candidate is `https://localhost:4179`. The full current-origin
fresh-install/repair/uninstall sequence is **BLOCKED** and is not reported as passing.

Preflight confirmed no listener, LaunchAgent, manifest, application-data directory,
`WordResearcher.Phase1` credential, relevant trusted root, or installer-owned hosts-file
mapping. Word was running with one unsaved document, so the task's safe-restart rule
prohibited quitting Word or continuing into real-host acceptance.

An earlier installer attempt against the rejected `word-researcher.localhost` candidate
generated per-install TLS files and a Keychain credential, then stopped at macOS's required
per-user trust authentication dialog before manifest or LaunchAgent registration. Repair
encountered the same authentication boundary. The partial state was uninstalled; follow-up
checks found no listener, LaunchAgent/plist, manifest, application-data directory,
credential, or trust certificate. That cleanup is useful failure-path evidence but does not
validate the final origin.

Current macOS implementation behavior:

- generates a unique EC root and leaf with final SAN `DNS:localhost`;
- writes private keys with mode `0600` through the TLS adapter;
- stores the installation secret in the user's login Keychain through `SecItem*`;
- installs trust into the user login Keychain and requires the operating-system
  authentication dialog rather than bypassing it;
- places the development manifest in Word's `wef` directory, with a Finder Automation
  fallback when TCC denies direct shell access;
- registers a per-user LaunchAgent and waits for normal, trusted
  `https://localhost:4179/taskpane` readiness;
- keeps repair fail-closed when private material is incomplete; and
- removes exact LaunchAgent, trust, credential, manifest, keys, logs, and state on uninstall.

The login-Keychain choice is a feasibility limitation: the unsigned spike cannot use the
data-protection Keychain without an entitlement (`OSStatus -34018`). A future signed package
must retest the entitled store. No insecure trust or TLS bypass was added.

## Windows implementation result

Windows scripts were refactored into:

- `policy.ps1`: pure installation plan, stable-origin policy, and dry-run output;
- `common.ps1`: install/repair/uninstall coordination;
- `platform.ps1`: filesystem, certificate store, Credential Manager CLI bridge, catalog,
  launcher, and Scheduled Task mechanics; and
- `tests/phase1.tests.ps1`: parser, dry-run, isolated lifecycle, production-origin, repeated
  repair, duplicate-root, credential cleanup, trust cleanup, manifest cleanup, and task
  cleanup checks.

The final Windows workflow targets `windows-2025` and is configured to execute the isolated
lifecycle with a temporary catalog and application-data directory. It has not executed
against the final source because commit/push authorization was not provided. Windows trust,
Credential Manager, certificate store, Scheduled Task, catalog, and cleanup results are
therefore **BLOCKED**, not passed.

## Distribution-only work

Production signing/notarization, enterprise deployment, upgrades, rollback, and a full
certificate rotation/revocation framework remain later distribution work. They are not
substitutes for the present blocked real-host and runner checks.

## macOS continuation — actual final-origin lifecycle

This dated result supersedes the earlier final-origin installer blockage while preserving
that history.

### Clean pre-install

Word and the companion were stopped. Port 4179 had no listener. The LaunchAgent/plist,
active manifest, application directory, Keychain credential, and relevant login/system
trust certificates were absent. `/etc/hosts` contained only standard localhost mappings;
normal resolution returned `127.0.0.1` and `::1`, both loopback.

### Fresh install and installed origin

Fresh installation passed with the normal macOS trust/authentication flow. It provisioned:

- listener `127.0.0.1:4179` only;
- server subject `CN=localhost`, issuer `CN=Word Researcher Local Root`, SAN
  `DNS:localhost`, and a per-install root;
- root/server private-key mode `0600`;
- installer-owned `runtime`, `content`, and `tls` directories at mode `0700`;
- one login-Keychain credential;
- one relevant login-Keychain trusted root and none in the system keychain;
- one LaunchAgent with `KeepAlive` and `RunAtLoad`; and
- one active Word development manifest.

Normal `https://localhost:4179/taskpane` returned HTTP 200 from `127.0.0.1` with TLS verify
result 0. `/api/v1/health` returned 401 without a session. The final exact-source install
used leaf SHA-256
`7a2de5d1ae378df9534252f6fb20310c24161a334ee0a57c5e58bcabe3ef579e`
and root SHA-256
`b3d7446bd3a202add5e109b60b83a87066c65194eb73b17238d8703a39641ca2`.
The generated client completed bootstrap/session/authenticated health with status `ok`.

### Real-host defect and repair finding

The first real Word attempt found that the installed LaunchAgent still served late-bound
assets from the checkout under `Documents`; TCC denied the read and produced HTTP 500. The
installer was corrected to stage companion source, migrations, and task-pane assets under
the private application runtime. The same staging boundary was applied to Windows launcher
design. After repair, the pane loaded without that exception.

Diagnostic repairs preserved the credential and certificate material and restored one
LaunchAgent, manifest, and trusted root. They are not counted as the two repair acceptance
passes because the initial real Word session later failed its strict Origin boundary.

### Uninstall

Full uninstall passed twice, including the final exact-source cycle. It removed the
listener/process, LaunchAgent/plist, active manifest, credential, server key/certificate,
installer root/key, logs, state, staged runtime, and application-data directory. Login and
system relevant-certificate counts were both zero, `https://localhost:4179` no longer
responded, and Word no longer offered the developer add-in after restart. Finder moved
removed manifests to Trash; those copies were inactive and recorded as such.

No installer downloader exists or ran. System `curl` was used only for the exact local
readiness URL. The installer result is PASS; the separate real Word session result is FAIL.
