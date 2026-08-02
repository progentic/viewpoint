#!/bin/zsh
set -euo pipefail

SCRIPT_DIRECTORY=${0:A:h}
PROJECT_ROOT=${SCRIPT_DIRECTORY:h:h}
PYTHON_EXECUTABLE=${PYTHON_EXECUTABLE:-"$PROJECT_ROOT/.venv/bin/python"}
APP_DATA=${WORD_RESEARCHER_DATA:-"$HOME/Library/Application Support/WordResearcher"}
LAUNCH_AGENT="$HOME/Library/LaunchAgents/local.word-researcher.companion.plist"
MANIFEST_DIRECTORY="$HOME/Library/Containers/com.microsoft.Word/Data/Documents/wef"
WORD_DOCUMENTS="$HOME/Library/Containers/com.microsoft.Word/Data/Documents"
LOGIN_KEYCHAIN="$HOME/Library/Keychains/login.keychain-db"

verify_private_material() {
  local required
  for required in root-ca.pem root-ca-key.pem server-cert.pem server-key.pem tls-metadata.json; do
    [[ -f "$APP_DATA/tls/$required" ]] || { print -u2 "TLS repair requires reinstall: $required is missing"; return 1; }
  done
  PYTHONPATH="$PROJECT_ROOT/companion/src" "$PYTHON_EXECUTABLE" \
    -m researcher_companion.install_cli check-secret
}

repair_public_registration() {
  security add-trusted-cert -r trustRoot -k "$LOGIN_KEYCHAIN" "$APP_DATA/tls/root-ca.pem"
  if ! { mkdir -p "$MANIFEST_DIRECTORY" 2>/dev/null && cp "$PROJECT_ROOT/manifest/word-researcher.xml" "$MANIFEST_DIRECTORY/word-researcher.xml" 2>/dev/null; }; then
    osascript "$SCRIPT_DIRECTORY/word_manifest.applescript" register \
      "$PROJECT_ROOT/manifest/word-researcher.xml" "$WORD_DOCUMENTS"
  fi
  launchctl bootout "gui/$UID" "$LAUNCH_AGENT" 2>/dev/null || true
  launchctl bootstrap "gui/$UID" "$LAUNCH_AGENT"
}

verify_private_material
repair_public_registration
